from abc import ABC, abstractmethod
import hashlib
import math

class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError

class DeterministicEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 1536):
        self.dimensions = dimensions

    async def embed(self, text: str) -> list[float]:
        # Deterministic development fallback. Production adapters can implement
        # OpenAI, Voyage, Cohere, or local embedding models without changing RAG.
        values = []
        seed = hashlib.sha256(text.encode("utf-8")).digest()
        for index in range(self.dimensions):
            b = seed[index % len(seed)]
            values.append((b / 127.5) - 1.0)
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]
