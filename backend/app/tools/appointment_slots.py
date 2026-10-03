from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.models.entities import Appointment
from app.tools.base import AuthorizedTool, ToolContext

class CheckAppointmentSlotsTool(AuthorizedTool):
    name="check_appointment_slots"
    description="Return available test-drive slots for the authenticated tenant."
    def __init__(self, db):
        self.db=db
    async def execute(self, context:ToolContext, arguments:dict)->dict:
        self.validate(arguments)
        start=datetime.now(timezone.utc).replace(hour=9,minute=0,second=0,microsecond=0)
        slots=[start+timedelta(hours=h) for h in (0,1,3,5,7)]
        result=await self.db.execute(select(Appointment.starts_at).where(
            Appointment.organization_id==context.tenant_id,
            Appointment.starts_at>=start,
            Appointment.starts_at<start+timedelta(days=1),
            Appointment.status=="BOOKED",
        ))
        booked={x[0].replace(second=0,microsecond=0) for x in result.all()}
        available=[x.isoformat() for x in slots if x not in booked]
        return {"date":start.date().isoformat(),"available_slots":available}
