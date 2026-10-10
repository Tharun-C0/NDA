from fastapi import APIRouter
try:
    from backend.app.core.config import settings
    from backend.app.schemas.health import HealthResponse
except ModuleNotFoundError:
    from app.core.config import settings
    from app.schemas.health import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Application Health Check")
async def health_check() -> HealthResponse:
    """Return health status, version, and application name."""
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        app_name=settings.APP_NAME,
    )
