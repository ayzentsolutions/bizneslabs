from fastapi import APIRouter,Depends,HTTPException,status
from pydantic import BaseModel,EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext,get_auth_context
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.entities import Membership
from app.services.auth_service import AuthService

router=APIRouter()
class LoginRequest(BaseModel):
    email:EmailStr
    password:str
class TokenResponse(BaseModel):
    access_token:str
    token_type:str="bearer"
    memberships:list[dict]=[]
class SwitchRequest(BaseModel):
    organization_id:str

@router.post("/login",response_model=TokenResponse)
async def login(payload:LoginRequest,db:AsyncSession=Depends(get_db)):
    try: user,membership=await AuthService(db).authenticate(payload.email,payload.password)
    except ValueError as exc: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=str(exc)) from exc
    memberships=(await db.execute(select(Membership).where(Membership.user_id==user.id).order_by(Membership.id))).scalars().all()
    return TokenResponse(
        access_token=AuthService(db).issue_token(user,membership),
        memberships=[{"organization_id":str(x.organization_id),"role":x.role.value} for x in memberships],
    )

@router.post("/switch")
async def switch(payload:SwitchRequest,ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    from uuid import UUID
    try: organization_id=UUID(payload.organization_id)
    except ValueError: raise HTTPException(400,"Invalid organization id")
    membership=(await db.execute(select(Membership).where(Membership.user_id==ctx.user_id,Membership.organization_id==organization_id))).scalar_one_or_none()
    if not membership: raise HTTPException(403,"You do not belong to that organization")
    return {"access_token":create_access_token(str(ctx.user_id),membership.role.value,str(membership.organization_id)),"token_type":"bearer","organization_id":str(organization_id),"role":membership.role.value}
