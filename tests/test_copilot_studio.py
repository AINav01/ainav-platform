from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_COPILOT_STUDIO_FACT_IDS,
    HONEST_COPILOT_STUDIO_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.copilot_studio import (
    public_review,
    run_copilot_studio_certification,
    validate_honest_copilot_studio,
)


def test_studio_review_is_not_job_c():
    body = public_review()
    assert body["kind"] == "ainav.honest.copilot_studio.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["honest"] is True
    assert body["href"] == "#success"
    assert "human looked" in body["lede"].lower()
    assert "copilot studio is not job c" in body["note"].lower()
    assert "copilot studio is not a sku" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_COPILOT_STUDIO_FACT_IDS)
    assert "Treat Copilot Studio as Job C." in body["this_agent_cannot"]
    assert "Treat Copilot Studio as a SKU." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["is_job_c"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/studio.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_copilot_studio_certification_holds_launch():
    probes = run_copilot_studio_certification()
    assert probes["kind"] == "ainav.honest.copilot_studio.v1"
    assert probes["considered"] is True
    assert probes["is_job_c"] is False
    assert probes["is_sku"] is False
    assert probes["is_admit_plane"] is False
    assert probes["is_complement"] is False
    assert probes["is_seat"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_copilot_studio_fail_closed():
    cat = load_catalog()
    hole = copy.deepcopy(cat)
    hole["honest_copilot_studio"]["is_job_c"] = True
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(hole)
    sku = copy.deepcopy(cat)
    sku["honest_copilot_studio"]["is_sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(sku)
    admit = copy.deepcopy(cat)
    admit["honest_copilot_studio"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(admit)
    seat = copy.deepcopy(cat)
    seat["honest_copilot_studio"]["is_seat"] = True
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(seat)
    href = copy.deepcopy(cat)
    href["honest_copilot_studio"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(href)
    live = copy.deepcopy(cat)
    live["programs"]["website"]["honest_copilot_studio_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_copilot_studio_more_fail_closed():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    missing.pop("honest_copilot_studio")
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(missing)
    kind = copy.deepcopy(cat)
    kind["honest_copilot_studio"]["kind"] = "ainav.honest.copilot_studio.v0"
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(kind)
    for flag in (
        "sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
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
        claimed["honest_copilot_studio"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_copilot_studio(claimed)
    honest = copy.deepcopy(cat)
    honest["honest_copilot_studio"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(honest)
    considered = copy.deepcopy(cat)
    considered["honest_copilot_studio"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(considered)
    href = copy.deepcopy(cat)
    href["honest_copilot_studio"]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(href)
    missing_job = copy.deepcopy(cat)
    missing_job["honest_copilot_studio"].pop("is_job_c")
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(missing_job)
    missing_sku = copy.deepcopy(cat)
    missing_sku["honest_copilot_studio"].pop("is_sku")
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(missing_sku)
    missing_admit = copy.deepcopy(cat)
    missing_admit["honest_copilot_studio"].pop("is_admit_plane")
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(missing_admit)
    missing_comp = copy.deepcopy(cat)
    missing_comp["honest_copilot_studio"].pop("is_complement")
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(missing_comp)
    missing_seat = copy.deepcopy(cat)
    missing_seat["honest_copilot_studio"].pop("is_seat")
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(missing_seat)
    facts_len = copy.deepcopy(cat)
    facts_len["honest_copilot_studio"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(facts_len)
    not_objects = copy.deepcopy(cat)
    not_objects["honest_copilot_studio"]["facts"] = list(HONEST_COPILOT_STUDIO_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(not_objects)
    facts_ids = copy.deepcopy(cat)
    facts_ids["honest_copilot_studio"]["facts"][0]["id"] = "bot"
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(facts_ids)
    fact_sku = copy.deepcopy(cat)
    fact_sku["honest_copilot_studio"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(fact_sku)
    fact_admit = copy.deepcopy(cat)
    fact_admit["honest_copilot_studio"]["facts"][1]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(fact_admit)
    fact_live = copy.deepcopy(cat)
    fact_live["honest_copilot_studio"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(fact_live)
    refuse_ids = copy.deepcopy(cat)
    refuse_ids["honest_copilot_studio"]["refuse"][0]["id"] = "studio_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(refuse_ids)
    refuse_text = copy.deepcopy(cat)
    refuse_text["honest_copilot_studio"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(refuse_text)
    refuse_href = copy.deepcopy(cat)
    refuse_href["honest_copilot_studio"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(refuse_href)
    leftover = copy.deepcopy(cat)
    leftover["honest_copilot_studio"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(leftover)
    leftover_live = copy.deepcopy(cat)
    leftover_live["honest_copilot_studio"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(leftover_live)
    note = copy.deepcopy(cat)
    note["honest_copilot_studio"]["note"] = "Copilot Studio is not Job C. Copilot Studio is not a SKU."
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(note)
    note_job = copy.deepcopy(cat)
    note_job["honest_copilot_studio"]["note"] = "Honest Copilot Studio. Copilot Studio is not a SKU."
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(note_job)
    note_sku = copy.deepcopy(cat)
    note_sku["honest_copilot_studio"]["note"] = "Honest Copilot Studio. Copilot Studio is not Job C."
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(note_sku)
    lede = copy.deepcopy(cat)
    lede["honest_copilot_studio"]["lede"] = "Copilot Studio is not Job C."
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(lede)
    lede_job = copy.deepcopy(cat)
    lede_job["honest_copilot_studio"]["lede"] = "Microsoft Copilot Studio is an agent-builder. A human looked."
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(lede_job)
    site = copy.deepcopy(cat)
    site["honest_copilot_studio"]["site"] = (
        "Considered. Copilot Studio is not Job C. Not a /copilot-studio route. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(site)
    site_route = copy.deepcopy(cat)
    site_route["honest_copilot_studio"]["site"] = (
        "Honest Copilot Studio on #success. Copilot Studio is not Job C. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(site_route)
    site_glance = copy.deepcopy(cat)
    site_glance["honest_copilot_studio"]["site"] = (
        "Honest Copilot Studio on #success. Copilot Studio is not Job C. Not a /copilot-studio route."
    )
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(site_glance)
    complements = copy.deepcopy(cat)
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(complements)
    ninth = copy.deepcopy(cat)
    ninth["connections"]["complements"][0]["id"] = "copilot.studio"
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(ninth)
    actor = copy.deepcopy(cat)
    actor["honest_copilot_studio"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(actor)
    cannot = copy.deepcopy(cat)
    cannot["honest_copilot_studio"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_copilot_studio(cannot)
    refuse_text_law = HONEST_COPILOT_STUDIO_REFUSE_TEXT["studio_as_job_c"]
    assert refuse_text_law == "Refused. Copilot Studio is not Job C."


def test_run_copilot_studio_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_copilot_studio_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_copilot_studio_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.copilot_studio.validate_honest_copilot_studio", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after Copilot Studio consider"):
        run_copilot_studio_certification(short)
