from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import KnowledgeChunk
from app.rag.embeddings import EmbeddingProvider
from app.rag.schemas import RAGContext, RetrievedChunk

class TenantRetriever:
    def __init__(self, db: AsyncSession, embeddings: EmbeddingProvider):
        self.db=db
        self.embeddings=embeddings

    async def retrieve(self, tenant_id: UUID, query: str, limit: int = 6, min_score: float = 0.18) -> RAGContext:
        vector=await self.embeddings.embed(query)
        statement=(
            select(
                KnowledgeChunk,
                KnowledgeChunk.embedding.cosine_distance(vector).label("distance"),
            )
            .where(
                KnowledgeChunk.organization_id==tenant_id,
                KnowledgeChunk.embedding.is_not(None),
            )
            .order_by("distance")
            .limit(max(1,min(limit,20)))
        )
        result=await self.db.execute(statement)
        chunks=[]
        for row in result:
            score=max(0.0,1.0-float(row.distance))
            if score < min_score:
                continue
            chunks.append(RetrievedChunk(
                document_id=row.KnowledgeChunk.document_id,
                chunk_id=row.KnowledgeChunk.id,
                content=row.KnowledgeChunk.content,
                score=score,
            ))
        return RAGContext(chunks=chunks,query=query)
