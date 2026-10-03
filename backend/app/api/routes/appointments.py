from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.entities import Appointment

router=APIRouter()

class AppointmentCreate(BaseModel):
    customer_name:str
    customer_phone:str
    vehicle:str|None=None
    starts_at:datetime
    lead_id:str|None=None
    agent_id:str|None=None

@router.get("/")
async def list_appointments(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if ctx.tenant_id is None: raise HTTPException(403,"Tenant context required")
    result=await db.execute(select(Appointment).where(Appointment.organization_id==ctx.tenant_id).order_by(Appointment.starts_at))
    return {"items":[{"id":str(x.id),"customer_name":x.customer_name,"vehicle":x.vehicle,"starts_at":x.starts_at.isoformat(),"status":x.status} for x in result.scalars().all()]}

@router.post("/",status_code=201)
async def book(payload:AppointmentCreate,ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if ctx.tenant_id is None: raise HTTPException(403,"Tenant context required")
    appointment=Appointment(organization_id=ctx.tenant_id,customer_name=payload.customer_name,customer_phone=payload.customer_phone,vehicle=payload.vehicle,starts_at=payload.starts_at,status="BOOKED")
    db.add(appointment); await db.commit(); await db.refresh(appointment)
    return {"id":str(appointment.id),"status":appointment.status}
