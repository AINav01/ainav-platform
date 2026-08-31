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


def _mail_dns(*, teams: bool = False) -> dict:
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
            "dmarc": ["v=DMARC1; p=quarantine;"],
            "teams_sip": teams,
            "lyncdiscover": ["webdir.online.lync.com"] if teams else [],
            "sip_srv": ["100 1 443 sipdir.online.lync.com"] if teams else [],
            "federation_srv": ["100 1 5061 sipfed.online.lync.com"] if teams else [],
        },
    }


def test_catalog_rejects_edge_fiction():
    cat = load_catalog()
    gone = copy.deepcopy(cat)
    gone["microsoft_stack"]["edge"] = None
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(gone)
    assert exc.value.reason_code == "CATALOG_EDGE"
    bad_id = copy.deepcopy(cat)
    bad_id["microsoft_stack"]["edge"]["id"] = "invented.dns"
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(bad_id)
    assert exc2.value.reason_code == "CATALOG_EDGE"
    product = copy.deepcopy(cat)
    product["microsoft_stack"]["edge"]["product"] = "Squarespace"
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(product)
    assert exc3.value.reason_code == "CATALOG_EDGE"
    role = copy.deepcopy(cat)
    role["microsoft_stack"]["edge"]["role"] = "admit"
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(role)
    assert exc4.value.reason_code == "CATALOG_EDGE"
    dash = copy.deepcopy(cat)
    dash["microsoft_stack"]["edge"]["dashboard_url"] = "https://example.test"
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(dash)
    assert exc5.value.reason_code == "CATALOG_EDGE"
    apex = copy.deepcopy(cat)
    apex["microsoft_stack"]["edge"]["apex"] = "example.test"
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(apex)
    assert exc6.value.reason_code == "CATALOG_EDGE"
    already = copy.deepcopy(cat)
    already["microsoft_stack"]["edge"]["already"] = ["nameservers"]
    already["microsoft_stack"]["edge"]["full"] = False
    already["microsoft_stack"]["edge"]["missing"] = ["Teams SIP / lync SRV"]
    already["microsoft_stack"]["edge"]["note"] = (
        "Cloudflare is not the product. MX stays DNS-only. This Cloud Agent cannot edit Cloudflare. "
        "Not Institute launch. Full is false."
    )
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(already)
    assert exc7.value.reason_code == "CATALOG_EDGE"
    not_blob = copy.deepcopy(cat)
    not_blob["microsoft_stack"]["edge"]["not"] = ["seat"]
    with pytest.raises(IntegrityError) as exc8:
        validate_catalog(not_blob)
    assert exc8.value.reason_code == "CATALOG_EDGE"
    note = copy.deepcopy(cat)
    note["microsoft_stack"]["edge"]["note"] = "DNS only. Cannot edit. Not Institute launch. DNS is full."
    with pytest.raises(IntegrityError) as exc9:
        validate_catalog(note)
    assert exc9.value.reason_code == "CATALOG_EDGE"
    none = copy.deepcopy(cat)
    none["microsoft_stack"]["edge"]["full"] = None
    with pytest.raises(IntegrityError) as exc10:
        validate_catalog(none)
    assert exc10.value.reason_code == "CATALOG_EDGE"


def test_catalog_edge_records_dns_full_not_launch():
    edge = catalog_edge()
    assert edge["id"] == "cloudflare.dns"
    assert edge["role"] == "dns_edge"
    assert edge["sku"] is False
    assert edge["connection"] is False
    assert edge["complement"] is False
    assert edge["live"] is False
    assert edge["live_pin_ok"] is False
    assert edge["is_admit_plane"] is False
    assert edge["full"] is True
    assert edge["missing"] == []
    assert "sip" in " ".join(edge["already"]).lower()
    assert "dns is full" in edge["note"].lower()
    assert "not institute launch" in edge["note"].lower()
    assert edge["dashboard_url"] == "https://dash.cloudflare.com"


def test_live_scoreboard_mail_on_cloudflare_is_not_full_without_teams():
    scored = score_e7_on_cloudflare(_mail_dns(teams=False))
    assert scored["mail_on_cloudflare"] is True
    assert scored["full"] is False
    assert scored["sku"] is False
    assert scored["live_pin_ok"] is False
    assert "teams_sip" in scored["missing"]


def test_cannot_claim_full_while_teams_sip_is_missing():
    scored = score_e7_on_cloudflare(_mail_dns(teams=False))
    assert scored["checks"]["teams_sip"] is False
    assert scored["full"] is False


def test_full_only_when_every_check_is_present():
    scored = score_e7_on_cloudflare(_mail_dns(teams=True))
    assert scored["full"] is True
    assert scored["missing"] == []
    assert "dns is full" in scored["note"].lower()


def _incomplete_edge(cat: dict) -> dict:
    edge = cat["microsoft_stack"]["edge"]
    edge["full"] = False
    edge["missing"] = ["Teams SIP / lync SRV"]
    edge["already"] = [item for item in edge["already"] if "sip" not in item.lower() and "lync" not in item.lower()]
    edge["note"] = (
        "Nameservers for ainav.institute. Teams SIP is missing. Full is false. "
        "Cloudflare is not the product. MX stays DNS-only. This is not Institute launch. "
        "This Cloud Agent cannot edit Cloudflare."
    )
    return cat


def test_catalog_allows_recorded_incomplete_dns():
    cat = _incomplete_edge(copy.deepcopy(load_catalog()))
    validate_catalog(cat)


def test_catalog_rejects_incomplete_without_sip_or_false_note():
    no_sip = _incomplete_edge(copy.deepcopy(load_catalog()))
    no_sip["microsoft_stack"]["edge"]["missing"] = ["something else"]
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(no_sip)
    assert exc.value.reason_code == "CATALOG_EDGE"
    bad_note = _incomplete_edge(copy.deepcopy(load_catalog()))
    bad_note["microsoft_stack"]["edge"]["note"] = (
        "Cloudflare is not the product. MX stays DNS-only. "
        "This is not Institute launch. This Cloud Agent cannot edit Cloudflare."
    )
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(bad_note)
    assert exc2.value.reason_code == "CATALOG_EDGE"


def test_catalog_rejects_non_boolean_full_or_full_without_sip():
    none = copy.deepcopy(load_catalog())
    none["microsoft_stack"]["edge"]["full"] = None
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(none)
    assert exc.value.reason_code == "CATALOG_EDGE"
    no_sip = copy.deepcopy(load_catalog())
    no_sip["microsoft_stack"]["edge"]["already"] = [
        item for item in no_sip["microsoft_stack"]["edge"]["already"] if "sip" not in item.lower()
    ]
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(no_sip)
    assert exc2.value.reason_code == "CATALOG_EDGE"
    no_phrase = copy.deepcopy(load_catalog())
    no_phrase["microsoft_stack"]["edge"]["note"] = (
        "Cloudflare is not the product. MX stays DNS-only. "
        "This is not Institute launch. This Cloud Agent cannot edit Cloudflare."
    )
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(no_phrase)
    assert exc3.value.reason_code == "CATALOG_EDGE"


def test_catalog_rejects_sku_live_or_full_with_missing():
    sku = copy.deepcopy(load_catalog())
    sku["microsoft_stack"]["edge"]["sku"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(sku)
    assert exc.value.reason_code == "CATALOG_EDGE"
    live = copy.deepcopy(load_catalog())
    live["microsoft_stack"]["edge"]["live"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(live)
    assert exc2.value.reason_code == "CATALOG_EDGE"
    fiction = copy.deepcopy(load_catalog())
    fiction["microsoft_stack"]["edge"]["full"] = True
    fiction["microsoft_stack"]["edge"]["missing"] = ["Teams SIP / lync SRV"]
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(fiction)
    assert exc3.value.reason_code == "CATALOG_EDGE"


def test_public_status_keeps_cloudflare_off_the_write_path():
    body = public_status()
    path_ids = [item["id"] for item in body["fabric"]["path"]]
    assert "cloudflare.dns" not in path_ids
    assert [item["id"] for item in body["complements"]] == list(COMPLEMENT_IDS)
    edge = body["e7_cloudflare"]
    assert edge["id"] == "cloudflare.dns"
    assert edge["full"] is True
    assert edge["complement"] is False
    assert edge["live_pin_ok"] is False


def test_review_model_carries_catalog_edge():
    model = review_model()
    assert model["e7_cloudflare"]["full"] is True
    assert model["e7_cloudflare"]["sku"] is False
    assert model["engineering"]["gold_ci"]["exists"] is True
    assert model["engineering"]["sku"] is False
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
    assert "dns is full" in html.lower()
    assert "not a ninth complement" in html.lower()
    assert "e7_cloudflare" in js
    assert "refuse to paint a fiction scoreboard" in js
    assert "None. E7 DNS is full." in js
    assert "#e7-cloudflare" in css
