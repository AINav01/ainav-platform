from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.governance import governance_markdown, public_governance
from ainav.packs import book_service
from ainav.provision import provision_l1, provision_l1_padm


def test_governance_is_a_failsafe_not_a_certificate():
    body = public_governance()
    assert body["kind"] == "ainav.governance.v1"
    assert body["sku"] is False
    assert body["certified"] is False
    assert body["replaces_counsel"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    fail = body["failsafe"]
    assert fail["client_utilizes_ai"] is True
    assert fail["human_control"] is True
    assert fail["ainav_is_client_ai"] is False
    joined = " ".join(fail["separate_from"]).lower()
    assert "client ai" in joined
    assert "copilot" in joined
    assert "agent 365" in joined
    ids = {item["id"] for item in body["maps"]}
    assert {"nist.ai_rmf", "eu.ai_act", "iso.42001", "sox.icfr"} <= ids
    assert all(item["claimed"] is False for item in body["maps"])
    assert any(item["id"] == "unauthorized_sor" for item in body["risks"])
    md = governance_markdown()
    assert "client utilizes ai" in md.lower()
    assert "human control" in md.lower() or "humans control" in md.lower()
    assert "certified: false" in md.lower()
    assert body["cascade"]["counterparties_utilize_ai"] is True
    assert body["cascade"]["client_institutes_ainav"] is True
    assert body["cascade"]["do_not_invent_names"] is True
    assert "sor" in body["records"]["first"]["what"].lower()
    assert "decisionrecord" in body["records"]["second"]["what"].lower().replace(" ", "")
    assert "first record" in md.lower()
    assert "second record" in md.lower()
    assert "cascade" in md.lower()
    assert body["must_have"]["mandated"] is False
    assert body["plane"]["sits_over_client_ai"] is True
    assert body["plane"]["is_the_clients_ai"] is False
    assert "fail-closed" in body["plane"]["off_switch"]["does"].lower()
    assert "compensating" in body["plane"]["rollback"]["does"].lower()
    assert "off switch" in md.lower()
    assert "must-have" in md.lower()


def test_governance_pack_is_included_l1_seating():
    local = provision_l1("acme")
    pack = local.attach_industry("industry.governance")
    assert pack["requires_sku"] == "L1"
    assert pack["sku"] is False
    assert pack["included_in_sku"] is True
    assert "bc.general_journal.post" in local.allowed_actions
    lib = local.attach_library("lib.l1.failsafe")
    assert lib["sku"] is False
    booked = book_service("ffs.governance_workshop", skus=("L1",))
    assert booked["billed"] is True
    assert booked["sku"] is None


def test_oversight_keep_requires_padm():
    local = provision_l1("acme")
    with pytest.raises(Exception) as exc:
        local.attach_industry("industry.oversight")
    assert exc.value.reason_code == "PACK_SCOPE"
    keep = provision_l1_padm("acme")
    pack = keep.attach_industry("industry.oversight")
    assert pack["requires_sku"] == "P-ADM"
    assert pack["attach_usd"]["min"] == 5000
    keep.attach_library("lib.padm.governance")
    assert "lib.padm.governance" in keep.libraries


def test_cannot_claim_eu_ai_act_certified():
    cat = copy.deepcopy(load_catalog())
    cat["governance"]["certified"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["governance"]["maps"][0]["claimed"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_governance_validator_refuses_sku_and_seat_collapse():
    cases = [
        {"sku": True},
        {"replaces_counsel": True},
        {"live": True},
        {"thesis": "A map of instruments with no humans."},
        {"failsafe": {"separate_from": ["Microsoft 365 Copilot"], "does": "x", "does_not": []}},
        {"maps": [{"id": "nist.ai_rmf", "name": "NIST", "scope": "US", "maps_to": "x", "claimed": False}]},
        {"refuse": ["LIVE_PIN_OK from a governance map"]},
        {"risks": []},
        {"kind": None},
    ]
    for patch in cases:
        cat = copy.deepcopy(load_catalog())
        if patch.get("kind") is None and "kind" in patch:
            cat.pop("governance", None)
        else:
            cat["governance"].update(patch)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)


def test_cascade_desk_and_second_record_are_not_skus():
    local = provision_l1("acme")
    pack = local.attach_industry("industry.cascade")
    assert pack["requires_sku"] == "L1"
    assert pack["sku"] is False
    assert pack["attach_usd"]["min"] == 6000
    assert "bc.general_journal.post" in local.allowed_actions
    keep = provision_l1_padm("acme")
    second = keep.attach_industry("industry.second_record")
    assert second["requires_sku"] == "P-ADM"
    assert second["sku"] is False
    booked = book_service("ffs.institute_failsafe", skus=("L1",))
    assert booked["billed"] is True
    assert booked["sku"] is None
    plane = local.attach_industry("industry.control_plane")
    assert plane["sku"] is False
    assert plane["included_in_sku"] is True
    switch = local.attach_industry("industry.off_switch")
    assert switch["attach_usd"]["min"] == 6000
    local.attach_industry("industry.rollback")
    keep = provision_l1_padm("board-keep")
    board = keep.attach_industry("industry.board")
    assert board["requires_sku"] == "P-ADM"
    assert board["sku"] is False
    briefed = book_service("ffs.board_briefing", skus=("L1",))
    assert briefed["billed"] is True


def test_cascade_and_records_validators_refuse_fiction():
    cases = [
        {"cascade": {"counterparties_utilize_ai": False, "client_institutes_ainav": True, "do_not_invent_names": True, "buyer_is_the_client": True}},
        {"cascade": {"counterparties_utilize_ai": True, "client_institutes_ainav": False, "do_not_invent_names": True, "buyer_is_the_client": True}},
        {"cascade": {"counterparties_utilize_ai": True, "client_institutes_ainav": True, "do_not_invent_names": False, "buyer_is_the_client": True}},
        {"records": {"sku": True, "certified": False, "first": {"what": "SoR write"}, "second": {"what": "DecisionRecord"}}},
        {"records": {"sku": False, "certified": True, "first": {"what": "SoR write"}, "second": {"what": "DecisionRecord"}}},
        {"records": {"sku": False, "certified": False, "first": {"what": "a memo"}, "second": {"what": "DecisionRecord"}}},
        {"records": {"sku": False, "certified": False, "first": {"what": "SoR write"}, "second": {"what": "a memo"}}},
    ]
    for patch in cases:
        cat = copy.deepcopy(load_catalog())
        cat["governance"].update(patch)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["equations"]["cascade"] = "something else"
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["icp"]["counterparties_utilize_ai"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["icp"]["do_not_invent_counterparty_names"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["icp"]["institutes_ainav"] = "no"
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["governance"]["failsafe"]["separate_from"] = [
        item for item in cat["governance"]["failsafe"]["separate_from"] if "counterparty" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["equations"]["umbrella"] = "something else"
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["equations"]["plane"] = "something else"
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["icp"]["sits_over_client_ai"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["governance"]["must_have"]["mandated"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["governance"]["plane"]["is_the_clients_ai"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["governance"]["plane"]["rollback"]["does_not"] = "a memo"
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_docs_governance_matches_generator():
    on_disk = Path("docs/GOVERNANCE.md").read_text(encoding="utf-8")
    assert on_disk == governance_markdown()
