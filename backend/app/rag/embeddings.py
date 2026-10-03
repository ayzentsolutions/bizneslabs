from abc import ABC, abstractmethod
import hashlib, math
import httpx
from app.core.config import settings

class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self,text:str)->list[float]:
        raise NotImplementedError

class DeterministicEmbeddingProvider(EmbeddingProvider):
    def __init__(self,dimensions:int|None=None):
        self.dimensions=dimensions or settings.vector_dimensions
    async def embed(self,text:str)->list[float]:
        values=[]
        seed=hashlib.sha256(text.encode("utf-8")).digest()
        for index in range(self.dimensions):
            values.append((seed[index%len(seed)]/127.5)-1.0)
        norm=math.sqrt(sum(v*v for v in values)) or 1.0
        return [v/norm for v in values]

class OpenAIEmbeddingProvider(EmbeddingProvider):
    async def embed(self,text:str)->list[float]:
        if not settings.embedding_api_key:
            raise RuntimeError("EMBEDDING_API_KEY is required for the configured embedding provider")
        async with httpx.AsyncClient(timeout=30) as client:
            response=await client.post(
                settings.embedding_base_url.rstrip("/")+"/embeddings",
                headers={"Authorization":f"Bearer {settings.embedding_api_key}"},
                json={"model":settings.embedding_model,"input":text},
            )
            response.raise_for_status()
            vector=response.json()["data"][0]["embedding"]
        if len(vector)!=settings.vector_dimensions:
            raise RuntimeError(f"Embedding dimension {len(vector)} does not match configured {settings.vector_dimensions}")
        return vector

def get_embedding_provider()->EmbeddingProvider:
    if settings.embedding_provider.lower() in {"openai","openai_compatible"}:
        return OpenAIEmbeddingProvider()
    return DeterministicEmbeddingProvider()
