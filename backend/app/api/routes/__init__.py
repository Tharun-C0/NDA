from fastapi import APIRouter
from backend.app.api.routes import health, document

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health Check"])
api_router.include_router(document.router, tags=["Document Analysis"])
