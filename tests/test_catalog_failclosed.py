from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog


def test_mailbox_law_refuses_stale_seat_note_and_letter():
    cat = load_catalog()
    stale = copy.deepcopy(cat)
    for item in stale["plane_interface"]["authorizations"]:
        if item["id"] == "seat":
            item["note"] = "Own Entra object id. Own click. 0 recorded / 1 invited."
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(stale)
    assert exc.value.reason_code == "CATALOG_PLANE"
    letter = copy.deepcopy(cat)
    letter["investor"]["letter_body"] = (
        "I trust you. Seat B. Invited, not recorded. Not stock. Not a priced round. "
        "Mailbox recorded: chodnett@ainav.institute. I will not ask. Recognized revenue is $0."
    )
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(letter)
    assert exc2.value.reason_code == "CATALOG_INVESTOR"
    role = copy.deepcopy(cat)
    role["organization"]["contacts"]["invited"]["seat_role"] = "invented"
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(role)
    assert exc3.value.reason_code == "ORG_SECOND_OFFICER"
    gate = copy.deepcopy(cat)
    for item in gate["owner_gates"]:
        if item["id"] == "invite.seat_b":
            item["do"] = "Ask someone. Invited, not recorded."
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(gate)
    assert exc4.value.reason_code == "ORG_SECOND_OFFICER"
    glance = copy.deepcopy(cat)
    glance["plane_interface"]["floor"]["first_glance"]["lede"] = "A company exists."
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(glance)
    assert exc5.value.reason_code == "CATALOG_PLANE"
    face = copy.deepcopy(cat)
    face["plane_interface"]["floor"]["public_face"]["cms"] = True
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(face)
    assert exc6.value.reason_code == "CATALOG_PLANE"
    launch = copy.deepcopy(cat)
    launch["plane_interface"]["floor"]["public_face"]["launch"] = True
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(launch)
    assert exc7.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    nav = copy.deepcopy(cat)
    nav["plane_interface"]["floor"]["public_face"]["primary"][2]["label"] = "Finance"
    with pytest.raises(IntegrityError) as exc8:
        validate_catalog(nav)
    assert exc8.value.reason_code == "CATALOG_PLANE"
    rail = copy.deepcopy(cat)
    rail["plane_interface"]["floor"]["first_glance"]["write_rail"] = []
    with pytest.raises(IntegrityError) as exc9:
        validate_catalog(rail)
    assert exc9.value.reason_code == "CATALOG_PLANE"


def test_catalog_refuses_live_proof_pin_sandbox_and_buyer_inbox():
    cat = load_catalog()
    proof = copy.deepcopy(cat)
    proof["proof_day"]["signed_l1"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(proof)
    assert exc.value.reason_code == "SIGNED_L1_OPEN"
    minutes = copy.deepcopy(cat)
    minutes["proof_day"]["minutes"] = 60
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(minutes)
    assert exc2.value.reason_code == "CATALOG_PROOF_DAY"
    pin = copy.deepcopy(cat)
    pin["next_pin"]["production"] = True
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(pin)
    assert exc3.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    live_pin = copy.deepcopy(cat)
    live_pin["next_pin"]["live_pin_ok"] = True
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(live_pin)
    assert exc4.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    sandbox = copy.deepcopy(cat)
    sandbox["sandbox_evidence"]["live"] = True
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(sandbox)
    assert exc5.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    inbox = copy.deepcopy(cat)
    inbox["buyer"]["contact_email"] = "invented@example.com"
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(inbox)
    assert exc6.value.reason_code == "BUYER_INBOX"
    seats = copy.deepcopy(cat)
    seats["buyer"]["seats"] = ["invented"]
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(seats)
    assert exc7.value.reason_code == "CATALOG_BUYER"


def test_catalog_refuses_finance_live_upgrade_pin_and_empty_gate():
    cat = load_catalog()
    rev = copy.deepcopy(cat)
    rev["financial_model"]["recognized_revenue"] = 1
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(rev)
    assert exc.value.reason_code == "CATALOG_FINANCE"
    upgrade = copy.deepcopy(cat)
    upgrade["expert_review"]["upgrades"][0]["marks_live_pin"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(upgrade)
    assert exc2.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    gate = copy.deepcopy(cat)
    gate["owner_gates"][0]["url"] = ""
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(gate)
    assert exc3.value.reason_code == "CATALOG_ORG"
    rehearsal = copy.deepcopy(cat)
    rehearsal["plane_interface"]["rehearsal"]["named_humans"] = True
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(rehearsal)
    assert exc4.value.reason_code == "CATALOG_PLANE"
    clock = copy.deepcopy(cat)
    clock["plane_interface"]["clock"]["pending_binds"] = 2
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(clock)
    assert exc5.value.reason_code == "CATALOG_PLANE"
    repo = copy.deepcopy(cat)
    repo["repositories"][0]["live"] = True
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(repo)
    assert exc6.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    bake = copy.deepcopy(cat)
    bake["expert_review"]["success"]["bake_off"]["we_win"] = []
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(bake)
    assert exc7.value.reason_code == "CATALOG_REVIEW"
    walk = copy.deepcopy(cat)
    walk["expert_review"]["success"]["qualify"]["walk_away"] = ["invented"]
    with pytest.raises(IntegrityError) as exc8:
        validate_catalog(walk)
    assert exc8.value.reason_code == "CATALOG_REVIEW"
    pin = copy.deepcopy(cat)
    pin["expert_review"]["success"]["live_pin_ok"] = True
    with pytest.raises(IntegrityError) as exc9:
        validate_catalog(pin)
    assert exc9.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    seat = copy.deepcopy(cat)
    seat["expert_review"]["success"]["seat_b"]["mailbox"] = "invented@example.com"
    with pytest.raises(IntegrityError) as exc10:
        validate_catalog(seat)
    assert exc10.value.reason_code == "ORG_SECOND_OFFICER"
    walk = copy.deepcopy(cat)
    walk["microsoft_stack"]["walk"]["path"][0]["url"] = "http://localhost"
    with pytest.raises(IntegrityError) as exc11:
        validate_catalog(walk)
    assert exc11.value.reason_code == "CATALOG_STACK"
    pin = copy.deepcopy(cat)
    pin["microsoft_stack"]["walk"]["live_pin_ok"] = True
    with pytest.raises(IntegrityError) as exc12:
        validate_catalog(pin)
    assert exc12.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
