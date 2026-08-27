"""CLI: catalog, plan, provision, twin-demo."""

from __future__ import annotations

import argparse
import json
import sys

from agent_gov.hashing import canonical_json
from ainav.catalog import load_catalog
from ainav.mothership import MasterMothership
from ainav.plan import one_page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ainav")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("catalog")
    sub.add_parser("plan")
    prov = sub.add_parser("provision")
    prov.add_argument("client_id")
    prov.add_argument("--packs", default="L1")
    demo = sub.add_parser("twin-demo")
    demo.add_argument("--client-id", default="demo-client")
    args = parser.parse_args(argv)

    if args.cmd == "catalog":
        print(json.dumps(load_catalog(), indent=2, sort_keys=True))
        return 0
    if args.cmd == "plan":
        print(one_page(), end="")
        return 0
    if args.cmd == "provision":
        packs = tuple(p.strip() for p in args.packs.split(",") if p.strip())
        local = MasterMothership().provision(args.client_id, packs=packs)
        print(
            canonical_json(
                {
                    "client_id": local.client_id,
                    "packs": list(local.packs),
                    "allowed_actions": sorted(local.allowed_actions),
                    "live": False,
                }
            )
        )
        return 0
    if args.cmd == "twin-demo":
        return _twin_demo(args.client_id)
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
    local.teams.notify({"request_id": out["request_id"], "record_type": out["record_type"]})
    print(
        canonical_json(
            {
                "effect": out["record_type"],
                "apply_result": out.get("apply_result"),
                "audit": local.audit(),
                "twin_journals": local.bc.twin.journals,
                "teams_notified": len(local.teams.sent),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
