"""Providers de `Depends`: serviço único, configuração e verificação da chave de admin."""

import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

from app.config import Settings
from app.services.catalog_service import CatalogService


def get_settings(request: Request) -> Settings:
    """Configuração da aplicação (guardada em `app.state` por `create_app`)."""
    return request.app.state.settings


def get_catalog_service(request: Request) -> CatalogService:
    """Instância única do serviço, criada no `lifespan`.

    Tem que ser única: ela guarda o índice em memória, então várias instâncias
    teriam dados divergentes.
    """
    return request.app.state.catalog_service


def require_admin_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_admin_key: Annotated[str | None, Header()] = None,
) -> None:
    """Exige o header `X-Admin-Key` igual à `ADMIN_KEY` configurada.

    Com `ADMIN_KEY` vazia a rota fica sempre bloqueada (nunca "aberta por esquecimento").

    Raises:
        HTTPException: 401 se a chave estiver ausente, errada ou não configurada.
    """
    expected = settings.admin_key
    # compare_digest em tempo constante evita vazar a chave por diferença de tempo; em bytes
    # porque ele rejeita `str` com caracteres não ASCII.
    if (
        not expected
        or x_admin_key is None
        or not secrets.compare_digest(x_admin_key.encode(), expected.encode())
    ):
        raise HTTPException(status_code=401, detail="Chave de administrador inválida.")
