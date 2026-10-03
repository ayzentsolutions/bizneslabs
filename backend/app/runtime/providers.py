from abc import ABC, abstractmethod
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelMessage:
    role: str
    content: str

class ChatModel(ABC):
    @abstractmethod
    async def complete(self, messages: list[ModelMessage]) -> str:
        raise NotImplementedError

class ConfiguredChatModel(ChatModel):
    """Provider seam for hosted/local LLMs.

    The runtime deliberately does not contain vendor-specific SDK calls.
    A deployment can bind OpenAI-compatible, local, or another provider here.
    """
    async def complete(self, messages: list[ModelMessage]) -> str:
        provider = os.getenv("LLM_PROVIDER", "mock").lower()
        if provider == "mock":
            return messages[-1].content
        raise RuntimeError(f"LLM provider '{provider}' is not configured")

class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio: bytes, content_type: str) -> str:
        raise NotImplementedError

class TextToSpeechProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice: str | None = None) -> bytes:
        raise NotImplementedError

class TelephonyProvider(ABC):
    @abstractmethod
    async def transfer(self, call_id: str, destination: str) -> dict:
        raise NotImplementedError
