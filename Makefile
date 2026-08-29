.PHONY: test gold install plan-check

install:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest -q

plan-check:
	python3 -m ainav plan | diff -q docs/BUSINESS_PLAN.md -
	python3 -m ainav review | diff -q docs/REVIEW.md -
	python3 -m ainav pitch | diff -q docs/PROGRAMS.md -
	python3 -c "from ainav.microsoft.connections import stack_json; import json; print(json.dumps(stack_json(), indent=2, sort_keys=True))" | diff -q institute/stack.json -
	python3 -c "from ainav.business import public_business; import json; print(json.dumps(public_business(), indent=2, sort_keys=True))" | diff -q institute/business.json -
	python3 -c "from ainav.buyer import buyer_page; import json; print(json.dumps(buyer_page(), indent=2, sort_keys=True))" | diff -q institute/buyer.json -
	python3 -c "from ainav.org import public_org; import json; print(json.dumps(public_org(), indent=2, sort_keys=True))" | diff -q institute/org.json -
	python3 -c "from ainav.institute_status import public_status; import json; print(json.dumps(public_status(), indent=2, sort_keys=True))" | diff -q institute/status.json -
	python3 -c "from ainav.microsoft.agent_tools import public_review; import json; print(json.dumps(public_review(), indent=2, sort_keys=True))" | diff -q institute/agent-tools.json -
	python3 -c "from ainav.review import public_card; import json; print(json.dumps(public_card(), indent=2, sort_keys=True))" | diff -q institute/review.json -
	python3 -m ainav owner-steps | diff -q docs/OWNER_STEPS.md -
	python3 -m ainav order-form | diff -q docs/ORDER_FORM.md -
	python3 -m ainav msa | diff -q docs/MSA_SKELETON.md -
	python3 -c "from ainav.owner_steps import public_owner_steps; import json; print(json.dumps(public_owner_steps(), indent=2, sort_keys=True))" | diff -q institute/owner-steps.json -
	python3 -c "from ainav.brief_pdf import brief_markdown; print(brief_markdown(), end='')" | diff -q docs/CYNTHIA_HODNETT_BRIEF.md -
	python3 -c "from ainav.brief_pdf import brief_html; print(brief_html(), end='')" | diff -q docs/CYNTHIA_HODNETT_BRIEF.html -
	test -s docs/CYNTHIA_HODNETT_BRIEF.pdf

gold: plan-check
	python3 -m pytest -q --cov=agent_gov --cov=ainav --cov-report=term-missing
