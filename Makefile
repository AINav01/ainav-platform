.PHONY: test gold install plan-check regen

install:
	python3 -m pip install -e ".[dev]"

regen:
	python3 -m ainav plan > docs/BUSINESS_PLAN.md
	python3 -m ainav review > docs/REVIEW.md
	python3 -m ainav pitch > docs/PROGRAMS.md
	python3 -c "from ainav.microsoft.connections import stack_json; import json; print(json.dumps(stack_json(), indent=2, sort_keys=True))" > institute/stack.json
	python3 -c "from ainav.business import public_business; import json; print(json.dumps(public_business(), indent=2, sort_keys=True))" > institute/business.json
	python3 -c "from ainav.buyer import buyer_page; import json; print(json.dumps(buyer_page(), indent=2, sort_keys=True))" > institute/buyer.json
	python3 -c "from ainav.org import public_org; import json; print(json.dumps(public_org(), indent=2, sort_keys=True))" > institute/org.json
	python3 -c "from ainav.institute_status import public_status; import json; print(json.dumps(public_status(), indent=2, sort_keys=True))" > institute/status.json
	python3 -c "from ainav.microsoft.agent_tools import public_review; import json; print(json.dumps(public_review(), indent=2, sort_keys=True))" > institute/agent-tools.json
	python3 -c "from ainav.review import public_card; import json; print(json.dumps(public_card(), indent=2, sort_keys=True))" > institute/review.json
	python3 -c "from ainav.finance import public_finance; import json; print(json.dumps(public_finance(), indent=2, sort_keys=True))" > institute/finance.json
	python3 -c "from ainav.packs import public_packs; import json; print(json.dumps(public_packs(), indent=2, sort_keys=True))" > institute/packs.json
	python3 -c "from ainav.governance import public_governance; import json; print(json.dumps(public_governance(), indent=2, sort_keys=True))" > institute/governance.json
	python3 -c "from ainav.client_org import public_client_org; import json; print(json.dumps(public_client_org(), indent=2, sort_keys=True))" > institute/client-org.json
	python3 -c "from ainav.dashboard import public_dashboard; import json; print(json.dumps(public_dashboard(), indent=2, sort_keys=True))" > institute/control-plane.json
	python3 -m ainav control-plane > docs/CONTROL_PLANE.md
	python3 -c "from ainav.dashboard import dashboard_html; print(dashboard_html(), end='')" > docs/CONTROL_PLANE_DASHBOARD.html
	python3 -c "from ainav.ip import public_insulation; import json; print(json.dumps(public_insulation(), indent=2, sort_keys=True))" > institute/ip.json
	python3 -c "from ainav.investor import public_investor; import json; print(json.dumps(public_investor(), indent=2, sort_keys=True))" > institute/investor.json
	python3 -m ainav investor > docs/CYNTHIA_HODNETT_INVESTOR.md
	python3 -c "from ainav.investor import investor_html; print(investor_html(), end='')" > docs/CYNTHIA_HODNETT_INVESTOR.html
	python3 -m ainav investor-pdf
	python3 -m ainav governance > docs/GOVERNANCE.md
	python3 -m ainav owner-steps > docs/OWNER_STEPS.md
	python3 -m ainav order-form > docs/ORDER_FORM.md
	python3 -m ainav msa > docs/MSA_SKELETON.md
	python3 -c "from ainav.owner_steps import public_owner_steps; import json; print(json.dumps(public_owner_steps(), indent=2, sort_keys=True))" > institute/owner-steps.json
	python3 -m ainav brief-pdf
	python3 -m ainav finance > docs/FINANCIAL_MODEL.md

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
	python3 -c "from ainav.finance import public_finance; import json; print(json.dumps(public_finance(), indent=2, sort_keys=True))" | diff -q institute/finance.json -
	python3 -c "from ainav.packs import public_packs; import json; print(json.dumps(public_packs(), indent=2, sort_keys=True))" | diff -q institute/packs.json -
	python3 -c "from ainav.governance import public_governance; import json; print(json.dumps(public_governance(), indent=2, sort_keys=True))" | diff -q institute/governance.json -
	python3 -c "from ainav.client_org import public_client_org; import json; print(json.dumps(public_client_org(), indent=2, sort_keys=True))" | diff -q institute/client-org.json -
	python3 -c "from ainav.dashboard import public_dashboard; import json; print(json.dumps(public_dashboard(), indent=2, sort_keys=True))" | diff -q institute/control-plane.json -
	python3 -m ainav control-plane | diff -q docs/CONTROL_PLANE.md -
	python3 -c "from ainav.dashboard import dashboard_html; print(dashboard_html(), end='')" | diff -q docs/CONTROL_PLANE_DASHBOARD.html -
	python3 -c "from ainav.ip import public_insulation; import json; print(json.dumps(public_insulation(), indent=2, sort_keys=True))" | diff -q institute/ip.json -
	python3 -c "from ainav.investor import public_investor; import json; print(json.dumps(public_investor(), indent=2, sort_keys=True))" | diff -q institute/investor.json -
	python3 -m ainav investor | diff -q docs/CYNTHIA_HODNETT_INVESTOR.md -
	python3 -c "from ainav.investor import investor_html; print(investor_html(), end='')" | diff -q docs/CYNTHIA_HODNETT_INVESTOR.html -
	test -s docs/CYNTHIA_HODNETT_INVESTOR.pdf
	python3 -m ainav governance | diff -q docs/GOVERNANCE.md -
	python3 -m ainav owner-steps | diff -q docs/OWNER_STEPS.md -
	python3 -m ainav order-form | diff -q docs/ORDER_FORM.md -
	python3 -m ainav msa | diff -q docs/MSA_SKELETON.md -
	python3 -c "from ainav.owner_steps import public_owner_steps; import json; print(json.dumps(public_owner_steps(), indent=2, sort_keys=True))" | diff -q institute/owner-steps.json -
	python3 -c "from ainav.brief_pdf import brief_markdown; print(brief_markdown(), end='')" | diff -q docs/CYNTHIA_HODNETT_BRIEF.md -
	python3 -c "from ainav.brief_pdf import brief_html; print(brief_html(), end='')" | diff -q docs/CYNTHIA_HODNETT_BRIEF.html -
	python3 -m ainav finance | diff -q docs/FINANCIAL_MODEL.md -
	test -s docs/CYNTHIA_HODNETT_BRIEF.pdf

gold: plan-check
	python3 -m pytest -q --cov=agent_gov --cov=ainav --cov-report=term-missing
