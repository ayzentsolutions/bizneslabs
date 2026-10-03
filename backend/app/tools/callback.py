import re
from app.models.entities import Lead
from app.tools.base import AuthorizedTool,ToolContext
class ScheduleCallbackTool(AuthorizedTool):
    name="schedule_callback"
    description="Create a callback request for a customer after collecting a phone number."
    def __init__(self,db): self.db=db
    async def execute(self,context:ToolContext,arguments:dict)->dict:
        self.validate(arguments)
        phone=str(arguments.get("phone","")).strip()
        name=str(arguments.get("name","Customer")).strip() or "Customer"
        if not re.fullmatch(r"[+0-9() .-]{7,30}",phone): raise ValueError("A valid callback phone number is required")
        lead=Lead(organization_id=context.tenant_id,name=name,phone=phone,interested_product=arguments.get("interested_product"),notes="Callback requested through AI employee",source="AI_AGENT")
        self.db.add(lead); await self.db.commit(); await self.db.refresh(lead)
        return {"id":str(lead.id),"status":lead.status.value,"callback_requested":True,"phone":lead.phone}
