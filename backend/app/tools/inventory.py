from app.services.inventory_service import InventoryService
from app.tools.base import AuthorizedTool, ToolContext

class CheckInventoryTool(AuthorizedTool):
    name="check_inventory"
    description="Check live vehicle inventory. Never infer availability from language-model knowledge."
    def __init__(self, service:InventoryService):
        self.service=service
    async def execute(self, context:ToolContext, arguments:dict)->dict:
        self.validate(arguments)
        model=str(arguments.get("model","")).strip()
        if not model: raise ValueError("model is required")
        items=await self.service.check_inventory(context.tenant_id,model,arguments.get("variant"),arguments.get("color"))
        return {"items":[
            {"id":str(x.id),"brand":x.brand,"model":x.model,"variant":x.variant,"color":x.color,
             "price":x.price,"status":x.status.value,"stock_quantity":x.stock_quantity,
             "fuel_type":x.fuel_type,"transmission":x.transmission,"year":x.year}
            for x in items
        ]}
