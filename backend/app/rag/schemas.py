from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class RetrievedChunk:
    document_id: UUID
    chunk_id: UUID
    content: str
    score: float

@dataclass(frozen=True)
class RAGContext:
    chunks: list[RetrievedChunk]
    query: str
