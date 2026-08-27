.PHONY: test gold install

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

gold:
	python -m pytest -q --cov=agent_gov --cov=ainav --cov-report=term-missing
