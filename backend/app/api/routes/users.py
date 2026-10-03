from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext,require_roles
from app.db.session import get_db
from app.models.entities import Membership,Role,User
router=APIRouter()
@router.get("/")
async def users(ctx:AuthContext=Depends(require_roles(Role.OWNER,Role.ADMIN)),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    rows=(await db.execute(select(User,Membership.role).join(Membership,Membership.user_id==User.id).where(Membership.organization_id==ctx.tenant_id).order_by(User.created_at.desc()))).all()
    return {"items":[{"id":str(u.id),"name":u.full_name,"email":u.email,"role":role.value,"active":u.active,"created_at":u.created_at.isoformat()} for u,role in rows]}
