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
    review = sub.add_parser("review")
    review.add_argument(
        "--probe",
        action="store_true",
        help="overlay read-only Microsoft and DNS health. Never writes. Never publishes.",
    )
    sub.add_parser("ip")
    sub.add_parser("programs")
    sub.add_parser("pitch")
    org_cmd = sub.add_parser("org")
    org_cmd.add_argument(
        "--probe",
        action="store_true",
        help="overlay read-only stack health. Never writes. Never LIVE_PIN_OK.",
    )
    sub.add_parser("connections")
    sub.add_parser("dns")
    agent_tools = sub.add_parser("agent-tools")
    agent_tools.add_argument(
        "--probe",
        action="store_true",
        help="read-only Agent 365 SP check. Cannot approve tools. Never LIVE_PIN_OK.",
    )
    agent_tools.add_argument(
        "--steps",
        action="store_true",
        help="print the owner Leave Available playbook with Microsoft admin links.",
    )
    connect = sub.add_parser("connect")
    connect.add_argument(
        "--probe",
        action="store_true",
        help="read-only live health (Graph/ARM/BC). Never writes. Never LIVE_PIN_OK.",
    )
    connect.add_argument(
        "--bind-host",
        action="store_true",
        help="create Azure RG/Key Vault/Log Analytics. Never writes SoR. Never LIVE_PIN_OK.",
    )
    connect.add_argument(
        "--publish-institute",
        action="store_true",
        help="PUT Azure Static Web App and upload institute/. Never custom domain. Never LIVE_PIN_OK.",
    )
    connect.add_argument(
        "--sandbox-wedge",
        action="store_true",
        help="dual-admit then POST AINav DEFAULT journal in BC Sandbox. Never production. Never LIVE_PIN_OK.",
    )
    stack_demo = sub.add_parser("stack-demo")
    stack_demo.add_argument("--client-id", default="demo-client")
    sub.add_parser("company-demo")
    sub.add_parser("proof-day")
    sub.add_parser("buyer")
    brief = sub.add_parser("brief")
    brief.add_argument("--for", dest="for_controller", default="")
    sub.add_parser("next-pin")
    sub.add_parser("delivery")
    sub.add_parser("raci")
    pair = sub.add_parser("motherships")
    pair.add_argument("--client-id", default="demo-client")
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
    if args.cmd == "review":
        from ainav.review import deep_dive

        print(deep_dive(probe=bool(args.probe)), end="")
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
    if args.cmd == "org":
        from ainav.org import org_report

        print(canonical_json(org_report(probe=bool(args.probe))))
        return 0
    if args.cmd == "connect":
        from ainav.microsoft.health import stack_health

        if args.publish_institute:
            from ainav.microsoft.institute_publish import publish_institute

            published = publish_institute()
            print(canonical_json({"publish": published, "health": stack_health(probe=True)}))
            return 0 if published.get("ok") else 2
        if args.bind_host:
            from ainav.microsoft.host_bind import bind_host

            bound = bind_host()
            print(canonical_json({"bind": bound, "health": stack_health(probe=True)}))
            return 0 if bound.get("ok") else 2
        if args.sandbox_wedge:
            from ainav.microsoft.bc_sandbox import post_named_company

            local = MasterMothership().standard_l1_pack("ainav-inc")
            action = {
                "action_class": "bc.general_journal.post",
                "payload": {
                    "account": "11100",
                    "balancing_account": "22100",
                    "amount": "250.00",
                    "memo": "AINav L1 sandbox wedge",
                        "company": "AINav",
                    "journal": "DEFAULT",
                },
                "proposal_id": "prp-sandbox-wedge-1",
                "sor_target": "bc.sandbox",
                "policy_id": "dual-admit-v1",
            }

            def apply(grant: dict) -> dict:
                twin = local.router.apply(grant, trusted=True)
                http = post_named_company(grant)
                return {**twin, "microsoft_sandbox": http}

            out = local.client.run_and_apply(
                action,
                seat_a="oid-operator-a",
                seat_b="oid-operator-b",
                apply=apply,
            )
            print(
                canonical_json(
                    {
                        "kind": "ainav.sandbox_wedge.v1",
                        "effect": out,
                        "twin_journals": local.bc.twin.journals,
                        "health": stack_health(probe=True),
                        "live": False,
                        "live_pin_ok": False,
                    }
                )
            )
            http = (out.get("apply_result") or {}).get("microsoft_sandbox") or {}
            return 0 if http.get("ok") else 2
        print(canonical_json(stack_health(probe=True if args.probe else None)))
        return 0
    if args.cmd == "dns":
        from ainav.microsoft.dns import probe_dns

        print(canonical_json(probe_dns()))
        return 0
    if args.cmd == "agent-tools":
        from ainav.microsoft.agent_tools import probe_agent_tools, public_review, steps_markdown

        if args.steps:
            print(steps_markdown(), end="")
            return 0
        print(canonical_json(probe_agent_tools() if args.probe else public_review()))
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
    if args.cmd == "delivery":
        from ainav.delivery import public_delivery

        print(canonical_json(public_delivery()))
        return 0
    if args.cmd == "raci":
        from ainav.delivery import raci, week_one

        print(canonical_json({"raci": raci(), "week_one": week_one(), "live": False}))
        return 0
    if args.cmd == "motherships":
        return _motherships(args.client_id)
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


def _motherships(client_id: str) -> int:
    from ainav.delivery import DeliverySystem

    system = DeliverySystem()
    pair = system.provision_pair(client_id)
    local = pair["local"]
    cloud = pair["cloud"]
    action = {
        "action_class": "bc.general_journal.post",
        "payload": {"account": "1000", "amount": "1.00", "memo": "shared ledger"},
        "proposal_id": "prp-pair-1",
        "sor_target": "bc.sandbox",
        "policy_id": "dual-admit-v1",
    }
    out = local.run_and_apply(action, seat_a="oid-1", seat_b="oid-2")
    replay = None
    try:
        cloud.run_and_apply(action, seat_a="oid-1", seat_b="oid-2")
    except Exception as exc:
        replay = type(exc).__name__
    print(
        canonical_json(
            {
                "delivery": system.snapshot(client_id),
                "effect": out["record_type"],
                "cloud_replay": replay,
                "shared_digest": local.lockfile.digest() == cloud.lockfile.digest(),
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
