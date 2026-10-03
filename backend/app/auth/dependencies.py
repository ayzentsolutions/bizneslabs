from dataclasses import dataclass
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.security import decode_access_token
from app.models.entities import Role

bearer = HTTPBearer(auto_error=True)

@dataclass(frozen=True)
class AuthContext:
    user_id: UUID
    role: Role
    tenant_id: UUID | None

async def get_auth_context(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> AuthContext:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
        role = Role(payload["role"])
        tenant_id = UUID(payload["tenant_id"]) if payload.get("tenant_id") else None
        return AuthContext(user_id=user_id, role=role, tenant_id=tenant_id)
    except (KeyError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc

def require_roles(*roles: Role):
    async def dependency(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if ctx.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return ctx
    return dependency
