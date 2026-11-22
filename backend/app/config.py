from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode


class Settings(BaseSettings):
    """Configuração lida de variáveis de ambiente (ou do arquivo .env)."""

    database_url: str
    gemini_api_key: str = ""
    # Modelo configurável por env: modelos free tier são descontinuados com frequência.
    gemini_model: str = "gemini-3.5-flash-lite"
    admin_key: str = ""
    # NoDecode: sem isso o pydantic-settings exige JSON para listas vindas do ambiente.
    allowed_origins: Annotated[list[str], NoDecode] = ["http://localhost:8080"]
    log_level: str = "INFO"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        """Aceita `ALLOWED_ORIGINS=http://a.com,http://b.com` (separado por vírgula)."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value
