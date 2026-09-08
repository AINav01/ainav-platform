from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_READY_IDS,
    HONEST_READY_REFUSE_TEXT,
    HONEST_READY_ROLES,
    load_catalog,
    validate_catalog,
)
from ainav.microsoft.readiness import public_review, run_twin_certification, validate_honest_readiness


def test_readiness_review_is_not_launch_day():
    body = public_review()
    assert body["kind"] == "ainav.honest.readiness.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["gold_is_launch"] is False
    assert body["twin_is_launch_day"] is False
    assert body["sim_is_production"] is False
    assert body["update_is_live_pin"] is False
    assert body["launch_day_certified"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert "gold is not launch" in body["lede"].lower()
    assert "twin certified is not launch day" in body["lede"].lower()
    assert "owner gaps stay owner-only" in body["lede"].lower()
    assert [item["id"] for item in body["lanes"]] == list(HONEST_READY_IDS)
    assert {item["id"]: item["role"] for item in body["lanes"]} == dict(HONEST_READY_ROLES)
    assert all(item["installed"] is None and item.get("seat") is not True for item in body["lanes"])
    assert "Treat gold as launch." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["quality"] is True
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"
    on_disk = json.loads(Path("institute/ready.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_twin_certification_holds_launch():
    probes = run_twin_certification()
    assert probes["kind"] == "ainav.honest.readiness.v1"
    assert probes["quality"] is True
    assert probes["operability"] is True
    assert probes["simulation"] is True
    assert probes["deliverability"] is True
    assert probes["updateability"] is True
    assert probes["debugging"] is True
    assert probes["launch"] is False
    assert probes["launch_day_certified"] is False
    assert probes["live_pin_ok"] is False


def test_run_twin_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "launched"},
    )
    with pytest.raises(IntegrityError):
        run_twin_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.ops.STAGES", ("QUALIFY",))
    with pytest.raises(IntegrityError):
        run_twin_certification()
    monkeypatch.setattr("ainav.ops.STAGES", ("L1_SOLD", "KIT_PASS"))
    monkeypatch.setattr("ainav.ops.EXITS", ("CHURN",))
    with pytest.raises(IntegrityError):
        run_twin_certification()
    monkeypatch.setattr("ainav.ops.EXITS", ("LOST", "CHURN"))
    monkeypatch.setattr("ainav.examiner.action_schema", lambda: {})
    with pytest.raises(IntegrityError):
        run_twin_certification()
    monkeypatch.setattr("ainav.examiner.action_schema", lambda: {"kind": "ainav.action.v1"})
    monkeypatch.setattr("ainav.examiner.prove", "not-callable")
    with pytest.raises(IntegrityError):
        run_twin_certification()
    monkeypatch.setattr("ainav.examiner.prove", lambda record_id, store=None: {"ok": True})
    monkeypatch.setattr("agent_gov.lua_simulator", None)
    with pytest.raises(IntegrityError):
        run_twin_certification()


def test_catalog_refuses_gold_as_launch_and_launch_day():
    cat = copy.deepcopy(load_catalog())
    cat["microsoft_stack"]["readiness"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "MICROSOFT_PRODUCT"
    missing = copy.deepcopy(load_catalog())
    missing["microsoft_stack"].pop("readiness")
    with pytest.raises(IntegrityError):
        validate_honest_readiness(missing)
    gold = copy.deepcopy(load_catalog())
    gold["microsoft_stack"]["readiness"]["gold_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_readiness(gold)
    twin = copy.deepcopy(load_catalog())
    twin["microsoft_stack"]["readiness"]["twin_is_launch_day"] = True
    with pytest.raises(IntegrityError):
        validate_honest_readiness(twin)
    day = copy.deepcopy(load_catalog())
    day["microsoft_stack"]["readiness"]["launch_day_certified"] = True
    with pytest.raises(IntegrityError):
        validate_honest_readiness(day)
    sim = copy.deepcopy(load_catalog())
    sim["microsoft_stack"]["readiness"]["sim_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_honest_readiness(sim)
    pin = copy.deepcopy(load_catalog())
    pin["microsoft_stack"]["readiness"]["update_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_honest_readiness(pin)
    actor = copy.deepcopy(load_catalog())
    actor["microsoft_stack"]["readiness"]["owner_playbook"]["actor"] = "cursor.cloud_agent"
    with pytest.raises(IntegrityError):
        validate_honest_readiness(actor)
    cannot = copy.deepcopy(load_catalog())
    cannot["microsoft_stack"]["readiness"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_readiness(cannot)
    href = copy.deepcopy(load_catalog())
    href["microsoft_stack"]["readiness"]["lanes"][0]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        validate_honest_readiness(href)
    note = copy.deepcopy(load_catalog())
    note["microsoft_stack"]["readiness"]["note"] = "Honest readiness. Grok Build is mapped."
    with pytest.raises(IntegrityError):
        validate_honest_readiness(note)
    lede = copy.deepcopy(load_catalog())
    lede["microsoft_stack"]["readiness"]["lede"] = "Honest readiness. Cursor is recorded."
    with pytest.raises(IntegrityError):
        validate_honest_readiness(lede)
    refuse = copy.deepcopy(load_catalog())
    refuse["microsoft_stack"]["readiness"]["refuse"][0]["refuse_text"] = "Refused. Ask James for launch."
    with pytest.raises(IntegrityError):
        validate_honest_readiness(refuse)
    assert HONEST_READY_REFUSE_TEXT["gold_as_launch"].startswith("Refused.")
    stack = copy.deepcopy(load_catalog())
    stack["microsoft_stack"] = "not-a-stack"
    with pytest.raises(IntegrityError):
        validate_honest_readiness(stack)
    kind = copy.deepcopy(load_catalog())
    kind["microsoft_stack"]["readiness"]["kind"] = "ainav.honest.readiness.v0"
    with pytest.raises(IntegrityError):
        validate_honest_readiness(kind)
    lanes = copy.deepcopy(load_catalog())
    lanes["microsoft_stack"]["readiness"]["lanes"] = []
    with pytest.raises(IntegrityError):
        validate_honest_readiness(lanes)
    refuse_ids = copy.deepcopy(load_catalog())
    refuse_ids["microsoft_stack"]["readiness"]["refuse"][0]["refuse"] = False
    with pytest.raises(IntegrityError):
        validate_honest_readiness(refuse_ids)
    honest = copy.deepcopy(load_catalog())
    honest["microsoft_stack"]["readiness"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_readiness(honest)
    sku = copy.deepcopy(load_catalog())
    sku["microsoft_stack"]["readiness"]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_readiness(sku)
    seat = copy.deepcopy(load_catalog())
    seat["microsoft_stack"]["readiness"]["lanes"][0]["seat"] = True
    with pytest.raises(IntegrityError):
        validate_honest_readiness(seat)
    installed = copy.deepcopy(load_catalog())
    installed["microsoft_stack"]["readiness"]["lanes"][6]["installed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_readiness(installed)
    role = copy.deepcopy(load_catalog())
    role["microsoft_stack"]["readiness"]["lanes"][1]["role"] = "have"
    with pytest.raises(IntegrityError):
        validate_honest_readiness(role)
    operating = copy.deepcopy(load_catalog())
    operating["operating"]["operator"] = "grok.build"
    with pytest.raises(IntegrityError):
        validate_honest_readiness(operating)
    note_gold = copy.deepcopy(load_catalog())
    note_gold["microsoft_stack"]["readiness"]["note"] = (
        "Honest readiness. Twin certified is not launch day. Owner gaps stay owner-only."
    )
    with pytest.raises(IntegrityError):
        validate_honest_readiness(note_gold)
    note_twin = copy.deepcopy(load_catalog())
    note_twin["microsoft_stack"]["readiness"]["note"] = (
        "Honest readiness. Gold is not launch. Owner gaps stay owner-only."
    )
    with pytest.raises(IntegrityError):
        validate_honest_readiness(note_twin)
    note_owner = copy.deepcopy(load_catalog())
    note_owner["microsoft_stack"]["readiness"]["note"] = (
        "Honest readiness. Gold is not launch. Twin certified is not launch day."
    )
    with pytest.raises(IntegrityError):
        validate_honest_readiness(note_owner)
    lede_gold = copy.deepcopy(load_catalog())
    lede_gold["microsoft_stack"]["readiness"]["lede"] = (
        "Twin certified is not launch day. Owner gaps stay owner-only."
    )
    with pytest.raises(IntegrityError):
        validate_honest_readiness(lede_gold)
    lede_twin = copy.deepcopy(load_catalog())
    lede_twin["microsoft_stack"]["readiness"]["lede"] = (
        "Gold is not launch. Owner gaps stay owner-only."
    )
    with pytest.raises(IntegrityError):
        validate_honest_readiness(lede_twin)
    lede_owner = copy.deepcopy(load_catalog())
    lede_owner["microsoft_stack"]["readiness"]["lede"] = (
        "Gold is not launch. Twin certified is not launch day."
    )
    with pytest.raises(IntegrityError):
        validate_honest_readiness(lede_owner)
    refuse_href = copy.deepcopy(load_catalog())
    refuse_href["microsoft_stack"]["readiness"]["refuse"][0]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        validate_honest_readiness(refuse_href)
    cards = copy.deepcopy(load_catalog())
    cards["microsoft_stack"]["readiness"]["lanes"] = list(HONEST_READY_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_readiness(cards)
    missing_gold = copy.deepcopy(load_catalog())
    missing_gold["microsoft_stack"]["readiness"].pop("gold_is_launch")
    with pytest.raises(IntegrityError):
        validate_honest_readiness(missing_gold)
    missing_twin = copy.deepcopy(load_catalog())
    missing_twin["microsoft_stack"]["readiness"].pop("twin_is_launch_day")
    with pytest.raises(IntegrityError):
        validate_honest_readiness(missing_twin)
    missing_day = copy.deepcopy(load_catalog())
    missing_day["microsoft_stack"]["readiness"].pop("launch_day_certified")
    with pytest.raises(IntegrityError):
        validate_honest_readiness(missing_day)
    note_title = copy.deepcopy(load_catalog())
    note_title["microsoft_stack"]["readiness"]["note"] = (
        "Gold is not launch. Twin certified is not launch day. Owner gaps stay owner-only."
    )
    with pytest.raises(IntegrityError):
        validate_honest_readiness(note_title)
    operating_shape = copy.deepcopy(load_catalog())
    operating_shape["operating"] = "not-operating"
    with pytest.raises(IntegrityError):
        validate_honest_readiness(operating_shape)
