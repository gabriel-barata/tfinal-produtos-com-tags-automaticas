"""Criação da aplicação: lifespan (startup/shutdown), CORS, handlers de erro e rotas."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google import genai

from app.config import Settings
from app.exceptions import PersistenceError, ProductNotFoundError, TagGenerationError
from app.repositories.product_repository import ProductRepository, create_pool
from app.routes import health, products, tags
from app.services.catalog_index import CatalogIndex
from app.services.catalog_service import CatalogService
from app.services.tag_generator import GeminiTagGenerator

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Monta a aplicação. Receber `settings` permite aos testes usarem outra configuração."""
    settings = settings or Settings()
    logging.basicConfig(
        level=settings.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        pool = None
        try:
            pool = create_pool(settings.database_url)
            service = CatalogService(
                CatalogIndex(),
                ProductRepository(pool),
                GeminiTagGenerator(
                    # O client recusa chave vazia; um valor qualquer deixa a API subir (o
                    # /health mostra gemini_configured=false) e o cadastro falha com 503.
                    genai.Client(api_key=settings.gemini_api_key or "not-configured"),
                    settings.gemini_model,
                ),
            )
            loaded = service.load_index()
        except Exception:
            # Fail fast: sem o banco o índice nasceria vazio e a API serviria dados errados.
            # A exceção segue sem tratamento para o processo encerrar (o Render reinicia).
            logger.critical("Startup aborted: could not load the catalog", exc_info=True)
            if pool is not None:
                pool.close()
            raise
        app.state.catalog_service = service
        logger.info("Catalog index loaded with %d products", loaded)
        try:
            yield
        finally:
            pool.close()

    app = FastAPI(title="Catálogo de Produtos com Tags Automáticas", lifespan=lifespan)
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "X-Admin-Key"],
    )

    _register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(products.router)
    app.include_router(tags.router)
    return app


def _register_exception_handlers(app: FastAPI) -> None:
    """Traduz as exceções de domínio para HTTP (SPEC §9.4)."""

    def handler(status_code: int, detail: str):
        async def handle(request: Request, exc: Exception) -> JSONResponse:
            return JSONResponse(status_code=status_code, content={"detail": detail})

        return handle

    app.add_exception_handler(ProductNotFoundError, handler(404, "Produto não encontrado."))
    app.add_exception_handler(
        TagGenerationError, handler(503, "Serviço de IA indisponível, tente novamente.")
    )
    app.add_exception_handler(PersistenceError, handler(500, "Erro ao acessar o banco de dados."))


app = create_app()
