from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router=APIRouter()

@router.get("/")
async def health():
    return {"status":"ok","service":"bizneslabs-api"}

@router.get("/ready")
async def readiness(db:AsyncSession=__import__("fastapi").Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status":"ready","database":"ok"}
