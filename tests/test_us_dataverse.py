from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import catalog_us_dataverse, load_catalog, validate_catalog
from ainav.microsoft.connections import stack_json


def test_us_dataverse_stays_open_and_canada_is_not_united_states():
    cat = load_catalog()
    body = cat["microsoft_stack"]["us_dataverse"]
    assert body["kind"] == "ainav.us_dataverse.v1"
    assert body["closed"] is False
    assert body["united_states"] is False
    assert body["canada_is_united_states"] is False
    assert body["adr_purchased"] is False
    assert body["adr_eligible"] is False
    assert body["geo_to_geo_available"] is False
    assert body["dataverse_url_set"] is False
    assert body["engineering_exception_granted"] is False
    assert body["engineering_exception_routed"] is True
    assert body["ticket"] == "2609030040009525"
    assert "us dataverse stays open" in body["lede"].lower()
    exported = catalog_us_dataverse()
    assert exported["lede"] == body["lede"]
    assert exported["closed"] is False
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "canada as united states" in blob
    assert "advanced data residency" in blob
    assert "affinity" in blob
    assert "US Dataverse" in cat["plane_interface"]["gaps"]["owner_only_open"]
    pin = next(item for item in cat["expert_review"]["upgrades"] if item["n"] == 4)
    assert pin["who"] == "owner"
    assert pin.get("done") is not True
    assert pin["marks_live_pin"] is False
    assert "2609030040009525" in pin["do"]
    assert "create a us power platform" not in pin["do"].lower()
    catalog_text = Path("src/ainav/data/catalog.json").read_text(encoding="utf-8").lower()
    assert "90299caf" not in catalog_text
    page = stack_json()
    assert page["us_dataverse"]["united_states"] is False
    assert page["us_dataverse"]["ticket"] == "2609030040009525"
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "2609030040009525" in html
    assert "Canada affinity" in html
    assert "create a US Power Platform" not in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#dataverse"' not in nav


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_us_dataverse_fail_closed():
    def closed(cat):
        cat["microsoft_stack"]["us_dataverse"]["closed"] = True

    def united(cat):
        cat["microsoft_stack"]["us_dataverse"]["united_states"] = True

    def canada_is_us(cat):
        cat["microsoft_stack"]["us_dataverse"]["canada_is_united_states"] = True

    def adr(cat):
        cat["microsoft_stack"]["us_dataverse"]["adr_purchased"] = True

    def eligible(cat):
        cat["microsoft_stack"]["us_dataverse"]["adr_eligible"] = True

    def geo(cat):
        cat["microsoft_stack"]["us_dataverse"]["geo_to_geo_available"] = True

    def url_set(cat):
        cat["microsoft_stack"]["us_dataverse"]["dataverse_url_set"] = True

    def granted(cat):
        cat["microsoft_stack"]["us_dataverse"]["engineering_exception_granted"] = True

    def not_routed(cat):
        cat["microsoft_stack"]["us_dataverse"]["engineering_exception_routed"] = False

    def live(cat):
        cat["microsoft_stack"]["us_dataverse"]["live_pin_ok"] = True

    def ticket(cat):
        cat["microsoft_stack"]["us_dataverse"]["ticket"] = "nope"

    def lede(cat):
        cat["microsoft_stack"]["us_dataverse"]["lede"] = "United States is pinned."

    def finding(cat):
        cat["microsoft_stack"]["us_dataverse"]["finding"] = "Resolved."

    def owner(cat):
        cat["microsoft_stack"]["us_dataverse"]["owner"] = "Create a US environment."

    def is_not(cat):
        cat["microsoft_stack"]["us_dataverse"]["is_not"] = ["nope"]

    def cannot(cat):
        cat["microsoft_stack"]["us_dataverse"]["cannot"] = ["nope"]

    def scope(cat):
        cat["microsoft_stack"]["us_dataverse"]["scope_not"] = ["nope"]

    def note(cat):
        cat["microsoft_stack"]["us_dataverse"]["note"] = "Canada is close enough."

    def shape(cat):
        cat["microsoft_stack"]["us_dataverse"] = "nope"

    def guid(cat):
        cat["microsoft_stack"]["us_dataverse"]["finding"] += " 90299caf-e3a6-f111-8adb-6045bdcd66f2"

    def upgrade_done(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 4:
                item["done"] = True

    def upgrade_stale(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 4:
                item["do"] = "Create a US Power Platform environment with Dataverse."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "canada as united states" not in item.lower()
        ]

    def missing(cat):
        cat["honest_missing"] = [
            item for item in cat["honest_missing"] if "dataverse" not in item.lower()
        ]

    for mutator in (
        closed,
        united,
        canada_is_us,
        adr,
        eligible,
        geo,
        url_set,
        granted,
        not_routed,
        live,
        ticket,
        lede,
        finding,
        owner,
        is_not,
        cannot,
        scope,
        note,
        shape,
        guid,
        upgrade_done,
        upgrade_stale,
        principles,
        missing,
    ):
        _reject(mutator)


def test_validate_us_dataverse_direct_holes():
    good = dict(load_catalog()["microsoft_stack"]["us_dataverse"])
    with pytest.raises(IntegrityError):
        catmod._validate_us_dataverse({"microsoft_stack": {}})
    sku = dict(good)
    sku["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_us_dataverse({"microsoft_stack": {"us_dataverse": sku}})
    live = dict(good)
    live["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_us_dataverse({"microsoft_stack": {"us_dataverse": live}})
    kind = dict(good)
    kind["kind"] = "nope"
    with pytest.raises(IntegrityError):
        catmod._validate_us_dataverse({"microsoft_stack": {"us_dataverse": kind}})
    changed = dict(good)
    changed["support_changes_made"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_us_dataverse({"microsoft_stack": {"us_dataverse": changed}})
    learn = dict(good)
    learn["learn"] = "nope"
    with pytest.raises(IntegrityError):
        catmod._validate_us_dataverse({"microsoft_stack": {"us_dataverse": learn}})
    learn_key = dict(good)
    learn_key["learn"] = dict(good["learn"])
    learn_key["learn"]["geo_to_geo"] = "https://example.com"
    with pytest.raises(IntegrityError):
        catmod._validate_us_dataverse({"microsoft_stack": {"us_dataverse": learn_key}})


def test_us_dataverse_owner_surfaces_fail_closed():
    def sales_hop(cat):
        for item in cat["microsoft_stack"]["walk"]["path"]:
            if item.get("id") == "sales.enterprise":
                item["in_tree"] = "Sales licensed."
                item["owner"] = "Create a US Power Platform environment."

    def sales_create(cat):
        for item in cat["microsoft_stack"]["walk"]["path"]:
            if item.get("id") == "sales.enterprise":
                item["in_tree"] = (
                    "Ticket 2609030040009525. Canada. United States is not pinned. "
                    "Create a US Power Platform environment."
                )

    def walk_cannot(cat):
        cat["microsoft_stack"]["walk"]["cannot"] = [
            item
            for item in cat["microsoft_stack"]["walk"]["cannot"]
            if "canada" not in item.lower()
        ]

    def upgrade_create(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 4:
                item["do"] = (
                    "Ticket 2609030040009525 Canada ADR United States. "
                    "Create a US Power Platform environment."
                )

    def upgrade_who(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 4:
                item["who"] = "tree"
                item["done"] = True

    def integrate(cat):
        for item in cat["plane_interface"]["floor"]["integrate"]["items"]:
            if item.get("id") == "dataverse.us":
                item["note"] = "Create Dataverse later."

    def well(cat):
        cat["expert_review"]["working_well"] = [
            item
            for item in cat["expert_review"]["working_well"]
            if "2609030040009525" not in item
        ]

    def improve(cat):
        cat["expert_review"]["improve"] = [
            item for item in cat["expert_review"]["improve"] if "path b" not in item.lower()
        ]

    def cannot_close(cat):
        cat["engineering"]["cannot_close"] = [
            item for item in cat["engineering"]["cannot_close"] if "dataverse" not in item.lower()
        ]

    def gate(cat):
        for item in cat["owner_gates"]:
            if item.get("id") == "dataverse.us":
                item["do"] = "Create a US Power Platform environment with Dataverse."

    def gate_stem(cat):
        for item in cat["owner_gates"]:
            if item.get("id") == "dataverse.us":
                item["do"] = "Do something else."

    def gate_create(cat):
        for item in cat["owner_gates"]:
            if item.get("id") == "dataverse.us":
                item["do"] = (
                    f"{item['do']} Create a US Power Platform environment."
                )

    def principles_adr(cat):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "advanced data residency" not in item.lower()
            ]
        )

    for mutator in (
        sales_hop,
        sales_create,
        walk_cannot,
        upgrade_create,
        upgrade_who,
        integrate,
        well,
        improve,
        cannot_close,
        gate,
        gate_stem,
        gate_create,
    ):
        _reject(mutator)

    with pytest.raises(IntegrityError):
        principles_adr(load_catalog())
    missing = copy.deepcopy(load_catalog())
    missing["honest_missing"] = [
        item for item in missing["honest_missing"] if "canada" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_honest_missing(missing)
    plane = copy.deepcopy(load_catalog())
    plane["plane_interface"]["gaps"]["this_plane_cannot"] = [
        item
        for item in plane["plane_interface"]["gaps"]["this_plane_cannot"]
        if "canada" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_272(plane, plane["plane_interface"])
    integrate_only = copy.deepcopy(load_catalog())
    for item in integrate_only["plane_interface"]["floor"]["integrate"]["items"]:
        if item.get("id") == "dataverse.us":
            item["note"] = "Create Dataverse later."
    with pytest.raises(IntegrityError):
        catmod._validate_us_dataverse(integrate_only)
