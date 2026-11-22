"""Teste de fumaça ponta a ponta contra uma API em execução (local ou produção).

Cadastra um produto, busca por uma tag dele, confere /api/tags, exclui e
confere que sumiu. Usa só a biblioteca padrão, para rodar sem instalar nada.

Uso:
    python scripts/smoke_test.py http://localhost:8000 --admin-key SUA_CHAVE
    ADMIN_KEY=... python scripts/smoke_test.py https://catalogo-esportivo-api.onrender.com
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# Cold start do Render + chamada ao Gemini podem demorar.
TIMEOUT_SECONDS = 90


def request(method, base_url, path, body=None, headers=None):
    """Faz uma requisição HTTP e devolve (status, JSON ou None)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base_url + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as err:
        raw = err.read()
        return err.code, json.loads(raw) if raw else None


def check(condition, message):
    """Imprime o resultado de um passo e aborta no primeiro erro."""
    print(f"{'OK  ' if condition else 'FAIL'} {message}")
    if not condition:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("base_url", help="URL base da API, ex.: http://localhost:8000")
    parser.add_argument(
        "--admin-key",
        default=os.environ.get("ADMIN_KEY"),
        help="chave de administrador (ou variável ADMIN_KEY)",
    )
    args = parser.parse_args()
    if not args.admin_key:
        parser.error("informe --admin-key ou a variável ADMIN_KEY")
    base_url = args.base_url.rstrip("/")

    status, health = request("GET", base_url, "/health")
    check(status == 200 and health["status"] == "ok", "GET /health")

    status, product = request(
        "POST",
        base_url,
        "/api/products",
        {
            "name": "Tênis Smoke Test",
            "description": "Tênis azul para corrida em asfalto, amortecimento leve",
        },
    )
    check(status == 201 and product["tags"], f"POST /api/products (status {status})")
    product_id = product["id"]
    print(f"     id {product_id}, tags {product['tags']}")

    try:
        # Tag livre/específica evita depender de qual vocabulário o Gemini escolheu.
        tag = product["tags"][0]
        status, results = request("GET", base_url, "/api/products?q=" + urllib.parse.quote(tag))
        found = status == 200 and any(r["product"]["id"] == product_id for r in results)
        check(found, f"GET /api/products?q={tag} acha o produto")

        status, tags = request("GET", base_url, "/api/tags")
        check(status == 200 and any(t["tag"] == tag for t in tags), f"GET /api/tags lista '{tag}'")
    finally:
        # Mesmo se um passo falhar, não deixa lixo no catálogo.
        status, _ = request(
            "DELETE",
            base_url,
            f"/api/products/{product_id}",
            headers={"X-Admin-Key": args.admin_key},
        )
        check(status == 204, f"DELETE /api/products/{product_id}")

    status, _ = request("GET", base_url, f"/api/products/{product_id}")
    check(status == 404, "GET do produto excluído devolve 404")

    status, results = request("GET", base_url, "/api/products?q=" + urllib.parse.quote(tag))
    gone = status == 200 and all(r["product"]["id"] != product_id for r in results)
    check(gone, "busca não retorna mais o produto")

    print("Smoke test passou.")


if __name__ == "__main__":
    main()
