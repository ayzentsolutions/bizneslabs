from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db
from app.rag.embeddings import DeterministicEmbeddingProvider
from app.rag.retriever import TenantRetriever
from app.runtime.agent import AgentRuntime
from app.runtime.llm import MockGroundedLLM
from app.services.inventory_service import InventoryService
from app.tools.inventory import CheckInventoryTool

router = APIRouter()

class AgentMessage(BaseModel):
    agent_id: UUID | None = None
    message: str = Field(min_length=1, max_length=5000)
    tool_name: str | None = None
    tool_arguments: dict | None = None

@router.post("/respond")
async def respond(payload: AgentMessage, ctx: AuthContext = Depends(get_auth_context), db: AsyncSession = Depends(get_db)):
    if ctx.tenant_id is None:
        raise HTTPException(status_code=403, detail="Tenant context required")
    embeddings = DeterministicEmbeddingProvider()
    retriever = TenantRetriever(db, embeddings)
    inventory = CheckInventoryTool(InventoryService(db))
    runtime = AgentRuntime(retriever, MockGroundedLLM(), {"check_inventory": inventory})
    try:
        result = await runtime.respond(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id,
            agent_id=payload.agent_id,
            message=payload.message,
            tool_name=payload.tool_name,
            tool_arguments=payload.tool_arguments,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "response": result.text,
        "tool_result": result.tool_result,
        "rag_sources": result.rag_sources,
    }
