from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuração lida de variáveis de ambiente (ou do arquivo .env)."""

    database_url: str
    gemini_api_key: str = ""
    # Modelo configurável por env: modelos free tier são descontinuados com frequência.
    gemini_model: str = "gemini-2.5-flash"
    admin_key: str = ""
    allowed_origins: list[str] = ["http://localhost:8080"]
    log_level: str = "INFO"
