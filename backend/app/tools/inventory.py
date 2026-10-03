from app.services.inventory_service import InventoryService
from app.tools.base import AuthorizedTool, ToolContext

class CheckInventoryTool(AuthorizedTool):
    name = "check_inventory"
    description = "Check live inventory for a model, optional variant and color."

    def __init__(self, service: InventoryService):
        self.service = service

    async def execute(self, context: ToolContext, arguments: dict) -> dict:
        self.validate(arguments)
        model = str(arguments.get("model", "")).strip()
        if not model:
            raise ValueError("model is required")
        variant = arguments.get("variant")
        color = arguments.get("color")
        items = await self.service.check_inventory(
            context.tenant_id, model, str(variant).strip() if variant else None,
            str(color).strip() if color else None,
        )
        return {
            "source": "live_tenant_inventory",
            "items": [
                {
                    "id": str(item.id),
                    "model": item.model,
                    "variant": item.variant,
                    "color": item.color,
                    "price": item.price,
                    "status": item.status.value,
                    "stock_quantity": item.stock_quantity,
                }
                for item in items
            ],
        }
