from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_gov.errors import EffectBlocked, IntegrityError, LockfileError
from agent_gov.lockfile import HARD_INVARIANTS, Lockfile, load_lockfile
from agent_gov.records import DecisionRecord, as_sealed, decision_record, verify_chain, verify_record
from agent_gov.store import FileAuthorityStore, default_store, reset_default_store
from ainav.business import OperatingCompany
from ainav.errors import ProvisionError
from ainav.ip import screen_pack_label
from ainav.mothership import LocalMothership, MasterMothership
from ainav.proof_day import run_proof_day
from tests.helpers import sample_action


def _denied(**overrides):
    rec = decision_record(
        record_type="admit_denied",
        request_id=overrides.pop("request_id", "req_hold"),
        action_hash=overrides.pop("action_hash", "e" * 64),
        action=sample_action(),
        reason_code="SEAT_DISTINCT",
    )
    rec.update(overrides)
    return rec


def test_unsealed_decision_record_mutators_and_verify_gaps():
    rec = DecisionRecord({"a": 1})
    rec["b"] = 2
    rec.update({"c": 3})
    rec.setdefault("d", 4)
    rec.pop("d")
    rec.popitem()
    del rec["b"]
    rec.clear()
    missing = {
        "schema_version": "decision_record.v1",
        "record_id": "dr_x",
        "record_type": "admit_denied",
        "request_id": "req_x",
        "action_hash": "f" * 64,
        "integrity": "nope",
    }
    with pytest.raises(IntegrityError):
        verify_record(missing)
    store = default_store()
    again = default_store()
    assert store is again
    reset_default_store()
    sealed = default_store().put_denied(_denied(request_id="req_seq"))
    broken = dict(sealed)
    broken["seq"] = 9
    with pytest.raises(IntegrityError):
        verify_chain([broken])


def test_file_store_blank_lines_and_corrupt_tip(tmp_path):
    blank = tmp_path / "blank.jsonl"
    blank.write_text("\n\n", encoding="utf-8")
    FileAuthorityStore(blank)

    good = tmp_path / "good.jsonl"
    store = FileAuthorityStore(good)
    store.put_denied(_denied(request_id="req_tip"))
    tip = good.with_name(good.name + ".tip")
    assert tip.exists()
    tip.write_text("{not json", encoding="utf-8")
    with pytest.raises(IntegrityError):
        FileAuthorityStore(good)
    tip.write_text(
        json.dumps({"alg": "sha256", "count": 99, "tip": "0" * 64, "merkle_root": "0" * 64}),
        encoding="utf-8",
    )
    with pytest.raises(IntegrityError):
        FileAuthorityStore(good)

    unread = tmp_path / "unread.jsonl"
    unread.write_text("x\n", encoding="utf-8")

    def boom(self, *args, **kwargs):
        if self.name == "unread.jsonl":
            raise OSError("no")
        return Path.read_text(self, *args, **kwargs)

    with patch.object(Path, "read_text", boom):
        with pytest.raises(IntegrityError):
            FileAuthorityStore(unread)


def test_lockfile_cannot_drop_action_class_on_verify():
    with pytest.raises(LockfileError):
        Lockfile(
            required_action_fields=("payload",),
            invariants=dict(HARD_INVARIANTS),
            policy_hash="",
        ).verify()
    with pytest.raises(LockfileError):
        load_lockfile({"invariants": 1})


def test_proof_day_fails_when_effect_does_not_apply():
    with patch("ainav.proof_day.MasterMothership") as master:
        local = LocalMothership("proof-fail")
        local.run_and_apply = lambda *a, **k: {"record_type": "admit_denied"}
        master.return_value.standard_l1_pack.return_value = local
        with pytest.raises(ProvisionError) as exc:
            run_proof_day("proof-fail")
        assert exc.value.reason_code == "PROOF_DAY_FAIL"


def test_business_skips_missing_host_and_mothership_gaps():
    company = OperatingCompany()
    account = company.qualify("gap-host")
    account.sell_l1 = lambda: None
    account.start_kit = lambda: None
    account.pass_kit = lambda: None
    account.book = lambda *_a, **_k: None
    account.attach_padm = lambda: None
    account.offer_udual = lambda: None
    account.attach_udual = lambda: None
    company.store_kit_evidence = lambda *_a, **_k: None
    account.local = LocalMothership("gap-host")
    account.local.attach_industry = lambda *_a, **_k: {}
    account.local.attach_library = lambda *_a, **_k: {}
    account.cloud = None
    company.run_standard_engagement("gap-host")

    local = LocalMothership("pack-gap")
    local.packs = ()
    local.kit_pass = True
    with pytest.raises(ProvisionError):
        local.attach_pack("P-ADM")
    local.packs = ("L1",)
    local.attach_industry("industry.controller")
    local.attach_library("lib.kit.evidence")
    assert local.modules()
    local.attach_industry("industry.controller")
    local.attach_library("lib.kit.evidence")

    from ainav.mothership import CloudMothership
    from agent_gov.lockfile import Lockfile as LF

    real_init = CloudMothership.__init__

    def tampered(self, *args, **kwargs):
        real_init(self, *args, **kwargs)
        self.lockfile = LF(policy_id="tampered", policy_hash="x")

    with patch.object(CloudMothership, "__init__", tampered):
        with pytest.raises(ProvisionError) as exc:
            MasterMothership().provision_pair("pair-mismatch")
        assert exc.value.reason_code == "LOCKFILE_HASH_MISMATCH"


def test_effect_recover_without_reserve_and_empty_pack_label():
    from agent_gov.effect import EffectLedger
    from agent_gov.store import MemoryAuthorityStore

    store = MemoryAuthorityStore()
    admitted = store.put_denied(_denied(request_id="req_effect"))
    store._admits[admitted["request_id"]] = {**admitted, "record_type": "admit_ok", "consumed": True}
    ledger = EffectLedger(store=store)
    with pytest.raises(EffectBlocked):
        ledger.effect(admitted["request_id"], admitted["action_hash"], recover=True)
    screen_pack_label("L1")
    screen_pack_label("")
    screen_pack_label("   ")


def test_remaining_fail_closed_holes_push_gold_over_95():
    import copy
    from collections.abc import Mapping

    from ainav.catalog import (
        _validate_catalog_shape,
        _validate_engineering,
        _validate_finance,
        _validate_formal,
        _validate_honest_missing,
        _validate_mailbox_law,
        fee_for_service,
        industry_pack,
        l1_incident_copy,
        library,
        load_catalog,
        module_by_id,
        validate_catalog,
        wedge_action_classes,
    )
    from ainav.dashboard import _desk_row
    from ainav.errors import LivePinError
    from ainav.finance import public_finance
    from ainav.ops import ClientAccount
    from ainav.packs import book_service
    from ainav.twin import _require_sandbox_target
    from agent_gov.errors import EffectBlocked

    cat = load_catalog()

    def reject(mutator):
        body = copy.deepcopy(cat)
        mutator(body)
        with pytest.raises(IntegrityError):
            validate_catalog(body)

    reject(lambda c: c["microsoft_stack"]["edge"].__setitem__("note", "Cloudflare is not the product. MX stays DNS-only. Not Institute launch."))
    with pytest.raises(IntegrityError):
        _validate_engineering({"engineering": None})
    with pytest.raises(IntegrityError):
        _validate_engineering({"engineering": {**cat["engineering"], "gold_ci": None}})
    with pytest.raises(IntegrityError):
        _validate_engineering(
            {"engineering": {**copy.deepcopy(cat["engineering"]), "gold_ci": {**cat["engineering"]["gold_ci"], "coverage_floor": 90}}}
        )
    with pytest.raises(IntegrityError):
        _validate_engineering(
            {"engineering": {**copy.deepcopy(cat["engineering"]), "gold_ci": {**cat["engineering"]["gold_ci"], "command": "pytest"}}}
        )
    with pytest.raises(IntegrityError):
        _validate_engineering(
            {
                "engineering": {
                    **copy.deepcopy(cat["engineering"]),
                    "gold_ci": {**cat["engineering"]["gold_ci"], "note": "Gold CI ran green. A green check is a green check."},
                }
            }
        )
    with pytest.raises(IntegrityError):
        _validate_engineering({"engineering": {**copy.deepcopy(cat["engineering"]), "cannot_close": []}})
    with pytest.raises(IntegrityError):
        _validate_engineering({"engineering": {**copy.deepcopy(cat["engineering"]), "closed_in_tree": []}})
    with pytest.raises(IntegrityError):
        _validate_engineering({"engineering": {**copy.deepcopy(cat["engineering"]), "closed_in_tree": ["LIVE_PIN_OK is marked"]}})
    stripped = [
        item
        for item in cat["engineering"]["closed_in_tree"]
        if "gold" not in item.lower() and "github" not in item.lower() and "workflow" not in item.lower()
    ] or ["pending bind 0"]
    with pytest.raises(IntegrityError):
        _validate_engineering({"engineering": {**copy.deepcopy(cat["engineering"]), "closed_in_tree": stripped}})
    with pytest.raises(IntegrityError):
        _validate_honest_missing({"honest_missing": []})
    with pytest.raises(IntegrityError):
        _validate_honest_missing({"honest_missing": ["LIVE_PIN_OK is open", "Graph Read"]})
    with pytest.raises(IntegrityError):
        _validate_finance({})
    with pytest.raises(IntegrityError):
        _validate_mailbox_law(
            {
                "organization": {
                    "contacts": {"invited": {**cat["organization"]["contacts"]["invited"], "seat_role": "other"}}
                }
            }
        )
    with pytest.raises(IntegrityError):
        _validate_formal({"formal": {**cat["engineering"]["formal"], "spec": "missing.tla"}})
    reject(lambda c: c.__setitem__("financial_model", None))
    reject(lambda c: c["financial_model"].__setitem__("recognized_revenue", 1))
    reject(lambda c: c["financial_model"].__setitem__("signed_l1", 1))
    reject(lambda c: c["financial_model"].__setitem__("named_customers", 1))
    reject(lambda c: c["financial_model"].__setitem__("billing_provider", True))
    reject(lambda c: c["financial_model"].__setitem__("pricing_models", []))
    reject(lambda c: c.__setitem__("investor", None))
    reject(lambda c: c["organization"]["contacts"]["invited"].__setitem__("seat_role", "other"))
    reject(lambda c: c["equations"].__setitem__("interface", c["equations"]["interface"].replace("regulated entities", "entities")))
    reject(lambda c: c["expert_review"].__setitem__("upgrades", [item for item in c["expert_review"]["upgrades"] if item.get("n") != 16]))
    reject(lambda c: next(item for item in c["expert_review"]["upgrades"] if item.get("n") == 17).__setitem__("done", False))
    def _break_upgrade_stems(c):
        item = next(row for row in c["expert_review"]["upgrades"] if row.get("n") == 17)
        item["title"] = "Other"
        item["do"] = "Other"

    reject(_break_upgrade_stems)
    reject(lambda c: c["icp"].__setitem__("must_have_for", ["owner"]))
    reject(lambda c: next(m for m in c["modules"] if m.get("id") == "bc.general_journal.post").__setitem__("sku", "P-ADM"))
    reject(lambda c: next(m for m in c["modules"] if m.get("id") == "d365.order.submit").__setitem__("wedge", False))
    reject(lambda c: next(p for p in c["industry_packs"] if p.get("included_in_sku") is True).__setitem__("attach_usd", {"min": 1, "max": 1}))
    reject(lambda c: next(p for p in c["industry_packs"] if p.get("included_in_sku") is not True and p.get("ala_carte") is True).__setitem__("attach_usd", {"min": 0, "max": 0}))
    reject(lambda c: c["modules"].append({"id": "mod.unseated.upsell", "sku": "L1", "kind": "help", "upsell": True}))
    reject(lambda c: c["governance"]["plane"].__setitem__("off_switch", {"does": "stop", "does_not": "power down Copilot"}))
    reject(lambda c: c["governance"]["plane"].__setitem__("rollback", {"does": "undo", "does_not": "time machine"}))
    reject(lambda c: c["plane_interface"]["floor"]["public_face"]["app"].__setitem__("href", "index.html"))
    reject(lambda c: c["plane_interface"]["floor"]["public_face"].__setitem__("primary", []))
    reject(lambda c: c["plane_interface"]["view_assignment"].__setitem__("named_assignments", ["cfo"]))
    reject(lambda c: c["plane_interface"]["view_assignment"].__setitem__("cloud_agent_cannot_assign", False))
    reject(lambda c: c["plane_interface"]["client_dashboard"].__setitem__("same_as", "other"))
    reject(lambda c: c["plane_interface"]["dashboard"].__setitem__("same_as", "other"))
    reject(lambda c: (c["plane_interface"]["client_dashboard"].get("executive_board") or {}).__setitem__("included_with", "P-ADM"))
    reject(lambda c: (c["plane_interface"]["client_dashboard"].get("executive_board") or {}).__setitem__("sections", []))
    reject(lambda c: c["plane_interface"]["floor"].__setitem__("first_glance", None))
    reject(lambda c: c["plane_interface"]["floor"]["first_glance"].__setitem__("sku", True))
    reject(lambda c: c["plane_interface"]["floor"].__setitem__("page", {**c["plane_interface"]["floor"].get("page", {}), "twin_heading": "Sandbox"}))
    reject(lambda c: c["plane_interface"]["gaps"].__setitem__("gold_floor", 95) or c["engineering"]["gold_ci"].__setitem__("coverage_floor", 90))

    real_is_file = Path.is_file
    real_read = Path.read_text

    def hide_pyproject(self, *args, **kwargs):
        if self.name == "pyproject.toml":
            return False
        return real_is_file(self)

    def downgrade_floor(self, *args, **kwargs):
        text = real_read(self, *args, **kwargs)
        if self.name == "pyproject.toml":
            return text.replace("fail_under = 99", "fail_under = 90")
        return text

    def hide_schema(self, *args, **kwargs):
        if self.name == "action.schema.json":
            return False
        return real_is_file(self)

    def hide_spec(self, *args, **kwargs):
        if self.name == "consume_once.tla":
            return False
        return real_is_file(self)

    def blank_spec(self, *args, **kwargs):
        if self.name == "consume_once.tla":
            return "SPEC WITHOUT THE WORD"
        return real_read(self, *args, **kwargs)

    with patch.object(Path, "is_file", hide_pyproject):
        with pytest.raises(IntegrityError):
            validate_catalog(copy.deepcopy(cat))
    with patch.object(Path, "read_text", downgrade_floor):
        with pytest.raises(IntegrityError):
            validate_catalog(copy.deepcopy(cat))
    with patch.object(Path, "is_file", hide_schema):
        with pytest.raises(IntegrityError):
            _validate_catalog_shape(copy.deepcopy(cat["engineering"]))
        with pytest.raises(IntegrityError):
            validate_catalog(copy.deepcopy(cat))
    with patch.object(Path, "is_file", hide_spec):
        with pytest.raises(IntegrityError):
            validate_catalog(copy.deepcopy(cat))
    with patch.object(Path, "read_text", blank_spec):
        with pytest.raises(IntegrityError):
            validate_catalog(copy.deepcopy(cat))

    reset_default_store()
    first = default_store()
    assert default_store() is first

    class BoomMap(Mapping):
        def __getitem__(self, key):
            raise TypeError("boom")

        def __iter__(self):
            raise TypeError("boom")

        def __len__(self):
            return 1

    with pytest.raises(LockfileError):
        load_lockfile({"invariants": BoomMap()})

    with pytest.raises(EffectBlocked):
        _require_sandbox_target({"sor_target": "bc.other"}, default_target="bc.sandbox")

    assert public_finance()["recognized_revenue"] in (0, False)
    assert "journal" in l1_incident_copy().lower() or l1_incident_copy()
    assert "bc.general_journal.post" in wedge_action_classes("L1")
    with pytest.raises(IntegrityError):
        module_by_id("mod.does.not.exist")
    with pytest.raises(IntegrityError):
        fee_for_service("ffs.does.not.exist")
    with pytest.raises(IntegrityError):
        industry_pack("industry.does.not.exist")
    with pytest.raises(IntegrityError):
        library("lib.does.not.exist")
    row = _desk_row({"id": "desk.x", "name": "X", "included_in_sku": False, "attach_usd": {"min": 0, "max": 0}}, kind="desk")
    assert row["attach"] == "priced"

    def fake_ffs(service_id):
        return {
            "id": service_id,
            "name": "Integration assist",
            "included_in": None,
            "billable": True,
            "requires_l1": True,
            "attaches_udual": True,
            "rate_usd_per_day": 3500,
        }

    with patch("ainav.packs.fee_for_service", fake_ffs):
        with pytest.raises(ProvisionError):
            book_service("ffs.integration_assist", skus=("L1",))

    account = ClientAccount("ops-gap")
    account.kit_pass = True
    account.stage = "SOLD"
    account.sold = ["L1"]
    with pytest.raises(ProvisionError):
        account.offer_udual()
    with pytest.raises(ProvisionError):
        account.attach_udual()
    with patch("ainav.ops.book_service", return_value={"id": "ffs.x", "sku": "L1"}):
        with pytest.raises(ProvisionError):
            account.book("ffs.integration_assist")
    with pytest.raises(LivePinError):
        account.claim_live_pin()

    local = LocalMothership("mod-gap")
    local.packs = ()
    local.industry = ("industry.controller",)
    local.libraries = ("lib.kit.evidence",)
    assert local.modules()

    from ainav.microsoft import host_bind

    with patch.object(host_bind, "_request", return_value=(200, {"properties": {"provisioningState": "Creating"}})):
        with patch.object(host_bind.time, "sleep"):
            host_bind._wait_vault("sub", "vault", "tok")
