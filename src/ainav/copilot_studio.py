"""Honest Copilot Studio. Considered. Not Job C.

Copilot Studio is not a SKU. Copilot Studio is not the admit plane.
A human looked is not dual admit. Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_COPILOT_STUDIO_FACT_IDS,
    HONEST_COPILOT_STUDIO_HREFS,
    HONEST_COPILOT_STUDIO_REFUSE_IDS,
    HONEST_COPILOT_STUDIO_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.copilot_studio.v1"
COMPLEMENT_COUNT = 8


def validate_honest_copilot_studio(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_copilot_studio")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest Copilot Studio", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest Copilot Studio kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "cms",
        "host",
        "is_host",
        "apex",
        "closes_dual_admit",
        "wired",
        "claimed",
        "certified",
        "live",
        "live_pin_ok",
        "launch",
        "created",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest Copilot Studio cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest Copilot Studio stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest Copilot Studio stays considered", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#success":
        raise IntegrityError("honest Copilot Studio sits on #success", reason_code="CATALOG_REVIEW")
    if body.get("is_job_c") is not False:
        raise IntegrityError("Copilot Studio is not Job C", reason_code="CATALOG_REVIEW")
    if body.get("is_sku") is not False:
        raise IntegrityError("Copilot Studio is not a SKU", reason_code="CATALOG_REVIEW")
    if body.get("is_admit_plane") is not False:
        raise IntegrityError("Copilot Studio is not the admit plane", reason_code="CATALOG_REVIEW")
    if body.get("is_complement") is not False:
        raise IntegrityError("Copilot Studio is not a complement", reason_code="CATALOG_REVIEW")
    if body.get("is_seat") is not False:
        raise IntegrityError("Copilot Studio RFI is not seat B", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_COPILOT_STUDIO_FACT_IDS):
        raise IntegrityError("honest Copilot Studio stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest Copilot Studio facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_COPILOT_STUDIO_FACT_IDS):
        raise IntegrityError("honest Copilot Studio facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest Copilot Studio facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_COPILOT_STUDIO_REFUSE_IDS):
        raise IntegrityError("honest Copilot Studio refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_COPILOT_STUDIO_REFUSE_TEXT[key] for key in HONEST_COPILOT_STUDIO_REFUSE_IDS}:
        raise IntegrityError("honest Copilot Studio refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_COPILOT_STUDIO_HREFS[key] for key in HONEST_COPILOT_STUDIO_REFUSE_IDS}:
        raise IntegrityError("honest Copilot Studio refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest Copilot Studio refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest copilot studio" not in note:
        raise IntegrityError("honest Copilot Studio note keeps honest Copilot Studio", reason_code="CATALOG_REVIEW")
    if "copilot studio is not job c" not in note:
        raise IntegrityError("honest Copilot Studio note keeps Copilot Studio is not Job C", reason_code="CATALOG_REVIEW")
    if "copilot studio is not a sku" not in note:
        raise IntegrityError("honest Copilot Studio note keeps Copilot Studio is not a SKU", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "human looked" not in lede:
        raise IntegrityError("honest Copilot Studio lede keeps a human looked", reason_code="CATALOG_REVIEW")
    if "copilot studio is not job c" not in lede:
        raise IntegrityError("honest Copilot Studio lede keeps Copilot Studio is not Job C", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest copilot studio" not in site:
        raise IntegrityError("honest Copilot Studio site keeps honest Copilot Studio", reason_code="CATALOG_REVIEW")
    if "not a /copilot-studio route" not in site:
        raise IntegrityError("honest Copilot Studio site keeps not a /copilot-studio route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest Copilot Studio site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = ((catalog.get("connections") or {}).get("complements") or [])
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Copilot Studio is not a complement", reason_code="CATALOG_REVIEW")
    if any("copilot" in str(item.get("id") or "").lower() for item in complements):
        raise IntegrityError("Copilot Studio is not a complement", reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("Copilot Studio playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat Copilot Studio as Job C", reason_code="CATALOG_REVIEW")


def run_copilot_studio_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree consider. No live HTTP. Never Job C. Never a SKU. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_copilot_studio(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after Copilot Studio consider", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "is_job_c": False,
        "is_sku": False,
        "is_admit_plane": False,
        "is_complement": False,
        "is_seat": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_copilot_studio"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_copilot_studio_certification()
    cat = load_catalog()
    return {
        "kind": KIND,
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "product": body["product"],
        "microsoft_product": body.get("microsoft_product"),
        "is_sku": False,
        "fourth_sku": False,
        "is_connection": False,
        "is_complement": False,
        "is_admit_plane": False,
        "is_job_c": False,
        "is_seat": False,
        "created": False,
        "live": False,
        "live_pin_ok": False,
        "wired": False,
        "certified": False,
        "considered": True,
        "honest": True,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "href": "#success",
        "facts": [dict(item) for item in body.get("facts") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat Copilot Studio as Job C.",
            "Treat Copilot Studio as a SKU.",
            "Treat Copilot Studio as the admit plane.",
            "Treat Copilot Studio as a complement.",
            "Treat Copilot Studio as seat B.",
        ],
    }
