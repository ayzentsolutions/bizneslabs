from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext,get_auth_context,require_roles
from app.db.session import get_db
from app.models.entities import AuditLog,Role
router=APIRouter()
@router.get("/")
async def audit(ctx:AuthContext=Depends(require_roles(Role.OWNER,Role.ADMIN)),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    rows=(await db.execute(select(AuditLog).where(AuditLog.organization_id==ctx.tenant_id).order_by(AuditLog.created_at.desc()).limit(200))).scalars().all()
    return {"items":[{"id":str(x.id),"action":x.action,"resource_type":x.resource_type,"resource_id":x.resource_id,"metadata":x.metadata_json,"created_at":x.created_at.isoformat()} for x in rows]}
