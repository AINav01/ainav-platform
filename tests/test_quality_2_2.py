from __future__ import annotations

import copy

import pytest

from agent_gov import (
    AdmitDenied,
    ConsumeLedger,
    EffectBlocked,
    EffectLedger,
    IntegrityError,
    MemoryAuthorityStore,
    admit,
    default_lockfile,
)
from agent_gov.errors import IntegrityError as IE
from agent_gov.lua_simulator import LuaSimulator
from agent_gov.reasons import ALL, known
from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import ProvisionError
from ainav.mothership import LocalMothership, MasterMothership
from ainav.ops import ClientAccount
from ainav.provision import provision_l1
from ainav.twin import BusinessCentralTwin, SandboxRouter

from tests.helpers import sample_action


def test_missing_grant_id_blocks_effect():
    store = MemoryAuthorityStore()
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    store._admits[rec["request_id"]]["grant_id"] = ""
    with pytest.raises(EffectBlocked) as exc:
        EffectLedger(store=store).effect(rec["request_id"], rec["action_hash"])
    assert exc.value.reason_code == "GRANT_MISSING"


def test_redis_memory_failure_rolls_back_external_key():
    sim = LuaSimulator()

    class BoomStore(MemoryAuthorityStore):
        def try_consume(self, slot_key, record):
            raise IE("seal boom", reason_code="INTEGRITY")

    ledger = ConsumeLedger(store=BoomStore(), simulator=sim)
    with pytest.raises(IE):
        ledger.consume("dual:rollback", {"request_id": "req_x", "action_hash": "aa"})
    assert sim.exists("dual:rollback") is False


def test_seat_denials_are_audited():
    store = MemoryAuthorityStore()
    ledger = ConsumeLedger(store=store)
    with pytest.raises(AdmitDenied) as exc:
        admit(sample_action(), default_lockfile(), ledger=ledger, seat_a="", seat_b="oid-2")
    assert exc.value.reason_code == "SEAT_EMPTY"
    denied = [d for d in store.decisions() if d["record_type"] == "admit_denied"]
    assert denied
    assert denied[0]["reason_code"] == "SEAT_EMPTY"


def test_reserved_effect_recovers_without_reapplying():
    store = MemoryAuthorityStore()
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    store.reserve_effect(rec["request_id"], rec["action_hash"])
    gate = EffectLedger(store=store)
    with pytest.raises(EffectBlocked) as exc:
        gate.effect(
            rec["request_id"],
            rec["action_hash"],
            apply=lambda _g: {"x": 1},
            recover=True,
        )
    assert exc.value.reason_code == "EFFECT_RESERVED_ORPHAN"
    out = gate.effect(rec["request_id"], rec["action_hash"], recover=True)
    assert out["record_type"] == "effect_applied"


def test_abort_reserved_effect():
    store = MemoryAuthorityStore()
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    store.reserve_effect(rec["request_id"], rec["action_hash"])
    out = EffectLedger(store=store).abort_effect(rec["request_id"], rec["action_hash"])
    assert out["record_type"] == "effect_apply_failed"
    assert out["apply_result"]["aborted"] is True


def test_reason_codes_are_closed():
    assert known("GRANT_MISSING")
    assert "LIVE_PIN_OK" not in ALL


def test_direct_twin_write_is_sealed_on_mothership():
    local = provision_l1("acme")
    fake = {
        "record_type": "admit_ok",
        "proposal": {"action_class": "bc.general_journal.post", "sor_target": "bc.sandbox"},
        "action_hash": "a" * 64,
    }
    with pytest.raises(ProvisionError) as exc:
        local.bc.twin.post_journal(fake)
    assert exc.value.reason_code == "TWIN_SEALED"
    with pytest.raises(ProvisionError):
        local.sales.twin.apply(
            {
                "record_type": "admit_ok",
                "proposal": {
                    "action_class": "d365.quote.discount_override",
                    "sor_target": "d365.sales.sandbox",
                },
            }
        )
    with pytest.raises(ProvisionError):
        local.router.apply(fake)


def test_twin_refuses_live_sor_target():
    twin = BusinessCentralTwin()
    with pytest.raises(EffectBlocked) as exc:
        twin.post_journal(
            {
                "record_type": "admit_ok",
                "proposal": {
                    "action_class": "bc.general_journal.post",
                    "sor_target": "bc.live",
                },
            }
        )
    assert exc.value.reason_code == "TWIN_TARGET"
    with pytest.raises(EffectBlocked):
        SandboxRouter().apply({"record_type": "effect_applied", "proposal": {}})


def test_provision_padm_without_l1_or_kit_is_refused():
    with pytest.raises(ProvisionError) as exc:
        MasterMothership().provision("acme", packs=("P-ADM",))
    assert exc.value.reason_code == "PACK_SCOPE"
    with pytest.raises(ProvisionError) as exc2:
        MasterMothership().provision("acme", packs=("L1", "P-ADM"))
    assert exc2.value.reason_code == "ATTACH_GATE"


def test_udual_requires_kit_pass_not_just_stage():
    account = ClientAccount("spoof")
    account.sell_l1()
    account.stage = "KIT_PASS"
    assert account.kit_pass is False
    with pytest.raises(ProvisionError) as exc:
        account.attach_udual()
    assert exc.value.reason_code == "ATTACH_GATE"
    with pytest.raises(ProvisionError):
        account.offer_udual()


def test_catalog_validation_rejects_drift():
    cat = load_catalog()
    bad_job = copy.deepcopy(cat)
    bad_job["entity"]["job"] = "A"
    with pytest.raises(IntegrityError):
        validate_catalog(bad_job)
    bad_schema = copy.deepcopy(cat)
    bad_schema["schema_version"] = "nope"
    with pytest.raises(IntegrityError):
        validate_catalog(bad_schema)
    bad_sku = copy.deepcopy(cat)
    bad_sku["skus"] = [s for s in cat["skus"] if s["id"] != "U-DUAL"]
    with pytest.raises(IntegrityError):
        validate_catalog(bad_sku)
    from ainav.catalog import fee_for_service, industry_pack, library, sku

    with pytest.raises(IntegrityError):
        sku("NOPE")
    with pytest.raises(IntegrityError):
        industry_pack("nope")
    with pytest.raises(IntegrityError):
        library("nope")
    with pytest.raises(IntegrityError):
        fee_for_service("nope")
    with pytest.raises(EffectBlocked):
        EffectLedger().abort_effect("missing", "a" * 64)
    udual = copy.deepcopy(cat)
    for item in udual["skus"]:
        if item["id"] == "U-DUAL":
            item["never_free_with"] = ["U-SOR"]
    with pytest.raises(IntegrityError):
        validate_catalog(udual)
    mod = copy.deepcopy(cat)
    mod["modules"][0]["sku"] = "COPILOT"
    with pytest.raises(IntegrityError):
        validate_catalog(mod)
    ffs = copy.deepcopy(cat)
    ffs["fee_for_service"][0]["sku"] = "L1"
    with pytest.raises(IntegrityError):
        validate_catalog(ffs)
    ip = copy.deepcopy(cat)
    ip["industry_packs"][0]["id"] = "L1"
    with pytest.raises(IntegrityError):
        validate_catalog(ip)
    account = ClientAccount("no-l1")
    account.sell_l1()
    account.start_kit()
    account.pass_kit()
    account.sold = []
    with pytest.raises(ProvisionError) as no_l1:
        account.attach_udual()
    assert no_l1.value.reason_code == "PACK_SCOPE"
    local = provision_l1("libs")
    local.attach_library("lib.l1.wedge")
    local.attach_library("lib.l1.wedge")
    local.kit_pass = True
    local.attach_pack("P-ADM")
    local.attach_pack("P-ADM")
    ffs_inc = copy.deepcopy(cat)
    ffs_inc["fee_for_service"][1]["included_in"] = "NOPE"
    with pytest.raises(IntegrityError):
        validate_catalog(ffs_inc)
    lib_bad = copy.deepcopy(cat)
    lib_bad["libraries"][0]["modules"] = ["not.a.module"]
    with pytest.raises(IntegrityError):
        validate_catalog(lib_bad)
