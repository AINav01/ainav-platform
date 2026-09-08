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
