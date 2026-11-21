import pytest
from fastapi import APIRouter

from app.exceptions import PersistenceError, ProductNotFoundError, TagGenerationError


@pytest.mark.parametrize(
    ("error", "status", "detail"),
    [
        (ProductNotFoundError(1), 404, "Produto não encontrado."),
        (TagGenerationError("x"), 503, "Serviço de IA indisponível, tente novamente."),
        (PersistenceError("x"), 500, "Erro ao acessar o banco de dados."),
    ],
)
def test_domain_errors_become_http_errors(client, error, status, detail):
    router = APIRouter()

    @router.get("/boom")
    def boom():
        raise error

    client.app.include_router(router)

    response = client.get("/boom")

    assert response.status_code == status
    assert response.json() == {"detail": detail}
