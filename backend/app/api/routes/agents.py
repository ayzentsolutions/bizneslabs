from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context, require_roles
from app.db.session import get_db
from app.models.entities import Agent, Role

router = APIRouter()

class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    role: str = Field(min_length=1, max_length=150)
    description: str = ""
    language: str = "en-IN"
    greeting: str = ""
    personality: str = ""
    system_instructions: str = ""

@router.get("/")
async def list_agents(ctx: AuthContext = Depends(get_auth_context), db: AsyncSession = Depends(get_db)):
    if ctx.tenant_id is None:
        raise HTTPException(status_code=403, detail="Tenant context required")
    result = await db.execute(select(Agent).where(Agent.organization_id == ctx.tenant_id))
    return {"items": [
        {"id": str(a.id), "name": a.name, "role": a.role, "language": a.language, "active": a.active}
        for a in result.scalars().all()
    ]}

@router.post("/", status_code=201)
async def create_agent(
    payload: AgentCreate,
    ctx: AuthContext = Depends(require_roles(Role.OWNER, Role.ADMIN, Role.AGENT_MANAGER)),
    db: AsyncSession = Depends(get_db),
):
    if ctx.tenant_id is None:
        raise HTTPException(status_code=403, detail="Tenant context required")
    agent = Agent(organization_id=ctx.tenant_id, **payload.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return {"id": str(agent.id), "name": agent.name, "role": agent.role}
