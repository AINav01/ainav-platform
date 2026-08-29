from __future__ import annotations

import copy

import pytest

from agent_gov import default_lockfile, load_lockfile
from agent_gov.errors import IntegrityError, LockfileError
from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import IPError
from ainav.ip import (
    insulation_markdown,
    notice,
    public_insulation,
    refuse_claim,
    refuse_lockfile_rebrand,
    screen_pack_label,
)
from ainav.mothership import MasterMothership


def test_notice_is_ainav_owned_and_g12_open():
    text = notice()
    assert "AINav, Inc." in text
    assert "G12" in text
    assert "Microsoft" in text
    assert "not a signed opinion" in text.lower() or "not a signed" in text.lower()
    assert "not uncopyable" in text.lower()
    ins = public_insulation()
    assert ins["sku"] is False
    assert ins["patent_claimed"] is False
    assert "not a patent" in insulation_markdown().lower()


def test_microsoft_copilot_cannot_be_a_sku():
    with pytest.raises(IPError) as exc:
        screen_pack_label("COPILOT_PACK")
    assert exc.value.reason_code == "MICROSOFT_PRODUCT"
    with pytest.raises(IPError) as exc2:
        screen_pack_label("PURVIEW_PLANE")
    assert exc2.value.reason_code == "MICROSOFT_PRODUCT"


def test_competitor_aliases_cannot_be_provisioned():
    with pytest.raises(IPError) as exc:
        MasterMothership().provision("acme", packs=("L1", "SERVICENOW"))
    assert exc.value.reason_code == "COMPETITOR_SKU"
    with pytest.raises(IPError):
        screen_pack_label("agentforce")
    screen_pack_label("L1")


def test_forbidden_claims_and_rebrand():
    with pytest.raises(IPError) as exc:
        refuse_claim("AINav is a Microsoft product")
    assert exc.value.reason_code == "IP_CLAIM"
    with pytest.raises(IPError):
        refuse_claim("powered by Copilot")
    with pytest.raises(IPError):
        refuse_claim("uncopyable")
    with pytest.raises(IPError):
        refuse_claim("patent granted")
    with pytest.raises(IPError):
        refuse_claim("Microsoft cannot legally copy")
    with pytest.raises(LockfileError) as lock:
        refuse_lockfile_rebrand("copilot")
    assert lock.value.reason_code == "LOCKFILE_PRODUCT"
    with pytest.raises(LockfileError):
        load_lockfile({**default_lockfile().to_canonical(), "product": "copilot"})


def test_catalog_cannot_close_g12_or_rebrand():
    cat = load_catalog()
    closed = copy.deepcopy(cat)
    closed["ip"]["g12_open"] = False
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(closed)
    assert exc.value.reason_code == "GAP_OPEN"
    rebrand = copy.deepcopy(cat)
    rebrand["entity"]["product"] = "Microsoft Copilot Control Plane"
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(rebrand)
    assert exc2.value.reason_code == "IP_REBRAND"


def test_allowed_skus_are_not_competitor_aliases():
    cat = load_catalog()
    aliases = {a.lower() for a in cat["ip"]["competitor_aliases"]}
    assert not {"l1", "p-adm", "u-dual"} & aliases
    assert cat["ip"]["no_patent_claim_in_this_tree"] is True
    refuse_lockfile_rebrand("job_c")
    missing = copy.deepcopy(cat)
    del missing["ip"]
    with pytest.raises(IntegrityError) as no_ip:
        validate_catalog(missing)
    assert no_ip.value.reason_code == "CATALOG_IP"
    owner = copy.deepcopy(cat)
    owner["ip"]["owner"] = "Not AINav"
    with pytest.raises(IntegrityError) as own:
        validate_catalog(owner)
    assert own.value.reason_code == "IP_REBRAND"
    patent = copy.deepcopy(cat)
    patent["ip"]["no_patent_claim_in_this_tree"] = False
    with pytest.raises(IntegrityError) as pat:
        validate_catalog(patent)
    assert pat.value.reason_code == "IP_CLAIM"
    collide = copy.deepcopy(cat)
    collide["ip"]["competitor_aliases"] = ["L1"]
    with pytest.raises(IntegrityError) as hit:
        validate_catalog(collide)
    assert hit.value.reason_code == "CATALOG_SKU"
