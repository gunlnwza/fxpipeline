all:

lint:
	ruff check .

format:
	ruff format

PAT ?= .
test:
	PYTHONPATH=. pytest -k $(PAT)

cov:
	PYTHONPATH=. pytest --cov=fxpipeline --cov-report=term --cov-report=html

count:
	find . -path './.venv' -prune -o -name '*.py' -exec wc -l {} +

.PHONY: all lint test cov count
