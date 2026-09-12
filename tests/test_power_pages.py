from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_POWER_PAGES_FACT_IDS,
    HONEST_POWER_PAGES_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.power_pages import (
    public_review,
    run_power_pages_certification,
    validate_honest_power_pages,
)


def test_pages_review_is_not_host():
    body = public_review()
    assert body["kind"] == "ainav.honest.power_pages.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["cms"] is False
    assert body["is_host"] is False
    assert body["closes_dataverse"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["honest"] is True
    assert body["href"] == "#twin"
    assert "dataverse-backed" in body["lede"].lower()
    assert "power pages is not the institute host" in body["note"].lower()
    assert "power pages is not a sku" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_POWER_PAGES_FACT_IDS)
    assert "Treat Power Pages as the Institute host." in body["this_agent_cannot"]
    assert "Treat Power Pages as a SKU." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["is_host"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/pages.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_power_pages_certification_holds_launch():
    probes = run_power_pages_certification()
    assert probes["kind"] == "ainav.honest.power_pages.v1"
    assert probes["considered"] is True
    assert probes["is_host"] is False
    assert probes["is_sku"] is False
    assert probes["cms"] is False
    assert probes["closes_dataverse"] is False
    assert probes["is_complement"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_power_pages_fail_closed():
    cat = load_catalog()
    hole = copy.deepcopy(cat)
    hole["honest_power_pages"]["is_host"] = True
    with pytest.raises(IntegrityError):
        validate_honest_power_pages(hole)
    sku = copy.deepcopy(cat)
    sku["honest_power_pages"]["is_sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_power_pages(sku)
    cms = copy.deepcopy(cat)
    cms["honest_power_pages"]["cms"] = True
    with pytest.raises(IntegrityError):
        validate_honest_power_pages(cms)
    close = copy.deepcopy(cat)
    close["honest_power_pages"]["closes_dataverse"] = True
    with pytest.raises(IntegrityError):
        validate_honest_power_pages(close)
    href = copy.deepcopy(cat)
    href["honest_power_pages"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_power_pages(href)
    live = copy.deepcopy(cat)
    live["programs"]["website"]["honest_power_pages_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_power_pages_more_fail_closed():
    edge = load_catalog()
    missing = copy.deepcopy(edge)
    missing.pop("honest_power_pages")
    with pytest.raises(IntegrityError, match="catalog missing honest Power Pages"):
        validate_honest_power_pages(missing)
    kind = copy.deepcopy(edge)
    kind["honest_power_pages"]["kind"] = "ainav.honest.power_pages.v0"
    with pytest.raises(IntegrityError, match="kind stays catalog law"):
        validate_honest_power_pages(kind)
    for flag in (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "cms",
        "host",
        "is_host",
        "apex",
        "closes_dataverse",
        "wired",
        "claimed",
        "certified",
        "live",
        "live_pin_ok",
        "launch",
        "created",
    ):
        claimed = copy.deepcopy(edge)
        claimed["honest_power_pages"][flag] = True
        with pytest.raises(IntegrityError, match="cannot claim"):
            validate_honest_power_pages(claimed)
    honest = copy.deepcopy(edge)
    honest["honest_power_pages"]["honest"] = False
    with pytest.raises(IntegrityError, match="stays honest"):
        validate_honest_power_pages(honest)
    considered = copy.deepcopy(edge)
    considered["honest_power_pages"]["considered"] = False
    with pytest.raises(IntegrityError, match="stays considered"):
        validate_honest_power_pages(considered)
    href = copy.deepcopy(edge)
    href["honest_power_pages"]["href"] = "#whole"
    with pytest.raises(IntegrityError, match="sits on #twin"):
        validate_honest_power_pages(href)
    missing_host = copy.deepcopy(edge)
    missing_host["honest_power_pages"].pop("is_host")
    with pytest.raises(IntegrityError, match="Power Pages is not the Institute host"):
        validate_honest_power_pages(missing_host)
    missing_sku = copy.deepcopy(edge)
    missing_sku["honest_power_pages"].pop("is_sku")
    with pytest.raises(IntegrityError, match="Power Pages is not a SKU"):
        validate_honest_power_pages(missing_sku)
    missing_cms = copy.deepcopy(edge)
    missing_cms["honest_power_pages"].pop("cms")
    with pytest.raises(IntegrityError, match="Power Pages is not the CMS"):
        validate_honest_power_pages(missing_cms)
    missing_dv = copy.deepcopy(edge)
    missing_dv["honest_power_pages"].pop("closes_dataverse")
    with pytest.raises(IntegrityError, match="Power Pages does not close US Dataverse"):
        validate_honest_power_pages(missing_dv)
    facts_len = copy.deepcopy(edge)
    facts_len["honest_power_pages"]["facts"] = []
    with pytest.raises(IntegrityError, match="stays five facts"):
        validate_honest_power_pages(facts_len)
    not_objects = copy.deepcopy(edge)
    not_objects["honest_power_pages"]["facts"] = list(HONEST_POWER_PAGES_FACT_IDS)
    with pytest.raises(IntegrityError, match="facts stay objects"):
        validate_honest_power_pages(not_objects)
    facts_ids = copy.deepcopy(edge)
    facts_ids["honest_power_pages"]["facts"][0]["id"] = "portal"
    with pytest.raises(IntegrityError, match="facts stay catalog law"):
        validate_honest_power_pages(facts_ids)
    fact_sku = copy.deepcopy(edge)
    fact_sku["honest_power_pages"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError, match="facts are not SKUs or hosts"):
        validate_honest_power_pages(fact_sku)
    fact_host = copy.deepcopy(edge)
    fact_host["honest_power_pages"]["facts"][1]["host"] = True
    with pytest.raises(IntegrityError, match="facts are not SKUs or hosts"):
        validate_honest_power_pages(fact_host)
    fact_live = copy.deepcopy(edge)
    fact_live["honest_power_pages"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError, match="facts are not SKUs or hosts"):
        validate_honest_power_pages(fact_live)
    refuse_ids = copy.deepcopy(edge)
    refuse_ids["honest_power_pages"]["refuse"][0]["id"] = "pages_as_host"
    with pytest.raises(IntegrityError, match="refuse ids stay catalog law"):
        validate_honest_power_pages(refuse_ids)
    refuse_text = copy.deepcopy(edge)
    refuse_text["honest_power_pages"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError, match="refuse text stays catalog law"):
        validate_honest_power_pages(refuse_text)
    refuse_href = copy.deepcopy(edge)
    refuse_href["honest_power_pages"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError, match="refuse hrefs stay catalog law"):
        validate_honest_power_pages(refuse_href)
    leftover = copy.deepcopy(edge)
    leftover["honest_power_pages"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError, match="cannot leftover claimed or live"):
        validate_honest_power_pages(leftover)
    leftover_live = copy.deepcopy(edge)
    leftover_live["honest_power_pages"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError, match="cannot leftover claimed or live"):
        validate_honest_power_pages(leftover_live)
    note = copy.deepcopy(edge)
    note["honest_power_pages"]["note"] = "Power Pages is not the Institute host. Power Pages is not a SKU."
    with pytest.raises(IntegrityError, match="note keeps honest Power Pages"):
        validate_honest_power_pages(note)
    note_host = copy.deepcopy(edge)
    note_host["honest_power_pages"]["note"] = "Honest Power Pages. Power Pages is not a SKU."
    with pytest.raises(IntegrityError, match="note keeps Power Pages is not the Institute host"):
        validate_honest_power_pages(note_host)
    note_sku = copy.deepcopy(edge)
    note_sku["honest_power_pages"]["note"] = "Honest Power Pages. Power Pages is not the Institute host."
    with pytest.raises(IntegrityError, match="note keeps Power Pages is not a SKU"):
        validate_honest_power_pages(note_sku)
    lede = copy.deepcopy(edge)
    lede["honest_power_pages"]["lede"] = "Power Pages is not the Institute host."
    with pytest.raises(IntegrityError, match="lede keeps Dataverse-backed"):
        validate_honest_power_pages(lede)
    lede_host = copy.deepcopy(edge)
    lede_host["honest_power_pages"]["lede"] = "Microsoft Power Pages is a Dataverse-backed Power Platform website."
    with pytest.raises(IntegrityError, match="lede keeps Power Pages is not the Institute host"):
        validate_honest_power_pages(lede_host)
    site = copy.deepcopy(edge)
    site["honest_power_pages"]["site"] = (
        "Power Pages is not the Institute host. Not a /power-pages route. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError, match="site keeps honest Power Pages"):
        validate_honest_power_pages(site)
    site_route = copy.deepcopy(edge)
    site_route["honest_power_pages"]["site"] = (
        "Honest Power Pages on #twin. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError, match="site keeps not a /power-pages route"):
        validate_honest_power_pages(site_route)
    site_glance = copy.deepcopy(edge)
    site_glance["honest_power_pages"]["site"] = (
        "Honest Power Pages on #twin. Not a /power-pages route."
    )
    with pytest.raises(IntegrityError, match="site keeps first glance stays the write rail"):
        validate_honest_power_pages(site_glance)
    complements = copy.deepcopy(edge)
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight"):
        validate_honest_power_pages(complements)
    ninth = copy.deepcopy(edge)
    ninth["connections"]["complements"][0]["id"] = "power_pages"
    with pytest.raises(IntegrityError, match="Power Pages is not a complement"):
        validate_honest_power_pages(ninth)
    actor = copy.deepcopy(edge)
    actor["honest_power_pages"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError, match="sole owner"):
        validate_honest_power_pages(actor)
    cannot = copy.deepcopy(edge)
    cannot["honest_power_pages"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError, match="Cloud Agent cannot create a Power Pages site"):
        validate_honest_power_pages(cannot)
    refuse_text_law = HONEST_POWER_PAGES_REFUSE_TEXT["power_pages_as_host"]
    assert refuse_text_law == "Refused. Power Pages is not the Institute host."


def test_run_power_pages_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_power_pages_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_power_pages_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.power_pages.validate_honest_power_pages", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after Power Pages consider"):
        run_power_pages_certification(short)
