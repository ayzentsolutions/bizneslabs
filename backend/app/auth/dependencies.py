from dataclasses import dataclass
from uuid import UUID
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.entities import Membership,Organization,Role,User

bearer=HTTPBearer(auto_error=True)

@dataclass(frozen=True)
class AuthContext:
    user_id:UUID
    role:Role
    tenant_id:UUID|None

async def get_auth_context(credentials:HTTPAuthorizationCredentials=Depends(bearer),db:AsyncSession=Depends(get_db))->AuthContext:
    try:
        payload=decode_access_token(credentials.credentials)
        user_id=UUID(payload["sub"]); role=Role(payload["role"])
        tenant_id=UUID(payload["tenant_id"]) if payload.get("tenant_id") else None
    except (KeyError,ValueError,TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid authentication token")
    user=(await db.execute(select(User).where(User.id==user_id,User.active.is_(True)))).scalar_one_or_none()
    if not user: raise HTTPException(status_code=401,detail="User is inactive or no longer exists")
    if tenant_id is not None:
        membership=(await db.execute(select(Membership).where(Membership.user_id==user_id,Membership.organization_id==tenant_id,Membership.role==role))).scalar_one_or_none()
        org=(await db.execute(select(Organization).where(Organization.id==tenant_id,Organization.active.is_(True)))).scalar_one_or_none()
        if not membership or not org: raise HTTPException(status_code=403,detail="Tenant access is no longer active")
    return AuthContext(user_id=user_id,role=role,tenant_id=tenant_id)

def require_roles(*roles:Role):
    async def dependency(ctx:AuthContext=Depends(get_auth_context))->AuthContext:
        if ctx.role not in roles: raise HTTPException(status_code=403,detail="Insufficient permissions")
        return ctx
    return dependency
