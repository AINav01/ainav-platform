from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.investor import (
    investor_html,
    investor_markdown,
    public_investor,
    render_investor_pdf,
    write_investor,
)


def test_investor_packet_is_honest_and_not_a_round():
    body = public_investor()
    assert body["kind"] == "ainav.investor.v1"
    assert body["sku"] is False
    assert body["live"] is False
    assert body["priced_round"] is False
    assert body["raise_claimed"] is False
    assert body["valuation_claimed"] is False
    assert body["forecast"] is False
    assert body["equity_offered"] is False
    assert body["not_a_round"] is True
    assert body["invited"] == "Cynthia Hodnett"
    assert body["recorded"] is False
    assert body["email"] is None
    assert body["kpis"]["recognized_revenue"] == 0
    assert body["kpis"]["named_customers"] == 0
    assert body["kpis"]["signed_l1"] == 0
    assert body["year_one_if_all_three"]["min"] == 88000
    assert body["year_one_if_all_three"]["max"] == 135000
    assert {row["id"] for row in body["skus"]} == {"L1", "P-ADM", "U-DUAL"}
    assert body["include_upsells"] is True
    assert "Dear Cynthia" in (body.get("letter_open") or "")
    assert "Seat B" in (body.get("seat_b") or "")
    assert "stock" in (body.get("will_not_ask") or "").lower()
    assert "$6,000" in (body.get("stack") or "")
    assert any(item["id"] == "industry.payables" for item in body["industry"])
    assert any(item["id"] == "industry.ip_keep" for item in body["industry"])
    assert any(item["id"] == "ffs.ip_hygiene" for item in body["fee_for_service"])
    md = investor_markdown()
    assert "not a priced round" in md.lower()
    assert "cynthia hodnett" in md.lower()
    assert "dear cynthia" in md.lower()
    assert "what we will not ask" in md.lower()
    assert "$0" in md or "recognized revenue: $0" in md.lower()
    assert "industry.payables" in md
    assert "not a fourth" in md.lower()
    assert "$3,500" in md or "$3500" in md
    assert "what it is" in md.lower()
    html = investor_html()
    assert "Investor packet" in html
    assert "<table>" in html
    assert "industry.payables" in html or "payables" in html
    assert "Dear Cynthia" in html
    raw = render_investor_pdf()
    assert raw.startswith(b"%PDF-1.4")
    assert b"Cynthia" in raw or b"AINAV" in raw
    assert b"LIVE_PIN" in raw or b"priced" in raw


def test_investor_validators_refuse_fiction():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    del missing["investor"]
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(missing)
    assert exc.value.reason_code == "CATALOG_INVESTOR"
    raise_it = copy.deepcopy(cat)
    raise_it["investor"]["raise_claimed"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(raise_it)
    value = copy.deepcopy(cat)
    value["investor"]["valuation_claimed"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(value)
    forecast = copy.deepcopy(cat)
    forecast["investor"]["forecast"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(forecast)
    equity = copy.deepcopy(cat)
    equity["investor"]["equity_offered"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(equity)
    sku = copy.deepcopy(cat)
    sku["investor"]["sku"] = True
    with pytest.raises(IntegrityError) as sku_exc:
        validate_catalog(sku)
    assert sku_exc.value.reason_code == "CATALOG_SKU"
    equation = copy.deepcopy(cat)
    equation["equations"]["investor"] = "something else"
    with pytest.raises(IntegrityError):
        validate_catalog(equation)
    no_upsell = copy.deepcopy(cat)
    no_upsell["investor"]["include_upsells"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(no_upsell)
    no_letter = copy.deepcopy(cat)
    no_letter["investor"]["letter_open"] = "Hello"
    with pytest.raises(IntegrityError):
        validate_catalog(no_letter)


def test_institute_investor_is_catalog_honest():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'id="investor"' in html
    assert "investor.json" in js
    assert 'id="investor-ffs"' in html
    assert "fee_for_service" in js
    body = public_investor()
    on_disk = json.loads(Path("institute/investor.json").read_text(encoding="utf-8"))
    assert on_disk == body
    path = write_investor(Path("docs/CYNTHIA_HODNETT_INVESTOR.pdf"))
    assert path.exists()
    assert path.read_bytes().startswith(b"%PDF")
    assert Path("docs/CYNTHIA_HODNETT_INVESTOR.md").exists()
    assert Path("docs/CYNTHIA_HODNETT_INVESTOR.html").exists()
