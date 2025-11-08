lint:
	flake8

test:
	PYTHONPATH=. pytest

.PHONY: lint test
