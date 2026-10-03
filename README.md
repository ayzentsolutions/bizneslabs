# BiznesLabs

Multi-tenant AI employee platform: organizations create AI agents, connect tenant knowledge and live business data, and let agents perform authorized actions.

Current implementation:
- Python/FastAPI backend
- PostgreSQL + pgvector
- tenant-scoped RBAC
- RAG pipeline foundation
- controlled live inventory tool
- ABC Motors demonstration tenant
- frontend will consume the versioned backend API

Core demo:
ABC Motors -> Alex -> ask about a vehicle -> agent uses live inventory -> admin changes inventory -> next request sees the new state.
