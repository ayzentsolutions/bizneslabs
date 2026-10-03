from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext,get_auth_context,require_roles
from app.db.session import get_db
from app.models.entities import Lead,LeadStatus
router=APIRouter()
class LeadPatch(BaseModel):
    status:LeadStatus|None=None; notes:str|None=None; interested_product:str|None=None; budget:int|None=Field(default=None,ge=0)

@router.patch("/leads/{lead_id}")
async def update_lead(lead_id:UUID,payload:LeadPatch,ctx:AuthContext=Depends(require_roles(*__import__("app.models.entities",fromlist=["Role"]).Role.__members__.values())),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    lead=(await db.execute(select(Lead).where(Lead.id==lead_id,Lead.organization_id==ctx.tenant_id))).scalar_one_or_none()
    if not lead: raise HTTPException(404,"Lead not found")
    for k,v in payload.model_dump(exclude_none=True).items(): setattr(lead,k,v)
    await db.commit(); await db.refresh(lead)
    return {"id":str(lead.id),"status":lead.status.value,"notes":lead.notes}
