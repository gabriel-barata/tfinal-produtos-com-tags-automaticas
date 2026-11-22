from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Estado da API: contagens reais do índice e se há chave do Gemini configurada."""

    status: Literal["ok"]
    products: int
    tags: int
    gemini_configured: bool
