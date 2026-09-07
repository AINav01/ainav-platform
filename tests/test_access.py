from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import HONEST_ACCESS_OPERATOR_IDS, HONEST_ACCESS_REFUSE_TEXT, load_catalog, validate_catalog
from ainav.microsoft.access import public_review, validate_honest_access


def test_access_review_does_not_need_more():
    body = public_review()
    assert body["kind"] == "ainav.honest.access.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["need_more"] is False
    assert body["additional_access_needed"] is False
    assert body["grok_is_product"] is False
    assert body["grok_is_seat"] is False
    assert body["grok_installed"] is None
    assert body["live"] is False
    assert "does not need additional access" in body["lede"].lower()
    assert "grok build is not a seat" in body["lede"].lower()
    assert [item["id"] for item in body["operators"]] == list(HONEST_ACCESS_OPERATOR_IDS)
    assert all(item["installed"] is None and item.get("seat") is not True for item in body["operators"])
    cursor = next(item for item in body["operators"] if item["id"] == "cursor")
    assert cursor["recorded"] is True
    on_disk = json.loads(Path("institute/access.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_catalog_refuses_more_access_and_grok_as_seat():
    cat = copy.deepcopy(load_catalog())
    cat["microsoft_stack"]["access"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "MICROSOFT_PRODUCT"
    missing = copy.deepcopy(load_catalog())
    missing["microsoft_stack"].pop("access")
    with pytest.raises(IntegrityError):
        validate_honest_access(missing)
    need = copy.deepcopy(load_catalog())
    need["microsoft_stack"]["access"]["need_more"] = True
    with pytest.raises(IntegrityError):
        validate_honest_access(need)
    product = copy.deepcopy(load_catalog())
    product["microsoft_stack"]["access"]["grok_is_product"] = True
    with pytest.raises(IntegrityError):
        validate_honest_access(product)
    seat = copy.deepcopy(load_catalog())
    seat["microsoft_stack"]["access"]["grok_is_seat"] = True
    with pytest.raises(IntegrityError):
        validate_honest_access(seat)
    installed = copy.deepcopy(load_catalog())
    installed["microsoft_stack"]["access"]["grok_installed"] = True
    with pytest.raises(IntegrityError):
        validate_honest_access(installed)
    actor = copy.deepcopy(load_catalog())
    actor["microsoft_stack"]["access"]["owner_playbook"]["actor"] = "cursor.cloud_agent"
    with pytest.raises(IntegrityError):
        validate_honest_access(actor)
    cannot = copy.deepcopy(load_catalog())
    cannot["microsoft_stack"]["access"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_access(cannot)
    href = copy.deepcopy(load_catalog())
    href["microsoft_stack"]["access"]["lanes"][0]["items"][0]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        validate_honest_access(href)
    recorded = copy.deepcopy(load_catalog())
    recorded["microsoft_stack"]["access"]["operators"][1]["recorded"] = True
    with pytest.raises(IntegrityError):
        validate_honest_access(recorded)
    cursor = copy.deepcopy(load_catalog())
    cursor["microsoft_stack"]["access"]["operators"][0]["recorded"] = False
    with pytest.raises(IntegrityError):
        validate_honest_access(cursor)
    note = copy.deepcopy(load_catalog())
    note["microsoft_stack"]["access"]["note"] = "Honest access. Grok Build is mapped."
    with pytest.raises(IntegrityError):
        validate_honest_access(note)
    lede = copy.deepcopy(load_catalog())
    lede["microsoft_stack"]["access"]["lede"] = "Honest access. This plane is mapped."
    with pytest.raises(IntegrityError):
        validate_honest_access(lede)
    refuse = copy.deepcopy(load_catalog())
    refuse_lane = next(lane for lane in refuse["microsoft_stack"]["access"]["lanes"] if lane["id"] == "refuse")
    refuse_lane["items"][0]["refuse_text"] = "Refused. Ask James for admin."
    with pytest.raises(IntegrityError):
        validate_honest_access(refuse)
    assert HONEST_ACCESS_REFUSE_TEXT["ask_admin"].startswith("Refused.")
    stack = copy.deepcopy(load_catalog())
    stack["microsoft_stack"] = "not-a-stack"
    with pytest.raises(IntegrityError):
        validate_honest_access(stack)
    kind = copy.deepcopy(load_catalog())
    kind["microsoft_stack"]["access"]["kind"] = "ainav.honest.access.v0"
    with pytest.raises(IntegrityError):
        validate_honest_access(kind)
    lanes = copy.deepcopy(load_catalog())
    lanes["microsoft_stack"]["access"]["lanes"] = []
    with pytest.raises(IntegrityError):
        validate_honest_access(lanes)
    lane_items = copy.deepcopy(load_catalog())
    lane_items["microsoft_stack"]["access"]["lanes"][0]["items"] = []
    with pytest.raises(IntegrityError):
        validate_honest_access(lane_items)
    refuse_ids = copy.deepcopy(load_catalog())
    refuse_lane = next(lane for lane in refuse_ids["microsoft_stack"]["access"]["lanes"] if lane["id"] == "refuse")
    refuse_lane["items"][0]["refuse"] = False
    with pytest.raises(IntegrityError):
        validate_honest_access(refuse_ids)
    missing_need = copy.deepcopy(load_catalog())
    missing_need["microsoft_stack"]["access"].pop("need_more")
    with pytest.raises(IntegrityError):
        validate_honest_access(missing_need)
    seat_op = copy.deepcopy(load_catalog())
    seat_op["microsoft_stack"]["access"]["operators"][0]["seat"] = True
    with pytest.raises(IntegrityError):
        validate_honest_access(seat_op)
    installed = copy.deepcopy(load_catalog())
    installed["microsoft_stack"]["access"]["operators"][2]["installed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_access(installed)
    grok_note = copy.deepcopy(load_catalog())
    grok_note["microsoft_stack"]["access"]["note"] = (
        "Honest access. This Cloud Agent does not need Microsoft admin."
    )
    with pytest.raises(IntegrityError):
        validate_honest_access(grok_note)
    grok_lede = copy.deepcopy(load_catalog())
    grok_lede["microsoft_stack"]["access"]["lede"] = (
        "Honest access. This plane does not need additional access. Mapping stays a map."
    )
    with pytest.raises(IntegrityError):
        validate_honest_access(grok_lede)
    lanes = copy.deepcopy(load_catalog())
    lanes["microsoft_stack"]["access"]["operators"] = []
    with pytest.raises(IntegrityError):
        validate_honest_access(lanes)
    honest = copy.deepcopy(load_catalog())
    honest["microsoft_stack"]["access"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_access(honest)
    sku = copy.deepcopy(load_catalog())
    sku["microsoft_stack"]["access"]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_access(sku)
