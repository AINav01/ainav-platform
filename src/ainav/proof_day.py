"""Ninety-minute proof day. The sale is the proof. Not signed L1.

Two existing treasury seats bind one general-journal post. The grant
is consumed once. The DecisionRecord is sealed. Merkle / audit walks
out with the buyer. L1 is that week. G13 stays open.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from agent_gov.export import export_envelope, verify_export
from agent_gov.records import as_sealed
from ainav.catalog import acceptance_kit, load_catalog
from ainav.errors import LivePinError, ProvisionError
from ainav.mothership import MasterMothership


def proof_day_spec() -> dict[str, Any]:
    return dict(load_catalog()["proof_day"])


def runbook() -> list[str]:
    spec = proof_day_spec()
    return [
        "Confirm two existing treasury seats from the catalog",
        f"Propose one {spec['action_class']} on {spec['sor_target']}",
        "Admit both seats on the same action_hash",
        "Consume the grant once",
        "Effect on the Business Central twin",
        "Seal the DecisionRecord",
        "Export Merkle / audit",
        "Prepare the next-pin sandbox envelope (sent=False)",
        "Walk out — L1 is that week; signed L1 stays open",
    ]


def run_proof_day(
    client_id: str = "proof-day",
    *,
    seat_a: str | None = None,
    seat_b: str | None = None,
) -> dict[str, Any]:
    """Execute the proof-day runbook on the twin. Not a live pin and not signed L1.

    Named Entra object ids may be supplied. Lab oids are not two named treasury humans.
    """
    if not client_id.strip():
        raise ProvisionError("client_id is required")
    spec = proof_day_spec()
    kit = acceptance_kit()
    named_a = (seat_a or "").strip() or kit["seats"]["seat_a"]["lab"]
    named_b = (seat_b or "").strip() or kit["seats"]["seat_b"]["lab"]
    if named_a == named_b:
        raise ProvisionError("proof day requires two distinct seats", reason_code="SEAT_DISTINCT")
    local = MasterMothership().standard_l1_pack(client_id)
    action = {
        "action_class": spec["action_class"],
        "payload": {
            "account": "1000",
            "amount": "1.00",
            "memo": "proof day journal",
        },
        "proposal_id": f"prp-proof-day-{client_id}-{uuid4().hex[:8]}",
        "sor_target": spec["sor_target"],
        "policy_id": "dual-admit-v1",
    }
    effect = local.run_and_apply(
        action,
        seat_a=named_a,
        seat_b=named_b,
    )
    if effect.get("record_type") != "effect_applied":
        raise ProvisionError("proof day failed on the twin", reason_code="PROOF_DAY_FAIL")
    records = [as_sealed(rec) for rec in local.store.decisions()]
    envelope = export_envelope(records, tip=local.store.tip())
    verify_export(envelope)
    proof = local.client.prove(effect["record_id"])
    from ainav.next_pin import pin_from_twin

    nxt = pin_from_twin(local)
    return {
        "kind": "ainav.proof_day.v1",
        "minutes": spec["minutes"],
        "client_id": client_id,
        "sku": "L1",
        "seats": {
            "seat_a": {**kit["seats"]["seat_a"], "bound": named_a},
            "seat_b": {**kit["seats"]["seat_b"], "bound": named_b},
            "named_humans": bool(seat_a and seat_b),
            "lab_oids_are_not_named_seats": spec.get("lab_oids_are_not_named_seats", True),
        },
        "action_class": action["action_class"],
        "sor_target": action["sor_target"],
        "effect": effect["record_type"],
        "request_id": effect["request_id"],
        "action_hash": effect["action_hash"],
        "record_id": effect["record_id"],
        "sealed": True,
        "journal_seq": local.bc.twin.journals[-1]["request_id"],
        "audit": local.audit(),
        "export": {
            "schema_version": envelope["schema_version"],
            "count": envelope["count"],
            "tip": envelope["tip"],
            "merkle_root": envelope["merkle_root"],
        },
        "inclusion": {
            "record_id": proof.get("record_id"),
            "merkle_root": proof.get("merkle_root"),
        },
        "next_pin": nxt,
        "runbook": runbook(),
        "walk_out": list(spec["walk_out"]),
        "signed_l1": False,
        "live": False,
        "live_pin_ok": False,
        "note": spec["note"],
    }


def claim_signed_l1() -> None:
    raise ProvisionError(
        "Proof day is the path toward signed L1. G13 stays open.",
        reason_code="SIGNED_L1_OPEN",
    )


def claim_live_pin() -> None:
    raise LivePinError(
        "Proof day cannot mark LIVE_PIN_OK. G1/G10 are open.",
        reason_code="LIVE_PIN_NOT_CLAIMED",
    )
