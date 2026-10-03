from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,EmailStr,Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token,hash_password
from app.db.session import get_db
from app.models.entities import Agent,Membership,Organization,Role,User
router=APIRouter()
class RegisterRequest(BaseModel):
    organization_name:str=Field(min_length=2,max_length=200)
    industry:str=Field(min_length=2,max_length=100)
    country:str="India"
    timezone:str="Asia/Kolkata"
    email:EmailStr
    password:str=Field(min_length=8,max_length=200)
    full_name:str=Field(min_length=2,max_length=200)
    agent_name:str="AI Employee"
    agent_role:str="AI Assistant"

@router.post("/register",status_code=201)
async def register(payload:RegisterRequest,db:AsyncSession=Depends(get_db)):
    existing=(await db.execute(select(User).where(User.email==payload.email))).scalar_one_or_none()
    if existing: raise HTTPException(409,"Email already registered")
    org=Organization(name=payload.organization_name,industry=payload.industry,country=payload.country,timezone=payload.timezone,contact_email=payload.email)
    user=User(email=payload.email,password_hash=hash_password(payload.password),full_name=payload.full_name)
    db.add_all([org,user]); await db.flush()
    db.add(Membership(user_id=user.id,organization_id=org.id,role=Role.OWNER))
    db.add(Agent(organization_id=org.id,name=payload.agent_name,role=payload.agent_role,greeting=f"Hello, I am {payload.agent_name}. How can I help you?",system_instructions="Never invent live business facts. Verify through authorized tools."))
    await db.commit()
    token=create_access_token(str(user.id),Role.OWNER.value,str(org.id))
    return {"access_token":token,"token_type":"bearer","organization_id":str(org.id)}
