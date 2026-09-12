from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_PRODUCTION_FACT_IDS,
    HONEST_PRODUCTION_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.honest_production import (
    public_review,
    run_production_certification,
    validate_honest_production,
)


def test_production_review_is_not_launch():
    body = public_review()
    assert body["kind"] == "ainav.honest.production.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["production_sim_is_production"] is False
    assert body["fix_all_is_this_plane"] is False
    assert body["elements_are_live"] is False
    assert body["better_is_launch"] is False
    assert body["rehearsal_is_live_pin"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#firm"
    assert "a production sim is not production" in body["lede"].lower()
    assert "honest production" in body["note"].lower()
    assert "a rehearsal is not live_pin_ok" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_PRODUCTION_FACT_IDS)
    assert "Treat a production sim as production." in body["this_agent_cannot"]
    assert "Treat fixing all as this plane." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["production_sim_is_production"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/production.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_production_certification_holds_launch():
    probes = run_production_certification()
    assert probes["kind"] == "ainav.honest.production.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["production_sim_is_production"] is False
    assert probes["fix_all_is_this_plane"] is False
    assert probes["elements_are_live"] is False
    assert probes["better_is_launch"] is False
    assert probes["rehearsal_is_live_pin"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_production_fail_closed():
    cat = load_catalog()
    hole = copy.deepcopy(cat)
    hole["honest_production"]["production_sim_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_honest_production(hole)
    fix = copy.deepcopy(cat)
    fix["honest_production"]["fix_all_is_this_plane"] = True
    with pytest.raises(IntegrityError):
        validate_honest_production(fix)
    elements = copy.deepcopy(cat)
    elements["honest_production"]["elements_are_live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_production(elements)
    better = copy.deepcopy(cat)
    better["honest_production"]["better_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_production(better)
    rehearsal = copy.deepcopy(cat)
    rehearsal["honest_production"]["rehearsal_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_honest_production(rehearsal)
    href = copy.deepcopy(cat)
    href["honest_production"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_production(href)
    live = copy.deepcopy(cat)
    live["programs"]["website"]["honest_production_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_production_more_fail_closed():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    missing.pop("honest_production")
    with pytest.raises(IntegrityError):
        validate_honest_production(missing)
    kind = copy.deepcopy(cat)
    kind["honest_production"]["kind"] = "ainav.honest.production.v0"
    with pytest.raises(IntegrityError):
        validate_honest_production(kind)
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
        claimed["honest_production"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_production(claimed)
    honest = copy.deepcopy(cat)
    honest["honest_production"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_production(honest)
    considered = copy.deepcopy(cat)
    considered["honest_production"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_production(considered)
    recorded = copy.deepcopy(cat)
    recorded["honest_production"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_production(recorded)
    for key in (
        "production_sim_is_production",
        "fix_all_is_this_plane",
        "elements_are_live",
        "better_is_launch",
        "rehearsal_is_live_pin",
    ):
        missing_flag = copy.deepcopy(cat)
        missing_flag["honest_production"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_production(missing_flag)
    facts_len = copy.deepcopy(cat)
    facts_len["honest_production"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_production(facts_len)
    not_objects = copy.deepcopy(cat)
    not_objects["honest_production"]["facts"] = list(HONEST_PRODUCTION_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_production(not_objects)
    facts_ids = copy.deepcopy(cat)
    facts_ids["honest_production"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_production(facts_ids)
    fact_sku = copy.deepcopy(cat)
    fact_sku["honest_production"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_production(fact_sku)
    fact_admit = copy.deepcopy(cat)
    fact_admit["honest_production"]["facts"][1]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_production(fact_admit)
    fact_live = copy.deepcopy(cat)
    fact_live["honest_production"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_production(fact_live)
    refuse_ids = copy.deepcopy(cat)
    refuse_ids["honest_production"]["refuse"][0]["id"] = "prod_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_production(refuse_ids)
    refuse_text = copy.deepcopy(cat)
    refuse_text["honest_production"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_production(refuse_text)
    refuse_href = copy.deepcopy(cat)
    refuse_href["honest_production"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_production(refuse_href)
    leftover = copy.deepcopy(cat)
    leftover["honest_production"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_production(leftover)
    leftover_live = copy.deepcopy(cat)
    leftover_live["honest_production"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_production(leftover_live)
    note = copy.deepcopy(cat)
    note["honest_production"]["note"] = "A production sim is not production. Fixing all is not this plane."
    with pytest.raises(IntegrityError):
        validate_honest_production(note)
    note_sim = copy.deepcopy(cat)
    note_sim["honest_production"]["note"] = "Honest production. Fixing all is not this plane."
    with pytest.raises(IntegrityError):
        validate_honest_production(note_sim)
    note_fix = copy.deepcopy(cat)
    note_fix["honest_production"]["note"] = "Honest production. A production sim is not production."
    with pytest.raises(IntegrityError):
        validate_honest_production(note_fix)
    lede = copy.deepcopy(cat)
    lede["honest_production"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_production(lede)
    lede_better = copy.deepcopy(cat)
    lede_better["honest_production"]["lede"] = "A production sim is not production. Fixing all is not this plane."
    with pytest.raises(IntegrityError):
        validate_honest_production(lede_better)
    site = copy.deepcopy(cat)
    site["honest_production"]["site"] = (
        "Recorded. A production sim is not production. Not a /firm route. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_production(site)
    site_route = copy.deepcopy(cat)
    site_route["honest_production"]["site"] = (
        "Honest production on #firm. A production sim is not production. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_production(site_route)
    site_glance = copy.deepcopy(cat)
    site_glance["honest_production"]["site"] = (
        "Honest production on #firm. A production sim is not production. Not a /firm route."
    )
    with pytest.raises(IntegrityError):
        validate_honest_production(site_glance)
    complements = copy.deepcopy(cat)
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_production(complements)
    actor = copy.deepcopy(cat)
    actor["honest_production"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_production(actor)
    cannot = copy.deepcopy(cat)
    cannot["honest_production"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_production(cannot)
    assert HONEST_PRODUCTION_REFUSE_TEXT["production_sim_as_production"] == "Refused. A production sim is not production."


def test_run_production_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_production_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_production_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_production.validate_honest_production", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest production"):
        run_production_certification(short)
