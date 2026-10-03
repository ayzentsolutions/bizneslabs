from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from app.auth.dependencies import AuthContext,get_auth_context
router=APIRouter()
class VoiceSessionRequest(BaseModel):
    agent_id:UUID|None=None
    caller_phone:str|None=Field(default=None,max_length=50)
@router.post("/sessions",status_code=201)
async def create_session(payload:VoiceSessionRequest,ctx:AuthContext=Depends(get_auth_context)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    return {"session_id":f"voice-{ctx.tenant_id}-{ctx.user_id}","status":"READY","transport":"browser","stt_provider":"configured","tts_provider":"configured","agent_id":str(payload.agent_id) if payload.agent_id else None}
@router.get("/providers")
async def providers(ctx:AuthContext=Depends(get_auth_context)):
    return {"transport":"browser","stt":"provider-abstraction","tts":"provider-abstraction","telephony":"provider-abstraction"}
