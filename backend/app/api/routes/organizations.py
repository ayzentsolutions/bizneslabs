from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.entities import Organization

router = APIRouter()

@router.get("/me")
async def current_organization(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    if ctx.tenant_id is None:
        return {"organization": None, "role": ctx.role.value}
    result = await db.execute(select(Organization).where(Organization.id == ctx.tenant_id))
    organization = result.scalar_one_or_none()
    if not organization:
        return {"organization": None, "role": ctx.role.value}
    return {
        "organization": {
            "id": str(organization.id),
            "name": organization.name,
            "industry": organization.industry,
            "country": organization.country,
            "timezone": organization.timezone,
        },
        "role": ctx.role.value,
    }
