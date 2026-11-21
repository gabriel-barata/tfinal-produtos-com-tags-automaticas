from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.dependencies import get_catalog_service, require_admin_key
from app.schemas.product_create import ProductCreateRequest
from app.schemas.product_response import ProductResponse
from app.schemas.search_result import SearchResultResponse
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/api/products", tags=["products"])

CatalogServiceDep = Annotated[CatalogService, Depends(get_catalog_service)]


# Rotas síncronas (`def`): o FastAPI as roda em threadpool, então a chamada lenta ao
# Gemini no cadastro não trava o event loop; o `CatalogIndex` já é thread-safe.
@router.post("", status_code=201, response_model=ProductResponse)
def create_product(body: ProductCreateRequest, service: CatalogServiceDep) -> ProductResponse:
    return ProductResponse.from_entity(service.create_product(body.name, body.description))


@router.get("", response_model=list[SearchResultResponse])
def search_products(
    service: CatalogServiceDep,
    q: Annotated[str | None, Query(max_length=200)] = None,
) -> list[SearchResultResponse]:
    return [SearchResultResponse.from_hit(hit) for hit in service.search(q)]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, service: CatalogServiceDep) -> ProductResponse:
    return ProductResponse.from_entity(service.get_product(product_id))


@router.delete("/{product_id}", status_code=204, dependencies=[Depends(require_admin_key)])
def delete_product(product_id: int, service: CatalogServiceDep) -> Response:
    service.delete_product(product_id)
    return Response(status_code=204)
