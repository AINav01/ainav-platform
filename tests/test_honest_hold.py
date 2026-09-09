from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_HOLD_FACT_IDS,
    HONEST_HOLD_SECRET_NAMES,
    load_catalog,
    validate_catalog,
)
from ainav.honest_hold import (
    public_review,
    run_hold_certification,
    validate_honest_hold,
)


def test_hold_review_is_not_a_live_pin():
    body = public_review()
    assert body["kind"] == "ainav.honest.hold.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["fourth_sku"] is False
    assert body["is_connection"] is False
    assert body["is_complement"] is False
    assert body["is_job_c"] is False
    assert body["is_seat"] is False
    assert body["vault_as_live_pin"] is False
    assert body["names_as_wired"] is False
    assert body["secret_in_catalog"] is False
    assert body["sentinel_as_admit"] is False
    assert body["hold_as_seated"] is False
    assert body["created"] is False
    assert body["certified"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["considered"] is True
    assert body["recorded"] is True
    assert body["honest"] is True
    assert body["href"] == "#missing"
    assert "a vault hold is not live_pin_ok" in body["lede"].lower()
    assert "honest hold" in body["note"].lower()
    assert "sentinel is not the admit plane" in body["note"].lower()
    assert [item["id"] for item in body["facts"]] == list(HONEST_HOLD_FACT_IDS)
    assert list(body["secret_names"]) == list(HONEST_HOLD_SECRET_NAMES)
    assert "Treat a vault hold as LIVE_PIN_OK." in body["this_agent_cannot"]
    assert "Put secret values in the catalog." in body["this_agent_cannot"]
    probes = body["probes"]
    assert probes["complements"] == 8
    assert probes["vault_as_live_pin"] is False
    assert probes["launch"] is False
    on_disk = json.loads(Path("institute/hold.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_run_hold_certification_holds_launch():
    probes = run_hold_certification()
    assert probes["kind"] == "ainav.honest.hold.v1"
    assert probes["considered"] is True
    assert probes["recorded"] is True
    assert probes["vault_as_live_pin"] is False
    assert probes["names_as_wired"] is False
    assert probes["secret_in_catalog"] is False
    assert probes["sentinel_as_admit"] is False
    assert probes["hold_as_seated"] is False
    assert probes["complements"] == 8
    assert probes["created"] is False
    assert probes["certified"] is False
    assert probes["live"] is False
    assert probes["live_pin_ok"] is False
    assert probes["launch"] is False
    assert probes["institute_publish"] == "launch_not_ready"


def test_honest_hold_fail_closed():
    hole = copy.deepcopy(load_catalog())
    hole["honest_hold"]["vault_as_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(hole)
    wired = copy.deepcopy(load_catalog())
    wired["honest_hold"]["names_as_wired"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(wired)
    secret = copy.deepcopy(load_catalog())
    secret["honest_hold"]["secret_in_catalog"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(secret)
    sentinel = copy.deepcopy(load_catalog())
    sentinel["honest_hold"]["sentinel_as_admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(sentinel)
    seated = copy.deepcopy(load_catalog())
    seated["honest_hold"]["hold_as_seated"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(seated)
    href = copy.deepcopy(load_catalog())
    href["honest_hold"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_honest_hold(href)
    live = copy.deepcopy(load_catalog())
    live["programs"]["website"]["honest_hold_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)


def test_validate_honest_hold_more_fail_closed():
    missing = copy.deepcopy(load_catalog())
    missing.pop("honest_hold")
    with pytest.raises(IntegrityError):
        validate_honest_hold(missing)
    kind = copy.deepcopy(load_catalog())
    kind["honest_hold"]["kind"] = "ainav.honest.hold.v0"
    with pytest.raises(IntegrityError):
        validate_honest_hold(kind)
    for flag in (
        "sku",
        "certified",
        "live",
        "live_pin_ok",
        "launch",
        "created",
        "claimed",
        "values_in_tree",
        "ids_in_plane",
        "from_this_plane",
    ):
        claimed = copy.deepcopy(load_catalog())
        claimed["honest_hold"][flag] = True
        with pytest.raises(IntegrityError):
            validate_honest_hold(claimed)
    honest = copy.deepcopy(load_catalog())
    honest["honest_hold"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_hold(honest)
    considered = copy.deepcopy(load_catalog())
    considered["honest_hold"]["considered"] = False
    with pytest.raises(IntegrityError):
        validate_honest_hold(considered)
    recorded = copy.deepcopy(load_catalog())
    recorded["honest_hold"]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_hold(recorded)
    for key in (
        "vault_as_live_pin",
        "names_as_wired",
        "secret_in_catalog",
        "sentinel_as_admit",
        "hold_as_seated",
    ):
        missing_flag = copy.deepcopy(load_catalog())
        missing_flag["honest_hold"].pop(key)
        with pytest.raises(IntegrityError):
            validate_honest_hold(missing_flag)
    facts_len = copy.deepcopy(load_catalog())
    facts_len["honest_hold"]["facts"] = []
    with pytest.raises(IntegrityError):
        validate_honest_hold(facts_len)
    not_objects = copy.deepcopy(load_catalog())
    not_objects["honest_hold"]["facts"] = list(HONEST_HOLD_FACT_IDS)
    with pytest.raises(IntegrityError):
        validate_honest_hold(not_objects)
    facts_ids = copy.deepcopy(load_catalog())
    facts_ids["honest_hold"]["facts"][0]["id"] = "probe"
    with pytest.raises(IntegrityError):
        validate_honest_hold(facts_ids)
    fact_sku = copy.deepcopy(load_catalog())
    fact_sku["honest_hold"]["facts"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(fact_sku)
    fact_admit = copy.deepcopy(load_catalog())
    fact_admit["honest_hold"]["facts"][1]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(fact_admit)
    fact_live = copy.deepcopy(load_catalog())
    fact_live["honest_hold"]["facts"][2]["live"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(fact_live)
    refuse_ids = copy.deepcopy(load_catalog())
    refuse_ids["honest_hold"]["refuse"][0]["id"] = "hold_as_product"
    with pytest.raises(IntegrityError):
        validate_honest_hold(refuse_ids)
    refuse_text = copy.deepcopy(load_catalog())
    refuse_text["honest_hold"]["refuse"][0]["refuse_text"] = "No."
    with pytest.raises(IntegrityError):
        validate_honest_hold(refuse_text)
    refuse_href = copy.deepcopy(load_catalog())
    refuse_href["honest_hold"]["refuse"][0]["href"] = "#whole"
    with pytest.raises(IntegrityError):
        validate_honest_hold(refuse_href)
    leftover = copy.deepcopy(load_catalog())
    leftover["honest_hold"]["refuse"][0]["claimed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_hold(leftover)
    leftover_live = copy.deepcopy(load_catalog())
    leftover_live["honest_hold"]["refuse"][0]["live"] = False
    with pytest.raises(IntegrityError):
        validate_honest_hold(leftover_live)
    note = copy.deepcopy(load_catalog())
    note["honest_hold"]["note"] = "A vault hold is not LIVE_PIN_OK. Sentinel is not the admit plane."
    with pytest.raises(IntegrityError):
        validate_honest_hold(note)
    note_close = copy.deepcopy(load_catalog())
    note_close["honest_hold"]["note"] = "Honest hold. Sentinel is not the admit plane."
    with pytest.raises(IntegrityError):
        validate_honest_hold(note_close)
    note_sentinel = copy.deepcopy(load_catalog())
    note_sentinel["honest_hold"]["note"] = "Honest hold. A vault hold is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_hold(note_sentinel)
    lede = copy.deepcopy(load_catalog())
    lede["honest_hold"]["lede"] = "Complements stay eight."
    with pytest.raises(IntegrityError):
        validate_honest_hold(lede)
    lede_secret = copy.deepcopy(load_catalog())
    lede_secret["honest_hold"]["lede"] = "A vault hold is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_hold(lede_secret)
    site = copy.deepcopy(load_catalog())
    site["honest_hold"]["site"] = "Hold board. A vault hold is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_honest_hold(site)
    site_name = copy.deepcopy(load_catalog())
    site_name["honest_hold"]["site"] = site_name["honest_hold"]["site"].replace(
        "Honest hold",
        "Hold board",
    )
    with pytest.raises(IntegrityError):
        validate_honest_hold(site_name)
    site_route = copy.deepcopy(load_catalog())
    site_route["honest_hold"]["site"] = site_route["honest_hold"]["site"].replace(
        "Not a /hold route.",
        "A /hold route.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_hold(site_route)
    site_glance = copy.deepcopy(load_catalog())
    site_glance["honest_hold"]["site"] = site_glance["honest_hold"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the hold board.",
    )
    with pytest.raises(IntegrityError):
        validate_honest_hold(site_glance)
    complements = copy.deepcopy(load_catalog())
    complements["connections"]["complements"] = complements["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        validate_honest_hold(complements)
    actor = copy.deepcopy(load_catalog())
    actor["honest_hold"]["owner_playbook"]["actor"] = "Cursor"
    with pytest.raises(IntegrityError):
        validate_honest_hold(actor)
    cannot = copy.deepcopy(load_catalog())
    cannot["honest_hold"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_hold(cannot)
    wired_svc = copy.deepcopy(load_catalog())
    wired_svc["honest_hold"]["services"]["claimed_as_wired"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(wired_svc)
    vault = copy.deepcopy(load_catalog())
    vault["honest_hold"]["services"]["vault"]["values_in_tree"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(vault)
    sentinel_svc = copy.deepcopy(load_catalog())
    sentinel_svc["honest_hold"]["services"]["sentinel"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(sentinel_svc)
    plane = copy.deepcopy(load_catalog())
    plane["honest_hold"]["services"]["sentinel"]["from_this_plane"] = True
    with pytest.raises(IntegrityError):
        validate_honest_hold(plane)
    names = copy.deepcopy(load_catalog())
    names["honest_hold"]["secret_names"] = list(HONEST_HOLD_SECRET_NAMES)[:-1]
    with pytest.raises(IntegrityError):
        validate_honest_hold(names)
    vault_name = copy.deepcopy(load_catalog())
    vault_name["honest_hold"]["vault_name"] = "other"
    with pytest.raises(IntegrityError):
        validate_honest_hold(vault_name)
    law = copy.deepcopy(load_catalog())
    law["honest_hold"]["law_name"] = "other"
    with pytest.raises(IntegrityError):
        validate_honest_hold(law)
    owner = copy.deepcopy(load_catalog())
    owner["plane_interface"]["gaps"]["owner_only_open"] = [
        item
        for item in owner["plane_interface"]["gaps"]["owner_only_open"]
        if "seat B click" not in item
    ]
    with pytest.raises(IntegrityError):
        validate_honest_hold(owner)


def test_run_hold_certification_fail_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": True, "reason": "published"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_hold_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "other"},
    )
    with pytest.raises(IntegrityError, match="institute publish stays launch_not_ready"):
        run_hold_certification()
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {"ok": False, "reason": "launch_not_ready"},
    )
    monkeypatch.setattr("ainav.honest_hold.validate_honest_hold", lambda _catalog: None)
    short = copy.deepcopy(load_catalog())
    short["connections"]["complements"] = short["connections"]["complements"][:7]
    with pytest.raises(IntegrityError, match="complements stay eight after honest hold"):
        run_hold_certification(short)
