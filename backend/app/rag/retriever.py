from uuid import UUID
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import KnowledgeChunk
from app.rag.embeddings import DeterministicEmbeddingProvider,EmbeddingProvider
from app.rag.schemas import RAGContext,RetrievedChunk

class TenantRetriever:
    def __init__(self,db:AsyncSession,embeddings:EmbeddingProvider):
        self.db=db; self.embeddings=embeddings

    async def retrieve(self,tenant_id:UUID,query:str,limit:int=6,min_score:float=0.18)->RAGContext:
        if isinstance(self.embeddings,DeterministicEmbeddingProvider):
            return await self._lexical(tenant_id,query,limit)
        vector=await self.embeddings.embed(query)
        statement=(select(KnowledgeChunk,KnowledgeChunk.embedding.cosine_distance(vector).label("distance"))
            .where(KnowledgeChunk.organization_id==tenant_id,KnowledgeChunk.embedding.is_not(None))
            .order_by("distance").limit(max(1,min(limit,20))))
        result=await self.db.execute(statement)
        chunks=[]
        for row in result:
            score=max(0.0,1.0-float(row.distance))
            if score<min_score: continue
            chunks.append(RetrievedChunk(document_id=row.KnowledgeChunk.document_id,chunk_id=row.KnowledgeChunk.id,content=row.KnowledgeChunk.content,score=score))
        return RAGContext(chunks=chunks,query=query)

    async def _lexical(self,tenant_id:UUID,query:str,limit:int)->RAGContext:
        rows=(await self.db.execute(select(KnowledgeChunk).where(KnowledgeChunk.organization_id==tenant_id).limit(2000))).scalars().all()
        terms={x for x in re.findall(r"[a-z0-9]+",query.lower()) if len(x)>2}
        scored=[]
        for row in rows:
            tokens=set(re.findall(r"[a-z0-9]+",row.content.lower()))
            overlap=len(terms&tokens)
            score=overlap/max(len(terms),1)
            if score>0: scored.append((score,row))
        scored.sort(key=lambda x:x[0],reverse=True)
        return RAGContext(chunks=[RetrievedChunk(document_id=row.document_id,chunk_id=row.id,content=row.content,score=score) for score,row in scored[:max(1,min(limit,20))]],query=query)
