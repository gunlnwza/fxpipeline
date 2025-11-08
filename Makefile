lint:
	flake8

test:
	PYTHONPATH=. pytest

count:
	find fxpipeline main tests -name '*.py' -exec wc -l {} +

.PHONY: lint test count
