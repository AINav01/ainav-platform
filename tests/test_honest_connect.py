from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_CONNECT_FACT_IDS,
    HONEST_CONNECT_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.honest_connect import (
    public_review,
    run_connect_certification,
    validate_honest_connect,
)


def test_connect_review_is_not_live():
    body = public_review()
    assert body["kind"] == "ainav.honest.connect.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["connected_is_live"] is False
    assert body["licensed_is_wired"] is False
    assert body["available_is_seat"] is False
    assert body["graph_read_is_live_pin"] is False
    assert body["cursor_app_is_seat"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#missing"
    assert "licensed is not wired" in body["lede"].lower()
    assert "connected is not live" in body["note"].lower()
    assert "available is not a seat" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_CONNECT_FACT_IDS)
    assert "Treat connected as live." in body["this_agent_cannot"]
    assert "Treat licensed as wired." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["connected_is_live"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/connect.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_connect_certification_holds_launch():
    probes = run_connect_certification()
    assert probes["kind"] == "ainav.honest.connect.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["connected_is_live"] is False
    assert probes["licensed_is_wired"] is False
    assert probes["available_is_seat"] is False
    assert probes["graph_read_is_live_pin"] is False
    assert probes["cursor_app_is_seat"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_connect_fail_closed():
    cat = load_catalog()
    hole = copy.deepcopy(cat)
    hole["honest_connect"]["connected_is_live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_connect(hole)
    wired = copy.deepcopy(cat)
    wired["honest_connect"]["licensed_is_wired"] = True
    with pytest.raises(IntegrityError):
        validate_honest_connect(wired)
    seat = copy.deepcopy(cat)
    seat["honest_connect"]["available_is_seat"] = True
    with pytest.raises(IntegrityError):
        validate_honest_connect(seat)
    pin = copy.deepcopy(cat)
    pin["honest_connect"]["graph_read_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_honest_connect(pin)
    app = copy.deepcopy(cat)
    app["honest_connect"]["cursor_app_is_seat"] = True
    with pytest.raises(IntegrityError):
        validate_honest_connect(app)
    href = copy.deepcopy(cat)
    href["honest_connect"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_connect(href)
    live = copy.deepcopy(cat)
    live["programs"]["website"]["honest_connect_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_connect_more_fail_closed():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    missing.pop("honest_connect")
    with pytest.raises(IntegrityError):
        validate_honest_connect(missing)
    kind = copy.deepcopy(cat)
    kind["honest_connect"]["kind"] = "ainav.honest.connect.v0"
    with pytest.raises(IntegrityError):
        validate_honest_connect(kind)
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
        claimed["honest_connect"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_connect(claimed)
    honest = copy.deepcopy(cat)
    honest["honest_connect"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_connect(honest)
    considered = copy.deepcopy(cat)
    considered["honest_connect"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_connect(considered)
    recorded = copy.deepcopy(cat)
    recorded["honest_connect"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_connect(recorded)
    for key in (
        "connected_is_live",
        "licensed_is_wired",
        "available_is_seat",
        "graph_read_is_live_pin",
        "cursor_app_is_seat",
    ):
        missing_flag = copy.deepcopy(cat)
        missing_flag["honest_connect"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_connect(missing_flag)
    facts_len = copy.deepcopy(cat)
    facts_len["honest_connect"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_connect(facts_len)
    not_objects = copy.deepcopy(cat)
    not_objects["honest_connect"]["facts"] = list(HONEST_CONNECT_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_connect(not_objects)
    facts_ids = copy.deepcopy(cat)
    facts_ids["honest_connect"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_connect(facts_ids)
    fact_sku = copy.deepcopy(cat)
    fact_sku["honest_connect"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_connect(fact_sku)
    fact_admit = copy.deepcopy(cat)
    fact_admit["honest_connect"]["facts"][1]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_connect(fact_admit)
    fact_live = copy.deepcopy(cat)
    fact_live["honest_connect"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_connect(fact_live)
    refuse_ids = copy.deepcopy(cat)
    refuse_ids["honest_connect"]["refuse"][0]["id"] = "connect_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_connect(refuse_ids)
    refuse_text = copy.deepcopy(cat)
    refuse_text["honest_connect"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_connect(refuse_text)
    refuse_href = copy.deepcopy(cat)
    refuse_href["honest_connect"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_connect(refuse_href)
    leftover = copy.deepcopy(cat)
    leftover["honest_connect"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_connect(leftover)
    leftover_live = copy.deepcopy(cat)
    leftover_live["honest_connect"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_connect(leftover_live)
    note = copy.deepcopy(cat)
    note["honest_connect"]["note"] = "Connected is not live. Licensed is not wired."
    with pytest.raises(IntegrityError):
        validate_honest_connect(note)
    note_live = copy.deepcopy(cat)
    note_live["honest_connect"]["note"] = "Honest connect. Licensed is not wired."
    with pytest.raises(IntegrityError):
        validate_honest_connect(note_live)
    note_wired = copy.deepcopy(cat)
    note_wired["honest_connect"]["note"] = "Honest connect. Connected is not live."
    with pytest.raises(IntegrityError):
        validate_honest_connect(note_wired)
    lede = copy.deepcopy(cat)
    lede["honest_connect"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_connect(lede)
    lede_live = copy.deepcopy(cat)
    lede_live["honest_connect"]["lede"] = "Licensed is not wired. Available is not a seat."
    with pytest.raises(IntegrityError):
        validate_honest_connect(lede_live)
    site = copy.deepcopy(cat)
    site["honest_connect"]["site"] = (
        "Recorded. Connected is not live. Not a /connect route. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_connect(site)
    site_route = copy.deepcopy(cat)
    site_route["honest_connect"]["site"] = (
        "Honest connect on #missing. Connected is not live. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_connect(site_route)
    site_glance = copy.deepcopy(cat)
    site_glance["honest_connect"]["site"] = (
        "Honest connect on #missing. Connected is not live. Not a /connect route."
    )
    with pytest.raises(IntegrityError):
        validate_honest_connect(site_glance)
    complements = copy.deepcopy(cat)
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_connect(complements)
    actor = copy.deepcopy(cat)
    actor["honest_connect"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_connect(actor)
    cannot = copy.deepcopy(cat)
    cannot["honest_connect"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_connect(cannot)
    assert HONEST_CONNECT_REFUSE_TEXT["connected_as_live"] == "Refused. Connected is not live."


def test_run_connect_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_connect_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_connect_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_connect.validate_honest_connect", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest connect"):
        run_connect_certification(short)
