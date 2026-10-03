from uuid import UUID
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.entities import Call
from app.rag.embeddings import get_embedding_provider
from app.rag.retriever import TenantRetriever
from app.runtime.agent import AgentRuntime
from app.runtime.llm import get_llm_provider
from app.services.inventory_service import InventoryService
from app.tools.appointment import BookAppointmentTool
from app.tools.inventory import CheckInventoryTool
from app.tools.appointment_slots import CheckAppointmentSlotsTool
from app.tools.lead import CreateLeadTool

router=APIRouter()

class AgentMessage(BaseModel):
    agent_id:UUID|None=None
    message:str=Field(min_length=1,max_length=5000)
    caller_phone:str|None=Field(default=None,max_length=50)
    tool_name:str|None=None
    tool_arguments:dict|None=None

@router.post("/respond")
async def respond(payload:AgentMessage,ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if ctx.tenant_id is None: raise HTTPException(403,"Tenant context required")
    call=Call(organization_id=ctx.tenant_id,agent_id=payload.agent_id,caller_phone=payload.caller_phone,status="IN_PROGRESS",transcript=json.dumps([{"speaker":"customer","text":payload.message}]),tools_used="[]")
    db.add(call); await db.flush()
    runtime=AgentRuntime(
        TenantRetriever(db,get_embedding_provider()),get_llm_provider(),
        {"check_inventory":CheckInventoryTool(InventoryService(db)),"create_lead":CreateLeadTool(db),"book_appointment":BookAppointmentTool(db),"check_appointment_slots":CheckAppointmentSlotsTool(db)}
    )
    try:
        result=await runtime.respond(ctx.tenant_id,ctx.user_id,payload.agent_id,payload.message,payload.tool_name,payload.tool_arguments)
    except (ValueError,RuntimeError) as exc:
        call.status="FAILED"; call.outcome="ERROR"; await db.commit()
        raise HTTPException(400,str(exc)) from exc
    selected=result.intent.get("name")
    call.status="RESOLVED"; call.outcome=selected or "RAG_RESPONSE"
    call.tools_used=json.dumps([selected] if result.tool_result is not None and selected else [])
    call.transcript=json.dumps([{"speaker":"customer","text":payload.message},{"speaker":"agent","text":result.text},*([{"speaker":"tool","name":selected,"result":result.tool_result}] if result.tool_result is not None else [])],default=str)
    await db.commit()
    return {"call_id":str(call.id),"response":result.text,"tool_result":result.tool_result,"rag_sources":result.rag_sources,"intent":result.intent}
