from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.entities import Lead, LeadStatus

router=APIRouter()

class LeadCreate(BaseModel):
    name:str=Field(min_length=1,max_length=200)
    phone:str=Field(min_length=3,max_length=50)
    email:str|None=None
    interested_product:str|None=None
    budget:int|None=None
    notes:str=""

@router.get("/")
async def list_leads(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if ctx.tenant_id is None: raise HTTPException(403,"Tenant context required")
    result=await db.execute(select(Lead).where(Lead.organization_id==ctx.tenant_id).order_by(Lead.created_at.desc()))
    return {"items":[{"id":str(x.id),"name":x.name,"phone":x.phone,"status":x.status.value,"interested_product":x.interested_product} for x in result.scalars().all()]}

@router.post("/",status_code=201)
async def create_lead(payload:LeadCreate,ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if ctx.tenant_id is None: raise HTTPException(403,"Tenant context required")
    lead=Lead(organization_id=ctx.tenant_id,**payload.model_dump())
    db.add(lead); await db.commit(); await db.refresh(lead)
    return {"id":str(lead.id),"status":lead.status.value}
