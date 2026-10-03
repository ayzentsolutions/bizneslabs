from fastapi import APIRouter
from app.api.routes import auth, organizations, agents, inventory, knowledge

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(runtime.router, prefix="/runtime", tags=["runtime"])
