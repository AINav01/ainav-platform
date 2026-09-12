from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_PROTECT_FACT_IDS,
    HONEST_PROTECT_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.honest_protect import (
    public_review,
    run_protect_certification,
    validate_honest_protect,
)


def test_protect_review_is_not_a_patent():
    body = public_review()
    assert body["kind"] == "ainav.honest.protect.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["protect_as_patent"] is False
    assert body["protect_as_uncopyable"] is False
    assert body["client_license_as_assignment"] is False
    assert body["kit_pass_as_source"] is False
    assert body["g12_as_closed"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#ip"
    assert "an ip board is not a patent" in body["lede"].lower()
    assert "honest protect" in body["note"].lower()
    assert "an l1 license is not an assignment of job c" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_PROTECT_FACT_IDS)
    assert "Treat an IP board as a patent." in body["this_agent_cannot"]
    assert "Treat an L1 license as an assignment of Job C." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["protect_as_patent"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/protect.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_protect_certification_holds_launch():
    probes = run_protect_certification()
    assert probes["kind"] == "ainav.honest.protect.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["protect_as_patent"] is False
    assert probes["protect_as_uncopyable"] is False
    assert probes["client_license_as_assignment"] is False
    assert probes["kit_pass_as_source"] is False
    assert probes["g12_as_closed"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_protect_fail_closed():
    hole = copy.deepcopy(load_catalog())
    hole["honest_protect"]["protect_as_patent"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(hole)
    copyable = copy.deepcopy(load_catalog())
    copyable["honest_protect"]["protect_as_uncopyable"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(copyable)
    assign = copy.deepcopy(load_catalog())
    assign["honest_protect"]["client_license_as_assignment"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(assign)
    source = copy.deepcopy(load_catalog())
    source["honest_protect"]["kit_pass_as_source"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(source)
    g12 = copy.deepcopy(load_catalog())
    g12["honest_protect"]["g12_as_closed"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(g12)
    href = copy.deepcopy(load_catalog())
    href["honest_protect"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_protect(href)
    live = copy.deepcopy(load_catalog())
    live["programs"]["website"]["honest_protect_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_protect_more_fail_closed():
    missing = copy.deepcopy(load_catalog())
    missing.pop("honest_protect")
    with pytest.raises(IntegrityError):
        validate_honest_protect(missing)
    kind = copy.deepcopy(load_catalog())
    kind["honest_protect"]["kind"] = "ainav.honest.protect.v0"
    with pytest.raises(IntegrityError):
        validate_honest_protect(kind)
    for flag in (
        "sku",
        "certified",
        "live",
        "live_pin_ok",
        "launch",
        "created",
        "claimed",
    ):
        claimed = copy.deepcopy(load_catalog())
        claimed["honest_protect"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_protect(claimed)
    honest = copy.deepcopy(load_catalog())
    honest["honest_protect"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_protect(honest)
    considered = copy.deepcopy(load_catalog())
    considered["honest_protect"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_protect(considered)
    recorded = copy.deepcopy(load_catalog())
    recorded["honest_protect"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_protect(recorded)
    for key in (
        "protect_as_patent",
        "protect_as_uncopyable",
        "client_license_as_assignment",
        "kit_pass_as_source",
        "g12_as_closed",
    ):
        missing_flag = copy.deepcopy(load_catalog())
        missing_flag["honest_protect"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_protect(missing_flag)
    facts_len = copy.deepcopy(load_catalog())
    facts_len["honest_protect"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_protect(facts_len)
    not_objects = copy.deepcopy(load_catalog())
    not_objects["honest_protect"]["facts"] = list(HONEST_PROTECT_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_protect(not_objects)
    facts_ids = copy.deepcopy(load_catalog())
    facts_ids["honest_protect"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_protect(facts_ids)
    fact_sku = copy.deepcopy(load_catalog())
    fact_sku["honest_protect"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(fact_sku)
    fact_admit = copy.deepcopy(load_catalog())
    fact_admit["honest_protect"]["facts"][1]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(fact_admit)
    fact_live = copy.deepcopy(load_catalog())
    fact_live["honest_protect"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(fact_live)
    refuse_ids = copy.deepcopy(load_catalog())
    refuse_ids["honest_protect"]["refuse"][0]["id"] = "protect_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_protect(refuse_ids)
    refuse_text = copy.deepcopy(load_catalog())
    refuse_text["honest_protect"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_protect(refuse_text)
    refuse_href = copy.deepcopy(load_catalog())
    refuse_href["honest_protect"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_protect(refuse_href)
    leftover = copy.deepcopy(load_catalog())
    leftover["honest_protect"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_protect(leftover)
    leftover_live = copy.deepcopy(load_catalog())
    leftover_live["honest_protect"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_protect(leftover_live)
    note = copy.deepcopy(load_catalog())
    note["honest_protect"]["note"] = "An IP board is not a patent. An L1 license is not an assignment of Job C."
    with pytest.raises(IntegrityError):
        validate_honest_protect(note)
    note_close = copy.deepcopy(load_catalog())
    note_close["honest_protect"]["note"] = "Honest protect. An L1 license is not an assignment of Job C."
    with pytest.raises(IntegrityError):
        validate_honest_protect(note_close)
    note_assign = copy.deepcopy(load_catalog())
    note_assign["honest_protect"]["note"] = "Honest protect. An IP board is not a patent."
    with pytest.raises(IntegrityError):
        validate_honest_protect(note_assign)
    lede = copy.deepcopy(load_catalog())
    lede["honest_protect"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_protect(lede)
    lede_assign = copy.deepcopy(load_catalog())
    lede_assign["honest_protect"]["lede"] = "An IP board is not a patent."
    with pytest.raises(IntegrityError):
        validate_honest_protect(lede_assign)
    site = copy.deepcopy(load_catalog())
    site["honest_protect"]["site"] = "Protect board. An IP board is not a patent."
    with pytest.raises(IntegrityError):
        validate_honest_protect(site)
    site_name = copy.deepcopy(load_catalog())
    site_name["honest_protect"]["site"] = (
        "Protect board. Not a /protect route. First glance stays the write rail."
    )
    with pytest.raises(IntegrityError):
        validate_honest_protect(site_name)
    site_route = copy.deepcopy(load_catalog())
    site_route["honest_protect"]["site"] = (
        "Honest protect. Not a /protect route. Complements stay eight."
    )
    with pytest.raises(IntegrityError):
        validate_honest_protect(site_route)
    site_glance = copy.deepcopy(load_catalog())
    site_glance["honest_protect"]["site"] = (
        "Honest protect. First glance stays the write rail. Complements stay eight."
    )
    with pytest.raises(IntegrityError):
        validate_honest_protect(site_glance)
    complements = copy.deepcopy(load_catalog())
    complements["connections"]["complements"] = []
    with pytest.raises(IntegrityError):
        validate_honest_protect(complements)
    actor = copy.deepcopy(load_catalog())
    actor["honest_protect"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_protect(actor)
    cannot = copy.deepcopy(load_catalog())
    cannot["honest_protect"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_protect(cannot)
    assign_svc = copy.deepcopy(load_catalog())
    assign_svc["honest_protect"]["services"]["claimed_as_assignment"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(assign_svc)
    ms = copy.deepcopy(load_catalog())
    ms["honest_protect"]["services"]["microsoft"]["is_the_product"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(ms)
    client = copy.deepcopy(load_catalog())
    client["honest_protect"]["services"]["client"]["license_is_assignment"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(client)
    counsel = copy.deepcopy(load_catalog())
    counsel["honest_protect"]["services"]["counsel"]["g12_closed"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(counsel)
    layer = copy.deepcopy(load_catalog())
    layer["ip"]["insulation"]["layers"] = [
        item for item in layer["ip"]["insulation"]["layers"] if item.get("id") != "client"
    ]
    with pytest.raises(IntegrityError):
        validate_honest_protect(layer)
    reserved = copy.deepcopy(load_catalog())
    reserved["ip"]["reserved_work"] = [
        item for item in reserved["ip"]["reserved_work"] if "client license is use" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        validate_honest_protect(reserved)
    patent = copy.deepcopy(load_catalog())
    patent["ip"]["insulation"]["patent_claimed"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(patent)
    g12_open = copy.deepcopy(load_catalog())
    g12_open["ip"]["g12_open"] = False
    with pytest.raises(IntegrityError):
        validate_honest_protect(g12_open)
    no_patent = copy.deepcopy(load_catalog())
    no_patent["ip"]["no_patent_claim_in_this_tree"] = False
    with pytest.raises(IntegrityError):
        validate_honest_protect(no_patent)
    uncopyable = copy.deepcopy(load_catalog())
    uncopyable["ip"]["insulation"]["uncopyable"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(uncopyable)
    hire = copy.deepcopy(load_catalog())
    hire["ip"]["client_protect"]["work_for_hire"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(hire)
    seats = copy.deepcopy(load_catalog())
    seats["ip"]["client_protect"]["seats_are_inventors"] = True
    with pytest.raises(IntegrityError):
        validate_honest_protect(seats)


def test_run_protect_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_protect_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_protect_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_protect.validate_honest_protect", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest protect"):
        run_protect_certification(short)
