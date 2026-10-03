from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import Select

def require_tenant_id(tenant_id: UUID | None) -> UUID:
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant context required")
    return tenant_id

def tenant_filter(statement: Select, model, tenant_id: UUID) -> Select:
    # All tenant-owned reads must explicitly apply this predicate.
    return statement.where(model.organization_id == tenant_id)
