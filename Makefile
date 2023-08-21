.EXPORT_ALL_VARIABLES:
include .env.local 

python = ./venv/bin/python
pip    = ./venv/bin/pip


.PHONY: pip-install
pip-install:
	$(pip) install $(args)

.PHONY: py
py:
	$(python) $(args)

.PHONY: shell
shell:
	DEBUG= /bin/bash


.PHONY: setup
setup:
	python -m venv venv
	$(pip) install -e .
	$(pip) install -e '.[dev]'


.PHONY: fmt
fmt:
	$(python) -m black .


.PHONY: db
db:
	docker compose up mongo


.PHONY: start 
start:
	$(python) -m uvicorn chak.app:create_app --factory --reload --host 0.0.0.0 --port $(PORT)


.PHONY: tests
tests:
	$(python) -m pytest -s tests/