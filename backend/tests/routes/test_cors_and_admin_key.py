import pytest
from fastapi import APIRouter, Depends

from app.dependencies import require_admin_key
from tests.routes.conftest import ADMIN_KEY


def preflight(client, origin: str, method: str = "DELETE"):
    return client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "X-Admin-Key",
        },
    )


def test_preflight_from_allowed_origin_is_accepted(client):
    response = preflight(client, "http://allowed.test")

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://allowed.test"


def test_preflight_from_unknown_origin_is_rejected(client):
    response = preflight(client, "http://evil.test")

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_preflight_rejects_method_outside_the_allowed_list(client):
    assert preflight(client, "http://allowed.test", method="PUT").status_code == 400


@pytest.fixture
def protected_client(client):
    router = APIRouter()

    @router.get("/protected", dependencies=[Depends(require_admin_key)])
    def protected():
        return {"ok": True}

    client.app.include_router(router)
    return client


# Bytes latin-1: o client de teste não aceita `str` não ASCII em header.
@pytest.mark.parametrize(
    "headers",
    [{}, {"X-Admin-Key": "wrong"}, {"X-Admin-Key": "çã".encode("latin-1")}],
)
def test_missing_or_wrong_admin_key_is_401(protected_client, headers):
    response = protected_client.get("/protected", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Chave de administrador inválida."}


def test_valid_admin_key_passes(protected_client):
    assert protected_client.get("/protected", headers={"X-Admin-Key": ADMIN_KEY}).status_code == 200


def test_empty_configured_key_always_returns_401(protected_client):
    protected_client.app.state.settings.admin_key = ""

    assert protected_client.get("/protected", headers={"X-Admin-Key": ""}).status_code == 401
    assert protected_client.get("/protected").status_code == 401
