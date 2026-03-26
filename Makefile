PYTHON ?= python3

.PHONY: install dev test run-api sample countries

install:
	$(PYTHON) -m pip install -e .

dev:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest -q

run-api:
	uvicorn synthetic_profiles.api.app:app --reload

sample:
	$(PYTHON) main.py generate --c BR --g male

countries:
	$(PYTHON) main.py countries
