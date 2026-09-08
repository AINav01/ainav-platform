from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_INDUSTRY_LIBRARY_PAIRS,
    HONEST_INDUSTRY_PACK_COUNT,
    HONEST_INDUSTRY_REFUSE_TEXT,
    HONEST_INDUSTRY_STANDARD_COUNT,
    HONEST_INDUSTRY_UNPAIRED_LIBS,
    HONEST_INDUSTRY_UNPAIRED_PACKS,
    HONEST_INDUSTRY_UPSELL_COUNT,
    LIBRARY_COUNT,
    MODULE_COUNT,
    REPOSITORY_COUNT,
    load_catalog,
    validate_catalog,
)
from ainav.industry_certify import (
    certify_industry,
    public_review,
    run_industry_certification,
    validate_honest_industry,
)


def test_industry_review_is_not_launch():
    body = public_review()
    assert body["kind"] == "ainav.honest.industry.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["packs_are_skus"] is False
    assert body["industry_certified_launch"] is False
    assert body["certified"] is False
    assert body["complete"] is True
    assert body["live"] is False
    assert "industry certify is not launch" in body["lede"].lower()
    assert "packs are not skus" in body["note"].lower()
    assert len(body["rows"]) == HONEST_INDUSTRY_PACK_COUNT
    assert sum(1 for item in body["rows"] if item["class"] == "standard") == HONEST_INDUSTRY_STANDARD_COUNT
    assert sum(1 for item in body["rows"] if item["class"] == "upsell") == HONEST_INDUSTRY_UPSELL_COUNT
    assert len(body["modules"]) == MODULE_COUNT
    assert len(body["libraries"]) == LIBRARY_COUNT
    assert len(body["repositories"]) == REPOSITORY_COUNT
    assert "Treat an industry pack as a SKU." in body["this_agent_cannot"]
    assert "Treat industry certify as launch." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["packs"] == 26
    assert probes["launch"] is False
    assert probes["industry_certified_launch"] is False
    on_disk = json.loads(Path("institute/industry.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_certify_industry_pairs_and_unpaired():
    rows = certify_industry()
    by_id = {item["id"]: item for item in rows}
    assert by_id["industry.treasury"]["libraries"] == ["lib.l1.wedge"]
    assert by_id["industry.treasury"]["class"] == "standard"
    assert by_id["industry.payables"]["class"] == "upsell"
    assert by_id["industry.credit"]["libraries"] == []
    assert by_id["industry.inventory"]["libraries"] == []
    assert by_id["industry.pricing"]["libraries"] == []
    assert set(HONEST_INDUSTRY_UNPAIRED_PACKS) <= set(by_id)
    paired_libs = {lib for libs in HONEST_INDUSTRY_LIBRARY_PAIRS.values() for lib in libs}
    assert HONEST_INDUSTRY_UNPAIRED_LIBS.isdisjoint(paired_libs)


def test_run_industry_certification_holds_launch():
    probes = run_industry_certification()
    assert probes["kind"] == "ainav.honest.industry.v1"
    assert probes["packs"] == 26
    assert probes["standard"] == 8
    assert probes["upsell"] == 18
    assert probes["modules"] == 30
    assert probes["libraries"] == 23
    assert probes["repositories"] == 11
    assert probes["launch"] is False
    assert probes["live_pin_ok"] is False


def test_run_industry_certification_fail_closed(monkeypatch):
    def bad_rows(_catalog=None):
        raise IntegrityError("broken pair", reason_code="CATALOG_REVIEW")

    monkeypatch.setattr("ainav.industry_certify.certify_industry", bad_rows)
    with pytest.raises(IntegrityError):
        run_industry_certification()
    cat = copy.deepcopy(load_catalog())
    cat["repositories"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        run_industry_certification(cat)
    live = copy.deepcopy(load_catalog())
    live["repositories"][0]["live"] = True
    with pytest.raises(IntegrityError):
        run_industry_certification(live)
    named = copy.deepcopy(load_catalog())
    named["repositories"][0]["id"] = "L1"
    with pytest.raises(IntegrityError):
        run_industry_certification(named)


def test_validate_honest_industry_fail_closed():
    edge = load_catalog()
    missing = copy.deepcopy(edge)
    missing.pop("industry_certify")
    with pytest.raises(IntegrityError):
        validate_honest_industry(missing)
    kind = copy.deepcopy(edge)
    kind["industry_certify"]["kind"] = "ainav.honest.industry.v0"
    with pytest.raises(IntegrityError):
        validate_honest_industry(kind)
    sku = copy.deepcopy(edge)
    sku["industry_certify"]["packs_are_skus"] = True
    with pytest.raises(IntegrityError):
        validate_honest_industry(sku)
    launch = copy.deepcopy(edge)
    launch["industry_certify"]["industry_certified_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_industry(launch)
    honest = copy.deepcopy(edge)
    honest["industry_certify"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_industry(honest)
    complete = copy.deepcopy(edge)
    complete["industry_certify"]["complete"] = False
    with pytest.raises(IntegrityError):
        validate_honest_industry(complete)
    href = copy.deepcopy(edge)
    href["industry_certify"]["href"] = "#industry"
    with pytest.raises(IntegrityError):
        validate_honest_industry(href)
    rows = copy.deepcopy(edge)
    rows["industry_certify"]["rows"] = rows["industry_certify"]["rows"][:-1]
    with pytest.raises(IntegrityError):
        validate_honest_industry(rows)
    refuse = copy.deepcopy(edge)
    refuse["industry_certify"]["refuse"][0]["refuse_text"] = "Nope"
    with pytest.raises(IntegrityError):
        validate_honest_industry(refuse)
    leftover = copy.deepcopy(edge)
    leftover["industry_certify"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_industry(leftover)
    note = copy.deepcopy(edge)
    note["industry_certify"]["note"] = "Industry board."
    with pytest.raises(IntegrityError):
        validate_honest_industry(note)
    site = copy.deepcopy(edge)
    site["industry_certify"]["site"] = "Industry on #packs."
    with pytest.raises(IntegrityError):
        validate_honest_industry(site)
    with pytest.raises(IntegrityError):
        validate_catalog(sku)


def test_refuse_text_starts_refused():
    assert HONEST_INDUSTRY_REFUSE_TEXT["industry_pack_as_sku"].startswith("Refused.")
    assert HONEST_INDUSTRY_REFUSE_TEXT["industry_certify_as_launch"].startswith("Refused.")
