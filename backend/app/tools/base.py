from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class ToolContext:
    tenant_id: UUID
    user_id: UUID | None
    agent_id: UUID | None

class AuthorizedTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, context: ToolContext, arguments: dict) -> dict:
        raise NotImplementedError

    def validate(self, arguments: dict) -> None:
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object")
