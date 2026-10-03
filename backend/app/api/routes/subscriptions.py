from datetime import datetime,timedelta,timezone
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import func,select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext,get_auth_context
from app.db.session import get_db
from app.models.entities import Agent,Call,KnowledgeDocument,Organization
router=APIRouter()
PLANS={
 "starter":{"agents":1,"phone_numbers":1,"minutes":1000,"storage_mb":500},
 "business":{"agents":10,"phone_numbers":5,"minutes":10000,"storage_mb":5000},
 "enterprise":{"agents":100000,"phone_numbers":1000,"minutes":1000000,"storage_mb":100000},
}
@router.get("/plans")
async def plans(): return {"plans":PLANS}
@router.get("/usage")
async def usage(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    since=datetime.now(timezone.utc)-timedelta(days=30)
    calls=(await db.execute(select(func.count(Call.id)).where(Call.organization_id==ctx.tenant_id,Call.created_at>=since))).scalar_one()
    seconds=(await db.execute(select(func.coalesce(func.sum(Call.duration_seconds),0)).where(Call.organization_id==ctx.tenant_id,Call.created_at>=since))).scalar_one()
    agents=(await db.execute(select(func.count(Agent.id)).where(Agent.organization_id==ctx.tenant_id,Agent.active.is_(True)))).scalar_one()
    docs=(await db.execute(select(func.count(KnowledgeDocument.id)).where(KnowledgeDocument.organization_id==ctx.tenant_id))).scalar_one()
    return {"period":"30_days","plan":"business","calls":calls,"voice_minutes":round(float(seconds)/60,2),"active_agents":agents,"documents":docs,"limits":PLANS["business"]}
@router.get("/current")
async def current(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    org=(await db.execute(select(Organization).where(Organization.id==ctx.tenant_id))).scalar_one()
    return {"organization_id":str(org.id),"plan":"business","status":"ACTIVE"}
