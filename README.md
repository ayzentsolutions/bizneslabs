# BiznesLabs

BiznesLabs is a multi-tenant AI employee platform. Organizations create AI employees that can understand customer requests, retrieve tenant knowledge, query live business data and execute explicitly authorized business actions.

## Architecture
Customer -> browser/telephony -> STT -> intent/runtime -> authorized tools -> tenant DB/RAG -> verified result -> LLM -> TTS.

The LLM is not the source of truth. Inventory, appointments, CRM records and tenant documents are authoritative.

## Implemented
- FastAPI + PostgreSQL + pgvector + Redis
- JWT authentication and tenant-scoped RBAC
- Organization and agent management
- Live inventory CRUD and controlled inventory tool
- CRM leads and appointment workflows
- RAG with tenant filtering
- PDF/DOCX/TXT/Markdown/CSV ingestion
- Configurable OpenAI-compatible LLM and embedding providers
- Prompt-injection defense for untrusted text
- Call persistence and analytics
- Browser voice-session abstraction
- Platform-admin metrics
- Responsive tenant control plane
- ABC Motors demo seed

## Run locally
1. Copy `backend/.env.example` to `backend/.env` and set `SECRET_KEY`.
2. Run `docker compose up --build`.
3. Run migrations: `docker compose exec api alembic upgrade head`.
4. Seed the demo: `docker compose exec api python scripts/seed_demo.py`.
5. Run frontend if not using compose: `cd frontend && npm install && npm run dev`.

## Demo flow
Login as the seeded ABC Motors owner. Ask whether the white Creta SX is available. The runtime checks live tenant inventory. Change that vehicle to SOLD from Inventory and ask again; the next request reads the changed database state.

For production, configure a real LLM and embedding provider and use a managed PostgreSQL/pgvector deployment. Never commit secrets.
