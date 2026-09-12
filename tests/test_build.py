from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import HONEST_BUILD_IDS, HONEST_BUILD_REFUSE_TEXT, HONEST_BUILD_ROLES, load_catalog, validate_catalog
from ainav.microsoft.build import public_review, validate_honest_build


def test_build_review_does_not_need_full_access():
    body = public_review()
    assert body["kind"] == "ainav.honest.build.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["need_full"] is False
    assert body["full_access_needed"] is False
    assert body["more_secrets_needed"] is False
    assert body["twin_is_launch"] is False
    assert body["packs_are_skus"] is False
    assert body["live"] is False
    assert "does not need full access" in body["lede"].lower()
    assert "twin is not launch" in body["lede"].lower()
    assert "packs, modules, and repositories are not skus" in body["lede"].lower()
    assert [item["id"] for item in body["three"]] == list(HONEST_BUILD_IDS)
    assert {item["id"]: item["role"] for item in body["three"]} == dict(HONEST_BUILD_ROLES)
    assert all(item["installed"] is None and item.get("seat") is not True for item in body["three"])
    assert "Request full access as this Cloud Agent." in body["this_agent_cannot"]
    on_disk = json.loads(Path("institute/build.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_catalog_refuses_full_access_and_twin_as_launch():
    cat = copy.deepcopy(load_catalog())
    cat["microsoft_stack"]["build"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "MICROSOFT_PRODUCT"
    missing = copy.deepcopy(load_catalog())
    missing["microsoft_stack"].pop("build")
    with pytest.raises(IntegrityError):
        validate_honest_build(missing)
    need = copy.deepcopy(load_catalog())
    need["microsoft_stack"]["build"]["need_full"] = True
    with pytest.raises(IntegrityError):
        validate_honest_build(need)
    twin = copy.deepcopy(load_catalog())
    twin["microsoft_stack"]["build"]["twin_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_honest_build(twin)
    packs = copy.deepcopy(load_catalog())
    packs["microsoft_stack"]["build"]["packs_are_skus"] = True
    with pytest.raises(IntegrityError):
        validate_honest_build(packs)
    secrets = copy.deepcopy(load_catalog())
    secrets["microsoft_stack"]["build"]["more_secrets_needed"] = True
    with pytest.raises(IntegrityError):
        validate_honest_build(secrets)
    actor = copy.deepcopy(load_catalog())
    actor["microsoft_stack"]["build"]["owner_playbook"]["actor"] = "cursor.cloud_agent"
    with pytest.raises(IntegrityError):
        validate_honest_build(actor)
    cannot = copy.deepcopy(load_catalog())
    cannot["microsoft_stack"]["build"]["owner_playbook"]["cannot_be_done_by"] = "james"
    with pytest.raises(IntegrityError):
        validate_honest_build(cannot)
    href = copy.deepcopy(load_catalog())
    href["microsoft_stack"]["build"]["three"][0]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        validate_honest_build(href)
    note = copy.deepcopy(load_catalog())
    note["microsoft_stack"]["build"]["note"] = "Honest build. Grok Build is mapped."
    with pytest.raises(IntegrityError):
        validate_honest_build(note)
    lede = copy.deepcopy(load_catalog())
    lede["microsoft_stack"]["build"]["lede"] = "Honest build. Cursor is recorded."
    with pytest.raises(IntegrityError):
        validate_honest_build(lede)
    refuse = copy.deepcopy(load_catalog())
    refuse["microsoft_stack"]["build"]["refuse"][0]["refuse_text"] = "Refused. Ask James for admin."
    with pytest.raises(IntegrityError):
        validate_honest_build(refuse)
    assert HONEST_BUILD_REFUSE_TEXT["full_access_as_admit"].startswith("Refused.")
    stack = copy.deepcopy(load_catalog())
    stack["microsoft_stack"] = "not-a-stack"
    with pytest.raises(IntegrityError):
        validate_honest_build(stack)
    kind = copy.deepcopy(load_catalog())
    kind["microsoft_stack"]["build"]["kind"] = "ainav.honest.build.v0"
    with pytest.raises(IntegrityError):
        validate_honest_build(kind)
    three = copy.deepcopy(load_catalog())
    three["microsoft_stack"]["build"]["three"] = []
    with pytest.raises(IntegrityError):
        validate_honest_build(three)
    refuse_ids = copy.deepcopy(load_catalog())
    refuse_ids["microsoft_stack"]["build"]["refuse"][0]["refuse"] = False
    with pytest.raises(IntegrityError):
        validate_honest_build(refuse_ids)
    honest = copy.deepcopy(load_catalog())
    honest["microsoft_stack"]["build"]["honest"] = False
    with pytest.raises(IntegrityError):
        validate_honest_build(honest)
    sku = copy.deepcopy(load_catalog())
    sku["microsoft_stack"]["build"]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_honest_build(sku)
    seat = copy.deepcopy(load_catalog())
    seat["microsoft_stack"]["build"]["three"][0]["seat"] = True
    with pytest.raises(IntegrityError):
        validate_honest_build(seat)
    installed = copy.deepcopy(load_catalog())
    installed["microsoft_stack"]["build"]["three"][2]["installed"] = False
    with pytest.raises(IntegrityError):
        validate_honest_build(installed)
    role = copy.deepcopy(load_catalog())
    role["microsoft_stack"]["build"]["three"][1]["role"] = "have"
    with pytest.raises(IntegrityError):
        validate_honest_build(role)
    operating = copy.deepcopy(load_catalog())
    operating["operating"]["operator"] = "grok.build"
    with pytest.raises(IntegrityError):
        validate_honest_build(operating)
    note_full = copy.deepcopy(load_catalog())
    note_full["microsoft_stack"]["build"]["note"] = (
        "Honest build. The twin is not launch. Packs, modules, and repositories are not SKUs."
    )
    with pytest.raises(IntegrityError):
        validate_honest_build(note_full)
    note_twin = copy.deepcopy(load_catalog())
    note_twin["microsoft_stack"]["build"]["note"] = (
        "Honest build. This plane does not need full access. Packs, modules, and repositories are not SKUs."
    )
    with pytest.raises(IntegrityError):
        validate_honest_build(note_twin)
    note_packs = copy.deepcopy(load_catalog())
    note_packs["microsoft_stack"]["build"]["note"] = (
        "Honest build. This plane does not need full access. The twin is not launch."
    )
    with pytest.raises(IntegrityError):
        validate_honest_build(note_packs)
    lede_full = copy.deepcopy(load_catalog())
    lede_full["microsoft_stack"]["build"]["lede"] = (
        "The twin is not launch. Packs, modules, and repositories are not SKUs."
    )
    with pytest.raises(IntegrityError):
        validate_honest_build(lede_full)
    lede_twin = copy.deepcopy(load_catalog())
    lede_twin["microsoft_stack"]["build"]["lede"] = (
        "This plane does not need full access. Packs, modules, and repositories are not SKUs."
    )
    with pytest.raises(IntegrityError):
        validate_honest_build(lede_twin)
    lede_packs = copy.deepcopy(load_catalog())
    lede_packs["microsoft_stack"]["build"]["lede"] = (
        "This plane does not need full access. The twin is not launch."
    )
    with pytest.raises(IntegrityError):
        validate_honest_build(lede_packs)
    refuse_href = copy.deepcopy(load_catalog())
    refuse_href["microsoft_stack"]["build"]["refuse"][0]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        validate_honest_build(refuse_href)
    cards = copy.deepcopy(load_catalog())
    cards["microsoft_stack"]["build"]["three"] = ["enough", "build", "launch"]
    with pytest.raises(IntegrityError):
        validate_honest_build(cards)
    missing_need = copy.deepcopy(load_catalog())
    missing_need["microsoft_stack"]["build"].pop("need_full")
    with pytest.raises(IntegrityError):
        validate_honest_build(missing_need)
    missing_twin = copy.deepcopy(load_catalog())
    missing_twin["microsoft_stack"]["build"].pop("twin_is_launch")
    with pytest.raises(IntegrityError):
        validate_honest_build(missing_twin)
    note_title = copy.deepcopy(load_catalog())
    note_title["microsoft_stack"]["build"]["note"] = (
        "This plane does not need full access. The twin is not launch. "
        "Packs, modules, and repositories are not SKUs."
    )
    with pytest.raises(IntegrityError):
        validate_honest_build(note_title)
    operating_shape = copy.deepcopy(load_catalog())
    operating_shape["operating"] = "not-operating"
    with pytest.raises(IntegrityError):
        validate_honest_build(operating_shape)
