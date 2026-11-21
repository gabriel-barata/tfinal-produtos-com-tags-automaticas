from pydantic import BaseModel

from app.schemas.product_response import ProductResponse
from app.services.catalog_index import SearchHit


class SearchResultResponse(BaseModel):
    """Um resultado de busca: produto, nº de termos que casaram e quais foram."""

    product: ProductResponse
    score: int
    matched_tags: list[str]

    @classmethod
    def from_hit(cls, hit: SearchHit) -> "SearchResultResponse":
        return cls(
            product=ProductResponse.from_entity(hit.product),
            score=hit.score,
            matched_tags=list(hit.matched_tags),
        )
