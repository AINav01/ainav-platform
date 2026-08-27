"""CLI: version, invariants, demo, verify."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_gov import (
    ConsumeLedger,
    EffectLedger,
    __version__,
    admit,
    default_lockfile,
)
from agent_gov.hashing import canonical_json
from agent_gov.lockfile import HARD_INVARIANTS, dumps_lockfile
from agent_gov.records import verify_chain, verify_record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent_gov")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("version", help="print package version")
    sub.add_parser("invariants", help="print pinned Job C lockfile")
    demo = sub.add_parser("demo", help="run the canonical admit → effect snippet")
    demo.add_argument("--seat-a", default="oid-1")
    demo.add_argument("--seat-b", default="oid-2")
    verify = sub.add_parser("verify", help="verify a DecisionRecord JSON or JSONL chain")
    verify.add_argument("path")
    args = parser.parse_args(argv)

    if args.cmd == "version":
        print(__version__)
        return 0
    if args.cmd == "invariants":
        print(dumps_lockfile(default_lockfile()), end="")
        print(json.dumps(HARD_INVARIANTS, sort_keys=True))
        return 0
    if args.cmd == "demo":
        return _demo(args.seat_a, args.seat_b)
    if args.cmd == "verify":
        return _verify(Path(args.path))
    return 2


def _demo(seat_a: str, seat_b: str) -> int:
    from agent_gov.store import reset_default_store

    reset_default_store()
    action = {
        "action_class": "custody.withdraw.execute",
        "payload": {"amount": "100", "asset": "USDC"},
        "proposal_id": "prp-demo",
        "sor_target": "custody.core",
        "policy_id": "dual-admit-v1",
    }
    rec = admit(
        action,
        default_lockfile(),
        ledger=ConsumeLedger(),
        seat_a=seat_a,
        seat_b=seat_b,
    )
    out = EffectLedger().effect(rec["request_id"], rec["action_hash"])
    print(
        canonical_json(
            {
                "admit": rec["record_type"],
                "effect": out["record_type"],
                "request_id": rec["request_id"],
                "action_hash": rec["action_hash"],
                "seat_a": rec["seat_a"],
                "seat_b": rec["seat_b"],
                "consumed": rec["consumed"],
            }
        )
    )
    return 0


def _verify(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        records = data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        records = [json.loads(line) for line in text.splitlines() if line.strip()]
    if len(records) == 1 and "prev_receipt_hash" not in records[0]:
        verify_record(records[0])
    else:
        verify_chain(records)
    print(canonical_json({"ok": True, "count": len(records)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
