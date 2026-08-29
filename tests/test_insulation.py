from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.ip import insulation_markdown, public_insulation
from ainav.packs import book_service
from ainav.provision import provision_l1, provision_l1_padm


def test_insulation_is_hygiene_not_a_patent():
    body = public_insulation()
    assert body["kind"] == "ainav.ip.insulation.v1"
    assert body["sku"] is False
    assert body["patent_claimed"] is False
    assert body["uncopyable"] is False
    assert body["g12_open"] is True
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert "independen" in body["thesis"].lower()
    assert "not a patent" in body["thesis"].lower()
    assert "independence" in (body.get("equation") or "").lower()
    assert {item["id"] for item in body["layers"]} >= {
        "independence",
        "job_c",
        "fail_closed",
        "gold",
        "catalog_law",
        "umbrella",
    }
    assert "last" in (body.get("why_ultimate_plane") or "").lower()
    assert any("job_c" in item.lower() for item in body["what_the_build_pins"])
    md = insulation_markdown()
    assert "not a patent" in md.lower()
    assert "not uncopyable" in md.lower()
    assert "microsoft" in md.lower()
    assert "ultimate control plane" in md.lower()


def test_independence_desk_and_ip_keep_are_not_skus():
    local = provision_l1("independence-map")
    pack = local.attach_industry("industry.independence")
    assert pack["sku"] is False
    assert pack["included_in_sku"] is True
    keep = provision_l1_padm("ip-keep")
    ip_keep = keep.attach_industry("industry.ip_keep")
    assert ip_keep["requires_sku"] == "P-ADM"
    assert ip_keep["sku"] is False
    booked = book_service("ffs.ip_hygiene", skus=("L1",))
    assert booked["billed"] is True
    assert booked["sku"] is None


def test_insulation_validators_refuse_fiction():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    del missing["ip"]["insulation"]
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(missing)
    assert exc.value.reason_code == "CATALOG_IP"
    sku = copy.deepcopy(cat)
    sku["ip"]["insulation"]["sku"] = True
    with pytest.raises(IntegrityError) as sku_exc:
        validate_catalog(sku)
    assert sku_exc.value.reason_code == "CATALOG_SKU"
    patent = copy.deepcopy(cat)
    patent["ip"]["insulation"]["patent_claimed"] = True
    with pytest.raises(IntegrityError) as pat:
        validate_catalog(patent)
    assert pat.value.reason_code == "IP_CLAIM"
    copyable = copy.deepcopy(cat)
    copyable["ip"]["insulation"]["uncopyable"] = True
    with pytest.raises(IntegrityError) as un:
        validate_catalog(copyable)
    assert un.value.reason_code == "IP_CLAIM"
    thesis = copy.deepcopy(cat)
    thesis["ip"]["insulation"]["thesis"] = "A lockfile with no independence and no patent sentence."
    with pytest.raises(IntegrityError):
        validate_catalog(thesis)
    equation = copy.deepcopy(cat)
    equation["equations"]["insulation"] = "something else"
    with pytest.raises(IntegrityError):
        validate_catalog(equation)
    icp = copy.deepcopy(cat)
    icp["icp"]["independent_of_microsoft"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(icp)
    refuse = copy.deepcopy(cat)
    refuse["ip"]["insulation"]["refuse"] = ["AINav is a Microsoft product"]
    with pytest.raises(IntegrityError):
        validate_catalog(refuse)


def test_institute_ip_is_catalog_honest():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'id="ip"' in html
    assert "ip.json" in js
    body = public_insulation()
    on_disk = json.loads(Path("institute/ip.json").read_text(encoding="utf-8"))
    assert on_disk == body
