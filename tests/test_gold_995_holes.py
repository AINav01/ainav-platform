from __future__ import annotations

import json
import re
import runpy
import sys
from pathlib import Path

import pytest

from agent_gov.consume import ConsumeLedger
from agent_gov.errors import IntegrityError
from agent_gov.lua_simulator import OK
from agent_gov.records import as_sealed, decision_record, verify_chain
from agent_gov.redis_consume import RedisDualConsume
from agent_gov.store import FileAuthorityStore, MemoryAuthorityStore
from ainav import catalog as catmod
from ainav.catalog import load_catalog, validate_catalog
from ainav.honest_whole import run_whole_certification
from ainav.investor import _wrap
from ainav.next_pin import sandbox_envelope
from ainav.ops import ClientAccount
from ainav.proof_day import run_proof_day
from tests.helpers import sample_action


def _cat() -> dict:
    return json.loads(json.dumps(load_catalog()))


def _reject(fn, *args):
    with pytest.raises(IntegrityError):
        fn(*args)


def _scrub(text: str, *needles: str) -> str:
    out = text
    for needle in needles:
        out = re.sub(re.escape(needle), "hold", out, flags=re.I)
    return out


def _scrub_principles(*needles: str) -> list[str]:
    return [_scrub(item, *needles) for item in load_catalog()["expert_review"]["first_principles"]]


def test_first_principles_late_honest_boards():
    _reject(catmod._validate_first_principles, _scrub_principles("licensed is not wired"))
    _reject(catmod._validate_first_principles, _scrub_principles("available is not a seat"))
    _reject(catmod._validate_first_principles, _scrub_principles("outlook mail is not a click"))
    _reject(catmod._validate_first_principles, _scrub_principles("grok login is not this plane"))
    _reject(catmod._validate_first_principles, _scrub_principles("operate sim is not production"))
    _reject(catmod._validate_first_principles, _scrub_principles("10/10 polish is not launch"))
    _reject(catmod._validate_first_principles, _scrub_principles("shared sandbox is not production"))
    _reject(catmod._validate_first_principles, _scrub_principles("hours are not a sku"))
    _reject(catmod._validate_first_principles, _scrub_principles("rollback is not live_pin_ok"))
    _reject(catmod._validate_first_principles, _scrub_principles("a redeploy is not launch"))
    _reject(catmod._validate_first_principles, _scrub_principles("fixing all is not this plane"))
    _reject(catmod._validate_first_principles, _scrub_principles("rehearsed elements are not live"))
    _reject(catmod._validate_first_principles, _scrub_principles("making all much better is not launch"))
    _reject(catmod._validate_first_principles, _scrub_principles("a rehearsal is not live_pin_ok"))
    _reject(catmod._validate_first_principles, _scrub_principles("a remainder close is not launch"))
    _reject(catmod._validate_first_principles, _scrub_principles("leftover copy is not live_pin_ok"))
    _reject(catmod._validate_first_principles, _scrub_principles("owner hrefs are not owner clicks"))
    _reject(catmod._validate_first_principles, _scrub_principles("gold 99.5 is not production"))
    _reject(catmod._validate_first_principles, _scrub_principles("a deep remainder is not a seated second human"))


def test_ciso_and_success_hosted_holes():
    cat = _cat()
    ciso = cat["expert_review"]["success"]["ciso"]["does_not"]
    cat["expert_review"]["success"]["ciso"]["does_not"] = [
        _scrub(item, "maps as certificates on the industry drawer") for item in ciso
    ]
    _reject(catmod._validate_success_program, cat["expert_review"]["success"])
    cat = _cat()
    cat["expert_review"]["success"]["microsoft_agents"] = None
    _reject(catmod._validate_success_program, cat["expert_review"]["success"])
    cat = _cat()
    cat["expert_review"]["success"]["honest_access"] = None
    _reject(catmod._validate_success_program, cat["expert_review"]["success"])
    cat = _cat()
    cat["expert_review"]["success"]["honest_readiness"]["launch_day_certified"] = True
    _reject(catmod._validate_success_program, cat["expert_review"]["success"])
    cat = _cat()
    cat["expert_review"]["success"]["honest_industry"]["industry_certified_launch"] = True
    _reject(catmod._validate_success_program, cat["expert_review"]["success"])


def test_operating_company_and_launch_gate_holes():
    firm = json.loads(json.dumps(load_catalog()["expert_review"]["success"]["operating_company"]))
    firm["site"] = _scrub(firm["site"], "operating day", "launch gate")
    _reject(catmod._validate_operating_company, firm)
    firm = json.loads(json.dumps(load_catalog()["expert_review"]["success"]["operating_company"]))
    firm["note"] = _scrub(firm["note"], "launch stays false")
    _reject(catmod._validate_operating_company, firm)
    gates = json.loads(json.dumps(load_catalog()["expert_review"]["success"]["operating_company"]["gates"]))
    for item in gates["items"]:
        if item.get("id") == "seat_b":
            item["held"] = True
    _reject(catmod._validate_launch_gate, gates)
    gates = json.loads(json.dumps(load_catalog()["expert_review"]["success"]["operating_company"]["gates"]))
    for item in gates["items"]:
        if item.get("id") == "gold":
            item["note"] = "Gold is not launch."
    _reject(catmod._validate_launch_gate, gates)


def test_industry_drawer_and_rooms_holes():
    drawer = json.loads(json.dumps(load_catalog()["expert_review"]["success"]["industry_drawer"]))
    drawer["glance"] = _scrub(drawer["glance"], "complete industry drawer")
    _reject(catmod._validate_industry_drawer, drawer)
    drawer = json.loads(json.dumps(load_catalog()["expert_review"]["success"]["industry_drawer"]))
    drawer["site"] = _scrub(drawer["site"], "complete industry drawer")
    _reject(catmod._validate_industry_drawer, drawer)
    drawer = json.loads(json.dumps(load_catalog()["expert_review"]["success"]["industry_drawer"]))
    drawer["note"] = _scrub(drawer["note"], "complete industry drawer")
    _reject(catmod._validate_industry_drawer, drawer)
    rooms = json.loads(
        json.dumps(load_catalog()["expert_review"]["success"]["industry_drawer"]["rooms"])
    )
    rooms["site"] = _scrub(rooms["site"], "#packs", "#industry")
    _reject(catmod._validate_industry_rooms, rooms)


def test_edge_quality_activate_and_confirm_holes():
    cat = _cat()
    now = cat["microsoft_stack"]["edge"]["activate"]["now"]
    for item in now:
        item["id"] = _scrub(str(item.get("id") or ""), "grey", "outlook")
        item["do"] = _scrub(str(item.get("do") or ""), "grey", "outlook")
    _reject(catmod._validate_microsoft_edge, cat)
    cat = _cat()
    wait = cat["microsoft_stack"]["edge"]["activate"]["wait"]
    for item in wait:
        item["id"] = _scrub(str(item.get("id") or ""), "reject")
        item["do"] = _scrub(str(item.get("do") or ""), "reject")
    _reject(catmod._validate_microsoft_edge, cat)
    edge = json.loads(json.dumps(load_catalog()["microsoft_stack"]["edge"]))
    edge["quality"]["confirm"] = [
        item for item in edge["quality"]["confirm"] if "403-vs-404" not in str(item).lower()
    ]
    _reject(catmod._validate_edge_quality, edge)


def test_engineering_cannot_close_and_dataverse_integrate():
    cat = _cat()
    cat["engineering"]["cannot_close"] = [
        item for item in cat["engineering"]["cannot_close"] if "live_pin" not in item.lower()
    ]
    _reject(catmod._validate_engineering, cat)
    cat = _cat()
    cat["engineering"]["cannot_close"] = [
        item
        for item in cat["engineering"]["cannot_close"]
        if "cynthia" not in item.lower() and "second unique" not in item.lower()
    ]
    _reject(catmod._validate_engineering, cat)
    cat = _cat()
    items = ((cat.get("plane_interface") or {}).get("floor") or {}).get("integrate") or {}
    items["items"] = [item for item in items.get("items") or [] if item.get("id") != "dataverse.us"]
    _reject(catmod._validate_us_dataverse, cat)


def test_instrument_history_and_plane_holes():
    cat = _cat()
    cat["microsoft_stack"]["edge"]["quality"]["ssl_full_claimed"] = True
    _reject(catmod._validate_instrument_275, cat, cat["plane_interface"])
    cat = _cat()
    cat["expert_review"]["success"]["operating_company"]["gates"]["kind"] = "invented"
    _reject(catmod._validate_instrument_287, cat, cat["plane_interface"])
    cat = _cat()
    cat["expert_review"]["success"]["operating_company"]["gates"]["launch"] = True
    _reject(catmod._validate_instrument_287, cat, cat["plane_interface"])
    cat = _cat()
    cat["operations"]["note"] = "SKU attach only"
    _reject(catmod._validate_instrument_302, cat, cat["plane_interface"])
    cat = _cat()
    cat["expert_review"]["first_principles"] = _scrub_principles("does not need full access")
    _reject(catmod._validate_instrument_305, cat, cat["plane_interface"])
    cat = _cat()
    cat["expert_review"]["first_principles"] = _scrub_principles("gold is not launch")
    _reject(catmod._validate_instrument_306, cat, cat["plane_interface"])
    cat = _cat()
    demo = cat["plane_interface"]["examiner_walk"]["demo"]
    demo["record_id"] = "named.record"
    demo["included"] = True
    demo["leaf"] = "named"
    demo["root"] = "named"
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    demo = cat["plane_interface"]["examiner_walk"]["demo"]
    demo["record_id"] = "named.record"
    demo["included"] = False
    demo["leaf"] = "named"
    _reject(catmod._validate_plane_interface, cat)


def test_plane_interface_late_holes():
    cat = _cat()
    cat["plane_interface"]["thesis"] = "dashboard remote compliance"
    cat["plane_interface"]["letter"] = "human dashboard remote compliance"
    cat["plane_interface"]["refuse"] = ["fourth sku"]
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    cat["plane_interface"]["client_dashboard"]["executive_board"]["sku"] = True
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    cat["plane_interface"]["provision_bands"]["attach_means"] = "priced desks"
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    cat["plane_interface"]["included_and_upsells"]["standard_vs_advanced_dashboard"] = True
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    offer = cat["plane_interface"]["included_and_upsells"]
    offer["attach_means"] = "different"
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    cat["plane_interface"]["included_and_upsells"]["thesis"] = "three sku upsell band"
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    for item in cat["plane_interface"]["included_and_upsells"]["refuse"]:
        if "included means free" in str(item).lower():
            cat["plane_interface"]["included_and_upsells"]["refuse"].remove(item)
            break
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    cat["plane_interface"]["floor"]["lede"] = cat["plane_interface"]["floor"]["lede"].replace(
        "already have", "hold"
    )
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    rail = cat["plane_interface"]["floor"]["first_glance"]["write_rail"]
    rail[0]["name"] = "hold"
    rail[0]["note"] = "hold"
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    gates = cat["owner_gates"]
    items = cat["plane_interface"]["floor"]["integrate"]["items"]
    if items and gates:
        items[0]["note"] = "hold"
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    items = cat["plane_interface"]["floor"]["integrate"]["items"]
    if items:
        items[0]["url"] = "https://example.com/?entra_client_id=2ad041b8"
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    cat["plane_interface"]["provision_bands"]["desk_band_means"] = "priced"
    _reject(catmod._validate_plane_interface, cat)
    cat = _cat()
    for item in cat["plane_interface"]["authorizations"]:
        if item.get("id") == "seat":
            item["note"] = "mailbox recorded"
    _reject(catmod._validate_plane_interface, cat)


def test_view_estate_audit_upsell_repo_day_map_holes():
    cat = _cat()
    assign = cat["plane_interface"]["view_assignment"]
    assign["matrix"][0]["allowed_views"] = ["invented"]
    assign["matrix"][0]["default_view"] = "invented"
    _reject(catmod._validate_view_assignment, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["view_assignment"]["mfa"]["internal"]["admit"] = True
    _reject(catmod._validate_view_assignment, cat, cat["plane_interface"])
    cat = _cat()
    rec_col = next(
        item
        for item in cat["plane_interface"]["estate"]["first_glance"]["columns"]
        if item.get("id") == "records_maps"
    )
    rec_col["items"] = ["two records"]
    _reject(catmod._validate_estate, cat, cat["plane_interface"])
    cat = _cat()
    prove = next(
        item
        for item in cat["plane_interface"]["estate"]["other_uses"]["bands"]
        if item.get("id") == "prove"
    )
    prove["desks"] = ["invented.desk"]
    _reject(catmod._validate_estate, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["audit"]["thesis"] = "internal audit does not admit"
    _reject(catmod._validate_audit, cat, cat["plane_interface"])
    cat = _cat()
    for pack in cat["industry_packs"]:
        pack["runbook"] = ""
        break
    _reject(catmod._validate_upsells, cat)
    cat = _cat()
    cat["repositories"] = []
    _reject(catmod._validate_repositories, cat)
    cat = _cat()
    cat["repositories"][0]["sku"] = True
    _reject(catmod._validate_repositories, cat)
    cat = _cat()
    run = cat["expert_review"]["success"]["operating_company"]["microsoft_run"]
    for item in run["day_map"]:
        if item.get("id") == "launch":
            item["on"] = []
    _reject(catmod._validate_microsoft_run, run)


def test_consume_rollback_and_store_holes(tmp_path):
    class BoomRedis:
        def __init__(self) -> None:
            self.deleted = None

        def eval(self, keys, argv):
            return OK

        def delete(self, key):
            self.deleted = key

    class BoomStore(MemoryAuthorityStore):
        def try_consume(self, slot_key, record):
            raise RuntimeError("store fail after external ok")

    redis = BoomRedis()
    ledger = ConsumeLedger(store=BoomStore(), redis=redis)
    with pytest.raises(RuntimeError):
        ledger.consume(
            "slot-995",
            {
                "request_id": "req-995",
                "action_hash": "a" * 64,
                "seat_a": "oid-1",
                "seat_b": "oid-2",
                "consumed_at": "now",
            },
        )
    assert redis.deleted == "slot-995"

    class NoDelete:
        delete = "missing"

    bare = ConsumeLedger(store=MemoryAuthorityStore(), redis=NoDelete())
    bare._rollback_external("slot-bare")
    RedisDualConsume(NoDelete()).delete("slot-bare")

    rec = decision_record(
        record_type="admit_denied",
        request_id="req-seq-995",
        action_hash="b" * 64,
        action=sample_action(),
        reason_code="SEAT_DISTINCT",
    )
    sealed = dict(as_sealed(rec))
    sealed["seq"] = 9
    sealed["prev_receipt_hash"] = sealed.get("integrity", {}).get("prev_receipt_hash")
    with pytest.raises(IntegrityError):
        verify_chain([sealed])

    store = MemoryAuthorityStore()
    assert store.get_record("missing-995") is None
    path = tmp_path / "ledger.jsonl"
    FileAuthorityStore(path)
    denied = {
        "record_type": "admit_denied",
        "request_id": "req-file-995",
        "integrity": {"content_hash": "c" * 64},
    }
    file_store = FileAuthorityStore(path)
    file_store._replay(denied)


def test_small_module_holes(monkeypatch):
    assert _wrap("supercalifragilistic", 8)
    assert _wrap("a b c d e", 20)
    assert _wrap("", 10) == [""]
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "launched"},
    )
    with pytest.raises(IntegrityError):
        run_whole_certification()
    env = sandbox_envelope({"sor_target": "lab.sandbox.other", "payload": {}})
    assert env
    life = ClientAccount("cli-995")
    life.stage = "KIT_IN_PROGRESS"
    monkeypatch.setattr(life, "run_kit", lambda: {"passed": False})
    with pytest.raises(Exception):
        life.pass_kit()
    life.local = None
    life.cloud = None
    monkeypatch.setattr(life, "run_kit", lambda: {"passed": True})
    life.stage = "KIT_IN_PROGRESS"
    life.pass_kit()
    life.kit_pass = True
    life.sold = ["L1"]
    life.stage = "SOLD"
    with pytest.raises(Exception):
        life.attach_udual()
    from ainav.proof_day import proof_day_spec

    spec = dict(proof_day_spec())
    spec.pop("grant_ttl_seconds", None)
    monkeypatch.setattr("ainav.proof_day.proof_day_spec", lambda: spec)
    run_proof_day("cli-ttl-995")


def test_main_modules_as_scripts(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["agent_gov", "--help"])
    with pytest.raises(SystemExit):
        runpy.run_module("agent_gov.__main__", run_name="__main__")
    monkeypatch.setattr(sys, "argv", ["ainav", "--help"])
    with pytest.raises(SystemExit):
        runpy.run_module("ainav.__main__", run_name="__main__")
    from ainav.__main__ import _examiner_prove

    assert _examiner_prove(record_id="") == 0
