"""P-ADM weekly keep artifact. Catalog-list export. Not live Purview."""

from __future__ import annotations

from typing import Any

from agent_gov.export import export_envelope, verify_export
from agent_gov.records import as_sealed
from ainav.catalog import load_catalog, sku
from ainav.errors import ProvisionError
from ainav.mothership import MasterMothership


def keep_spec() -> dict[str, Any]:
    return dict(sku("P-ADM")["keep_artifact"])


def weekly_keep(*, client_id: str = "keep-demo") -> dict[str, Any]:
    """Seal twin DecisionRecords as the P-ADM keep artifact. Not live. Not signed L1."""
    if not client_id.strip():
        raise ProvisionError("client_id is required")
    spec = keep_spec()
    local = MasterMothership().standard_l1_pack(client_id)
    local.kit_pass = True
    local.attach_pack("P-ADM")
    action = {
        "action_class": "bc.general_journal.post",
        "payload": {"account": "1000", "amount": "1.00", "memo": "padm weekly keep"},
        "proposal_id": f"prp-keep-{client_id}",
        "sor_target": "bc.sandbox",
        "policy_id": "dual-admit-v1",
    }
    effect = local.run_and_apply(action, seat_a="oid-1", seat_b="oid-2")
    records = [as_sealed(rec) for rec in local.store.decisions()]
    envelope = export_envelope(records, tip=local.store.tip())
    verify_export(envelope)
    return {
        "kind": "ainav.padm.keep.v1",
        "client_id": client_id,
        "artifact": spec["id"],
        "cadence": spec["cadence"],
        "sink": spec["sink"],
        "export_module": spec["export"],
        "effect": effect["record_type"],
        "merkle_root": envelope["merkle_root"],
        "count": envelope["count"],
        "wired": False,
        "live": False,
        "live_pin_ok": False,
        "signed_l1": False,
        "note": spec["note"],
    }
