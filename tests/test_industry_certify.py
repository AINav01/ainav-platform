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


def test_run_industry_certification_repos_fail_closed():
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
    named["industry_certify"]["repositories"] = [item["id"] for item in named["repositories"]]
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


def test_validate_honest_industry_more_fail_closed(monkeypatch):
    edge = load_catalog()
    missing_flag = copy.deepcopy(edge)
    missing_flag["industry_certify"].pop("packs_are_skus")
    with pytest.raises(IntegrityError):
        validate_honest_industry(missing_flag)
    missing_launch = copy.deepcopy(edge)
    missing_launch["industry_certify"].pop("industry_certified_launch")
    with pytest.raises(IntegrityError):
        validate_honest_industry(missing_launch)
    not_objects = copy.deepcopy(edge)
    not_objects["industry_certify"]["rows"] = list(HONEST_INDUSTRY_LIBRARY_PAIRS)
    with pytest.raises(IntegrityError):
        validate_honest_industry(not_objects)
    order = copy.deepcopy(edge)
    order["industry_certify"]["rows"] = list(reversed(order["industry_certify"]["rows"]))
    with pytest.raises(IntegrityError):
        validate_honest_industry(order)
    monkeypatch.setattr("ainav.industry_certify.HONEST_INDUSTRY_STANDARD_COUNT", 1)
    with pytest.raises(IntegrityError):
        validate_honest_industry(copy.deepcopy(edge))
    monkeypatch.setattr("ainav.industry_certify.HONEST_INDUSTRY_STANDARD_COUNT", HONEST_INDUSTRY_STANDARD_COUNT)
    monkeypatch.setattr("ainav.industry_certify.MODULE_COUNT", 1)
    with pytest.raises(IntegrityError):
        validate_honest_industry(copy.deepcopy(edge))
    monkeypatch.setattr("ainav.industry_certify.MODULE_COUNT", MODULE_COUNT)
    monkeypatch.setattr("ainav.industry_certify.LIBRARY_COUNT", 1)
    with pytest.raises(IntegrityError):
        validate_honest_industry(copy.deepcopy(edge))
    monkeypatch.setattr("ainav.industry_certify.LIBRARY_COUNT", LIBRARY_COUNT)
    monkeypatch.setattr("ainav.industry_certify.HONEST_INDUSTRY_UNPAIRED_LIBS", frozenset({"lib.ghost"}))
    with pytest.raises(IntegrityError):
        validate_honest_industry(copy.deepcopy(edge))
    monkeypatch.setattr("ainav.industry_certify.HONEST_INDUSTRY_UNPAIRED_LIBS", HONEST_INDUSTRY_UNPAIRED_LIBS)
    monkeypatch.setattr("ainav.industry_certify.REPOSITORY_COUNT", 1)
    with pytest.raises(IntegrityError):
        validate_honest_industry(copy.deepcopy(edge))
    monkeypatch.setattr("ainav.industry_certify.REPOSITORY_COUNT", REPOSITORY_COUNT)
    note = copy.deepcopy(edge)
    note["industry_certify"]["note"] = "Honest industry. Industry certify is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_industry(note)
    note2 = copy.deepcopy(edge)
    note2["industry_certify"]["note"] = "Honest industry. Packs are not SKUs."
    with pytest.raises(IntegrityError):
        validate_honest_industry(note2)
    lede = copy.deepcopy(edge)
    lede["industry_certify"]["lede"] = "Industry certify is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_industry(lede)
    lede2 = copy.deepcopy(edge)
    lede2["industry_certify"]["lede"] = "Standard and upsell desks."
    with pytest.raises(IntegrityError):
        validate_honest_industry(lede2)
    site = copy.deepcopy(edge)
    site["industry_certify"]["site"] = "Honest industry on #packs. Packs are not SKUs."
    with pytest.raises(IntegrityError):
        validate_honest_industry(site)
    site2 = copy.deepcopy(edge)
    site2["industry_certify"]["site"] = (
        "Honest industry. Industry certify is not launch. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        validate_honest_industry(site2)
    site3 = copy.deepcopy(edge)
    site3["industry_certify"]["site"] = (
        "Honest industry on #packs. Industry certify is not launch."
    )
    with pytest.raises(IntegrityError):
        validate_honest_industry(site3)
    operator = copy.deepcopy(edge)
    operator["operating"]["operator"] = "grok.build"
    with pytest.raises(IntegrityError):
        validate_honest_industry(operator)
    mods = copy.deepcopy(edge)
    mods["industry_certify"]["modules"] = list(mods["industry_certify"]["modules"])
    mods["industry_certify"]["modules"][0] = "bc.ghost.post"
    with pytest.raises(IntegrityError):
        validate_honest_industry(mods)
    libs = copy.deepcopy(edge)
    libs["industry_certify"]["libraries"] = list(libs["industry_certify"]["libraries"])
    libs["industry_certify"]["libraries"][0] = "lib.ghost"
    with pytest.raises(IntegrityError):
        validate_honest_industry(libs)
    repos = copy.deepcopy(edge)
    repos["industry_certify"]["repositories"] = list(repos["industry_certify"]["repositories"])
    repos["industry_certify"]["repositories"][0] = "repo.ghost"
    with pytest.raises(IntegrityError):
        validate_honest_industry(repos)
    klass = copy.deepcopy(edge)
    klass["industry_certify"]["rows"][0]["class"] = "upsell"
    with pytest.raises(IntegrityError):
        validate_honest_industry(klass)
    row_mod = copy.deepcopy(edge)
    row_mod["industry_certify"]["rows"][0]["modules"] = ["bc.ghost.post"]
    with pytest.raises(IntegrityError):
        validate_honest_industry(row_mod)
    row_lib = copy.deepcopy(edge)
    row_lib["industry_certify"]["rows"][0]["libraries"] = ["lib.ghost"]
    with pytest.raises(IntegrityError):
        validate_honest_industry(row_lib)
    row_sku = copy.deepcopy(edge)
    row_sku["industry_certify"]["rows"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_industry(row_sku)
    row_href = copy.deepcopy(edge)
    row_href["industry_certify"]["rows"][0]["href"] = "#industry"
    with pytest.raises(IntegrityError):
        validate_honest_industry(row_href)
    refuse_href = copy.deepcopy(edge)
    refuse_href["industry_certify"]["refuse"][0]["href"] = "#industry"
    with pytest.raises(IntegrityError):
        validate_honest_industry(refuse_href)
    playbook = copy.deepcopy(edge)
    playbook["industry_certify"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_industry(playbook)
    playbook2 = copy.deepcopy(edge)
    playbook2["industry_certify"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_industry(playbook2)
    refuse_ids = copy.deepcopy(edge)
    refuse_ids["industry_certify"]["refuse"] = refuse_ids["industry_certify"]["refuse"][:-1]
    with pytest.raises(IntegrityError):
        validate_honest_industry(refuse_ids)


def test_certify_industry_fail_closed(monkeypatch):
    edge = load_catalog()
    short = copy.deepcopy(edge)
    short["industry_packs"] = short["industry_packs"][:1]
    with pytest.raises(IntegrityError):
        certify_industry(short)
    unknown = copy.deepcopy(edge)
    unknown["industry_packs"][0]["id"] = "industry.ghost"
    with pytest.raises(IntegrityError):
        certify_industry(unknown)
    sku = copy.deepcopy(edge)
    sku["industry_packs"][0]["requires_sku"] = "L2"
    with pytest.raises(IntegrityError):
        certify_industry(sku)
    pack_sku = copy.deepcopy(edge)
    pack_sku["industry_packs"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        certify_industry(pack_sku)
    pack_named = copy.deepcopy(edge)
    pack_named["industry_packs"][0]["id"] = "L1"
    with pytest.raises(IntegrityError):
        certify_industry(pack_named)
    bad_mod = copy.deepcopy(edge)
    bad_mod["industry_packs"][0]["modules"] = ["bc.ghost.post"]
    with pytest.raises(IntegrityError):
        certify_industry(bad_mod)
    pairs = dict(HONEST_INDUSTRY_LIBRARY_PAIRS)
    pairs["industry.credit"] = ["lib.udual.sales"]
    monkeypatch.setattr("ainav.industry_certify.HONEST_INDUSTRY_LIBRARY_PAIRS", pairs)
    with pytest.raises(IntegrityError):
        certify_industry(copy.deepcopy(edge))
    empty = dict(HONEST_INDUSTRY_LIBRARY_PAIRS)
    empty["industry.treasury"] = []
    monkeypatch.setattr("ainav.industry_certify.HONEST_INDUSTRY_LIBRARY_PAIRS", empty)
    with pytest.raises(IntegrityError):
        certify_industry(copy.deepcopy(edge))
    ghost_lib = dict(HONEST_INDUSTRY_LIBRARY_PAIRS)
    ghost_lib["industry.treasury"] = ["lib.ghost"]
    monkeypatch.setattr("ainav.industry_certify.HONEST_INDUSTRY_LIBRARY_PAIRS", ghost_lib)
    with pytest.raises(IntegrityError):
        certify_industry(copy.deepcopy(edge))
    mismatch = copy.deepcopy(edge)
    for lib in mismatch["libraries"]:
        if lib["id"] == "lib.l1.wedge":
            lib["requires_sku"] = "P-ADM"
    monkeypatch.setattr("ainav.industry_certify.HONEST_INDUSTRY_LIBRARY_PAIRS", dict(HONEST_INDUSTRY_LIBRARY_PAIRS))
    with pytest.raises(IntegrityError):
        certify_industry(mismatch)
    lib_sku = copy.deepcopy(edge)
    for lib in lib_sku["libraries"]:
        if lib["id"] == "lib.l1.wedge":
            lib["sku"] = True
    with pytest.raises(IntegrityError):
        certify_industry(lib_sku)
