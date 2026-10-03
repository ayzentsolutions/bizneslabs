from sqlalchemy import select
from app.models.entities import Lead
from app.tools.base import AuthorizedTool,ToolContext

class CreateLeadTool(AuthorizedTool):
    name="create_lead"
    description="Create or reuse a customer lead inside the authenticated tenant."
    def __init__(self,db): self.db=db
    async def execute(self,context:ToolContext,arguments:dict)->dict:
        self.validate(arguments)
        name=str(arguments.get("name","")).strip(); phone=str(arguments.get("phone","")).strip()
        if not name or not phone: raise ValueError("name and phone are required")
        existing=(await self.db.execute(select(Lead).where(Lead.organization_id==context.tenant_id,Lead.phone==phone).order_by(Lead.created_at.desc()).limit(1))).scalar_one_or_none()
        if existing:
            return {"id":str(existing.id),"status":existing.status.value,"name":existing.name,"phone":existing.phone,"deduplicated":True}
        lead=Lead(organization_id=context.tenant_id,name=name,phone=phone,email=arguments.get("email"),interested_product=arguments.get("interested_product"),budget=arguments.get("budget"),notes=str(arguments.get("notes","")),source="AI_AGENT")
        self.db.add(lead); await self.db.commit(); await self.db.refresh(lead)
        return {"id":str(lead.id),"status":lead.status.value,"name":lead.name,"phone":lead.phone,"deduplicated":False}
