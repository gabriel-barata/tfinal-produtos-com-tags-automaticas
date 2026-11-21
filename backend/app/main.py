from fastapi import FastAPI

app = FastAPI(title="Catálogo de Produtos com Tags Automáticas")


@app.get("/health")
def health() -> dict[str, str]:
    """Stub do health check; a versão real (com contagens) chega no card 14."""
    return {"status": "ok"}
