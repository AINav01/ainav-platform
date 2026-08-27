.PHONY: test gold install plan-check

install:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest -q

plan-check:
	python3 -m ainav plan | diff -q docs/BUSINESS_PLAN.md -
	python3 -m ainav pitch | diff -q docs/PROGRAMS.md -

gold: plan-check
	python3 -m pytest -q --cov=agent_gov --cov=ainav --cov-report=term-missing
