from abc import ABC, abstractmethod
from dataclasses import dataclass
import httpx
from app.core.config import settings
from app.rag.schemas import RAGContext

@dataclass(frozen=True)
class GenerationRequest:
    system: str
    user: str
    context: RAGContext
    tool_result: dict | None = None

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> str:
        raise NotImplementedError

class MockGroundedLLM(LLMProvider):
    async def generate(self, request: GenerationRequest) -> str:
        if request.tool_result is not None:
            items=request.tool_result.get("items")
            if items is not None:
                if not items:
                    return "I checked the live inventory and that vehicle is not currently available."
                first=items[0]
                return f"I checked the live inventory. {first['brand']} {first['model']} {first['variant']} in {first['color']} is {first['status'].lower()} at ₹{first['price']:,}."
            if "available_slots" in request.tool_result:
                slots=request.tool_result["available_slots"]
                return "Available test-drive slots: " + (", ".join(slots) if slots else "none today.")
            if request.tool_result.get("status")=="BOOKED":
                return f"Your appointment is booked for {request.tool_result.get('starts_at')}."
        if request.context.chunks:
            return "Based on the verified business knowledge: " + " ".join(x.content for x in request.context.chunks[:3])
        return "I don't have verified information for that request yet."

class OpenAICompatibleLLM(LLMProvider):
    async def generate(self, request: GenerationRequest) -> str:
        if not settings.llm_api_key:
            raise RuntimeError("LLM_API_KEY is required for the configured LLM provider")
        context="\n".join(x.content for x in request.context.chunks[:6])
        tool=str(request.tool_result or {})
        messages=[
            {"role":"system","content":request.system+"\nVerified retrieval context:\n"+context+"\nVerified tool result:\n"+tool},
            {"role":"user","content":request.user},
        ]
        async with httpx.AsyncClient(timeout=30) as client:
            response=await client.post(
                settings.llm_base_url.rstrip("/")+"/chat/completions",
                headers={"Authorization":f"Bearer {settings.llm_api_key}"},
                json={"model":settings.llm_model,"messages":messages,"temperature":0.2},
            )
            response.raise_for_status()
            data=response.json()
        return data["choices"][0]["message"]["content"]

def get_llm_provider() -> LLMProvider:
    if settings.llm_provider.lower() in {"openai","openai_compatible"}:
        return OpenAICompatibleLLM()
    return MockGroundedLLM()
