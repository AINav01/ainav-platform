from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_REMAINDER_FACT_IDS,
    HONEST_REMAINDER_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.honest_remainder import (
    public_review,
    run_remainder_certification,
    validate_honest_remainder,
)


def test_remainder_review_is_not_launch():
    body = public_review()
    assert body["kind"] == "ainav.honest.remainder.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["remainder_is_launch"] is False
    assert body["leftover_copy_is_live_pin"] is False
    assert body["owner_hrefs_are_clicks"] is False
    assert body["gold_995_is_production"] is False
    assert body["deep_remainder_is_seated"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#missing"
    assert "a remainder close is not launch" in body["lede"].lower()
    assert "honest remainder" in body["note"].lower()
    assert "leftover copy is not live_pin_ok" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_REMAINDER_FACT_IDS)
    assert "Treat a remainder close as launch." in body["this_agent_cannot"]
    assert "Treat leftover copy as LIVE_PIN_OK." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["remainder_is_launch"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/remainder.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_remainder_certification_holds_launch():
    probes = run_remainder_certification()
    assert probes["kind"] == "ainav.honest.remainder.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["remainder_is_launch"] is False
    assert probes["leftover_copy_is_live_pin"] is False
    assert probes["owner_hrefs_are_clicks"] is False
    assert probes["gold_995_is_production"] is False
    assert probes["deep_remainder_is_seated"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_remainder_fail_closed():
    cat = load_catalog()
    hole = copy.deepcopy(cat)
    hole["honest_remainder"]["remainder_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_remainder(hole)
    leftover = copy.deepcopy(cat)
    leftover["honest_remainder"]["leftover_copy_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_honest_remainder(leftover)
    hrefs = copy.deepcopy(cat)
    hrefs["honest_remainder"]["owner_hrefs_are_clicks"] = True
    with pytest.raises(IntegrityError):
        validate_honest_remainder(hrefs)
    gold = copy.deepcopy(cat)
    gold["honest_remainder"]["gold_995_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_honest_remainder(gold)
    seated = copy.deepcopy(cat)
    seated["honest_remainder"]["deep_remainder_is_seated"] = True
    with pytest.raises(IntegrityError):
        validate_honest_remainder(seated)
    href = copy.deepcopy(cat)
    href["honest_remainder"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_remainder(href)
    live = copy.deepcopy(cat)
    live["programs"]["website"]["honest_remainder_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_remainder_more_fail_closed():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    missing.pop("honest_remainder")
    with pytest.raises(IntegrityError):
        validate_honest_remainder(missing)
    kind = copy.deepcopy(cat)
    kind["honest_remainder"]["kind"] = "ainav.honest.remainder.v0"
    with pytest.raises(IntegrityError):
        validate_honest_remainder(kind)
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
        claimed["honest_remainder"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_remainder(claimed)
    honest = copy.deepcopy(cat)
    honest["honest_remainder"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_remainder(honest)
    considered = copy.deepcopy(cat)
    considered["honest_remainder"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_remainder(considered)
    recorded = copy.deepcopy(cat)
    recorded["honest_remainder"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_remainder(recorded)
    for key in (
        "remainder_is_launch",
        "leftover_copy_is_live_pin",
        "owner_hrefs_are_clicks",
        "gold_995_is_production",
        "deep_remainder_is_seated",
    ):
        missing_flag = copy.deepcopy(cat)
        missing_flag["honest_remainder"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_remainder(missing_flag)
    facts_len = copy.deepcopy(cat)
    facts_len["honest_remainder"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_remainder(facts_len)
    not_objects = copy.deepcopy(cat)
    not_objects["honest_remainder"]["facts"] = list(HONEST_REMAINDER_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_remainder(not_objects)
    facts_ids = copy.deepcopy(cat)
    facts_ids["honest_remainder"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_remainder(facts_ids)
    fact_sku = copy.deepcopy(cat)
    fact_sku["honest_remainder"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_remainder(fact_sku)
    fact_admit = copy.deepcopy(cat)
    fact_admit["honest_remainder"]["facts"][1]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_remainder(fact_admit)
    fact_live = copy.deepcopy(cat)
    fact_live["honest_remainder"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_remainder(fact_live)
    refuse_ids = copy.deepcopy(cat)
    refuse_ids["honest_remainder"]["refuse"][0]["id"] = "remain_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_remainder(refuse_ids)
    refuse_text = copy.deepcopy(cat)
    refuse_text["honest_remainder"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_remainder(refuse_text)
    refuse_href = copy.deepcopy(cat)
    refuse_href["honest_remainder"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_remainder(refuse_href)
    leftover = copy.deepcopy(cat)
    leftover["honest_remainder"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_remainder(leftover)
    leftover_live = copy.deepcopy(cat)
    leftover_live["honest_remainder"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_remainder(leftover_live)
    note = copy.deepcopy(cat)
    note["honest_remainder"]["note"] = "A remainder close is not launch. Leftover copy is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_remainder(note)
    note_close = copy.deepcopy(cat)
    note_close["honest_remainder"]["note"] = "Honest remainder. Leftover copy is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_remainder(note_close)
    note_leftover = copy.deepcopy(cat)
    note_leftover["honest_remainder"]["note"] = "Honest remainder. A remainder close is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_remainder(note_leftover)
    lede = copy.deepcopy(cat)
    lede["honest_remainder"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_remainder(lede)
    lede_gold = copy.deepcopy(cat)
    lede_gold["honest_remainder"]["lede"] = "A remainder close is not launch. Leftover copy is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_remainder(lede_gold)
    site = copy.deepcopy(cat)
    site["honest_remainder"]["site"] = (
        "Recorded. A remainder close is not launch. Not a /remainder route. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_remainder(site)
    site_route = copy.deepcopy(cat)
    site_route["honest_remainder"]["site"] = (
        "Honest remainder on #missing. A remainder close is not launch. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_remainder(site_route)
    site_glance = copy.deepcopy(cat)
    site_glance["honest_remainder"]["site"] = (
        "Honest remainder on #missing. A remainder close is not launch. Not a /remainder route."
    )
    with pytest.raises(IntegrityError):
        validate_honest_remainder(site_glance)
    complements = copy.deepcopy(cat)
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_remainder(complements)
    actor = copy.deepcopy(cat)
    actor["honest_remainder"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_remainder(actor)
    cannot = copy.deepcopy(cat)
    cannot["honest_remainder"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_remainder(cannot)
    assert HONEST_REMAINDER_REFUSE_TEXT["remainder_as_launch"] == "Refused. A remainder close is not launch."


def test_run_remainder_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_remainder_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_remainder_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_remainder.validate_honest_remainder", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest remainder"):
        run_remainder_certification(short)
