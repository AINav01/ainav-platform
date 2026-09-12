from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import AGENTS_ALL_URL, MICROSOFT_AGENT_AROUND_IDS, load_catalog, validate_catalog
from ainav.microsoft.agents import public_review, validate_microsoft_agents


def test_agents_review_is_not_the_admit_plane():
    body = public_review()
    assert body["kind"] == "ainav.microsoft.agents.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["inventory_claimed"] is False
    assert body["agent_365_is_product"] is False
    assert body["cloud_agent_can_approve"] is False
    assert body["live"] is False
    assert body["admin_url"] == AGENTS_ALL_URL
    assert "An agent is not a seat" in body["lede"]
    assert [item["id"] for item in body["around"]] == list(MICROSOFT_AGENT_AROUND_IDS)
    assert all(item["claimed"] is False and item["installed"] is None for item in body["around"])
    on_disk = json.loads(Path("institute/agents.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_catalog_refuses_agents_as_admit_or_census():
    cat = copy.deepcopy(load_catalog())
    cat["microsoft_stack"]["agents"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "MICROSOFT_PRODUCT"
    missing = copy.deepcopy(load_catalog())
    missing["microsoft_stack"].pop("agents")
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(missing)
    census = copy.deepcopy(load_catalog())
    census["microsoft_stack"]["agents"]["inventory_claimed"] = True
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(census)
    product = copy.deepcopy(load_catalog())
    product["microsoft_stack"]["agents"]["agent_365_is_product"] = True
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(product)
    actor = copy.deepcopy(load_catalog())
    actor["microsoft_stack"]["agents"]["owner_playbook"]["actor"] = "cursor.cloud_agent"
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(actor)
    types = copy.deepcopy(load_catalog())
    types["microsoft_stack"]["agents"]["types"] = []
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(types)
    href = copy.deepcopy(load_catalog())
    href["microsoft_stack"]["agents"]["lanes"][0]["items"][0]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(href)
    around = copy.deepcopy(load_catalog())
    around["microsoft_stack"]["agents"]["around"][0]["installed"] = True
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(around)
    draft = copy.deepcopy(load_catalog())
    draft["microsoft_stack"]["agents"]["draft"][0]["installed"] = True
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(draft)
    note = copy.deepcopy(load_catalog())
    note["microsoft_stack"]["agents"]["note"] = "Honest agents. An agent is not a seat."
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(note)
    empty_note = copy.deepcopy(load_catalog())
    empty_note["microsoft_stack"]["agents"]["note"] = "Maps only."
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(empty_note)
    claimed_type = copy.deepcopy(load_catalog())
    claimed_type["microsoft_stack"]["agents"]["types"][0]["claimed"] = True
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(claimed_type)
    stack = copy.deepcopy(load_catalog())
    stack["microsoft_stack"] = ["not-a-stack"]
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(stack)
    lede = copy.deepcopy(load_catalog())
    lede["microsoft_stack"]["agents"]["lede"] = "Agents > All is the registry."
    lede["microsoft_stack"]["agents"]["site"] = "Agents > All."
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(lede)
    lede_hole = copy.deepcopy(load_catalog())
    lede_hole["microsoft_stack"]["agents"]["lede"] = "Something else."
    lede_hole["microsoft_stack"]["agents"]["site"] = "Something else."
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(lede_hole)
    lane_items = copy.deepcopy(load_catalog())
    lane_items["microsoft_stack"]["agents"]["lanes"][0]["items"] = []
    with pytest.raises(IntegrityError):
        validate_microsoft_agents(lane_items)
