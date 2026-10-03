from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.entities import KnowledgeDocument
from app.knowledge.extractors import ExtractorRegistry
from app.rag.embeddings import DeterministicEmbeddingProvider
from app.rag.ingestion import index_document

router=APIRouter()
extractors=ExtractorRegistry()

@router.get("/")
async def list_documents(ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if ctx.tenant_id is None: raise HTTPException(403,"Tenant context required")
    result=await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.organization_id==ctx.tenant_id).order_by(KnowledgeDocument.created_at.desc()))
    return {"items":[{"id":str(x.id),"title":x.title,"source_type":x.source_type,"status":x.status,"created_at":x.created_at.isoformat()} for x in result.scalars().all()]}

@router.post("/upload",status_code=201)
async def upload(file:UploadFile=File(...),ctx:AuthContext=Depends(get_auth_context),db:AsyncSession=Depends(get_db)):
    if ctx.tenant_id is None: raise HTTPException(403,"Tenant context required")
    data=await file.read()
    if len(data)>10*1024*1024: raise HTTPException(413,"Document exceeds 10 MB")
    text=extractors.get(file.filename or "document.txt").extract(file.filename or "",data)
    if not text.strip(): raise HTTPException(400,"Document contains no extractable text")
    doc=KnowledgeDocument(organization_id=ctx.tenant_id,title=file.filename or "Untitled",source_type="UPLOAD",extracted_text=text,status="PROCESSING")
    db.add(doc); await db.commit(); await db.refresh(doc)
    await index_document(db,ctx.tenant_id,doc,DeterministicEmbeddingProvider())
    return {"id":str(doc.id),"title":doc.title,"status":doc.status}
