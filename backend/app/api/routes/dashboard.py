from datetime import datetime,timedelta,timezone
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import func,select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext,get_auth_context
from app.db.session import get_db
from app.models.entities import Agent,Appointment,Call,InventoryItem,Lead
router=APIRouter()
@router.get("/summary")
async def summary(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    since=datetime.now(timezone.utc)-timedelta(days=1)
    def count(model): return select(func.count(model.id)).where(model.organization_id==ctx.tenant_id,model.created_at>=since)
    return {
        "calls_24h":(await db.execute(count(Call))).scalar_one(),
        "leads_24h":(await db.execute(count(Lead))).scalar_one(),
        "appointments_24h":(await db.execute(count(Appointment))).scalar_one(),
        "agents":(await db.execute(select(func.count(Agent.id)).where(Agent.organization_id==ctx.tenant_id,Agent.active.is_(True)))).scalar_one(),
        "inventory":(await db.execute(select(func.count(InventoryItem.id)).where(InventoryItem.organization_id==ctx.tenant_id))).scalar_one(),
        "available_inventory":(await db.execute(select(func.count(InventoryItem.id)).where(InventoryItem.organization_id==ctx.tenant_id,InventoryItem.status=="AVAILABLE"))).scalar_one(),
    }
@router.get("/calls")
async def calls(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    rows=(await db.execute(select(Call).where(Call.organization_id==ctx.tenant_id).order_by(Call.created_at.desc()).limit(50))).scalars().all()
    return {"items":[{"id":str(x.id),"caller_phone":x.caller_phone,"status":x.status,"outcome":x.outcome,"duration_seconds":x.duration_seconds,"created_at":x.created_at.isoformat()} for x in rows]}
