from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import InventoryItem, InventoryStatus

class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_inventory(
        self, tenant_id: UUID, model: str, variant: str | None = None, color: str | None = None
    ) -> list[InventoryItem]:
        statement = select(InventoryItem).where(
            InventoryItem.organization_id == tenant_id,
            InventoryItem.model.ilike(model),
        )
        if variant:
            statement = statement.where(InventoryItem.variant.ilike(variant))
        if color:
            statement = statement.where(InventoryItem.color.ilike(color))
        result = await self.db.execute(statement.order_by(InventoryItem.created_at.desc()))
        return list(result.scalars().all())

    async def set_status(self, tenant_id: UUID, item_id: UUID, status: InventoryStatus) -> InventoryItem:
        result = await self.db.execute(
            select(InventoryItem).where(
                InventoryItem.id == item_id,
                InventoryItem.organization_id == tenant_id,
            )
        )
        item = result.scalar_one()
        item.status = status
        await self.db.commit()
        await self.db.refresh(item)
        return item
