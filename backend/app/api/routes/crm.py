from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext,get_auth_context,require_roles
from app.db.session import get_db
from app.models.entities import Lead,LeadStatus,Role\nfrom app.services.audit import record_audit
router=APIRouter()
class LeadPatch(BaseModel):
    status:LeadStatus|None=None
    notes:str|None=None
    interested_product:str|None=None
    budget:int|None=Field(default=None,ge=0)

@router.get("/leads")
async def leads(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    rows=(await db.execute(select(Lead).where(Lead.organization_id==ctx.tenant_id).order_by(Lead.created_at.desc()).limit(500))).scalars().all()
    return {"items":[{"id":str(x.id),"name":x.name,"phone":x.phone,"email":x.email,"status":x.status.value,"interested_product":x.interested_product,"budget":x.budget,"notes":x.notes,"created_at":x.created_at.isoformat()} for x in rows]}

@router.patch("/leads/{lead_id}")
async def update_lead(lead_id:UUID,payload:LeadPatch,ctx:AuthContext=Depends(require_roles(Role.OWNER,Role.ADMIN,Role.AGENT_MANAGER)),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    lead=(await db.execute(select(Lead).where(Lead.id==lead_id,Lead.organization_id==ctx.tenant_id))).scalar_one_or_none()
    if not lead: raise HTTPException(404,"Lead not found")
    for k,v in payload.model_dump(exclude_none=True).items(): setattr(lead,k,v)
    await db.commit(); await db.refresh(lead)
    return {"id":str(lead.id),"status":lead.status.value,"notes":lead.notes}
