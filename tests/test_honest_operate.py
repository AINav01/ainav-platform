from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_OPERATE_FACT_IDS,
    HONEST_OPERATE_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.honest_operate import (
    public_review,
    run_operate_certification,
    validate_honest_operate,
)


def test_operate_review_is_not_launch():
    body = public_review()
    assert body["kind"] == "ainav.honest.operate.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["close_gaps_is_this_plane"] is False
    assert body["outlook_is_click"] is False
    assert body["grok_login_is_this_plane"] is False
    assert body["operate_sim_is_production"] is False
    assert body["polish_ten_is_launch"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#agent-tools"
    assert "outlook mail is not a click" in body["lede"].lower()
    assert "closing all gaps is not this plane" in body["note"].lower()
    assert "10/10 polish is not launch" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_OPERATE_FACT_IDS)
    assert "Treat closing all gaps as this plane." in body["this_agent_cannot"]
    assert "Treat Outlook mail as a click." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["close_gaps_is_this_plane"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/operate.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_operate_certification_holds_launch():
    probes = run_operate_certification()
    assert probes["kind"] == "ainav.honest.operate.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["close_gaps_is_this_plane"] is False
    assert probes["outlook_is_click"] is False
    assert probes["grok_login_is_this_plane"] is False
    assert probes["operate_sim_is_production"] is False
    assert probes["polish_ten_is_launch"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_operate_fail_closed():
    cat = load_catalog()
    hole = copy.deepcopy(cat)
    hole["honest_operate"]["close_gaps_is_this_plane"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operate(hole)
    click = copy.deepcopy(cat)
    click["honest_operate"]["outlook_is_click"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operate(click)
    grok = copy.deepcopy(cat)
    grok["honest_operate"]["grok_login_is_this_plane"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operate(grok)
    sim = copy.deepcopy(cat)
    sim["honest_operate"]["operate_sim_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operate(sim)
    ten = copy.deepcopy(cat)
    ten["honest_operate"]["polish_ten_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operate(ten)
    href = copy.deepcopy(cat)
    href["honest_operate"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_operate(href)
    live = copy.deepcopy(cat)
    live["programs"]["website"]["honest_operate_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_operate_more_fail_closed():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    missing.pop("honest_operate")
    with pytest.raises(IntegrityError):
        validate_honest_operate(missing)
    kind = copy.deepcopy(cat)
    kind["honest_operate"]["kind"] = "ainav.honest.operate.v0"
    with pytest.raises(IntegrityError):
        validate_honest_operate(kind)
    for flag in (
        "sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "cms",
        "host",
        "is_host",
        "apex",
        "closes_dual_admit",
        "wired",
        "claimed",
        "certified",
        "live",
        "live_pin_ok",
        "launch",
        "created",
    ):
        claimed = copy.deepcopy(cat)
        claimed["honest_operate"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_operate(claimed)
    honest = copy.deepcopy(cat)
    honest["honest_operate"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_operate(honest)
    considered = copy.deepcopy(cat)
    considered["honest_operate"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_operate(considered)
    recorded = copy.deepcopy(cat)
    recorded["honest_operate"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_operate(recorded)
    for key in (
        "close_gaps_is_this_plane",
        "outlook_is_click",
        "grok_login_is_this_plane",
        "operate_sim_is_production",
        "polish_ten_is_launch",
    ):
        missing_flag = copy.deepcopy(cat)
        missing_flag["honest_operate"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_operate(missing_flag)
    facts_len = copy.deepcopy(cat)
    facts_len["honest_operate"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_operate(facts_len)
    not_objects = copy.deepcopy(cat)
    not_objects["honest_operate"]["facts"] = list(HONEST_OPERATE_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_operate(not_objects)
    facts_ids = copy.deepcopy(cat)
    facts_ids["honest_operate"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_operate(facts_ids)
    fact_sku = copy.deepcopy(cat)
    fact_sku["honest_operate"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operate(fact_sku)
    fact_admit = copy.deepcopy(cat)
    fact_admit["honest_operate"]["facts"][1]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operate(fact_admit)
    fact_live = copy.deepcopy(cat)
    fact_live["honest_operate"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operate(fact_live)
    refuse_ids = copy.deepcopy(cat)
    refuse_ids["honest_operate"]["refuse"][0]["id"] = "operate_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_operate(refuse_ids)
    refuse_text = copy.deepcopy(cat)
    refuse_text["honest_operate"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_operate(refuse_text)
    refuse_href = copy.deepcopy(cat)
    refuse_href["honest_operate"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_operate(refuse_href)
    leftover = copy.deepcopy(cat)
    leftover["honest_operate"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_operate(leftover)
    leftover_live = copy.deepcopy(cat)
    leftover_live["honest_operate"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_operate(leftover_live)
    note = copy.deepcopy(cat)
    note["honest_operate"]["note"] = "Closing all gaps is not this plane. Outlook mail is not a click."
    with pytest.raises(IntegrityError):
        validate_honest_operate(note)
    note_gaps = copy.deepcopy(cat)
    note_gaps["honest_operate"]["note"] = "Honest operate. Outlook mail is not a click."
    with pytest.raises(IntegrityError):
        validate_honest_operate(note_gaps)
    note_click = copy.deepcopy(cat)
    note_click["honest_operate"]["note"] = "Honest operate. Closing all gaps is not this plane."
    with pytest.raises(IntegrityError):
        validate_honest_operate(note_click)
    lede = copy.deepcopy(cat)
    lede["honest_operate"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_operate(lede)
    lede_gaps = copy.deepcopy(cat)
    lede_gaps["honest_operate"]["lede"] = "Outlook mail is not a click. grok login is not this plane."
    with pytest.raises(IntegrityError):
        validate_honest_operate(lede_gaps)
    site = copy.deepcopy(cat)
    site["honest_operate"]["site"] = (
        "Recorded. Closing all gaps is not this plane. Not a /operate route. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_operate(site)
    site_route = copy.deepcopy(cat)
    site_route["honest_operate"]["site"] = (
        "Honest operate on #agent-tools. Closing all gaps is not this plane. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_operate(site_route)
    site_glance = copy.deepcopy(cat)
    site_glance["honest_operate"]["site"] = (
        "Honest operate on #agent-tools. Closing all gaps is not this plane. Not a /operate route."
    )
    with pytest.raises(IntegrityError):
        validate_honest_operate(site_glance)
    complements = copy.deepcopy(cat)
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_operate(complements)
    actor = copy.deepcopy(cat)
    actor["honest_operate"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_operate(actor)
    cannot = copy.deepcopy(cat)
    cannot["honest_operate"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_operate(cannot)
    assert HONEST_OPERATE_REFUSE_TEXT["close_gaps_as_this_plane"] == "Refused. Closing all gaps is not this plane."


def test_run_operate_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_operate_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_operate_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_operate.validate_honest_operate", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest operate"):
        run_operate_certification(short)
