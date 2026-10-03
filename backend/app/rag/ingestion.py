from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import KnowledgeChunk, KnowledgeDocument
from app.rag.embeddings import EmbeddingProvider

def chunk_text(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    chunks = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + size)
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = max(end - overlap, start + 1)
    return chunks

async def index_document(
    db: AsyncSession,
    tenant_id: UUID,
    document: KnowledgeDocument,
    embeddings: EmbeddingProvider,
) -> int:
    chunks = chunk_text(document.extracted_text)
    for index, content in enumerate(chunks):
        vector = await embeddings.embed(content)
        db.add(KnowledgeChunk(
            organization_id=tenant_id,
            document_id=document.id,
            content=content,
            embedding=vector,
            chunk_index=index,
        ))
    document.status = "INDEXED"
    await db.commit()
    return len(chunks)
