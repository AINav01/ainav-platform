from __future__ import annotations

import json

import pytest

from agent_gov.errors import IntegrityError
from agent_gov.records import as_sealed, decision_record, verify_chain
from agent_gov.store import default_store
from ainav import catalog as catmod
from ainav.brief_pdf import brief_lines
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import dashboard_html, public_dashboard
from ainav.microsoft.dns import _tls_accepts
from ainav.org import validate_organization
from tests.helpers import sample_action


def _cat() -> dict:
    return json.loads(json.dumps(load_catalog()))


def _reject(fn, catalog, *args):
    with pytest.raises(IntegrityError):
        fn(catalog, *args)


def test_as_dict_and_shape_wrapper():
    with pytest.raises(IntegrityError) as exc:
        catmod._as_dict("x", "lab")
    assert exc.value.reason_code == "CATALOG_SHAPE"
    broken = _cat()
    broken["skus"] = [{}]
    with pytest.raises(IntegrityError) as wrap:
        validate_catalog(broken)
    assert wrap.value.reason_code == "CATALOG_SHAPE"


def test_departments_must_be_objects():
    cat = _cat()
    cat["organization"]["departments"] = ["nope"]
    _reject(validate_organization, cat)


def test_mailbox_law_direct_holes():
    cat = _cat()
    cat["organization"]["contacts"]["invited"]["recorded"] = False
    catmod._validate_mailbox_law(cat)
    cat = _cat()
    cat["organization"]["contacts"]["invited"]["seat_role"] = "owner"
    _reject(catmod._validate_mailbox_law, cat)
    cat = _cat()
    for item in cat["plane_interface"]["authorizations"]:
        if item.get("id") == "seat":
            item["note"] = "1 mailbox / 0 oid. invited, not recorded."
    _reject(catmod._validate_mailbox_law, cat)
    cat = _cat()
    cat["investor"]["letter_body"] = cat["investor"]["letter_body"] + " invited, not recorded"
    _reject(catmod._validate_mailbox_law, cat)


def test_edge_quality_and_walk_direct():
    cat = _cat()
    cat["microsoft_stack"]["edge"] = None
    _reject(catmod._validate_microsoft_edge, cat)
    edge = json.loads(json.dumps(load_catalog()["microsoft_stack"]["edge"]))
    edge["quality"] = None
    _reject(catmod._validate_edge_quality, edge)
    edge = json.loads(json.dumps(load_catalog()["microsoft_stack"]["edge"]))
    edge["quality"]["owner_ssl"] = "x"
    _reject(catmod._validate_edge_quality, edge)
    edge = json.loads(json.dumps(load_catalog()["microsoft_stack"]["edge"]))
    edge["quality"]["owner_ssl"]["visitor_cert_is_not_proof"] = False
    _reject(catmod._validate_edge_quality, edge)
    edge = json.loads(json.dumps(load_catalog()["microsoft_stack"]["edge"]))
    edge["quality"]["owner_ssl"]["flexible"] = True
    _reject(catmod._validate_edge_quality, edge)
    edge = json.loads(json.dumps(load_catalog()["microsoft_stack"]["edge"]))
    edge["quality"]["owner_recorded"] = ["owner"]
    _reject(catmod._validate_edge_quality, edge)
    edge = json.loads(json.dumps(load_catalog()["microsoft_stack"]["edge"]))
    edge["quality"]["verified"] = ["tls"]
    _reject(catmod._validate_edge_quality, edge)
    cat = _cat()
    cat["microsoft_stack"]["walk"] = None
    _reject(catmod._validate_stack_walk, cat)
    cat = _cat()
    cat["microsoft_stack"]["graph"] = {}
    _reject(catmod._validate_graph_owner_consent, cat)
    cat = _cat()
    cat["microsoft_stack"]["graph"]["remove_before_grant"] = []
    _reject(catmod._validate_graph_owner_consent, cat)
    cat = _cat()
    cat["microsoft_stack"]["graph"]["four_reads"] = []
    _reject(catmod._validate_graph_owner_consent, cat)
    cat = _cat()
    cat["microsoft_stack"]["graph"]["note"] = "not live_pin_ok"
    _reject(catmod._validate_graph_owner_consent, cat)


def test_first_principles_refuse_mfa_admit():
    items = list(load_catalog()["expert_review"]["first_principles"])
    _reject(catmod._validate_first_principles, items + ["MFA admits"])
    _reject(catmod._validate_first_principles, ["identify is not admit"])


def test_instrument_history_direct_holes():
    cat = _cat()
    body = cat["plane_interface"]
    well = [item for item in cat["expert_review"]["working_well"] if "gold floor" not in item.lower()]
    cat["expert_review"]["working_well"] = well
    _reject(catmod._validate_instrument_272, cat, body)
    cat = _cat()
    cat["expert_review"]["working_well"] = [
        item for item in cat["expert_review"]["working_well"] if "gaps board" not in item.lower()
    ]
    _reject(catmod._validate_instrument_272, cat, cat["plane_interface"])
    cat = _cat()
    cat["investor"]["traction"] = "Gold floor is rehearsal."
    _reject(catmod._validate_instrument_272, cat, cat["plane_interface"])
    cat = _cat()
    cat["engineering"]["closed_in_tree"] = [
        item for item in cat["engineering"]["closed_in_tree"] if "2.72.0" not in item
    ]
    _reject(catmod._validate_instrument_272, cat, cat["plane_interface"])
    cat = _cat()
    cat["engineering"]["closed_in_tree"] = [
        item for item in cat["engineering"]["closed_in_tree"] if "2.73.0" not in item
    ]
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["proof_day_floor"]["view_shows"] = None
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["proof_day_floor"]["duty_hints"] = None
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["examiner_walk"]["demo"]["included"] = False
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["gaps"]["owner_only_hrefs"] = {"a": "missing"}
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["lab_vs_commercial"] = None
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["board_packet"] = None
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["expert_review"]["working_well"] = [
        item
        for item in cat["expert_review"]["working_well"]
        if "view_shows" not in item.lower() and "catalog-driven" not in item.lower()
    ]
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["expert_review"]["working_well"] = [
        item for item in cat["expert_review"]["working_well"] if "provision spine" not in item.lower()
    ]
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["expert_review"]["working_well"] = [
        item for item in cat["expert_review"]["working_well"] if "board packet" not in item.lower()
    ]
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["expert_review"]["improve"] = [
        item for item in cat["expert_review"]["improve"] if "seat b click" not in item.lower()
    ]
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["gaps"]["owner_only_open"] = ["Graph Writes revoke"]
    _reject(catmod._validate_instrument_274, cat, cat["plane_interface"])
    cat = _cat()
    cat["expert_review"]["working_well"] = [
        item
        for item in cat["expert_review"]["working_well"]
        if "quality probe" not in item.lower() and "live cloudflare quality" not in item.lower()
    ]
    _reject(catmod._validate_instrument_274, cat, cat["plane_interface"])
    cat = _cat()
    for item in cat["expert_review"]["upgrades"]:
        if item.get("n") == 41:
            item["title"] = "Hold"
            item["do"] = "Hold"
    _reject(catmod._validate_instrument_274, cat, cat["plane_interface"])
    cat = _cat()
    cat["engineering"]["closed_in_tree"] = [
        item for item in cat["engineering"]["closed_in_tree"] if "2.75.0" not in item
    ]
    _reject(catmod._validate_instrument_275, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["gaps"]["owner_only_open"] = ["Rocket Loader confirm"]
    _reject(catmod._validate_instrument_275, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["gaps"]["owner_only_open"] = ["seat B click"]
    _reject(catmod._validate_instrument_275, cat, cat["plane_interface"])
    cat = _cat()
    for item in cat["expert_review"]["upgrades"]:
        if item.get("n") == 45:
            item["title"] = "Hold"
            item["do"] = "Hold"
    _reject(catmod._validate_instrument_275, cat, cat["plane_interface"])
    cat = _cat()
    cat["equations"]["interface"] = "pending bind"
    _reject(catmod._validate_instrument_276, cat, cat["plane_interface"])
    cat = _cat()
    for item in cat["expert_review"]["upgrades"]:
        if item.get("n") == 46:
            item["done"] = False
    _reject(catmod._validate_instrument_276, cat, cat["plane_interface"])
    cat = _cat()
    for item in cat["expert_review"]["upgrades"]:
        if item.get("n") == 46:
            item["marks_live_pin"] = True
    _reject(catmod._validate_instrument_276, cat, cat["plane_interface"])


def test_receipt_seq_and_default_store_create():
    rec = decision_record(
        record_type="admit_denied",
        request_id="req_seq_99",
        action_hash="a" * 64,
        action=sample_action(),
        reason_code="SEAT_DISTINCT",
    )
    sealed = dict(as_sealed(rec))
    sealed["seq"] = 9
    with pytest.raises(IntegrityError):
        verify_chain([sealed])
    import agent_gov.store as store

    store._DEFAULT = None
    assert default_store() is not None


def test_brief_rule_block_and_tls_ok(monkeypatch):
    monkeypatch.setattr("ainav.brief_pdf.brief_document", lambda: [{"kind": "rule"}])
    rows = brief_lines()
    assert any(kind == "rule" for kind, _text in rows)

    class Ctx:
        def __init__(self, *args, **kwargs):
            self.check_hostname = False
            self.verify_mode = None
            self.minimum_version = None
            self.maximum_version = None

        def wrap_socket(self, sock, server_hostname=None):
            return sock

    class Sock:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    import ssl

    monkeypatch.setattr("ainav.microsoft.dns.ssl.SSLContext", Ctx)
    monkeypatch.setattr("ainav.microsoft.dns.socket.create_connection", lambda *args, **kwargs: Sock())
    assert _tls_accepts("ainav.institute", ssl.TLSVersion.TLSv1_2) is True


def test_dashboard_html_falls_back_to_floor_rail(monkeypatch):
    body = public_dashboard()
    dash = json.loads(json.dumps(body))
    dash["dashboard"]["first_glance"]["write_rail"] = []
    monkeypatch.setattr("ainav.dashboard.public_dashboard", lambda: dash)
    html = dashboard_html()
    assert "seat" in html.lower()


def test_more_catalog_direct_holes():
    edge = json.loads(json.dumps(load_catalog()["microsoft_stack"]["edge"]))
    edge["quality"]["owner_ssl"]["automatic"] = False
    _reject(catmod._validate_edge_quality, edge)
    cat = _cat()
    cat["microsoft_stack"]["graph"]["sku"] = True
    _reject(catmod._validate_graph_owner_consent, cat)
    cat = _cat()
    cat["microsoft_stack"]["graph"]["owner_recorded"] = ["speech only"]
    _reject(catmod._validate_graph_owner_consent, cat)
    cat = _cat()
    cat["investor"] = None
    _reject(catmod._validate_investor, cat)
    cat = _cat()
    cat["investor"]["executive_summary"] = None
    _reject(catmod._validate_investor, cat)
    cat = _cat()
    cat["investor"]["executive_summary"]["opens"] = "Seat B click still open. Graph Writes revoke."
    _reject(catmod._validate_investor, cat)
    cat = _cat()
    for item in cat["owner_gates"]:
        if item.get("id") == "invite.seat_b":
            item["do"] = str(item.get("do") or "") + " Invited, not recorded."
    _reject(catmod._validate_owner_gates, cat)
    cat = _cat()
    cat["governance"]["thesis"] = "Two dual humans utilize nothing."
    _reject(catmod._validate_governance, cat)
    cat = _cat()
    cat["governance"]["refuse"] = [
        item for item in cat["governance"]["refuse"] if "time-machine" not in str(item).lower()
    ]
    _reject(catmod._validate_governance, cat)
    _reject(catmod._validate_face_kit, None)
    cat = _cat()
    kit = json.loads(json.dumps(((cat.get("plane_interface") or {}).get("floor") or {}).get("public_face") or {}))
    face_kit = kit.get("kit") if isinstance(kit.get("kit"), dict) else None
    if face_kit is None:
        face_kit = json.loads(json.dumps(cat["plane_interface"].get("public_face", {}).get("kit") or cat.get("face_kit") or {}))
    if face_kit:
        face_kit["thesis"] = "kit eleventy identify not a cms"
        _reject(catmod._validate_face_kit, face_kit)
    cat = _cat()
    cat["plane_interface"]["view_assignment"]["thesis"] = "one dashboard fail-closed"
    _reject(catmod._validate_view_assignment, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["view_assignment"]["first_glance"]["lede"] = "org chart"
    _reject(catmod._validate_view_assignment, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["view_assignment"]["matrix"][0] = "nope"
    _reject(catmod._validate_view_assignment, cat, cat["plane_interface"])
    cat = _cat()
    row = cat["plane_interface"]["view_assignment"]["matrix"][0]
    row["org_nodes"].append(row["org_nodes"][0])
    _reject(catmod._validate_view_assignment, cat, cat["plane_interface"])
    cat = _cat()
    for row in cat["plane_interface"]["view_assignment"]["matrix"]:
        if row.get("org_role") != "admit":
            row["may_bind"] = True
            break
    _reject(catmod._validate_view_assignment, cat, cat["plane_interface"])
    cat = _cat()
    mfa = cat["plane_interface"]["view_assignment"]["mfa"]
    mfa["internal"]["mfa_live"] = True
    _reject(catmod._validate_view_assignment, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["view_assignment"]["mfa"]["note"] = "identify"
    _reject(catmod._validate_view_assignment, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["estate"] = None
    _reject(catmod._validate_estate, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["estate"]["thesis"] = "failsafe not the ai two records"
    _reject(catmod._validate_estate, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["proof_day_floor"]["owner_shows"] = [
        item for item in cat["plane_interface"]["proof_day_floor"]["owner_shows"] if item != "board_packet"
    ]
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["plane_interface"]["examiner_walk"]["demo"]["record_id"] = "named.record"
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    for item in cat["expert_review"]["upgrades"]:
        if item.get("n") == 33:
            item["title"] = "Hold"
            item["do"] = "Hold"
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    for item in cat["expert_review"]["upgrades"]:
        if item.get("n") == 33:
            item["done"] = False
    _reject(catmod._validate_instrument_273, cat, cat["plane_interface"])
    cat = _cat()
    cat["equations"]["interface"] = "pending bind gold floor"
    _reject(catmod._validate_instrument_274, cat, cat["plane_interface"])
    cat = _cat()
    for item in cat["expert_review"]["upgrades"]:
        if item.get("n") == 41:
            item["done"] = False
    _reject(catmod._validate_instrument_274, cat, cat["plane_interface"])
    cat = _cat()
    for item in cat["expert_review"]["upgrades"]:
        if item.get("n") == 45:
            item["who"] = "owner"
    _reject(catmod._validate_instrument_275, cat, cat["plane_interface"])
    cat = _cat()
    for item in cat["expert_review"]["upgrades"]:
        if item.get("n") == 46:
            item["title"] = "Hold"
            item["do"] = "Hold"
    _reject(catmod._validate_instrument_276, cat, cat["plane_interface"])
