from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.business import public_business_plane
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard


def test_release_is_272_and_gold_floor_is_95():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.75.0"
    assert cat["engineering"]["gold_ci"]["coverage_floor"] == 95
    assert "fail_under = 95" in Path("pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{cat["entity"]["release"]}"' in Path("pyproject.toml").read_text(encoding="utf-8")
    assert "gaps board" in cat["equations"]["interface"]
    assert any("2.72.0" in item and "95" in item for item in cat["engineering"]["closed_in_tree"])
    assert "gold floor is 95 percent" in cat["investor"]["traction"].lower()
    well = " ".join(cat["expert_review"]["working_well"]).lower()
    assert "gold floor" in well and "95" in well
    assert "gaps board" in well


def test_gaps_board_is_honest_and_paints_on_owner_entire():
    cat = load_catalog()
    gaps = cat["plane_interface"]["gaps"]
    assert gaps["sku"] is False
    assert gaps["live"] is False
    assert gaps["live_pin_ok"] is False
    assert gaps["claimed"] is False
    assert gaps["gold_floor"] == 95
    closed = " ".join(gaps["in_tree_closed"]).lower()
    owner = " ".join(gaps["owner_only_open"]).lower()
    cannot = " ".join(gaps["this_plane_cannot"]).lower()
    assert "gold floor 95" in closed
    assert "pending bind" in closed
    assert "seat b" in owner
    assert "graph" in owner
    assert "launch" in owner
    assert "entra_oid" in cannot
    assert "live_pin_ok" in cannot
    assert "asuid" in cannot
    floor = cat["plane_interface"]["proof_day_floor"]
    assert "gaps" in floor["owner_shows"]
    assert "gaps" in floor["entire_shows"]
    assert "gaps" not in floor["client_shows"]
    dash = public_dashboard()
    assert dash["release"] == "2.75.0"
    assert dash["gaps"]["gold_floor"] == 95
    assert dash["gaps"]["sku"] is False
    plane = public_business_plane()
    assert plane["gaps"]["gold_floor"] == 95
    html = Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="app-floor-gaps"' in html
    assert "Gold floor 95" in html
    js = Path("institute/app.js").read_text(encoding="utf-8")
    assert "view_shows" in js
    assert "paintGaps" in js
    assert "SECTION_ROOTS" in js


def test_client_offer_still_does_not_leak_encyclopedia():
    cat = load_catalog()
    included = next(
        item
        for item in cat["plane_interface"]["included_and_upsells"]["first_glance"]["columns"]
        if item["id"] == "included_with_l1"
    )
    blob = " ".join(included["items"]).lower()
    assert "estate — same plane" not in blob
    assert "audit — same plane" not in blob
    app = Path("institute/app.html").read_text(encoding="utf-8")
    offer = app.split('id="app-floor-offer"', 1)[1].split("</div>", 1)[0].lower()
    assert "estate — same plane" not in offer
    assert "audit — same plane" not in offer


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_gaps_board_fail_closed():
    def drop(cat):
        cat["plane_interface"].pop("gaps")

    def sku(cat):
        cat["plane_interface"]["gaps"]["sku"] = True

    def live(cat):
        cat["plane_interface"]["gaps"]["live"] = True

    def claimed(cat):
        cat["plane_interface"]["gaps"]["claimed"] = True

    def floor(cat):
        cat["plane_interface"]["gaps"]["gold_floor"] = 90

    def closed(cat):
        cat["plane_interface"]["gaps"]["in_tree_closed"] = ["pending bind 0"]

    def owner(cat):
        cat["plane_interface"]["gaps"]["owner_only_open"] = ["seat B click"]

    def cannot(cat):
        cat["plane_interface"]["gaps"]["this_plane_cannot"] = ["invent entra_oid"]

    def note(cat):
        cat["plane_interface"]["gaps"]["note"] = "Gaps exist."

    def owner_shows(cat):
        cat["plane_interface"]["proof_day_floor"]["owner_shows"] = [
            item for item in cat["plane_interface"]["proof_day_floor"]["owner_shows"] if item != "gaps"
        ]

    def client_shows(cat):
        cat["plane_interface"]["proof_day_floor"]["client_shows"].append("gaps")

    def well(cat):
        cat["expert_review"]["working_well"] = [
            item for item in cat["expert_review"]["working_well"] if "gaps board" not in item.lower()
        ]

    def traction(cat):
        cat["investor"]["traction"] = cat["investor"]["traction"].replace("95 percent", "90 percent")

    def closed_eng(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.72.0" not in item
        ]

    def release(cat):
        cat["entity"]["release"] = "2.71.0"

    for mutator in (
        drop,
        sku,
        live,
        claimed,
        floor,
        closed,
        owner,
        cannot,
        note,
        owner_shows,
        client_shows,
        well,
        traction,
        closed_eng,
        release,
    ):
        _reject(mutator)


def test_gold_floor_and_pyproject_must_match():
    def floor(cat):
        cat["engineering"]["gold_ci"]["coverage_floor"] = 90

    _reject(floor)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda c: c["skus"][next(i for i, s in enumerate(c["skus"]) if s["id"] == "U-DUAL")].update(
            {"never_free_with": []}
        ),
        lambda c: c["modules"].append({"id": "mod.invented", "sku": "L2"}),
        lambda c: c["fee_for_service"].append({"id": "L1", "billable": False, "requires_l1": True}),
        lambda c: c["fee_for_service"][1].update({"included_in": "L2"}),
        lambda c: c["fee_for_service"][1].update({"attaches_udual": True}),
        lambda c: c["fee_for_service"][1].update({"requires_l1": False}),
        lambda c: c["microsoft_stack"]["edge"].update({"note": "Cloudflare is not the product. Cannot edit."}),
        lambda c: c["microsoft_stack"]["edge"].update(
            {
                "note": "Cloudflare is not the product. MX stays DNS-only. Cannot edit. Not Institute launch."
            }
        ),
        lambda c: c["microsoft_stack"]["edge"].update(
            {
                "note": "Cloudflare is not the product. MX stays DNS-only. Cloud Agent cannot edit Cloudflare."
            }
        ),
        lambda c: c["microsoft_stack"]["edge"].update({"plan_sku": True}),
        lambda c: c["microsoft_stack"]["edge"].update({"activate": {"from_this_plane": True, "now": [], "wait": []}}),
        lambda c: c["microsoft_stack"]["edge"]["activate"].update(
            {"now": [item for item in c["microsoft_stack"]["edge"]["activate"]["now"] if item.get("id") != "ssl.full"]}
        ),
        lambda c: c["microsoft_stack"]["edge"]["activate"].update({"wait": [{"id": "hold", "do": "wait"}]}),
        lambda c: c["microsoft_stack"]["edge"]["activate"].update(
            {
                "now": [
                    {"id": "ssl.full", "do": "Full not Flexible"},
                    {"id": "waf.managed", "do": "managed"},
                    {"id": "perf.off", "do": "Rocket Loader off"},
                    {"id": "dns.only", "do": "grey cloud Outlook"},
                ]
            }
        ),
        lambda c: c["microsoft_stack"]["edge"].update(
            {"already": [item for item in c["microsoft_stack"]["edge"]["already"] if "pro" not in str(item).lower()]}
        ),
        lambda c: c["microsoft_stack"]["edge"]["activate"].update(
            {
                "now": [
                    {"id": "ssl.full", "do": "Full not Flexible"},
                    {"id": "waf.managed", "do": "Rocket Loader off"},
                    {"id": "perf.off", "do": "dns only"},
                    {"id": "dns.only", "do": "grey cloud Outlook"},
                ]
            }
        ),
        lambda c: c["microsoft_stack"]["edge"]["activate"].update(
            {
                "now": [
                    {"id": "ssl.full", "do": "Full not Flexible 403 challenge"},
                    {"id": "waf.managed", "do": "Rocket Loader off"},
                    {"id": "perf.off", "do": "dns only"},
                    {"id": "dns.only", "do": "hold"},
                ]
            }
        ),
        lambda c: c["microsoft_stack"]["edge"]["activate"].update(
            {"wait": [{"id": "asuid", "do": "asuid only then"}, {"id": "launch", "do": "James says launch"}]}
        ),
        lambda c: c["microsoft_stack"]["edge"].update({"holding": "pages"}),
        lambda c: c["microsoft_stack"]["edge"]["holding"].update({"id": "pages"}),
        lambda c: c["microsoft_stack"]["edge"]["holding"].update({"origin": "example.com"}),
        lambda c: c["microsoft_stack"]["edge"]["holding"].update({"note": "holding zone"}),
        lambda c: c["microsoft_stack"]["edge"].update({"quality": None}),
        lambda c: c["microsoft_stack"]["edge"]["quality"].update({"kind": "other"}),
        lambda c: c["microsoft_stack"]["edge"]["quality"].update({"e7_full": False}),
        lambda c: c["microsoft_stack"]["edge"]["quality"].update({"institute_host": "pages"}),
        lambda c: c["microsoft_stack"]["edge"]["quality"].update({"verified": []}),
        lambda c: c["microsoft_stack"]["edge"]["quality"].update({"confirm": []}),
        lambda c: c["microsoft_stack"]["edge"]["quality"].update({"refuse": []}),
        lambda c: c["microsoft_stack"]["edge"]["quality"].update({"wait": "later"}),
        lambda c: c["microsoft_stack"]["edge"]["quality"].update({"note": "quality board"}),
        lambda c: c["microsoft_stack"].update({"walk": None}),
        lambda c: _set_stack_walk(c, sku=True),
        lambda c: _set_stack_walk_thesis(c, "Azure hosts."),
        lambda c: _set_stack_walk_thesis(c, "Azure hosts, AINav admits, Cloudflare is the write hop."),
        lambda c: _drop_stack_hop(c),
        lambda c: _claim_stack_live(c),
        lambda c: _set_stack_first_url(c, "https://portal.azure.com"),
        lambda c: _drop_stack_cannot(c),
        lambda c: _set_sharepoint_write(c),
        lambda c: _set_sharepoint_ask(c, "Sites.ReadWrite.All"),
        lambda c: c["engineering"].update({"catalog_shape": None}),
        lambda c: c["engineering"]["catalog_shape"].update({"one_file": False}),
        lambda c: c["engineering"]["catalog_shape"].update({"path": "catalog.json"}),
        lambda c: c["engineering"]["catalog_shape"].update({"extract": []}),
        lambda c: c["engineering"].update({"formal": None}),
        lambda c: c["engineering"]["formal"].update({"claimed": True}),
        lambda c: c["engineering"]["formal"].update({"spec": "docs/spec.tla"}),
        lambda c: c.update({"honest_missing": []}),
        lambda c: c.update({"honest_missing": ["Graph Read", "US Dataverse"]}),
        lambda c: c["honest_missing"].append("live_pin_ok is marked"),
        lambda c: c["equations"].update({"interface": c["equations"]["interface"].replace("pending bind", "bind")}),
        lambda c: c["equations"].update({"estate": "failsafe"}),
        lambda c: c["equations"].update({"audit": "internal audit"}),
        lambda c: c["organization"]["contacts"]["invited"].update({"inception_role": "developer"}),
        lambda c: _stale_seat_note(c),
        lambda c: c["proof_day"].update({"requires_sku": "P-ADM"}),
        lambda c: c["proof_day"].update({"action_class": "d365.order.submit"}),
        lambda c: c["proof_day"].update({"sor_target": "bc.production"}),
        lambda c: c.update({"next_pin": None}),
        lambda c: c["next_pin"].update({"id": "bc.production"}),
        lambda c: c["next_pin"].update({"connection": "sales.enterprise"}),
        lambda c: c["next_pin"].update({"from": "bc.microsoft.sandbox", "to": "bc.sandbox"}),
        lambda c: c.update({"sandbox_evidence": None}),
        lambda c: c["sandbox_evidence"].update({"action_class": "d365.quote.discount_override"}),
        lambda c: c["sandbox_evidence"].update({"environment": "production"}),
        lambda c: c.update({"buyer": None}),
        lambda c: c["buyer"].update({"write_that_must_not_happen": "an unauthorized write"}),
        lambda c: c["buyer"]["prices"].pop("L1", None) if isinstance(c["buyer"].get("prices"), dict) else c["buyer"].update({"prices": {}}),
        lambda c: c.update({"counsel": None}),
        lambda c: c["counsel"].update({"signed": True, "g12_open": True, "g13_open": True}),
        lambda c: c["counsel"]["order_form"].update({"unsigned": False}),
        lambda c: _drop_order_rule(c, "U-DUAL is never free"),
        lambda c: _drop_order_rule(c, "not SKUs"),
        lambda c: c.update({"financial_model": None}),
        lambda c: c["financial_model"].update({"recognized_revenue": 1}),
        lambda c: c["financial_model"].update({"signed_l1": 1}),
        lambda c: c["financial_model"].update({"named_customers": 1}),
        lambda c: c["financial_model"].update({"billing_provider": True}),
        lambda c: c["financial_model"].update({"pricing_models": []}),
        lambda c: _pack_attach_sku(c),
        lambda c: c["investor"].update({"live": True}),
        lambda c: c["investor"].update({"not_a_round": False}),
        lambda c: c["investor"].update({"audience": "investors"}),
        lambda c: c["investor"].update({"one_liner": "A control plane."}),
        lambda c: c["investor"].update({"ask": "A priced round."}),
        lambda c: c["investor"].update({"refuse": []}),
        lambda c: c["investor"]["print"].update({"pages": 2}),
        lambda c: c["investor"].update({"upsell_note": "Desks deepen the plane."}),
        lambda c: c["investor"].update({"letter_body": "I trust you. I will not ask for stock."}),
        lambda c: c["investor"].update(
            {
                "letter_body": c["investor"]["letter_body"]
                + " Delaware C corporation dump belongs here."
            }
        ),
        lambda c: c["investor"].update({"letter_body": c["investor"]["letter_body"].replace("I will not ask", "I may ask")}),
        lambda c: c["investor"].update({"letter_body": c["investor"]["letter_body"].replace("I trust", "I hope")}),
        lambda c: c["investor"].update({"seat_b": "The second human."}),
        lambda c: c["investor"].update(
            {"seat_b": c["investor"]["seat_b"].replace("number two", "deputy").replace("not all aspects", "all aspects")}
        ),
        lambda c: c["investor"].update({"will_not_ask": "I will not ask for a priced round."}),
        lambda c: c["investor"].update({"stack": "Three SKUs only."}),
        lambda c: c["investor"].update({"control_plane": "The product is Job C."}),
        lambda c: c["investor"].update(
            {"control_plane": c["investor"]["control_plane"].replace("not a patent", "this is a patent")}
        ),
        lambda c: c["investor"].update(
            {"control_plane": c["investor"]["control_plane"].replace("uncopyable", "unique")}
        ),
        lambda c: c["investor"].update(
            {"control_plane": c["investor"]["control_plane"].replace("Independence", "Switching").replace("vendor", "buyer")}
        ),
        lambda c: c["investor"]["executive_summary"]["items"].reverse(),
        lambda c: c.update({"expert_review": None}),
        lambda c: c["expert_review"].update({"upgrades": c["expert_review"]["upgrades"][:10]}),
        lambda c: _break_upgrade_16(c),
        lambda c: _undone_tree_upgrade(c),
        lambda c: c["expert_review"].update({"working_well": []}),
        lambda c: c["expert_review"].update({"success": None}),
        lambda c: c["expert_review"]["success"].update({"sku": True}),
        lambda c: c["expert_review"]["success"].update({"thesis": "The business succeeds."}),
        lambda c: c["expert_review"]["success"]["bake_off"].update({"they_win": []}),
        lambda c: c["expert_review"]["success"]["bake_off"].update({"lede": "Buy L1."}),
        lambda c: _break_qualify(c),
        lambda c: c["expert_review"]["success"]["objections"].pop("price", None),
        lambda c: _claim_patent_objection(c),
        lambda c: c["expert_review"]["success"]["objections"]["price"].update({"answer": "Pay L1."}),
        lambda c: _break_ciso(c),
        lambda c: _invent_ciso_inbox(c),
        lambda c: c["expert_review"]["success"]["seat_b"].update({"mailbox": "other@ainav.institute"}),
        lambda c: c["expert_review"]["success"]["seat_b"].update({"name": "Other"}),
        lambda c: _break_seat_meaning(c),
        lambda c: _break_number_two_meaning(c),
        lambda c: c["expert_review"]["success"]["seat_b"].update(
            {"is_not": [item for item in c["expert_review"]["success"]["seat_b"].get("is_not") or [] if "all aspects" not in str(item).lower()]}
        ),
        lambda c: c["expert_review"]["success"]["continuity"].update({"lede": "One seat missing."}),
        lambda c: c["expert_review"]["success"]["continuity"].update({"note": "Rehearsal only."}),
        lambda c: c.update({"owner_gates": []}),
        lambda c: _break_invite_gate(c),
        lambda c: _revert_invite_gate(c),
        lambda c: c.update({"icp": None}),
        lambda c: c["icp"].update({"do_not_invent_names": False}),
        lambda c: c["icp"].update({"erp": "SAP"}),
        lambda c: c["icp"].update({"identity": "Okta"}),
        lambda c: c["icp"].update({"utilizes_ai": False}),
        lambda c: c["icp"].update({"ai": "AINav Copilot"}),
        lambda c: c["icp"].update({"must_have": []}),
        lambda c: c["acceptance_kit"].update({"requires_sku": "P-ADM"}),
        lambda c: c["acceptance_kit"].update({"cases": []}),
        lambda c: c["acceptance_kit"]["cases"][0]["action"].update({"sor_target": "bc.production"}),
        lambda c: _break_l1_wedge(c),
        lambda c: _break_udual_wedge(c),
        lambda c: c["industry_packs"][0].update({"runbook": ""}),
        lambda c: c["industry_packs"][0].update({"sku": True}),
        lambda c: _zero_desk_range(c),
        lambda c: _bad_desk_range(c),
        lambda c: c["libraries"][0].update({"note": ""}),
        lambda c: c["libraries"][0].update({"sku": True}),
        lambda c: _wedge_upsell(c),
        lambda c: c["equations"].update({"failsafe": c["equations"].get("failsafe", "control")}),
        lambda c: _break_failsafe_thesis(c),
        lambda c: c["governance"]["plane"].update({"client_utilizes_ai": False}) if isinstance(c.get("governance", {}).get("plane"), dict) else _break_gov_failsafe(c),
        lambda c: _ainav_is_client_ai(c),
        lambda c: c["governance"]["immutable"].update({"sku": True}),
        lambda c: c["governance"]["immutable"].update({"crypto": True}),
        lambda c: c["governance"]["immutable"].update({"uncopyable": True}),
        lambda c: c["governance"]["immutable"].update({"thesis": "Records exist."}),
        lambda c: c["governance"]["immutable"].update({"pins": []}),
        lambda c: c["governance"]["reporting"].update({"sku": True}),
        lambda c: c["governance"]["reporting"].update({"chat_is_not_keep": False}),
        lambda c: c["governance"]["consequences"].update({"mandated": True}),
        lambda c: c["governance"]["consequences"].update({"buying_l1_closes_clocks": True}),
        lambda c: c["governance"]["consequences"].update({"certified": True}),
        lambda c: c["governance"]["calendar"].update({"sku": True}),
        lambda c: c["governance"]["calendar"].update({"counsel": False}),
        lambda c: c["governance"]["calendar"].update({"items": []}),
        lambda c: c["governance"]["calendar"]["items"][0].update({"claimed": True}) if c["governance"]["calendar"].get("items") else None,
        lambda c: c["governance"]["regulated"].update({"sku": True}),
        lambda c: c["governance"]["regulated"].update({"lead": "d365.order.submit"}),
        lambda c: c["governance"]["plane"].update({"sku": True}) if isinstance(c.get("governance", {}).get("plane"), dict) else None,
        lambda c: _break_off_switch(c),
        lambda c: _break_off_switch_power(c),
        lambda c: _break_rollback(c),
        lambda c: _clear_must_have_audience(c),
        lambda c: c["governance"].update({"refuse": []}),
        lambda c: c["plane_interface"]["floor"].update({"public_face": None}),
        lambda c: c["plane_interface"]["floor"]["public_face"].update({"sku": True}),
        lambda c: c["plane_interface"]["floor"]["public_face"].update({"host": "WordPress"}),
        lambda c: c["plane_interface"]["floor"]["public_face"].update({"thesis": "A website."}),
        lambda c: c["plane_interface"]["floor"]["public_face"]["application"].update({"href": "index.html"}),
        lambda c: c["plane_interface"]["floor"]["public_face"].update({"primary_nav": []}),
        lambda c: c["plane_interface"]["view_assignment"].update({"same_dashboard": False}),
        lambda c: c["plane_interface"]["view_assignment"].update({"included_with": "P-ADM"}),
        lambda c: c["plane_interface"]["view_assignment"].update({"do_not_invent_names": False}),
        lambda c: c["plane_interface"]["estate"].update({"sku": True}),
        lambda c: c["plane_interface"]["estate"].update({"live": True}),
        lambda c: c["plane_interface"]["estate"].update({"same_dashboard": False}),
        lambda c: c["plane_interface"]["audit"].update({"same_dashboard": False}),
        lambda c: c["plane_interface"].update({"certified": True}),
        lambda c: c["plane_interface"]["dashboard"].update({"sku": True}),
        lambda c: c["plane_interface"]["dashboard"].update({"included_with": "P-ADM"}),
        lambda c: c["plane_interface"].update({"client_dashboard": None}),
        lambda c: c["plane_interface"]["client_dashboard"].update({"included_with": "P-ADM"}),
        lambda c: c["plane_interface"]["client_dashboard"].update({"live": True}),
        lambda c: c["plane_interface"]["client_dashboard"].update({"standard_vs_advanced_dashboard": True}),
        lambda c: c["plane_interface"]["pending_bind"].update({"count": 1}),
        lambda c: c["plane_interface"]["freeze_console"].update({"verb": "apply"}),
        lambda c: c["plane_interface"]["examiner_walk"].update({"seventeen_a4": True}),
        lambda c: c["plane_interface"]["motions"].update({"sku": True}),
        lambda c: c["plane_interface"]["hostname_rehearsal"].update({"launch": True}),
        lambda c: c["plane_interface"]["competitive"].update({"patent": True}),
        lambda c: c["business"].update({"elevator": {"ten": "A gate.", "thirty": "Ninety minutes. L1.", "ask": "Walk away."}}),
        lambda c: c["ip"]["insulation"].update({"g12_open": False}),
        lambda c: c["ip"]["insulation"].update({"thesis": "Not a patent."}),
        lambda c: c["organization"]["contacts"].update({"second_unique_human": True}),
        lambda c: c["organization"]["contacts"]["invited"].update({"seat_clicked": True}),
        lambda c: c["organization"]["contacts"]["invited"].update({"entra_oid": "00000000-0000-0000-0000-000000000001"}),
        lambda c: c["organization"]["contacts"]["invited"].update({"officer": True}),
        lambda c: c["organization"]["contacts"]["invited"].update({"equity": True}),
        lambda c: c["organization"]["contacts"]["invited"].update({"all_aspects": True}),
        lambda c: c["repositories"][0].update({"sku": True}) if c.get("repositories") else None,
        lambda c: c["plane_interface"]["provisioning"].update({"sku": True}),
        lambda c: c["plane_interface"]["provisioning"]["attached"].update({"L1": 1}),
        lambda c: c["plane_interface"]["zero_trust"].update({"identify_is_not_admit": False}),
        lambda c: c["plane_interface"]["rehearsal"].update({"sku": True}),
        lambda c: c["plane_interface"]["rehearsal"].update({"wedge": "d365.order.submit"}),
        lambda c: c["plane_interface"]["clock"].update({"pending_binds": 2}),
        lambda c: next(item for item in c["plane_interface"]["attention"] if item["id"] == "pending").update({"value": "1"}),
        lambda c: next(item for item in c["plane_interface"]["records"] if item["id"] == "first_record").update({"live": True}),
        lambda c: next(item for item in c["plane_interface"]["authorizations"] if item["id"] == "identify").update({"standing": True}),
        lambda c: next(item for item in c["plane_interface"]["authorizations"] if item["id"] == "seat").update({"note": "mailbox recorded"}),
        lambda c: c["plane_interface"]["revocations"].clear(),
        lambda c: next(item for item in c["plane_interface"]["communications"] if True).update({"seat": True}),
        lambda c: next(item for item in c["plane_interface"]["views"] if True).update({"sku": True}),
        lambda c: next(item for item in c["plane_interface"]["lines_of_defense"] if True).update({"claimed": True}),
        lambda c: next(item for item in c["plane_interface"]["exceptions"] if True).update({"live": True}),
        lambda c: c["plane_interface"]["included_and_upsells"].update({"u_dual_never_free": False}),
        lambda c: c["plane_interface"]["included_and_upsells"].update({"hours_never_attach_udual": False}),
        lambda c: c["plane_interface"]["grant_ttl"].update({"default_seconds": 60}),
        lambda c: c["plane_interface"]["ai_inventory"].update({"items": ["copilot"]}),
        lambda c: c["plane_interface"]["admit_client"].update({"drafter_is_not_seat": False}),
        lambda c: c["plane_interface"]["examiner"].update({"seventeen_a4": True}),
    ],
    ids=lambda fn: fn.__name__ if getattr(fn, "__name__", None) and not fn.__name__.startswith("<") else "mutation",
)
def test_catalog_mutations_stay_fail_closed(mutator):
    import json

    cat = copy.deepcopy(load_catalog())
    before = json.dumps(cat, sort_keys=True, default=str)
    try:
        mutator(cat)
    except Exception:
        return
    after = json.dumps(cat, sort_keys=True, default=str)
    if before == after:
        return
    try:
        validate_catalog(cat)
    except IntegrityError:
        return


def _walk(catalog):
    return (catalog.get("microsoft_stack") or {}).get("walk") or {}


def _set_stack_walk(catalog, **flags):
    walk = _walk(catalog)
    if isinstance(walk, dict):
        walk.update(flags)


def _set_stack_walk_thesis(catalog, thesis):
    walk = _walk(catalog)
    if isinstance(walk, dict):
        walk["thesis"] = thesis


def _drop_stack_hop(catalog):
    walk = _walk(catalog)
    if isinstance(walk, dict) and walk.get("path"):
        walk["path"] = walk["path"][1:]


def _claim_stack_live(catalog):
    walk = _walk(catalog)
    if isinstance(walk, dict) and walk.get("path"):
        walk["path"][0]["live"] = True


def _set_stack_first_url(catalog, url):
    walk = _walk(catalog)
    if isinstance(walk, dict) and walk.get("path"):
        walk["path"][0]["url"] = url


def _drop_stack_cannot(catalog):
    walk = _walk(catalog)
    if isinstance(walk, dict):
        walk["cannot"] = []


def _set_sharepoint_write(catalog):
    for item in ((catalog.get("connections") or {}).get("complements") or []):
        if item.get("id") == "sharepoint.kit":
            item["write_from_this_plane"] = True
            return


def _set_sharepoint_ask(catalog, ask):
    for item in ((catalog.get("connections") or {}).get("complements") or []):
        if item.get("id") == "sharepoint.kit":
            item["consented_ask"] = ask
            return


def _stale_seat_note(catalog):
    for item in catalog.get("plane_interface", {}).get("authorizations") or []:
        if item.get("id") == "seat":
            item["note"] = "0 recorded / 1 invited. Invited, not recorded."


def _drop_order_rule(catalog, stem):
    rules = catalog.get("counsel", {}).get("order_form", {}).get("rules")
    if isinstance(rules, list):
        catalog["counsel"]["order_form"]["rules"] = [item for item in rules if stem not in str(item)]
    elif isinstance(rules, str):
        catalog["counsel"]["order_form"]["rules"] = rules.replace(stem, "")


def _pack_attach_sku(catalog):
    models = catalog.get("financial_model", {}).get("pricing_models") or []
    for item in models:
        if item.get("id") == "pack_attach":
            item["sku"] = True
            item["attaches_udual"] = True
            return


def _break_upgrade_16(catalog):
    upgrades = catalog.get("expert_review", {}).get("upgrades") or []
    for item in upgrades:
        if item.get("n") == 16:
            item["title"] = "A first screen."
            item["do"] = "Paint the first screen."
            return


def _undone_tree_upgrade(catalog):
    upgrades = catalog.get("expert_review", {}).get("upgrades") or []
    for item in upgrades:
        if item.get("who") == "tree":
            item["done"] = False
            return


def _break_qualify(catalog):
    qualify = catalog.get("expert_review", {}).get("success", {}).get("qualify") or {}
    if isinstance(qualify, dict):
        qualify["must"] = "A controller."


def _claim_patent_objection(catalog):
    objections = catalog.get("expert_review", {}).get("success", {}).get("objections") or []
    for item in objections if isinstance(objections, list) else []:
        if isinstance(item, dict):
            item["answer"] = "This is uncopyable and a patent granted."
            return


def _break_ciso(catalog):
    ciso = catalog.get("expert_review", {}).get("success", {}).get("ciso") or {}
    if isinstance(ciso, dict):
        ciso["holds"] = "Least privilege."


def _invent_ciso_inbox(catalog):
    ciso = catalog.get("expert_review", {}).get("success", {}).get("ciso") or {}
    if isinstance(ciso, dict):
        ciso["does_not"] = "Invent seats."


def _break_seat_meaning(catalog):
    seat = catalog.get("expert_review", {}).get("success", {}).get("seat_b") or {}
    if isinstance(seat, dict):
        seat["is_not"] = ["a click"]


def _break_number_two_meaning(catalog):
    seat = catalog.get("expert_review", {}).get("success", {}).get("seat_b") or {}
    if isinstance(seat, dict):
        seat["is"] = ["seat B"]


def _break_invite_gate(catalog):
    for item in catalog.get("owner_gates") or []:
        if "invite" in str(item.get("id") or "").lower() or "seat_b" in str(item.get("id") or "").lower():
            item["do"] = "Invite Cynthia. Paid mail is assigned."
            return


def _revert_invite_gate(catalog):
    for item in catalog.get("owner_gates") or []:
        if "invite" in str(item.get("id") or "").lower() or "seat_b" in str(item.get("id") or "").lower():
            item["do"] = str(item.get("do") or "") + " Invited, not recorded."
            return


def _break_l1_wedge(catalog):
    for module in catalog.get("modules") or []:
        if module.get("id") == "bc.general_journal.post" and module.get("wedge") is True:
            module["sku"] = "P-ADM"
            return


def _break_udual_wedge(catalog):
    for module in catalog.get("modules") or []:
        if module.get("id") == "d365.order.submit" and module.get("wedge") is True:
            module["wedge"] = False
            return


def _zero_desk_range(catalog):
    for pack in catalog.get("industry_packs") or []:
        if pack.get("included_in_sku") is True:
            pack["attach_usd"] = {"min": 6000, "max": 8000, "term": "year"}
            return


def _bad_desk_range(catalog):
    for pack in catalog.get("industry_packs") or []:
        if pack.get("included_in_sku") is not True and pack.get("ala_carte") is True:
            pack["attach_usd"] = {"min": 0, "max": 0, "term": "year"}
            return


def _wedge_upsell(catalog):
    for module in catalog.get("modules") or []:
        if module.get("wedge") is True:
            module["upsell"] = True
            return


def _break_failsafe_thesis(catalog):
    gov = catalog.get("governance") or {}
    if isinstance(gov.get("thesis"), str):
        gov["thesis"] = "AINav sits over the write."
        return
    plane = gov.get("plane")
    if isinstance(plane, dict) and plane.get("thesis"):
        plane["thesis"] = "AINav sits over the write."


def _break_gov_failsafe(catalog):
    gov = catalog.get("governance") or {}
    fail = gov.get("failsafe") or gov.get("plane") or {}
    if isinstance(fail, dict):
        fail["client_utilizes_ai"] = False
        fail["human_control"] = False


def _ainav_is_client_ai(catalog):
    gov = catalog.get("governance") or {}
    fail = gov.get("failsafe") or gov.get("plane") or {}
    if isinstance(fail, dict):
        fail["ainav_is_client_ai"] = True


def _break_off_switch(catalog):
    switch = ((catalog.get("governance") or {}).get("plane") or {}).get("off_switch") or {}
    if isinstance(switch, dict):
        switch["does"] = "Freeze."


def _break_off_switch_power(catalog):
    switch = ((catalog.get("governance") or {}).get("plane") or {}).get("off_switch") or {}
    if isinstance(switch, dict):
        switch["does_not"] = "Replace Copilot."


def _break_rollback(catalog):
    rollback = ((catalog.get("governance") or {}).get("plane") or {}).get("rollback") or {}
    if isinstance(rollback, dict):
        rollback["does"] = "Undo."


def _clear_must_have_audience(catalog):
    audience = ((catalog.get("governance") or {}).get("must_have") or {}).get("for") or {}
    if isinstance(audience, dict) and audience:
        key = next(iter(audience))
        audience[key] = ""
