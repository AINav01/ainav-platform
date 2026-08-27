.PHONY: test gold install

install:
	python -m pip install -e ".[dev]"

test gold:
	python -m pytest -q
