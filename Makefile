.PHONY: up down logs test lint format reset-db

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	docker compose run --rm api pytest

lint:
	docker compose run --rm api sh -c "ruff check . && ruff format --check ."

format:
	docker compose run --rm api ruff format .

# Apaga o volume; a migração é reaplicada no próximo `make up`.
reset-db:
	docker compose down -v
