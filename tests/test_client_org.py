from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.client_org import client_org_markdown, public_client_org, REQUIRED_CLIENT_DEPTS
from ainav.packs import book_service
from ainav.provision import provision_l1, provision_l1_padm


def test_client_org_is_a_template_not_a_named_customer():
    body = public_client_org()
    assert body["kind"] == "ainav.client_org.v1"
    assert body["sku"] is False
    assert body["live"] is False
    assert body["named_customers"] == []
    assert body["replaces_org_chart"] is False
    assert body["do_not_invent_department_heads"] is True
    assert [item["id"] for item in body["departments"]] == list(REQUIRED_CLIENT_DEPTS)
    assert all(item["department_ai_is_seat"] is False for item in body["departments"])
    assert all(item["named_head"] is None for item in body["departments"])
    assert body["seats"]["seat_a"]["role"] == "treasury_approver"
    assert body["seats"]["seat_b"]["role"] == "treasury_controller"
    md = client_org_markdown()
    assert "org chart" in md.lower()
    assert "not a seat" in md.lower()


def test_org_desk_and_internal_audit_are_not_skus():
    local = provision_l1("org-map")
    pack = local.attach_industry("industry.org")
    assert pack["sku"] is False
    assert pack["included_in_sku"] is True
    keep = provision_l1_padm("audit-keep")
    audit = keep.attach_industry("industry.internal_audit")
    assert audit["requires_sku"] == "P-ADM"
    assert audit["sku"] is False
    booked = book_service("ffs.org_workshop", skus=("L1",))
    assert booked["billed"] is True
    assert booked["sku"] is None


def test_client_org_validators_refuse_fiction():
    cat = copy.deepcopy(load_catalog())
    cat["client_org"]["named_customers"] = ["Invented Corp"]
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["client_org"]["replaces_org_chart"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["client_org"]["departments"][0]["department_ai_is_seat"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["client_org"]["departments"][0]["named_head"] = "Jane Doe"
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["equations"]["org"] = "something else"
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
    cat = copy.deepcopy(load_catalog())
    cat["icp"]["do_not_invent_department_heads"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_institute_client_org_is_catalog_honest():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'id="client-org"' in html
    assert "client-org.json" in js
    body = public_client_org()
    on_disk = Path("institute/client-org.json").read_text(encoding="utf-8")
    import json

    assert json.loads(on_disk) == body
