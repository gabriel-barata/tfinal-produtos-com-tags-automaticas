from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import Settings
from app.dependencies import get_catalog_service, get_settings
from app.schemas.health import HealthResponse
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    """Health check do Render, alvo do keep-alive e "despertador" do front (fora de `/api`)."""
    products, tags = service.stats()
    return HealthResponse(
        status="ok",
        products=products,
        tags=tags,
        gemini_configured=bool(settings.gemini_api_key),
    )
