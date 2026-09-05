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
from agent_gov.errors import AgentGovError
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
    sub.add_parser("vectors", help="print frozen gold action_hash")
    audit = sub.add_parser("audit", help="admit→effect then print a verified audit")
    audit.add_argument("--ledger", default="", help="optional JSONL ledger path")
    prove = sub.add_parser("prove", help="print a Merkle inclusion proof from a JSONL ledger")
    prove.add_argument("ledger")
    prove.add_argument("record_id")
    export = sub.add_parser("export", help="print an export envelope from a JSONL ledger")
    export.add_argument("ledger")
    vexp = sub.add_parser("verify-export", help="verify an export envelope JSON file")
    vexp.add_argument("path")
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
    if args.cmd == "vectors":
        from importlib.resources import files

        print(files("agent_gov.gold").joinpath("vectors.json").read_text(encoding="utf-8"), end="")
        return 0
    if args.cmd == "audit":
        return _audit(args.ledger or None)
    if args.cmd == "prove":
        return _prove(Path(args.ledger), args.record_id)
    if args.cmd == "export":
        return _export(Path(args.ledger))
    if args.cmd == "verify-export":
        return _verify_export(Path(args.path))
    return 2


def _demo(seat_a: str, seat_b: str) -> int:
    from agent_gov.store import reset_default_store

    reset_default_store()
    action = {
        "action_class": "bc.general_journal.post",
        "payload": {"account": "1000", "amount": "100.00", "memo": "public demo"},
        "proposal_id": "prp-demo",
        "sor_target": "bc.sandbox",
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
    try:
        if len(records) == 1 and "prev_receipt_hash" not in records[0]:
            verify_record(records[0])
        else:
            verify_chain(records)
    except AgentGovError as exc:
        print(canonical_json({"ok": False, "reason_code": exc.reason_code}))
        return 1
    print(canonical_json({"ok": True, "count": len(records)}))
    return 0


def _audit(ledger: str | None) -> int:
    if ledger:
        from agent_gov.store import FileAuthorityStore

        store = FileAuthorityStore(ledger)
        print(canonical_json(store.audit()))
        return 0
    from agent_gov.store import default_store, reset_default_store

    reset_default_store()
    rec = admit(
        {
            "action_class": "bc.general_journal.post",
            "payload": {"account": "1000", "amount": "100.00", "memo": "public audit"},
            "proposal_id": "prp-audit",
            "sor_target": "bc.sandbox",
            "policy_id": "dual-admit-v1",
        },
        default_lockfile(),
        ledger=ConsumeLedger(),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    EffectLedger().effect(rec["request_id"], rec["action_hash"])
    print(canonical_json(default_store().audit()))
    return 0


def _prove(path: Path, record_id: str) -> int:
    from agent_gov.store import FileAuthorityStore

    store = FileAuthorityStore(path)
    print(canonical_json(store.prove(record_id)))
    return 0


def _export(path: Path) -> int:
    from agent_gov.export import export_envelope
    from agent_gov.store import FileAuthorityStore

    store = FileAuthorityStore(path)
    records = store.decisions()
    print(canonical_json(export_envelope(records, tip=store.tip())))
    return 0


def _verify_export(path: Path) -> int:
    from agent_gov.export import verify_export

    try:
        tip = verify_export(json.loads(path.read_text(encoding="utf-8")))
    except AgentGovError as exc:
        print(canonical_json({"ok": False, "reason_code": exc.reason_code}))
        return 1
    print(canonical_json({"ok": True, "tip": tip}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
