from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_PATH_FACT_IDS,
    HONEST_PATH_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.honest_path import (
    public_review,
    run_path_certification,
    validate_honest_path,
)


def test_path_review_is_not_launch():
    body = public_review()
    assert body["kind"] == "ainav.honest.path.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["industry_is_named_client"] is False
    assert body["shared_sandbox_is_production"] is False
    assert body["hours_is_sku"] is False
    assert body["rollback_is_live_pin"] is False
    assert body["redeploy_is_launch"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#path"
    assert "an industry is not a named client" in body["lede"].lower()
    assert "honest path" in body["note"].lower()
    assert "a redeploy is not launch" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_PATH_FACT_IDS)
    assert "Treat an industry as a named client." in body["this_agent_cannot"]
    assert "Treat a shared sandbox as production." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["industry_is_named_client"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/path.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_path_certification_holds_launch():
    probes = run_path_certification()
    assert probes["kind"] == "ainav.honest.path.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["industry_is_named_client"] is False
    assert probes["shared_sandbox_is_production"] is False
    assert probes["hours_is_sku"] is False
    assert probes["rollback_is_live_pin"] is False
    assert probes["redeploy_is_launch"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_path_fail_closed():
    cat = load_catalog()
    hole = copy.deepcopy(cat)
    hole["honest_path"]["industry_is_named_client"] = True
    with pytest.raises(IntegrityError):
        validate_honest_path(hole)
    shared = copy.deepcopy(cat)
    shared["honest_path"]["shared_sandbox_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_honest_path(shared)
    hours = copy.deepcopy(cat)
    hours["honest_path"]["hours_is_sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_path(hours)
    rollback = copy.deepcopy(cat)
    rollback["honest_path"]["rollback_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_honest_path(rollback)
    redeploy = copy.deepcopy(cat)
    redeploy["honest_path"]["redeploy_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_path(redeploy)
    href = copy.deepcopy(cat)
    href["honest_path"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_path(href)
    live = copy.deepcopy(cat)
    live["programs"]["website"]["honest_path_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_path_more_fail_closed():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    missing.pop("honest_path")
    with pytest.raises(IntegrityError):
        validate_honest_path(missing)
    kind = copy.deepcopy(cat)
    kind["honest_path"]["kind"] = "ainav.honest.path.v0"
    with pytest.raises(IntegrityError):
        validate_honest_path(kind)
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
        claimed["honest_path"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_path(claimed)
    honest = copy.deepcopy(cat)
    honest["honest_path"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_path(honest)
    considered = copy.deepcopy(cat)
    considered["honest_path"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_path(considered)
    recorded = copy.deepcopy(cat)
    recorded["honest_path"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_path(recorded)
    for key in (
        "industry_is_named_client",
        "shared_sandbox_is_production",
        "hours_is_sku",
        "rollback_is_live_pin",
        "redeploy_is_launch",
    ):
        missing_flag = copy.deepcopy(cat)
        missing_flag["honest_path"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_path(missing_flag)
    facts_len = copy.deepcopy(cat)
    facts_len["honest_path"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_path(facts_len)
    not_objects = copy.deepcopy(cat)
    not_objects["honest_path"]["facts"] = list(HONEST_PATH_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_path(not_objects)
    facts_ids = copy.deepcopy(cat)
    facts_ids["honest_path"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_path(facts_ids)
    fact_sku = copy.deepcopy(cat)
    fact_sku["honest_path"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_path(fact_sku)
    fact_admit = copy.deepcopy(cat)
    fact_admit["honest_path"]["facts"][1]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_path(fact_admit)
    fact_live = copy.deepcopy(cat)
    fact_live["honest_path"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_path(fact_live)
    refuse_ids = copy.deepcopy(cat)
    refuse_ids["honest_path"]["refuse"][0]["id"] = "path_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_path(refuse_ids)
    refuse_text = copy.deepcopy(cat)
    refuse_text["honest_path"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_path(refuse_text)
    refuse_href = copy.deepcopy(cat)
    refuse_href["honest_path"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_path(refuse_href)
    leftover = copy.deepcopy(cat)
    leftover["honest_path"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_path(leftover)
    leftover_live = copy.deepcopy(cat)
    leftover_live["honest_path"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_path(leftover_live)
    note = copy.deepcopy(cat)
    note["honest_path"]["note"] = "An industry is not a named client. A shared sandbox is not production."
    with pytest.raises(IntegrityError):
        validate_honest_path(note)
    note_industry = copy.deepcopy(cat)
    note_industry["honest_path"]["note"] = "Honest path. A shared sandbox is not production."
    with pytest.raises(IntegrityError):
        validate_honest_path(note_industry)
    note_shared = copy.deepcopy(cat)
    note_shared["honest_path"]["note"] = "Honest path. An industry is not a named client."
    with pytest.raises(IntegrityError):
        validate_honest_path(note_shared)
    lede = copy.deepcopy(cat)
    lede["honest_path"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_path(lede)
    lede_hours = copy.deepcopy(cat)
    lede_hours["honest_path"]["lede"] = "An industry is not a named client. A shared sandbox is not production."
    with pytest.raises(IntegrityError):
        validate_honest_path(lede_hours)
    site = copy.deepcopy(cat)
    site["honest_path"]["site"] = (
        "Recorded. An industry is not a named client. Not a /path route. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_path(site)
    site_route = copy.deepcopy(cat)
    site_route["honest_path"]["site"] = (
        "Honest path on #path. An industry is not a named client. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_path(site_route)
    site_glance = copy.deepcopy(cat)
    site_glance["honest_path"]["site"] = (
        "Honest path on #path. An industry is not a named client. Not a /path route."
    )
    with pytest.raises(IntegrityError):
        validate_honest_path(site_glance)
    complements = copy.deepcopy(cat)
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_path(complements)
    actor = copy.deepcopy(cat)
    actor["honest_path"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_path(actor)
    cannot = copy.deepcopy(cat)
    cannot["honest_path"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_path(cannot)
    assert HONEST_PATH_REFUSE_TEXT["industry_as_named_client"] == "Refused. An industry is not a named client."


def test_run_path_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_path_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_path_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_path.validate_honest_path", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest path"):
        run_path_certification(short)
