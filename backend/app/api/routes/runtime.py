from uuid import UUID
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.entities import Call
from app.rag.embeddings import DeterministicEmbeddingProvider
from app.rag.retriever import TenantRetriever
from app.runtime.agent import AgentRuntime
from app.runtime.llm import MockGroundedLLM
from app.services.inventory_service import InventoryService
from app.tools.appointment import BookAppointmentTool
from app.tools.inventory import CheckInventoryTool
from app.tools.lead import CreateLeadTool

router = APIRouter()

class AgentMessage(BaseModel):
    agent_id: UUID | None = None
    message: str = Field(min_length=1, max_length=5000)
    caller_phone: str | None = Field(default=None, max_length=50)
    tool_name: str | None = None
    tool_arguments: dict | None = None

@router.post("/respond")
async def respond(payload: AgentMessage, ctx: AuthContext = Depends(get_auth_context), db: AsyncSession = Depends(get_db)):
    if ctx.tenant_id is None:
        raise HTTPException(status_code=403, detail="Tenant context required")
    call = Call(
        organization_id=ctx.tenant_id, agent_id=payload.agent_id,
        caller_phone=payload.caller_phone, status="IN_PROGRESS",
        transcript=json.dumps([{"speaker":"customer","text":payload.message}]),
        tools_used="[]",
    )
    db.add(call)
    await db.flush()
    runtime = AgentRuntime(
        TenantRetriever(db, DeterministicEmbeddingProvider()),
        MockGroundedLLM(),
        {
            "check_inventory": CheckInventoryTool(InventoryService(db)),
            "create_lead": CreateLeadTool(db),
            "book_appointment": BookAppointmentTool(db),
        },
    )
    try:
        result = await runtime.respond(
            ctx.tenant_id, ctx.user_id, payload.agent_id, payload.message,
            payload.tool_name, payload.tool_arguments,
        )
    except ValueError as exc:
        call.status = "FAILED"
        await db.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    call.status = "RESOLVED"
    call.outcome = payload.tool_name or "RAG_RESPONSE"
    call.tools_used = json.dumps([payload.tool_name] if payload.tool_name else [])
    call.transcript = json.dumps([
        {"speaker":"customer","text":payload.message},
        {"speaker":"agent","text":result.text},
        *([{"speaker":"tool","name":payload.tool_name,"result":result.tool_result}] if payload.tool_name else []),
    ], default=str)
    await db.commit()
    return {
        "call_id": str(call.id),
        "response": result.text,
        "tool_result": result.tool_result,
        "rag_sources": result.rag_sources,
    }
