from pydantic import BaseModel, ConfigDict, Field


class ProductCreateRequest(BaseModel):
    """Corpo do `POST /api/products`. Os limites espelham os `CHECK` da tabela."""

    # O strip vem antes da validação de tamanho: "  a  " não vira um nome válido.
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=1000)
