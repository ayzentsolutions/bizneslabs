from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class ToolContext:
    tenant_id: UUID
    user_id: UUID | None = None
    agent_id: UUID | None = None

class AuthorizedTool:
    name: str
    description: str
    async def execute(self, context: ToolContext, arguments: dict) -> dict:
        raise NotImplementedError
    def validate(self, arguments: dict) -> None:
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object")
        if len(arguments) > 20:
            raise ValueError("Too many tool arguments")
        for key, value in arguments.items():
            if len(str(key)) > 100 or len(str(value)) > 2000:
                raise ValueError("Tool argument exceeds allowed size")
