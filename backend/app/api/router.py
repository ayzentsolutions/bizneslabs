from fastapi import APIRouter
from app.api.routes import auth, organizations, agents, inventory, knowledge, runtime, leads, appointments, analytics, health

api_router=APIRouter()
api_router.include_router(health.router,prefix="/health",tags=["health"])
api_router.include_router(auth.router,prefix="/auth",tags=["auth"])
api_router.include_router(organizations.router,prefix="/organizations",tags=["organizations"])
api_router.include_router(agents.router,prefix="/agents",tags=["agents"])
api_router.include_router(inventory.router,prefix="/inventory",tags=["inventory"])
api_router.include_router(knowledge.router,prefix="/knowledge",tags=["knowledge"])
api_router.include_router(runtime.router,prefix="/runtime",tags=["runtime"])
api_router.include_router(leads.router,prefix="/leads",tags=["leads"])
api_router.include_router(appointments.router,prefix="/appointments",tags=["appointments"])
api_router.include_router(analytics.router,prefix="/analytics",tags=["analytics"])
