.PHONY: test gold install plan-check

install:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest -q

plan-check:
	python3 -m ainav plan | diff -q docs/BUSINESS_PLAN.md -
	python3 -m ainav pitch | diff -q docs/PROGRAMS.md -
	python3 -c "from ainav.microsoft.connections import stack_json; import json; print(json.dumps(stack_json(), indent=2, sort_keys=True))" | diff -q institute/stack.json -
	python3 -c "from ainav.business import public_business; import json; print(json.dumps(public_business(), indent=2, sort_keys=True))" | diff -q institute/business.json -
	python3 -c "from ainav.buyer import buyer_page; import json; print(json.dumps(buyer_page(), indent=2, sort_keys=True))" | diff -q institute/buyer.json -

gold: plan-check
	python3 -m pytest -q --cov=agent_gov --cov=ainav --cov-report=term-missing
