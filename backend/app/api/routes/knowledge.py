from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.entities import KnowledgeDocument

router = APIRouter()

class TextDocument(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    source_type: str = "TEXT"

@router.post("/documents", status_code=201)
async def create_document(
    payload: TextDocument,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    if ctx.tenant_id is None:
        raise HTTPException(status_code=403, detail="Tenant context required")
    document = KnowledgeDocument(
        organization_id=ctx.tenant_id,
        title=payload.title,
        source_type=payload.source_type,
        extracted_text=payload.content,
        status="READY",
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return {"id": str(document.id), "title": document.title, "status": document.status}
