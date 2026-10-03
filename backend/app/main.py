from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Multi-tenant AI agent infrastructure with RAG and authorized business tools.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "bizneslabs-api"}

@app.get("/api/v1", tags=["system"])
async def api_root() -> dict[str, str]:
    return {"service": "bizneslabs-api", "version": "v1"}
