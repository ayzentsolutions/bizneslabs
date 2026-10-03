from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.entities import Appointment, Call, Lead

router=APIRouter()

@router.get("/overview")
async def overview(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if ctx.tenant_id is None: raise HTTPException(403,"Tenant context required")
    since=datetime.now(timezone.utc)-timedelta(days=1)
    calls=(await db.execute(select(func.count(Call.id)).where(Call.organization_id==ctx.tenant_id,Call.created_at>=since))).scalar_one()
    leads=(await db.execute(select(func.count(Lead.id)).where(Lead.organization_id==ctx.tenant_id,Lead.created_at>=since))).scalar_one()
    appointments=(await db.execute(select(func.count(Appointment.id)).where(Appointment.organization_id==ctx.tenant_id,Appointment.created_at>=since))).scalar_one()
    return {"period":"last_24_hours","calls":calls,"leads":leads,"appointments":appointments}
