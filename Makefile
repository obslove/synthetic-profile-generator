PYTHON ?= python3

.PHONY: install dev test run-api sample countries

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"

test:
	pytest

run-api:
	uvicorn synthetic_profiles.api.app:app --reload

sample:
	$(PYTHON) main.py generate --country BR --gender male --age-min 18 --age-max 35 --realism-level highly_natural --rarity balanced --emails 3 --password-length 24 --include-identifiers --identifier-types cpf --diversity-mode extreme --format json

countries:
	$(PYTHON) main.py countries
