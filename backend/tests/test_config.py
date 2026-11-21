import pytest

from app.config import Settings


def test_allowed_origins_default():
    assert Settings(database_url="postgresql://x").allowed_origins == ["http://localhost:8080"]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("http://localhost:8080", ["http://localhost:8080"]),
        ("http://a.com,http://b.com", ["http://a.com", "http://b.com"]),
        (" http://a.com , http://b.com, ", ["http://a.com", "http://b.com"]),
    ],
)
def test_allowed_origins_parsed_from_comma_separated_env(monkeypatch, raw, expected):
    monkeypatch.setenv("ALLOWED_ORIGINS", raw)

    assert Settings(database_url="postgresql://x").allowed_origins == expected
