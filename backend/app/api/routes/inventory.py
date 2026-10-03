from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext,get_auth_context,require_roles
from app.db.session import get_db
from app.models.entities import InventoryItem,InventoryStatus,Role\nfrom app.services.audit import record_audit

router=APIRouter()
class InventoryCreate(BaseModel):
    brand:str=Field(min_length=1,max_length=100); model:str=Field(min_length=1,max_length=100); variant:str=Field(min_length=1,max_length=100)
    color:str=Field(min_length=1,max_length=100); price:int=Field(ge=0); fuel_type:str="Petrol"; transmission:str="Automatic"; year:int=Field(ge=1900,le=2200)
    status:InventoryStatus=InventoryStatus.AVAILABLE; stock_quantity:int=Field(ge=0)
class InventoryPatch(BaseModel):
    price:int|None=Field(default=None,ge=0); status:InventoryStatus|None=None; stock_quantity:int|None=Field(default=None,ge=0); color:str|None=None; variant:str|None=None

def item(x): return {"id":str(x.id),"brand":x.brand,"model":x.model,"variant":x.variant,"color":x.color,"price":x.price,"fuel_type":x.fuel_type,"transmission":x.transmission,"year":x.year,"status":x.status.value,"stock_quantity":x.stock_quantity}

@router.get("/")
async def list_inventory(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    rows=(await db.execute(select(InventoryItem).where(InventoryItem.organization_id==ctx.tenant_id).order_by(InventoryItem.model,InventoryItem.variant))).scalars().all()
    return {"items":[item(x) for x in rows]}

@router.post("/",status_code=201)
async def create_inventory(payload:InventoryCreate,ctx:AuthContext=Depends(require_roles(Role.OWNER,Role.ADMIN,Role.AGENT_MANAGER)),db:AsyncSession=Depends(get_db)):
    x=InventoryItem(organization_id=ctx.tenant_id,**payload.model_dump()); db.add(x); await record_audit(db,ctx.tenant_id,ctx.user_id,"CREATE","inventory",str(x.id),{"model":x.model,"status":x.status.value}); await db.commit(); await db.refresh(x); return item(x)

@router.patch("/{item_id}")
async def update_inventory(item_id:UUID,payload:InventoryPatch,ctx:AuthContext=Depends(require_roles(Role.OWNER,Role.ADMIN,Role.AGENT_MANAGER)),db:AsyncSession=Depends(get_db)):
    if not ctx.tenant_id: raise HTTPException(403,"Tenant context required")
    x=(await db.execute(select(InventoryItem).where(InventoryItem.id==item_id,InventoryItem.organization_id==ctx.tenant_id))).scalar_one_or_none()
    if not x: raise HTTPException(404,"Inventory item not found")
    for k,v in payload.model_dump(exclude_none=True).items(): setattr(x,k,v)
    await db.commit(); await db.refresh(x); return item(x)
