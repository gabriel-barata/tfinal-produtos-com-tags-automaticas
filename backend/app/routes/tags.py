from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_catalog_service
from app.schemas.tag_count import TagCountResponse
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagCountResponse])
def list_tags(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> list[TagCountResponse]:
    return [
        TagCountResponse(tag=tag, count=count, group=group)
        for tag, count, group in service.list_tags()
    ]
