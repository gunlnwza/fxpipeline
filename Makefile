SRCS := fxpipeline main tests

lint:
	flake8 $(SRCS) --max-line-length 100 --extend-exclude .trash,venv,__init__.py

TESTS ?=
test:
	PYTHONPATH=. pytest $(TESTS)

cov:
	PYTHONPATH=. pytest --cov=fxpipeline --cov-report=term --cov-report=html

count:
	find $(SRCS) -name '*.py' -exec wc -l {} +

.PHONY: lint test cov count
