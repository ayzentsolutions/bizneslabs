# BiznesLabs API

FastAPI service for the BiznesLabs multi-tenant AI employee platform.

## Commands
`alembic upgrade head`
`uvicorn app.main:app --reload`
`python scripts/seed_demo.py`
`pytest -q`

The API uses tenant-scoped authorization on every business resource. Configure `LLM_PROVIDER=openai` and `EMBEDDING_PROVIDER=openai` only when the corresponding API credentials and vector dimensions are available.
