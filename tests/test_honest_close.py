from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_CLOSE_FACT_IDS,
    HONEST_CLOSE_HOP_HREFS,
    HONEST_CLOSE_HOP_IDS,
    load_catalog,
    validate_catalog,
)
from ainav.honest_close import (
    public_review,
    run_close_certification,
    validate_honest_close,
)


def test_close_review_is_not_launch():
    body = public_review()
    assert body["kind"] == "ainav.honest.close.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["close_as_launch"] is False
    assert body["booking_as_revenue"] is False
    assert body["twin_as_assigned"] is False
    assert body["custom_db_as_sku"] is False
    assert body["list_as_collection"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#path"
    assert "a 10/10 close is not launch" in body["lede"].lower()
    assert "honest close" in body["note"].lower()
    assert "a catalog list is not collection" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_CLOSE_FACT_IDS)
    assert [item["id"] for item in body["hops"]] == list(HONEST_CLOSE_HOP_IDS)
    hop_hrefs = {item["id"]: item["href"] for item in body["hops"]}
    assert hop_hrefs == {key: HONEST_CLOSE_HOP_HREFS[key] for key in HONEST_CLOSE_HOP_IDS}
    assert "Treat a 10/10 close as launch." in body["this_agent_cannot"]
    assert "Treat a catalog list as collection." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["close_as_launch"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/close.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_close_certification_holds_launch():
    probes = run_close_certification()
    assert probes["kind"] == "ainav.honest.close.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["close_as_launch"] is False
    assert probes["booking_as_revenue"] is False
    assert probes["twin_as_assigned"] is False
    assert probes["custom_db_as_sku"] is False
    assert probes["list_as_collection"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_close_fail_closed():
    hole = copy.deepcopy(load_catalog())
    hole["honest_close"]["close_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_close(hole)
    book = copy.deepcopy(load_catalog())
    book["honest_close"]["booking_as_revenue"] = True
    with pytest.raises(IntegrityError):
        validate_honest_close(book)
    twin = copy.deepcopy(load_catalog())
    twin["honest_close"]["twin_as_assigned"] = True
    with pytest.raises(IntegrityError):
        validate_honest_close(twin)
    sku = copy.deepcopy(load_catalog())
    sku["honest_close"]["custom_db_as_sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_close(sku)
    collect = copy.deepcopy(load_catalog())
    collect["honest_close"]["list_as_collection"] = True
    with pytest.raises(IntegrityError):
        validate_honest_close(collect)
    href = copy.deepcopy(load_catalog())
    href["honest_close"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_close(href)
    live = copy.deepcopy(load_catalog())
    live["programs"]["website"]["honest_close_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_close_more_fail_closed():
    missing = copy.deepcopy(load_catalog())
    missing.pop("honest_close")
    with pytest.raises(IntegrityError):
        validate_honest_close(missing)
    kind = copy.deepcopy(load_catalog())
    kind["honest_close"]["kind"] = "ainav.honest.close.v0"
    with pytest.raises(IntegrityError):
        validate_honest_close(kind)
    for flag in (
        "sku",
        "certified",
        "live",
        "live_pin_ok",
        "launch",
        "created",
        "claimed",
        "signed_l1",
        "named_client",
        "billing_provider",
    ):
        claimed = copy.deepcopy(load_catalog())
        claimed["honest_close"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_close(claimed)
    honest = copy.deepcopy(load_catalog())
    honest["honest_close"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_close(honest)
    considered = copy.deepcopy(load_catalog())
    considered["honest_close"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_close(considered)
    recorded = copy.deepcopy(load_catalog())
    recorded["honest_close"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_close(recorded)
    for key in (
        "close_as_launch",
        "booking_as_revenue",
        "twin_as_assigned",
        "custom_db_as_sku",
        "list_as_collection",
    ):
        missing_flag = copy.deepcopy(load_catalog())
        missing_flag["honest_close"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_close(missing_flag)
    hops = copy.deepcopy(load_catalog())
    hops["honest_close"]["hops"] = []
    with pytest.raises(IntegrityError):
        validate_honest_close(hops)
    hop_closed = copy.deepcopy(load_catalog())
    hop_closed["honest_close"]["hops"][0]["closed"] = True
    with pytest.raises(IntegrityError):
        validate_honest_close(hop_closed)
    hop_href = copy.deepcopy(load_catalog())
    hop_href["honest_close"]["hops"][0]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_close(hop_href)
    facts_len = copy.deepcopy(load_catalog())
    facts_len["honest_close"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_close(facts_len)
    not_objects = copy.deepcopy(load_catalog())
    not_objects["honest_close"]["facts"] = list(HONEST_CLOSE_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_close(not_objects)
    facts_ids = copy.deepcopy(load_catalog())
    facts_ids["honest_close"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_close(facts_ids)
    fact_sku = copy.deepcopy(load_catalog())
    fact_sku["honest_close"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_close(fact_sku)
    refuse_ids = copy.deepcopy(load_catalog())
    refuse_ids["honest_close"]["refuse"][0]["id"] = "close_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_close(refuse_ids)
    refuse_text = copy.deepcopy(load_catalog())
    refuse_text["honest_close"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_close(refuse_text)
    refuse_href = copy.deepcopy(load_catalog())
    refuse_href["honest_close"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_close(refuse_href)
    leftover = copy.deepcopy(load_catalog())
    leftover["honest_close"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_close(leftover)
    leftover_live = copy.deepcopy(load_catalog())
    leftover_live["honest_close"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_close(leftover_live)
    note = copy.deepcopy(load_catalog())
    note["honest_close"]["note"] = "A 10/10 close is not launch. A catalog list is not collection."
    with pytest.raises(IntegrityError):
        validate_honest_close(note)
    note_launch = copy.deepcopy(load_catalog())
    note_launch["honest_close"]["note"] = "Honest close. A catalog list is not collection."
    with pytest.raises(IntegrityError):
        validate_honest_close(note_launch)
    note_list = copy.deepcopy(load_catalog())
    note_list["honest_close"]["note"] = "Honest close. A 10/10 close is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_close(note_list)
    lede = copy.deepcopy(load_catalog())
    lede["honest_close"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_close(lede)
    lede_sku = copy.deepcopy(load_catalog())
    lede_sku["honest_close"]["lede"] = "A 10/10 close is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_close(lede_sku)
    site = copy.deepcopy(load_catalog())
    site["honest_close"]["site"] = "Close board. A 10/10 close is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_close(site)
    site_route = copy.deepcopy(load_catalog())
    site_route["honest_close"]["site"] = site_route["honest_close"]["site"].replace(
        "Not a /close route.",
        "A /close route.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_close(site_route)
    site_glance = copy.deepcopy(load_catalog())
    site_glance["honest_close"]["site"] = site_glance["honest_close"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the close board.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_close(site_glance)
    complements = copy.deepcopy(load_catalog())
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_close(complements)
    actor = copy.deepcopy(load_catalog())
    actor["honest_close"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_close(actor)
    cannot = copy.deepcopy(load_catalog())
    cannot["honest_close"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_close(cannot)
    owner = copy.deepcopy(load_catalog())
    owner["plane_interface"]["gaps"]["owner_only_open"] = [
        item
        for item in owner["plane_interface"]["gaps"]["owner_only_open"]
        if "seat B click" not in item
    ]
    with pytest.raises(IntegrityError):
        validate_honest_close(owner)


def test_run_close_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_close_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_close_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_close.validate_honest_close", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest close"):
        run_close_certification(short)
