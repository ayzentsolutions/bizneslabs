# BiznesLabs Backend

Python-first backend for a multi-tenant AI employee platform.

Architecture:
- FastAPI + async SQLAlchemy
- PostgreSQL + pgvector
- JWT authentication and RBAC
- Explicit organization/tenant scoping
- RAG ingestion, embeddings and vector retrieval
- Authorized server-side business tools
- Provider interfaces for LLM, embeddings, STT, TTS and telephony

The LLM is not the source of truth for dynamic business data. Live tenant tools are authoritative.

Local setup:
1. Copy .env.example to .env and set a strong SECRET_KEY.
2. Run docker compose up -d from this directory.
3. Install dependencies with pip install -e ".[dev]".
4. Run alembic upgrade head.
5. Run python scripts/seed_demo.py.
6. Run uvicorn app.main:app --reload.

Demo credentials are for local development only and must never be used in production.
