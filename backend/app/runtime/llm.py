from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.rag.schemas import RAGContext

@dataclass(frozen=True)
class GenerationRequest:
    system: str
    user: str
    context: RAGContext

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> str:
        raise NotImplementedError

class MockGroundedLLM(LLMProvider):
    async def generate(self, request: GenerationRequest) -> str:
        if request.context.chunks:
            context = " ".join(chunk.content for chunk in request.context.chunks[:3])
            return f"Based on the verified business knowledge: {context}"
        return "I can help with that, but I need verified business data before confirming it."
