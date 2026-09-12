from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_TEN_FACT_IDS,
    HONEST_TEN_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.honest_ten import (
    public_review,
    run_ten_certification,
    validate_honest_ten,
)


def test_ten_review_is_not_launch():
    body = public_review()
    assert body["kind"] == "ainav.honest.ten.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["quality_ten_is_launch"] is False
    assert body["gold_999_is_live_pin"] is False
    assert body["compete_is_named_client"] is False
    assert body["service_green_is_production"] is False
    assert body["quality_is_seated"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#success"
    assert "a 10/10 quality check is not launch" in body["lede"].lower()
    assert "honest ten" in body["note"].lower()
    assert "gold 99.9 is not live_pin_ok" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_TEN_FACT_IDS)
    assert "Treat a 10/10 quality check as launch." in body["this_agent_cannot"]
    assert "Treat gold 99.9 as LIVE_PIN_OK." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["quality_ten_is_launch"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/ten.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_ten_certification_holds_launch():
    probes = run_ten_certification()
    assert probes["kind"] == "ainav.honest.ten.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["quality_ten_is_launch"] is False
    assert probes["gold_999_is_live_pin"] is False
    assert probes["compete_is_named_client"] is False
    assert probes["service_green_is_production"] is False
    assert probes["quality_is_seated"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_ten_fail_closed():
    cat = load_catalog()
    hole = copy.deepcopy(cat)
    hole["honest_ten"]["quality_ten_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(hole)
    gold = copy.deepcopy(cat)
    gold["honest_ten"]["gold_999_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(gold)
    compete = copy.deepcopy(cat)
    compete["honest_ten"]["compete_is_named_client"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(compete)
    service = copy.deepcopy(cat)
    service["honest_ten"]["service_green_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(service)
    seated = copy.deepcopy(cat)
    seated["honest_ten"]["quality_is_seated"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(seated)
    href = copy.deepcopy(cat)
    href["honest_ten"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_ten(href)
    live = copy.deepcopy(cat)
    live["programs"]["website"]["honest_ten_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_ten_more_fail_closed():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    missing.pop("honest_ten")
    with pytest.raises(IntegrityError):
        validate_honest_ten(missing)
    kind = copy.deepcopy(cat)
    kind["honest_ten"]["kind"] = "ainav.honest.ten.v0"
    with pytest.raises(IntegrityError):
        validate_honest_ten(kind)
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
        claimed["honest_ten"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_ten(claimed)
    honest = copy.deepcopy(cat)
    honest["honest_ten"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_ten(honest)
    considered = copy.deepcopy(cat)
    considered["honest_ten"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_ten(considered)
    recorded = copy.deepcopy(cat)
    recorded["honest_ten"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_ten(recorded)
    for key in (
        "quality_ten_is_launch",
        "gold_999_is_live_pin",
        "compete_is_named_client",
        "service_green_is_production",
        "quality_is_seated",
    ):
        missing_flag = copy.deepcopy(cat)
        missing_flag["honest_ten"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_ten(missing_flag)
    facts_len = copy.deepcopy(cat)
    facts_len["honest_ten"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_ten(facts_len)
    not_objects = copy.deepcopy(cat)
    not_objects["honest_ten"]["facts"] = list(HONEST_TEN_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_ten(not_objects)
    facts_ids = copy.deepcopy(cat)
    facts_ids["honest_ten"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_ten(facts_ids)
    fact_sku = copy.deepcopy(cat)
    fact_sku["honest_ten"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(fact_sku)
    fact_admit = copy.deepcopy(cat)
    fact_admit["honest_ten"]["facts"][1]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(fact_admit)
    fact_live = copy.deepcopy(cat)
    fact_live["honest_ten"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(fact_live)
    refuse_ids = copy.deepcopy(cat)
    refuse_ids["honest_ten"]["refuse"][0]["id"] = "ten_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_ten(refuse_ids)
    refuse_text = copy.deepcopy(cat)
    refuse_text["honest_ten"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_ten(refuse_text)
    refuse_href = copy.deepcopy(cat)
    refuse_href["honest_ten"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_ten(refuse_href)
    leftover = copy.deepcopy(cat)
    leftover["honest_ten"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_ten(leftover)
    leftover_live = copy.deepcopy(cat)
    leftover_live["honest_ten"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_ten(leftover_live)
    note = copy.deepcopy(cat)
    note["honest_ten"]["note"] = "A 10/10 quality check is not launch. Gold 99.9 is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_ten(note)
    note_close = copy.deepcopy(cat)
    note_close["honest_ten"]["note"] = "Honest ten. Gold 99.9 is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_ten(note_close)
    note_gold = copy.deepcopy(cat)
    note_gold["honest_ten"]["note"] = "Honest ten. A 10/10 quality check is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_ten(note_gold)
    lede = copy.deepcopy(cat)
    lede["honest_ten"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_ten(lede)
    lede_gold = copy.deepcopy(cat)
    lede_gold["honest_ten"]["lede"] = "A 10/10 quality check is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_ten(lede_gold)
    site = copy.deepcopy(cat)
    site["honest_ten"]["site"] = (
        "Recorded. A 10/10 quality check is not launch. Not a /ten route. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_ten(site)
    site_route = copy.deepcopy(cat)
    site_route["honest_ten"]["site"] = (
        "Honest ten on #success. A 10/10 quality check is not launch. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_ten(site_route)
    site_glance = copy.deepcopy(cat)
    site_glance["honest_ten"]["site"] = (
        "Honest ten on #success. A 10/10 quality check is not launch. Not a /ten route."
    )
    with pytest.raises(IntegrityError):
        validate_honest_ten(site_glance)
    complements = copy.deepcopy(cat)
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_ten(complements)
    rows = copy.deepcopy(cat)
    rows["plane_interface"]["competitive"]["rows"] = [
        item
        for item in rows["plane_interface"]["competitive"]["rows"]
        if item.get("id") != "teams_vote"
    ]
    with pytest.raises(IntegrityError):
        validate_honest_ten(rows)
    actor = copy.deepcopy(cat)
    actor["honest_ten"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_ten(actor)
    cannot = copy.deepcopy(cat)
    cannot["honest_ten"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_ten(cannot)
    ssl = copy.deepcopy(cat)
    ssl["honest_ten"]["services"]["cloudflare"]["ssl_full_claimed"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(ssl)
    prod = copy.deepcopy(cat)
    prod["honest_ten"]["services"]["claimed_as_production"] = True
    with pytest.raises(IntegrityError):
        validate_honest_ten(prod)
    assert HONEST_TEN_REFUSE_TEXT["ten_as_launch"] == "Refused. A 10/10 quality check is not launch."


def test_run_ten_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_ten_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_ten_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_ten.validate_honest_ten", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest ten"):
        run_ten_certification(short)
