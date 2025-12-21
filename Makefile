SRCS := fxpipeline tests

lint:
	flake8 $(SRCS) --max-line-length 100 --extend-exclude .trash,venv,__init__.py

PAT ?= .
test:
	PYTHONPATH=. pytest -k $(PAT)

cov:
	PYTHONPATH=. pytest --cov=fxpipeline --cov-report=term --cov-report=html

count:
	find . -path './venv' -prune -o -name '*.py' -exec wc -l {} +

.PHONY: lint test cov count
