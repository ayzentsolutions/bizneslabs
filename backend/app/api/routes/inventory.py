from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context, require_roles
from app.db.session import get_db
from app.models.entities import InventoryItem, InventoryStatus, Role
from app.services.inventory_service import InventoryService

router = APIRouter()

class StatusUpdate(BaseModel):
    status: InventoryStatus

@router.get("/")
async def list_inventory(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    if ctx.tenant_id is None:
        raise HTTPException(status_code=403, detail="Tenant context required")
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.organization_id == ctx.tenant_id)
        .order_by(InventoryItem.created_at.desc())
    )
    return {"items": [
        {
            "id": str(item.id), "brand": item.brand, "model": item.model,
            "variant": item.variant, "color": item.color, "price": item.price,
            "status": item.status.value, "stock_quantity": item.stock_quantity,
        } for item in result.scalars().all()
    ]}

@router.patch("/{item_id}/status")
async def update_inventory_status(
    item_id: UUID,
    payload: StatusUpdate,
    ctx: AuthContext = Depends(require_roles(Role.OWNER, Role.ADMIN, Role.AGENT_MANAGER)),
    db: AsyncSession = Depends(get_db),
):
    if ctx.tenant_id is None:
        raise HTTPException(status_code=403, detail="Tenant context required")
    try:
        item = await InventoryService(db).set_status(ctx.tenant_id, item_id, payload.status)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Inventory item not found") from exc
    return {"id": str(item.id), "status": item.status.value}
