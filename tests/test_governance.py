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
    joined = " ".join(fail["separate_from"]).lower()
    assert "client ai" in joined
    assert "copilot" in joined
    assert "agent 365" in joined
    ids = {item["id"] for item in body["maps"]}
    assert {"nist.ai_rmf", "eu.ai_act", "iso.42001", "sox.icfr"} <= ids
    assert all(item["claimed"] is False for item in body["maps"])
    assert any(item["id"] == "unauthorized_sor" for item in body["risks"])
    md = governance_markdown()
    assert "separate failsafe" in md.lower() or "separate from client" in md.lower()
    assert "certified: false" in md.lower()


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


def test_docs_governance_matches_generator():
    on_disk = Path("docs/GOVERNANCE.md").read_text(encoding="utf-8")
    assert on_disk == governance_markdown()
