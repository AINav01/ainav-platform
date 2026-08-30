from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.institute_status import public_status
from ainav.microsoft.connections import COMPLEMENT_IDS
from ainav.microsoft.dns import catalog_edge, score_e7_on_cloudflare
from ainav.review import review_model


def _mail_dns(*, teams_sip: bool = False) -> dict:
    return {
        "cloudflare_nameservers": True,
        "microsoft_365": {
            "mx_outlook": True,
            "spf_outlook": True,
            "entra_txt": True,
            "autodiscover": ["autodiscover.outlook.com"],
            "enterpriseenrollment": ["enterpriseenrollment-s.manage.microsoft.com"],
            "enterpriseregistration": ["enterpriseregistration.windows.net"],
            "dkim": True,
            "dmarc": ["v=DMARC1; p=none;"],
            "teams_sip": teams_sip,
        },
    }


def test_catalog_edge_is_not_a_sku_or_full():
    edge = catalog_edge()
    assert edge["id"] == "cloudflare.dns"
    assert edge["role"] == "dns_edge"
    assert edge["sku"] is False
    assert edge["connection"] is False
    assert edge["complement"] is False
    assert edge["live"] is False
    assert edge["live_pin_ok"] is False
    assert edge["is_admit_plane"] is False
    assert edge["full"] is False
    assert "sip" in " ".join(edge["missing"]).lower()
    assert "not the product" in edge["note"].lower()
    assert edge["dashboard_url"] == "https://dash.cloudflare.com"


def test_live_scoreboard_mail_on_cloudflare_is_not_full():
    scored = score_e7_on_cloudflare(_mail_dns(teams_sip=False))
    assert scored["mail_on_cloudflare"] is True
    assert scored["full"] is False
    assert scored["sku"] is False
    assert scored["live_pin_ok"] is False
    assert "teams_sip" in scored["missing"]


def test_cannot_claim_full_while_teams_sip_is_missing():
    scored = score_e7_on_cloudflare(_mail_dns(teams_sip=False))
    assert scored["checks"]["teams_sip"] is False
    assert scored["full"] is False


def test_full_only_when_every_check_is_present():
    scored = score_e7_on_cloudflare(_mail_dns(teams_sip=True))
    assert scored["full"] is True
    assert scored["missing"] == []


def test_catalog_rejects_full_or_sku_edge():
    cat = copy.deepcopy(load_catalog())
    cat["microsoft_stack"]["edge"]["full"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "CATALOG_EDGE"
    sku = copy.deepcopy(load_catalog())
    sku["microsoft_stack"]["edge"]["sku"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(sku)
    assert exc2.value.reason_code == "CATALOG_EDGE"


def test_public_status_keeps_cloudflare_off_the_write_path():
    body = public_status()
    path_ids = [item["id"] for item in body["fabric"]["path"]]
    assert "cloudflare.dns" not in path_ids
    assert [item["id"] for item in body["complements"]] == list(COMPLEMENT_IDS)
    edge = body["e7_cloudflare"]
    assert edge["id"] == "cloudflare.dns"
    assert edge["full"] is False
    assert edge["complement"] is False
    assert edge["live_pin_ok"] is False


def test_review_model_carries_catalog_edge():
    model = review_model()
    assert model["e7_cloudflare"]["full"] is False
    assert model["e7_cloudflare"]["sku"] is False
    assert model["live_pin_ok"] is False
    assert model["launch_ready"] is False


def test_institute_paints_e7_cloudflare_strip():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    assert 'id="e7-cloudflare"' in html
    assert 'id="e7-cloudflare-already"' in html
    assert 'id="e7-cloudflare-missing"' in html
    assert "dash.cloudflare.com" in html
    assert "not a ninth complement" in html.lower()
    assert "e7_cloudflare" in js
    assert "refuse to paint a fiction scoreboard" in js
    assert "#e7-cloudflare" in css
