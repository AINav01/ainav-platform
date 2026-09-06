from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.buyer import success_program
from ainav.catalog import load_catalog, validate_catalog


def test_operating_company_is_catalog_law_and_on_the_sale_site():
    cat = load_catalog()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "operating company" in blob
    assert "operating day" in blob
    assert "launch gate" in blob
    assert "quality review" in blob
    assert "403 challenge" in blob
    assert "sku attach" in blob
    assert "five hundred" in blob
    assert "capacity" in blob
    firm = cat["expert_review"]["success"]["operating_company"]
    assert firm["kind"] == "ainav.operating_company.v1"
    assert firm["sku"] is False
    assert firm["crm"] is False
    assert firm["sales_team_claimed"] is False
    assert firm["payouts_booked"] is False
    assert firm["live_pin_ok"] is False
    assert firm["named_client"] is None
    assert firm["named_contractor"] is None
    assert firm["capacity"]["live_target"] == 500
    assert firm["capacity"]["pipeline_target"] == 500
    assert firm["capacity"]["live"] == 0
    assert firm["capacity"]["pipeline"] == 0
    assert [item["id"] for item in firm["rails"]] == ["pipeline", "live", "sandbox", "production"]
    assert [item["id"] for item in firm["roles"]] == ["owner", "number_two", "bd", "closer", "kit", "service", "ic"]
    assert [item["id"] for item in firm["day"]["stages"]] == [
        "qualify",
        "proof",
        "close",
        "assign",
        "service",
        "launch",
    ]
    assert firm["day"]["kind"] == "ainav.operating_day.v1"
    assert firm["gates"]["kind"] == "ainav.launch_gate.v1"
    assert firm["gates"]["launch"] is False
    assert firm["gates"]["gold_is_not_launch"] is True
    gold = next(item for item in firm["gates"]["items"] if item["id"] == "gold")
    assert gold["held"] is True
    assert gold["ready"] is False
    assert "floor held" in gold["note"].lower()
    assert cat["operations"]["note"].lower().startswith("sku attach")
    assert "#firm" in cat["operations"]["note"]
    assert firm["service"]["live"] == 0
    assert firm["service"]["hours_attach_udual"] is False
    assert firm["comp"]["booked"] is False
    assert firm["comp"]["paid_count"] == 0
    assert firm["comp"]["from_this_plane"] is False
    exported = success_program()["operating_company"]
    assert exported["lede"] == firm["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    assert 'id="firm-console"' in html
    assert 'id="firm-rails"' in html
    assert 'id="firm-day"' in html
    assert 'id="firm-gates"' in html
    assert 'src="site.js?v=2.88.0"' in html
    assert 'src="site.js?v=2.88.0"' in twin
    assert 'id="ops-note"' in html
    assert 'href="#firm"' in html.split('id="ops-note"', 1)[1].split("</p>", 1)[0]
    assert "Held. Floor held. Gold is not launch." in html
    assert 'data-held="yes"' in html
    assert "paintOperatingCompany" in js
    assert 'item.held ? "Held. "' in js
    assert "Run the firm" in html
    assert "firm-invent-lead" in html
    assert "firm-pay" in html
    assert "firm-crm" in html
    assert "firm-mark-launch" in html
    assert "firm-keep" in html
    assert "firm-hours-udual" in html
    assert 'href="/firm"' not in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#firm"' not in nav
    assert "index.html#firm" in twin
    assert "Firm bench" in twin
    objections = {item["id"] for item in cat["expert_review"]["success"]["objections"]}
    assert "firm" in objections
    walk = cat["expert_review"]["success"]["qualify"]["walk_away"]
    assert len(walk) == 20


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_operating_company_fail_closed():
    def sku(cat):
        cat["expert_review"]["success"]["operating_company"]["sku"] = True

    def crm(cat):
        cat["expert_review"]["success"]["operating_company"]["crm"] = True

    def live_book(cat):
        cat["expert_review"]["success"]["operating_company"]["capacity"]["live"] = 500

    def pipeline(cat):
        cat["expert_review"]["success"]["operating_company"]["capacity"]["pipeline"] = 500

    def named(cat):
        cat["expert_review"]["success"]["operating_company"]["named_contractor"] = "Acme"

    def team(cat):
        cat["expert_review"]["success"]["operating_company"]["sales_team_claimed"] = True

    def pay(cat):
        cat["expert_review"]["success"]["operating_company"]["comp"]["paid_count"] = 1

    def pin(cat):
        cat["expert_review"]["success"]["operating_company"]["live_pin_ok"] = True

    def kind(cat):
        cat["expert_review"]["success"]["operating_company"]["kind"] = "ainav.crm.v1"

    def rails(cat):
        cat["expert_review"]["success"]["operating_company"]["rails"] = [{"id": "shared"}]

    def lede(cat):
        cat["expert_review"]["success"]["operating_company"]["lede"] = "Flip HubSpot live."

    def refuse(cat):
        cat["expert_review"]["success"]["operating_company"]["refuse"] = ["A blog"]

    def site(cat):
        cat["expert_review"]["success"]["operating_company"]["site"] = "A /firm route."

    def note(cat):
        cat["expert_review"]["success"]["operating_company"]["note"] = "Live later."

    def objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item for item in cat["expert_review"]["success"]["objections"] if item.get("id") != "firm"
        ]

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "commission" not in item.lower()
        ]

    def upgrade(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 56:
                item["do"] = "Ship a CRM."

    def mgmt_live(cat):
        cat["business"]["management"]["capacity"]["live"] = 12

    def mgmt_pay(cat):
        cat["business"]["management"]["comp"]["from_this_plane"] = True

    def hubspot(cat):
        cat["expert_review"]["success"]["operating_company"]["hubspot"] = True

    def assigned(cat):
        cat["expert_review"]["success"]["operating_company"]["assigned"] = True

    def cms(cat):
        cat["expert_review"]["success"]["operating_company"]["cms"] = True

    def revenue(cat):
        cat["expert_review"]["success"]["operating_company"]["recognized_revenue_claimed"] = True

    def target(cat):
        cat["expert_review"]["success"]["operating_company"]["capacity"]["live_target"] = 50

    def sandboxes(cat):
        cat["expert_review"]["success"]["operating_company"]["capacity"]["sandboxes"] = 3

    def people_count(cat):
        cat["business"]["management"]["people"]["contractor_count"] = 4

    def people_named(cat):
        cat["business"]["management"]["people"]["named_contractors"] = ["Acme"]

    def people_team(cat):
        cat["business"]["management"]["people"]["sales_team_claimed"] = True

    def cannot(cat):
        cat["business"]["management"]["cannot_mark"] = [
            item for item in cat["business"]["management"]["cannot_mark"] if "commission" not in item.lower()
        ]

    def booked(cat):
        cat["business"]["management"]["comp"]["booked"] = True

    def day_kind(cat):
        cat["expert_review"]["success"]["operating_company"]["day"]["kind"] = "ainav.crm.v1"

    def day_stages(cat):
        cat["expert_review"]["success"]["operating_company"]["day"]["stages"] = [{"id": "crm"}]

    def gate_launch(cat):
        cat["expert_review"]["success"]["operating_company"]["gates"]["launch"] = True

    def gate_ready(cat):
        cat["expert_review"]["success"]["operating_company"]["gates"]["items"][0]["ready"] = True

    def gold_is_launch(cat):
        cat["expert_review"]["success"]["operating_company"]["gates"]["gold_is_not_launch"] = False

    def gold_held(cat):
        for item in cat["expert_review"]["success"]["operating_company"]["gates"]["items"]:
            if item.get("id") == "gold":
                item["held"] = False

    def ops_note(cat):
        cat["operations"]["note"] = "A second company."

    def service_hours(cat):
        cat["expert_review"]["success"]["operating_company"]["service"]["ffs_hours"] = 12

    def service_udual(cat):
        cat["expert_review"]["success"]["operating_company"]["service"]["hours_attach_udual"] = True

    def cannot_launch(cat):
        cat["business"]["management"]["cannot_mark"] = [
            item for item in cat["business"]["management"]["cannot_mark"] if "launch" not in item.lower()
        ]

    def upgrade_day(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 57:
                item["do"] = "Ship a CRM."

    def upgrade_quality(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 58:
                item["do"] = "Ship a CRM."

    def ciso_gate(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "launch gate" not in item.lower()
        ]

    for mutator in (
        sku,
        crm,
        live_book,
        pipeline,
        named,
        team,
        pay,
        pin,
        kind,
        rails,
        lede,
        refuse,
        site,
        note,
        objection,
        ciso,
        upgrade,
        mgmt_live,
        mgmt_pay,
        hubspot,
        assigned,
        cms,
        revenue,
        target,
        sandboxes,
        people_count,
        people_named,
        people_team,
        cannot,
        booked,
        day_kind,
        day_stages,
        gate_launch,
        gate_ready,
        gold_is_launch,
        gold_held,
        ops_note,
        service_hours,
        service_udual,
        cannot_launch,
        upgrade_day,
        upgrade_quality,
        ciso_gate,
    ):
        _reject(mutator)
