from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_WHOLE_LANE_IDS,
    HONEST_WHOLE_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.honest_whole import (
    public_review,
    run_whole_certification,
    validate_honest_whole,
)


def test_whole_review_is_not_launch():
    body = public_review()
    assert body["kind"] == "ainav.honest.whole.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["whole_is_launch"] is False
    assert body["ten_is_launch"] is False
    assert body["stitch_is_sku"] is False
    assert body["certified"] is False
    assert body["complete"] is True
    assert body["live"] is False
    assert "the whole firm is not launch" in body["lede"].lower()
    assert "10/10 review is not launch" in body["note"].lower()
    assert [item["id"] for item in body["lanes"]] == list(HONEST_WHOLE_LANE_IDS)
    assert "Treat the whole firm as launch." in body["this_agent_cannot"]
    assert "Treat a 10/10 review as launch." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["lanes"] == 7
    assert probes["launch"] is False
    assert probes["whole_is_launch"] is False
    on_disk = json.loads(Path("institute/whole.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_whole_certification_holds_launch():
    probes = run_whole_certification()
    assert probes["kind"] == "ainav.honest.whole.v1"
    assert probes["write"] is True
    assert probes["industry_packs"] == 26
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_whole_fail_closed():
    cat = load_catalog()
    hole = copy.deepcopy(cat)
    hole["honest_whole"]["whole_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_whole(hole)
    sku = copy.deepcopy(cat)
    sku["honest_whole"]["stitch_is_sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_whole(sku)
    ten = copy.deepcopy(cat)
    ten["honest_whole"]["ten_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_whole(ten)
    href = copy.deepcopy(cat)
    href["honest_whole"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_whole(href)
    live = copy.deepcopy(cat)
    live["programs"]["website"]["honest_whole_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_whole_more_fail_closed():
    edge = load_catalog()
    missing = copy.deepcopy(edge)
    missing.pop("honest_whole")
    with pytest.raises(IntegrityError, match="catalog missing honest whole"):
        validate_honest_whole(missing)
    kind = copy.deepcopy(edge)
    kind["honest_whole"]["kind"] = "ainav.honest.whole.v0"
    with pytest.raises(IntegrityError, match="kind stays catalog law"):
        validate_honest_whole(kind)
    honest = copy.deepcopy(edge)
    honest["honest_whole"]["honest"] = False
    with pytest.raises(IntegrityError, match="stays honest"):
        validate_honest_whole(honest)
    complete = copy.deepcopy(edge)
    complete["honest_whole"]["complete"] = False
    with pytest.raises(IntegrityError, match="inventory stays complete"):
        validate_honest_whole(complete)
    missing_whole = copy.deepcopy(edge)
    missing_whole["honest_whole"].pop("whole_is_launch")
    with pytest.raises(IntegrityError, match="the whole firm is not launch"):
        validate_honest_whole(missing_whole)
    missing_ten = copy.deepcopy(edge)
    missing_ten["honest_whole"].pop("ten_is_launch")
    with pytest.raises(IntegrityError, match="a 10/10 review is not launch"):
        validate_honest_whole(missing_ten)
    missing_stitch = copy.deepcopy(edge)
    missing_stitch["honest_whole"].pop("stitch_is_sku")
    with pytest.raises(IntegrityError, match="the stitch is not a SKU"):
        validate_honest_whole(missing_stitch)
    not_objects = copy.deepcopy(edge)
    not_objects["honest_whole"]["lanes"] = list(HONEST_WHOLE_LANE_IDS)
    with pytest.raises(IntegrityError, match="lanes stay objects"):
        validate_honest_whole(not_objects)
    leftover = copy.deepcopy(edge)
    leftover["honest_whole"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError, match="cannot leftover claimed or live"):
        validate_honest_whole(leftover)
    leftover_live = copy.deepcopy(edge)
    leftover_live["honest_whole"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError, match="cannot leftover claimed or live"):
        validate_honest_whole(leftover_live)
    note = copy.deepcopy(edge)
    note["honest_whole"]["note"] = "The whole firm is not launch. A 10/10 review is not launch."
    with pytest.raises(IntegrityError, match="note keeps honest whole"):
        validate_honest_whole(note)
    note_ten = copy.deepcopy(edge)
    note_ten["honest_whole"]["note"] = "Honest whole. The whole firm is not launch."
    with pytest.raises(IntegrityError, match="note keeps 10/10 review is not launch"):
        validate_honest_whole(note_ten)
    note_firm = copy.deepcopy(edge)
    note_firm["honest_whole"]["note"] = "Honest whole. A 10/10 review is not launch."
    with pytest.raises(IntegrityError, match="note keeps the whole firm is not launch"):
        validate_honest_whole(note_firm)
    lede = copy.deepcopy(edge)
    lede["honest_whole"]["lede"] = "The whole firm is not launch."
    with pytest.raises(IntegrityError, match="lede keeps business, build, and website"):
        validate_honest_whole(lede)
    lede_firm = copy.deepcopy(edge)
    lede_firm["honest_whole"]["lede"] = "Business, build, and website on one board."
    with pytest.raises(IntegrityError, match="lede keeps the whole firm is not launch"):
        validate_honest_whole(lede_firm)
    site = copy.deepcopy(edge)
    site["honest_whole"]["site"] = (
        "Honest whole on #whole. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError, match="site keeps not a /whole route"):
        validate_honest_whole(site)
    site_glance = copy.deepcopy(edge)
    site_glance["honest_whole"]["site"] = (
        "Honest whole on #whole. Not a /whole route."
    )
    with pytest.raises(IntegrityError, match="site keeps first glance stays the write rail"):
        validate_honest_whole(site_glance)
    actor = copy.deepcopy(edge)
    actor["honest_whole"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError, match="sole owner"):
        validate_honest_whole(actor)
    cannot = copy.deepcopy(edge)
    cannot["honest_whole"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError, match="Cloud Agent cannot mark the whole firm launch"):
        validate_honest_whole(cannot)


def test_run_whole_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_whole_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr(
        "ainav.industry_certify.run_industry_certification",
        lambda _catalog=None: {"packs": 25},
    )
    monkeypatch.setattr(
        "ainav.microsoft.readiness.run_twin_certification",
        lambda _catalog=None: {"launch": False},
    )
    with pytest.raises(IntegrityError, match="industry certified and launch open"):
        run_whole_certification()
    monkeypatch.setattr(
        "ainav.industry_certify.run_industry_certification",
        lambda _catalog=None: {"packs": 26},
    )
    monkeypatch.setattr(
        "ainav.microsoft.readiness.run_twin_certification",
        lambda _catalog=None: {"launch": True},
    )
    with pytest.raises(IntegrityError, match="industry certified and launch open"):
        run_whole_certification()
