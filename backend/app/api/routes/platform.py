from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import func,select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext,require_roles
from app.db.session import get_db
from app.models.entities import Organization,Agent,Call,Membership,Role
router=APIRouter()
@router.get("/overview")
async def overview(ctx:AuthContext=Depends(require_roles(Role.SUPER_ADMIN)),db:AsyncSession=Depends(get_db)):
    return {
        "organizations":(await db.execute(select(func.count(Organization.id)))).scalar_one(),
        "active_organizations":(await db.execute(select(func.count(Organization.id)).where(Organization.active.is_(True)))).scalar_one(),
        "agents":(await db.execute(select(func.count(Agent.id)))).scalar_one(),
        "calls":(await db.execute(select(func.count(Call.id)))).scalar_one(),
        "memberships":(await db.execute(select(func.count(Membership.id)))).scalar_one(),
    }
@router.get("/organizations")
async def organizations(ctx:AuthContext=Depends(require_roles(Role.SUPER_ADMIN)),db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(Organization).order_by(Organization.created_at.desc()).limit(200))).scalars().all()
    return {"items":[{"id":str(x.id),"name":x.name,"industry":x.industry,"country":x.country,"active":x.active,"created_at":x.created_at.isoformat()} for x in rows]}
@router.patch("/organizations/{organization_id}/status")
async def status(organization_id,active:bool,ctx:AuthContext=Depends(require_roles(Role.SUPER_ADMIN)),db:AsyncSession=Depends(get_db)):
    org=(await db.execute(select(Organization).where(Organization.id==organization_id))).scalar_one_or_none()
    if not org: raise HTTPException(404,"Organization not found")
    org.active=active; await db.commit(); return {"id":str(org.id),"active":org.active}
