from datetime import datetime
from app.models.entities import Appointment
from app.tools.base import AuthorizedTool, ToolContext

class BookAppointmentTool(AuthorizedTool):
    name="book_appointment"
    description="Book a test-drive appointment for a customer in the authenticated tenant."
    def __init__(self, db):
        self.db=db
    async def execute(self, context:ToolContext, arguments:dict)->dict:
        self.validate(arguments)
        required=("customer_name","customer_phone","starts_at")
        if any(not arguments.get(k) for k in required):
            raise ValueError("customer_name, customer_phone and starts_at are required")
        starts_at=datetime.fromisoformat(str(arguments["starts_at"]).replace("Z","+00:00"))
        appointment=Appointment(
            organization_id=context.tenant_id,
            agent_id=context.agent_id,
            customer_name=str(arguments["customer_name"]).strip(),
            customer_phone=str(arguments["customer_phone"]).strip(),
            vehicle=arguments.get("vehicle"),
            starts_at=starts_at,
            status="BOOKED",
        )
        self.db.add(appointment); await self.db.commit(); await self.db.refresh(appointment)
        return {"id":str(appointment.id),"status":"BOOKED","starts_at":appointment.starts_at.isoformat(),"vehicle":appointment.vehicle}
