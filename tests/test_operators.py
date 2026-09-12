from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import HONEST_OPERATOR_IDS, HONEST_OPERATOR_REFUSE_TEXT, HONEST_OPERATOR_ROLES, load_catalog, validate_catalog
from ainav.microsoft.operators import public_review, validate_honest_operators


def test_operators_review_keeps_three_way():
    body = public_review()
    assert body["kind"] == "ainav.honest.operators.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["swap"] is False
    assert body["grok_is_recorded"] is False
    assert body["bot_is_operator"] is False
    assert body["bot_is_admit"] is False
    assert body["live"] is False
    assert "cursor is recorded" in body["lede"].lower()
    assert "grok build is mapped" in body["lede"].lower()
    assert "grok bot is not admit" in body["lede"].lower()
    assert [item["id"] for item in body["three"]] == list(HONEST_OPERATOR_IDS)
    assert {item["id"]: item["role"] for item in body["three"]} == dict(HONEST_OPERATOR_ROLES)
    assert all(item["installed"] is None and item.get("seat") is not True for item in body["three"])
    cursor = next(item for item in body["three"] if item["id"] == "cursor")
    grok_bot = next(item for item in body["three"] if item["id"] == "grok_bot")
    assert cursor["recorded"] is True
    assert grok_bot["operator"] is not True
    assert "Swap Cursor for Grok Build as the recorded operator." in body["this_agent_cannot"]
    on_disk = json.loads(Path("institute/operators.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_catalog_refuses_operator_swap_and_bot_as_operator():
    cat = copy.deepcopy(load_catalog())
    cat["microsoft_stack"]["operators"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "MICROSOFT_PRODUCT"
    missing = copy.deepcopy(load_catalog())
    missing["microsoft_stack"].pop("operators")
    with pytest.raises(IntegrityError):
        validate_honest_operators(missing)
    swap = copy.deepcopy(load_catalog())
    swap["microsoft_stack"]["operators"]["swap"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(swap)
    recorded = copy.deepcopy(load_catalog())
    recorded["microsoft_stack"]["operators"]["grok_is_recorded"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(recorded)
    bot = copy.deepcopy(load_catalog())
    bot["microsoft_stack"]["operators"]["bot_is_operator"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(bot)
    admit = copy.deepcopy(load_catalog())
    admit["microsoft_stack"]["operators"]["bot_is_admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(admit)
    actor = copy.deepcopy(load_catalog())
    actor["microsoft_stack"]["operators"]["owner_playbook"]["actor"] = "cursor.cloud_agent"
    with pytest.raises(IntegrityError):
        validate_honest_operators(actor)
    cannot = copy.deepcopy(load_catalog())
    cannot["microsoft_stack"]["operators"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_operators(cannot)
    href = copy.deepcopy(load_catalog())
    href["microsoft_stack"]["operators"]["three"][0]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        validate_honest_operators(href)
    other = copy.deepcopy(load_catalog())
    other["microsoft_stack"]["operators"]["three"][1]["recorded"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(other)
    cursor = copy.deepcopy(load_catalog())
    cursor["microsoft_stack"]["operators"]["three"][0]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_operators(cursor)
    missing_swap = copy.deepcopy(load_catalog())
    missing_swap["microsoft_stack"]["operators"].pop("swap")
    with pytest.raises(IntegrityError):
        validate_honest_operators(missing_swap)
    note = copy.deepcopy(load_catalog())
    note["microsoft_stack"]["operators"]["note"] = "Honest operators. Grok Build is mapped."
    with pytest.raises(IntegrityError):
        validate_honest_operators(note)
    note_title = copy.deepcopy(load_catalog())
    note_title["microsoft_stack"]["operators"]["note"] = (
        "Cursor is recorded. Grok Build is mapped. Grok bot is not admit."
    )
    with pytest.raises(IntegrityError):
        validate_honest_operators(note_title)
    lede = copy.deepcopy(load_catalog())
    lede["microsoft_stack"]["operators"]["lede"] = "Honest operators. Cursor is recorded."
    with pytest.raises(IntegrityError):
        validate_honest_operators(lede)
    lede_cursor = copy.deepcopy(load_catalog())
    lede_cursor["microsoft_stack"]["operators"]["lede"] = (
        "Grok Build is mapped. Grok bot is not admit. They are not interchangeable."
    )
    with pytest.raises(IntegrityError):
        validate_honest_operators(lede_cursor)
    refuse = copy.deepcopy(load_catalog())
    refuse["microsoft_stack"]["operators"]["refuse"][0]["refuse_text"] = "Refused. Ask James to swap."
    with pytest.raises(IntegrityError):
        validate_honest_operators(refuse)
    assert HONEST_OPERATOR_REFUSE_TEXT["swap_operator"].startswith("Refused.")
    stack = copy.deepcopy(load_catalog())
    stack["microsoft_stack"] = "not-a-stack"
    with pytest.raises(IntegrityError):
        validate_honest_operators(stack)
    kind = copy.deepcopy(load_catalog())
    kind["microsoft_stack"]["operators"]["kind"] = "ainav.honest.operators.v0"
    with pytest.raises(IntegrityError):
        validate_honest_operators(kind)
    three = copy.deepcopy(load_catalog())
    three["microsoft_stack"]["operators"]["three"] = []
    with pytest.raises(IntegrityError):
        validate_honest_operators(three)
    refuse_ids = copy.deepcopy(load_catalog())
    refuse_ids["microsoft_stack"]["operators"]["refuse"][0]["refuse"] = False
    with pytest.raises(IntegrityError):
        validate_honest_operators(refuse_ids)
    honest = copy.deepcopy(load_catalog())
    honest["microsoft_stack"]["operators"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_operators(honest)
    sku = copy.deepcopy(load_catalog())
    sku["microsoft_stack"]["operators"]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(sku)
    seat = copy.deepcopy(load_catalog())
    seat["microsoft_stack"]["operators"]["three"][0]["seat"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(seat)
    installed = copy.deepcopy(load_catalog())
    installed["microsoft_stack"]["operators"]["three"][2]["installed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_operators(installed)
    role = copy.deepcopy(load_catalog())
    role["microsoft_stack"]["operators"]["three"][1]["role"] = "recorded"
    with pytest.raises(IntegrityError):
        validate_honest_operators(role)
    bot_op = copy.deepcopy(load_catalog())
    bot_op["microsoft_stack"]["operators"]["three"][2]["operator"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(bot_op)
    bot_admit = copy.deepcopy(load_catalog())
    bot_admit["microsoft_stack"]["operators"]["three"][2]["admit"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(bot_admit)
    operating = copy.deepcopy(load_catalog())
    operating["operating"]["operator"] = "grok.build"
    with pytest.raises(IntegrityError):
        validate_honest_operators(operating)
    note_mapped = copy.deepcopy(load_catalog())
    note_mapped["microsoft_stack"]["operators"]["note"] = (
        "Honest operators. Cursor is recorded. Grok bot is not admit."
    )
    with pytest.raises(IntegrityError):
        validate_honest_operators(note_mapped)
    note_bot = copy.deepcopy(load_catalog())
    note_bot["microsoft_stack"]["operators"]["note"] = (
        "Honest operators. Cursor is recorded. Grok Build is mapped."
    )
    with pytest.raises(IntegrityError):
        validate_honest_operators(note_bot)
    lede_bot = copy.deepcopy(load_catalog())
    lede_bot["microsoft_stack"]["operators"]["lede"] = (
        "Consider Cursor, Grok Build, and Grok bot. Cursor is recorded. Grok Build is mapped."
    )
    with pytest.raises(IntegrityError):
        validate_honest_operators(lede_bot)
    refuse_href = copy.deepcopy(load_catalog())
    refuse_href["microsoft_stack"]["operators"]["refuse"][0]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        validate_honest_operators(refuse_href)
    owner = copy.deepcopy(load_catalog())
    owner["microsoft_stack"]["operators"]["owner_is_operator"] = True
    with pytest.raises(IntegrityError):
        validate_honest_operators(owner)
    cards = copy.deepcopy(load_catalog())
    cards["microsoft_stack"]["operators"]["three"] = ["cursor", "grok_build", "grok_bot"]
    with pytest.raises(IntegrityError):
        validate_honest_operators(cards)
    operating_shape = copy.deepcopy(load_catalog())
    operating_shape["operating"] = "not-operating"
    with pytest.raises(IntegrityError):
        validate_honest_operators(operating_shape)
