from dataclasses import dataclass
from uuid import UUID
from app.rag.retriever import TenantRetriever
from app.runtime.llm import GenerationRequest, LLMProvider
from app.tools.base import AuthorizedTool, ToolContext

@dataclass(frozen=True)
class AgentResponse:
    text: str
    tool_result: dict | None
    rag_sources: list[dict]

class AgentRuntime:
    def __init__(self, retriever: TenantRetriever, llm: LLMProvider, tools: dict[str, AuthorizedTool]):
        self.retriever = retriever
        self.llm = llm
        self.tools = tools

    async def respond(
        self,
        tenant_id: UUID,
        user_id: UUID | None,
        agent_id: UUID | None,
        message: str,
        tool_name: str | None = None,
        tool_arguments: dict | None = None,
    ) -> AgentResponse:
        tool_result = None
        if tool_name:
            tool = self.tools.get(tool_name)
            if not tool:
                raise ValueError("Unknown or unauthorized tool")
            tool_result = await tool.execute(
                ToolContext(tenant_id=tenant_id, user_id=user_id, agent_id=agent_id),
                tool_arguments or {},
            )
        rag = await self.retriever.retrieve(tenant_id, message)
        generated = await self.llm.generate(
            GenerationRequest(
                system="Use retrieved tenant knowledge only. Never invent live business facts.",
                user=message,
                context=rag,
            )
        )
        return AgentResponse(
            text=generated,
            tool_result=tool_result,
            rag_sources=[
                {"document_id": str(c.document_id), "chunk_id": str(c.chunk_id), "score": c.score}
                for c in rag.chunks
            ],
        )
