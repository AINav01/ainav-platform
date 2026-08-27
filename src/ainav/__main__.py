"""CLI: catalog, plan, provision, twin-demo, ops-demo, manifest."""

from __future__ import annotations

import argparse
import json
import sys

from agent_gov.hashing import canonical_json
from ainav.catalog import load_catalog
from ainav.mothership import MasterMothership
from ainav.ops import ClientAccount
from ainav.plan import one_page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ainav")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("catalog")
    sub.add_parser("plan")
    sub.add_parser("ip")
    sub.add_parser("programs")
    sub.add_parser("pitch")
    sub.add_parser("connections")
    stack_demo = sub.add_parser("stack-demo")
    stack_demo.add_argument("--client-id", default="demo-client")
    sub.add_parser("company-demo")
    sub.add_parser("proof-day")
    sub.add_parser("buyer")
    brief = sub.add_parser("brief")
    brief.add_argument("--for", dest="for_controller", default="")
    sub.add_parser("next-pin")
    prov = sub.add_parser("provision")
    prov.add_argument("client_id")
    prov.add_argument("--packs", default="L1")
    prov.add_argument("--industry", default="")
    prov.add_argument(
        "--kit-pass",
        action="store_true",
        help="lab only: allow P-ADM/U-DUAL after Acceptance Kit PASS",
    )
    demo = sub.add_parser("twin-demo")
    demo.add_argument("--client-id", default="demo-client")
    ops = sub.add_parser("ops-demo")
    ops.add_argument("--client-id", default="demo-client")
    man = sub.add_parser("manifest")
    man.add_argument("client_id")
    man.add_argument("--packs", default="L1")
    man.add_argument("--industry", default="")
    man.add_argument("--kit-pass", action="store_true")
    args = parser.parse_args(argv)

    if args.cmd == "catalog":
        print(json.dumps(load_catalog(), indent=2, sort_keys=True))
        return 0
    if args.cmd == "plan":
        print(one_page(), end="")
        return 0
    if args.cmd == "ip":
        from ainav.ip import notice

        print(notice(), end="")
        return 0
    if args.cmd == "programs":
        from ainav.programs import application_order, programs, qualify

        print(
            canonical_json(
                {
                    "membership_claimed": False,
                    "application_order": application_order(),
                    "microsoft.founders_hub": qualify("microsoft.founders_hub"),
                    "nvidia.inception": qualify("nvidia.inception"),
                    "targets": programs()["targets"],
                }
            )
        )
        return 0
    if args.cmd == "pitch":
        from ainav.programs import pitch

        print(pitch(), end="")
        return 0
    if args.cmd == "connections":
        from ainav.microsoft.connections import stack_json

        master = MasterMothership()
        print(
            canonical_json(
                {
                    "institute_stack": stack_json(),
                    "company": master.company_surface(),
                    "live": False,
                }
            )
        )
        return 0
    if args.cmd == "stack-demo":
        return _stack_demo(args.client_id)
    if args.cmd == "company-demo":
        return _company_demo()
    if args.cmd == "proof-day":
        return _proof_day()
    if args.cmd == "buyer":
        from ainav.buyer import buyer_page

        print(canonical_json(buyer_page()))
        return 0
    if args.cmd == "brief":
        from ainav.buyer import proof_day_brief

        print(canonical_json(proof_day_brief(for_controller=args.for_controller or None)))
        return 0
    if args.cmd == "next-pin":
        from ainav.next_pin import sandbox_envelope

        print(canonical_json(sandbox_envelope()))
        return 0
    if args.cmd == "provision":
        packs = tuple(p.strip() for p in args.packs.split(",") if p.strip())
        industry = tuple(p.strip() for p in args.industry.split(",") if p.strip())
        local = MasterMothership().provision(
            args.client_id,
            packs=packs,
            industry=industry,
            kit_pass=args.kit_pass,
        )
        print(canonical_json(local.manifest()))
        return 0
    if args.cmd == "twin-demo":
        return _twin_demo(args.client_id)
    if args.cmd == "ops-demo":
        return _ops_demo(args.client_id)
    if args.cmd == "manifest":
        packs = tuple(p.strip() for p in args.packs.split(",") if p.strip())
        industry = tuple(p.strip() for p in args.industry.split(",") if p.strip())
        local = MasterMothership().provision(
            args.client_id,
            packs=packs,
            industry=industry,
            kit_pass=args.kit_pass,
        )
        print(canonical_json(local.manifest()))
        return 0
    return 2


def _twin_demo(client_id: str) -> int:
    local = MasterMothership().standard_l1_pack(client_id)
    action = {
        "action_class": "bc.general_journal.post",
        "payload": {"account": "1000", "amount": "250.00", "memo": "sandbox journal"},
        "proposal_id": "prp-twin-1",
        "sor_target": "bc.sandbox",
        "policy_id": "dual-admit-v1",
    }
    out = local.run_and_apply(action, seat_a="oid-1", seat_b="oid-2")
    print(
        canonical_json(
            {
                "effect": out["record_type"],
                "apply_result": out.get("apply_result"),
                "audit": local.audit(),
                "twin_journals": local.bc.twin.journals,
                "teams_notified": len(local.teams.sent),
                "connections": [item["id"] for item in local.stack.describe()["connections"]],
            }
        )
    )
    return 0


def _stack_demo(client_id: str) -> int:
    from ainav.microsoft.connections import stack_json

    master = MasterMothership()
    local = master.standard_l1_pack(client_id)
    out = local.run_and_apply(
        {
            "action_class": "bc.general_journal.post",
            "payload": {"account": "1000", "amount": "250.00", "memo": "sandbox journal"},
            "proposal_id": "prp-stack-1",
            "sor_target": "bc.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    print(
        canonical_json(
            {
                "company": master.company_surface(),
                "institute_stack": stack_json(),
                "effect": out["record_type"],
                "sor_connection": local.last_sor_connection,
                "teams": [item["connection"] for item in local.teams.sent],
                "live": False,
            }
        )
    )
    return 0


def _ops_demo(client_id: str) -> int:
    account = ClientAccount(client_id)
    account.sell_l1()
    account.start_kit()
    account.pass_kit()
    account.book("ffs.acceptance_kit")
    account.attach_padm()
    account.offer_udual()
    account.attach_udual()
    local = account.local
    assert local is not None
    sales = local.run_and_apply(
        {
            "action_class": "d365.quote.discount_override",
            "payload": {"discount": "12"},
            "proposal_id": "prp-ops-1",
            "sor_target": "d365.sales.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    print(
        canonical_json(
            {
                "account": account.snapshot(),
                "manifest": local.manifest(),
                "sales_effect": sales["record_type"],
                "sales_twin": local.sales.twin.writes,
            }
        )
    )
    return 0


def _company_demo() -> int:
    from ainav.business import OperatingCompany

    company = OperatingCompany()
    won = company.run_standard_engagement("acme")
    company.qualify("prospect")
    local = won.local
    assert local is not None
    local.run_and_apply(
        {
            "action_class": "bc.general_journal.post",
            "payload": {"account": "1000", "amount": "10.00", "memo": "company demo"},
            "proposal_id": "prp-co-1",
            "sor_target": "bc.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    print(
        canonical_json(
            {
                "management": company.management_snapshot(),
                "runbook": company.delivery_runbook(won),
                "evidence": company.evidence.stored[-1]["connection"] if company.evidence.stored else None,
                "live": False,
            }
        )
    )
    return 0


def _proof_day() -> int:
    from ainav.proof_day import run_proof_day

    print(canonical_json(run_proof_day("cli-proof-day")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
