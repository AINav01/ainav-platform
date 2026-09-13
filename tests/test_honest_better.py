from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_BETTER_FACT_IDS,
    HONEST_BETTER_HOP_HREFS,
    HONEST_BETTER_HOP_IDS,
    load_catalog,
    validate_catalog,
)
from ainav.honest_better import (
    public_review,
    run_better_certification,
    validate_honest_better,
)


def test_better_review_is_not_launch():
    body = public_review()
    assert body["kind"] == "ainav.honest.better.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["better_as_launch"] is False
    assert body["ten_as_seated"] is False
    assert body["systems_as_wired"] is False
    assert body["polish_as_production"] is False
    assert body["interpret_as_live_pin"] is False
    assert body["make_as_launch"] is False
    assert body["please_as_launch"] is False
    assert body["twin_http_is_launch"] is False
    assert body["sandbox_http_is_g14"] is False
    assert body["planes_as_launch"] is False
    assert body["industry_ten_as_launch"] is False
    assert body["client_ten_as_live_client"] is False
    assert body["twin_ten_as_launch"] is False
    assert body["shared_sandbox_is_production"] is False
    assert body["rails_as_launch"] is False
    assert body["roster_as_wired"] is False
    assert body["flag_strip_as_admit"] is False
    assert body["craft_as_launch"] is False
    assert body["look_as_production"] is False
    assert body["graphic_as_launch"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#success"
    assert "a much better build and business is not launch" in body["lede"].lower()
    assert "making better is not launch" in body["lede"].lower()
    assert "honest better" in body["note"].lower()
    assert "making better is not launch" in body["note"].lower()
    assert "interpretability is not live_pin_ok" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_BETTER_FACT_IDS)
    assert [item["id"] for item in body["hops"]] == list(HONEST_BETTER_HOP_IDS)
    hop_hrefs = {item["id"]: item["href"] for item in body["hops"]}
    assert hop_hrefs == {key: HONEST_BETTER_HOP_HREFS[key] for key in HONEST_BETTER_HOP_IDS}
    assert "Treat a much better build and business as launch." in body["this_agent_cannot"]
    assert "Treat interpretability as LIVE_PIN_OK." in body["this_agent_cannot"]
    assert "Treat making better as launch." in body["this_agent_cannot"]
    assert "Treat please make better as launch." in body["this_agent_cannot"]
    assert "Treat twin HTTP as launch." in body["this_agent_cannot"]
    assert "Treat a 10/10 of industry, client, and twin as launch." in body["this_agent_cannot"]
    assert "Treat a 10/10 of the write rail, proof day, and bake-off as launch." in body["this_agent_cannot"]
    assert "Treat a polished Microsoft roster as a wired firm." in body["this_agent_cannot"]
    assert "Treat an identify flag strip as admit." in body["this_agent_cannot"]
    assert "Treat a 10/10 of quality, content, format, and graphics as launch." in body["this_agent_cannot"]
    assert "Treat a 10/10 look as production." in body["this_agent_cannot"]
    assert "Treat a polished graphic as launch." in body["this_agent_cannot"]
    assert "Treat twin HTTP as launch." in body["this_agent_cannot"]
    assert "a 10/10 of industry, client, and twin planes is not launch" in body["lede"].lower()
    assert "a 10/10 of the write rail, proof day, and bake-off is not launch" in body["lede"].lower()
    assert "a 10/10 of quality, content, format, and graphics is not launch" in body["lede"].lower()
    assert "twin http 200 is not launch" in body["lede"].lower()
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["better_as_launch"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/better.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_better_certification_holds_launch():
    probes = run_better_certification()
    assert probes["kind"] == "ainav.honest.better.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["better_as_launch"] is False
    assert probes["ten_as_seated"] is False
    assert probes["systems_as_wired"] is False
    assert probes["polish_as_production"] is False
    assert probes["interpret_as_live_pin"] is False
    assert probes["make_as_launch"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_better_fail_closed():
    hole = copy.deepcopy(load_catalog())
    hole["honest_better"]["better_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(hole)
    seated = copy.deepcopy(load_catalog())
    seated["honest_better"]["ten_as_seated"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(seated)
    wired = copy.deepcopy(load_catalog())
    wired["honest_better"]["systems_as_wired"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(wired)
    polish = copy.deepcopy(load_catalog())
    polish["honest_better"]["polish_as_production"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(polish)
    interpret = copy.deepcopy(load_catalog())
    interpret["honest_better"]["interpret_as_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(interpret)
    make = copy.deepcopy(load_catalog())
    make["honest_better"]["make_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(make)
    please = copy.deepcopy(load_catalog())
    please["honest_better"]["please_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(please)
    twin_http = copy.deepcopy(load_catalog())
    twin_http["honest_better"]["twin_http_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(twin_http)
    sandbox_http = copy.deepcopy(load_catalog())
    sandbox_http["honest_better"]["sandbox_http_is_g14"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(sandbox_http)
    planes = copy.deepcopy(load_catalog())
    planes["honest_better"]["planes_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(planes)
    industry_ten = copy.deepcopy(load_catalog())
    industry_ten["honest_better"]["industry_ten_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(industry_ten)
    client_ten = copy.deepcopy(load_catalog())
    client_ten["honest_better"]["client_ten_as_live_client"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(client_ten)
    twin_ten = copy.deepcopy(load_catalog())
    twin_ten["honest_better"]["twin_ten_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(twin_ten)
    vertical = copy.deepcopy(load_catalog())
    vertical["honest_better"]["named_vertical_as_sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(vertical)
    assigned = copy.deepcopy(load_catalog())
    assigned["honest_better"]["institute_twin_is_assigned_sandbox"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(assigned)
    shared = copy.deepcopy(load_catalog())
    shared["honest_better"]["shared_sandbox_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(shared)
    rails = copy.deepcopy(load_catalog())
    rails["honest_better"]["rails_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(rails)
    roster = copy.deepcopy(load_catalog())
    roster["honest_better"]["roster_as_wired"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(roster)
    flags = copy.deepcopy(load_catalog())
    flags["honest_better"]["flag_strip_as_admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(flags)
    href = copy.deepcopy(load_catalog())
    href["honest_better"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_better(href)
    live = copy.deepcopy(load_catalog())
    live["programs"]["website"]["honest_better_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_better_more_fail_closed():
    missing = copy.deepcopy(load_catalog())
    missing.pop("honest_better")
    with pytest.raises(IntegrityError):
        validate_honest_better(missing)
    kind = copy.deepcopy(load_catalog())
    kind["honest_better"]["kind"] = "ainav.honest.better.v0"
    with pytest.raises(IntegrityError):
        validate_honest_better(kind)
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
        "running_firm",
        "recognized_revenue",
    ):
        claimed = copy.deepcopy(load_catalog())
        claimed["honest_better"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_better(claimed)
    honest = copy.deepcopy(load_catalog())
    honest["honest_better"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_better(honest)
    considered = copy.deepcopy(load_catalog())
    considered["honest_better"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_better(considered)
    recorded = copy.deepcopy(load_catalog())
    recorded["honest_better"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_better(recorded)
    for key in (
        "better_as_launch",
        "ten_as_seated",
        "systems_as_wired",
        "polish_as_production",
        "interpret_as_live_pin",
        "make_as_launch",
        "please_as_launch",
        "twin_http_is_launch",
        "sandbox_http_is_g14",
        "planes_as_launch",
        "industry_ten_as_launch",
        "client_ten_as_live_client",
        "twin_ten_as_launch",
        "named_vertical_as_sku",
        "institute_twin_is_assigned_sandbox",
        "shared_sandbox_is_production",
        "rails_as_launch",
        "roster_as_wired",
        "flag_strip_as_admit",
        "craft_as_launch",
        "look_as_production",
        "graphic_as_launch",
    ):
        missing_flag = copy.deepcopy(load_catalog())
        missing_flag["honest_better"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_better(missing_flag)
    hops = copy.deepcopy(load_catalog())
    hops["honest_better"]["hops"] = []
    with pytest.raises(IntegrityError):
        validate_honest_better(hops)
    hop_closed = copy.deepcopy(load_catalog())
    hop_closed["honest_better"]["hops"][0]["closed"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(hop_closed)
    hop_href = copy.deepcopy(load_catalog())
    hop_href["honest_better"]["hops"][0]["href"] = "#open"
    with pytest.raises(IntegrityError):
        validate_honest_better(hop_href)
    facts_len = copy.deepcopy(load_catalog())
    facts_len["honest_better"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_better(facts_len)
    not_objects = copy.deepcopy(load_catalog())
    not_objects["honest_better"]["facts"] = list(HONEST_BETTER_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_better(not_objects)
    facts_ids = copy.deepcopy(load_catalog())
    facts_ids["honest_better"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_better(facts_ids)
    fact_sku = copy.deepcopy(load_catalog())
    fact_sku["honest_better"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_better(fact_sku)
    refuse_ids = copy.deepcopy(load_catalog())
    refuse_ids["honest_better"]["refuse"][0]["id"] = "better_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_better(refuse_ids)
    refuse_text = copy.deepcopy(load_catalog())
    refuse_text["honest_better"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_better(refuse_text)
    refuse_href = copy.deepcopy(load_catalog())
    refuse_href["honest_better"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_better(refuse_href)
    leftover = copy.deepcopy(load_catalog())
    leftover["honest_better"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_better(leftover)
    leftover_live = copy.deepcopy(load_catalog())
    leftover_live["honest_better"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_better(leftover_live)
    note = copy.deepcopy(load_catalog())
    note["honest_better"]["note"] = "A much better build and business is not launch. Interpretability is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_better(note)
    note_launch = copy.deepcopy(load_catalog())
    note_launch["honest_better"]["note"] = "Honest better. Interpretability is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_better(note_launch)
    note_pin = copy.deepcopy(load_catalog())
    note_pin["honest_better"]["note"] = "Honest better. A much better build and business is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_better(note_pin)
    note_make = copy.deepcopy(load_catalog())
    note_make["honest_better"]["note"] = (
        "Honest better. A much better build and business is not launch. Interpretability is not LIVE_PIN_OK."
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_make)
    note_please = copy.deepcopy(load_catalog())
    note_please["honest_better"]["note"] = note_please["honest_better"]["note"].replace(
        "Please make better is not launch.",
        "Better is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_please)
    note_twin = copy.deepcopy(load_catalog())
    note_twin["honest_better"]["note"] = note_twin["honest_better"]["note"].replace(
        "Twin HTTP 200 is not launch.",
        "Twin HTTP is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_twin)
    note_sandbox = copy.deepcopy(load_catalog())
    note_sandbox["honest_better"]["note"] = note_sandbox["honest_better"]["note"].replace(
        "Sandbox HTTP is not G14.",
        "Sandbox HTTP is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_sandbox)
    note_planes = copy.deepcopy(load_catalog())
    note_planes["honest_better"]["note"] = note_planes["honest_better"]["note"].replace(
        "A 10/10 of industry, client, and twin planes is not launch.",
        "Planes are recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_planes)
    note_vertical = copy.deepcopy(load_catalog())
    note_vertical["honest_better"]["note"] = note_vertical["honest_better"]["note"].replace(
        "A named vertical is not a SKU.",
        "A named vertical is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_vertical)
    note_rails = copy.deepcopy(load_catalog())
    note_rails["honest_better"]["note"] = note_rails["honest_better"]["note"].replace(
        "A 10/10 of the write rail, proof day, and bake-off is not launch.",
        "Rails are recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_rails)
    note_roster = copy.deepcopy(load_catalog())
    note_roster["honest_better"]["note"] = note_roster["honest_better"]["note"].replace(
        "A polished Microsoft roster is not a wired firm.",
        "A polished roster is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_roster)
    note_flags = copy.deepcopy(load_catalog())
    note_flags["honest_better"]["note"] = note_flags["honest_better"]["note"].replace(
        "An identify flag strip is not admit.",
        "A flag strip is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_flags)
    note_craft = copy.deepcopy(load_catalog())
    note_craft["honest_better"]["note"] = note_craft["honest_better"]["note"].replace(
        "A 10/10 of quality, content, format, and graphics is not launch.",
        "Craft is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_craft)
    note_look = copy.deepcopy(load_catalog())
    note_look["honest_better"]["note"] = note_look["honest_better"]["note"].replace(
        "A 10/10 look is not production.",
        "A look is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_look)
    note_graphic = copy.deepcopy(load_catalog())
    note_graphic["honest_better"]["note"] = note_graphic["honest_better"]["note"].replace(
        "A polished graphic is not launch.",
        "A graphic is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(note_graphic)
    lede = copy.deepcopy(load_catalog())
    lede["honest_better"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_better(lede)
    lede_wired = copy.deepcopy(load_catalog())
    lede_wired["honest_better"]["lede"] = "A much better build and business is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_wired)
    lede_ten = copy.deepcopy(load_catalog())
    lede_ten["honest_better"]["lede"] = lede_ten["honest_better"]["lede"].replace(
        "A 10/10 is not a seated second human.",
        "Quality is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_ten)
    lede_make = copy.deepcopy(load_catalog())
    lede_make["honest_better"]["lede"] = lede_make["honest_better"]["lede"].replace(
        "Making better is not launch.",
        "Better is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_make)
    lede_please = copy.deepcopy(load_catalog())
    lede_please["honest_better"]["lede"] = lede_please["honest_better"]["lede"].replace(
        "Please make better is not launch.",
        "Better is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_please)
    lede_twin = copy.deepcopy(load_catalog())
    lede_twin["honest_better"]["lede"] = lede_twin["honest_better"]["lede"].replace(
        "Twin HTTP 200 is not launch.",
        "Twin HTTP is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_twin)
    lede_sandbox = copy.deepcopy(load_catalog())
    lede_sandbox["honest_better"]["lede"] = lede_sandbox["honest_better"]["lede"].replace(
        "Sandbox HTTP is not G14.",
        "Sandbox HTTP is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_sandbox)
    lede_planes = copy.deepcopy(load_catalog())
    lede_planes["honest_better"]["lede"] = lede_planes["honest_better"]["lede"].replace(
        "A 10/10 of industry, client, and twin planes is not launch.",
        "Planes are recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_planes)
    lede_rails = copy.deepcopy(load_catalog())
    lede_rails["honest_better"]["lede"] = lede_rails["honest_better"]["lede"].replace(
        "A 10/10 of the write rail, proof day, and bake-off is not launch.",
        "Rails are recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_rails)
    lede_roster = copy.deepcopy(load_catalog())
    lede_roster["honest_better"]["lede"] = lede_roster["honest_better"]["lede"].replace(
        "A polished Microsoft roster is not a wired firm.",
        "A polished roster is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_roster)
    lede_flags = copy.deepcopy(load_catalog())
    lede_flags["honest_better"]["lede"] = lede_flags["honest_better"]["lede"].replace(
        "An identify flag strip is not admit.",
        "A flag strip is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_flags)
    lede_craft = copy.deepcopy(load_catalog())
    lede_craft["honest_better"]["lede"] = lede_craft["honest_better"]["lede"].replace(
        "A 10/10 of quality, content, format, and graphics is not launch.",
        "Craft is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_craft)
    lede_look = copy.deepcopy(load_catalog())
    lede_look["honest_better"]["lede"] = lede_look["honest_better"]["lede"].replace(
        "A 10/10 look is not production.",
        "A look is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_look)
    lede_graphic = copy.deepcopy(load_catalog())
    lede_graphic["honest_better"]["lede"] = lede_graphic["honest_better"]["lede"].replace(
        "A polished graphic is not launch.",
        "A graphic is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(lede_graphic)
    site = copy.deepcopy(load_catalog())
    site["honest_better"]["site"] = "Better board. A much better build and business is not launch."
    with pytest.raises(IntegrityError):
        validate_honest_better(site)
    site_route = copy.deepcopy(load_catalog())
    site_route["honest_better"]["site"] = site_route["honest_better"]["site"].replace(
        "Not a /better route.",
        "A /better route.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_route)
    site_glance = copy.deepcopy(load_catalog())
    site_glance["honest_better"]["site"] = site_glance["honest_better"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the better board.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_glance)
    site_make = copy.deepcopy(load_catalog())
    site_make["honest_better"]["site"] = site_make["honest_better"]["site"].replace(
        "Making better is not launch.",
        "Better is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_make)
    site_please = copy.deepcopy(load_catalog())
    site_please["honest_better"]["site"] = site_please["honest_better"]["site"].replace(
        "Please make better is not launch.",
        "Better is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_please)
    site_twin = copy.deepcopy(load_catalog())
    site_twin["honest_better"]["site"] = site_twin["honest_better"]["site"].replace(
        "Twin HTTP 200 is not launch.",
        "Twin HTTP is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_twin)
    site_sandbox = copy.deepcopy(load_catalog())
    site_sandbox["honest_better"]["site"] = site_sandbox["honest_better"]["site"].replace(
        "Sandbox HTTP is not G14.",
        "Sandbox HTTP is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_sandbox)
    site_planes = copy.deepcopy(load_catalog())
    site_planes["honest_better"]["site"] = site_planes["honest_better"]["site"].replace(
        "A 10/10 of industry, client, and twin planes is not launch.",
        "Planes are recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_planes)
    site_vertical = copy.deepcopy(load_catalog())
    site_vertical["honest_better"]["site"] = site_vertical["honest_better"]["site"].replace(
        "A named vertical is not a SKU.",
        "A named vertical is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_vertical)
    site_assigned = copy.deepcopy(load_catalog())
    site_assigned["honest_better"]["site"] = site_assigned["honest_better"]["site"].replace(
        "The Institute twin is not the assigned client sandbox.",
        "The Institute twin is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_assigned)
    site_rails = copy.deepcopy(load_catalog())
    site_rails["honest_better"]["site"] = site_rails["honest_better"]["site"].replace(
        "A 10/10 of the write rail, proof day, and bake-off is not launch.",
        "Rails are recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_rails)
    site_roster = copy.deepcopy(load_catalog())
    site_roster["honest_better"]["site"] = site_roster["honest_better"]["site"].replace(
        "A polished Microsoft roster is not a wired firm.",
        "A polished roster is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_roster)
    site_flags = copy.deepcopy(load_catalog())
    site_flags["honest_better"]["site"] = site_flags["honest_better"]["site"].replace(
        "An identify flag strip is not admit.",
        "A flag strip is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_flags)
    site_craft = copy.deepcopy(load_catalog())
    site_craft["honest_better"]["site"] = site_craft["honest_better"]["site"].replace(
        "A 10/10 of quality, content, format, and graphics is not launch.",
        "Craft is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_craft)
    site_look = copy.deepcopy(load_catalog())
    site_look["honest_better"]["site"] = site_look["honest_better"]["site"].replace(
        "A 10/10 look is not production.",
        "A look is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_look)
    site_graphic = copy.deepcopy(load_catalog())
    site_graphic["honest_better"]["site"] = site_graphic["honest_better"]["site"].replace(
        "A polished graphic is not launch.",
        "A graphic is recorded.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_better(site_graphic)
    complements = copy.deepcopy(load_catalog())
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_better(complements)
    actor = copy.deepcopy(load_catalog())
    actor["honest_better"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_better(actor)
    cannot = copy.deepcopy(load_catalog())
    cannot["honest_better"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_better(cannot)
    owner = copy.deepcopy(load_catalog())
    owner["plane_interface"]["gaps"]["owner_only_open"] = [
        item
        for item in owner["plane_interface"]["gaps"]["owner_only_open"]
        if "seat B click" not in item
    ]
    with pytest.raises(IntegrityError):
        validate_honest_better(owner)


def test_run_better_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_better_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_better_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_better.validate_honest_better", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest better"):
        run_better_certification(short)
