from dataclasses import dataclass
from app.rag.safety import sanitize_untrusted_text

@dataclass(frozen=True)
class RetrievalEvaluation:
    query: str
    expected_document_ids: set[str]
    returned_document_ids: list[str]
    recall_at_k: float

def evaluate_retrieval(query: str, expected_document_ids: set[str], returned_document_ids: list[str]) -> RetrievalEvaluation:
    expected=set(expected_document_ids)
    returned=set(returned_document_ids)
    recall=len(expected & returned)/len(expected) if expected else 1.0
    return RetrievalEvaluation(query=sanitize_untrusted_text(query,1000),expected_document_ids=expected,returned_document_ids=returned_document_ids,recall_at_k=recall)
