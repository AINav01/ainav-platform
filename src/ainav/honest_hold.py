"""Honest hold. Recorded. A vault hold is not LIVE_PIN_OK.

Secret names are not wired notify. A catalog must not hold secret values.
Sentinel is not the admit plane. A vault hold is not a seated second human.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_HOLD_FACT_IDS,
    HONEST_HOLD_HREFS,
    HONEST_HOLD_REFUSE_IDS,
    HONEST_HOLD_REFUSE_TEXT,
    HONEST_HOLD_SECRET_NAMES,
    load_catalog,
)

KIND = "ainav.honest.hold.v1"
COMPLEMENT_COUNT = 8


def validate_honest_hold(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_hold")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest hold", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest hold kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "vault_as_live_pin",
        "names_as_wired",
        "secret_in_catalog",
        "sentinel_as_admit",
        "hold_as_seated",
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
        "values_in_tree",
        "ids_in_plane",
        "from_this_plane",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest hold cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest hold stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest hold stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest hold stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#missing":
        raise IntegrityError("honest hold sits on #missing", reason_code="CATALOG_REVIEW")
    if body.get("vault_as_live_pin") is not False:
        raise IntegrityError("a vault hold is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if body.get("names_as_wired") is not False:
        raise IntegrityError("secret names are not wired notify", reason_code="CATALOG_REVIEW")
    if body.get("secret_in_catalog") is not False:
        raise IntegrityError("a catalog must not hold secret values", reason_code="CATALOG_REVIEW")
    if body.get("sentinel_as_admit") is not False:
        raise IntegrityError("Sentinel is not the admit plane", reason_code="CATALOG_REVIEW")
    if body.get("hold_as_seated") is not False:
        raise IntegrityError("a vault hold is not a seated second human", reason_code="CATALOG_REVIEW")
    if body.get("vault_name") != "ainavinc7bfcff":
        raise IntegrityError("honest hold vault name stays ainavinc7bfcff", reason_code="CATALOG_REVIEW")
    if body.get("law_name") != "ainav-mothership":
        raise IntegrityError("honest hold LAW name stays ainav-mothership", reason_code="CATALOG_REVIEW")
    names = body.get("secret_names") or []
    if list(names) != list(HONEST_HOLD_SECRET_NAMES):
        raise IntegrityError("honest hold secret names stay catalog law", reason_code="CATALOG_REVIEW")
    if body.get("sentinel_on_law_owner") is not True:
        raise IntegrityError("honest hold records owner Sentinel on the LAW", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_HOLD_FACT_IDS):
        raise IntegrityError("honest hold stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest hold facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_HOLD_FACT_IDS):
        raise IntegrityError("honest hold facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest hold facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_HOLD_REFUSE_IDS):
        raise IntegrityError("honest hold refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_HOLD_REFUSE_TEXT[key] for key in HONEST_HOLD_REFUSE_IDS}:
        raise IntegrityError("honest hold refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_HOLD_HREFS[key] for key in HONEST_HOLD_REFUSE_IDS}:
        raise IntegrityError("honest hold refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest hold refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest hold" not in note:
        raise IntegrityError("honest hold note keeps honest hold", reason_code="CATALOG_REVIEW")
    if "a vault hold is not live_pin_ok" not in note:
        raise IntegrityError("honest hold note keeps a vault hold is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if "sentinel is not the admit plane" not in note:
        raise IntegrityError("honest hold note keeps Sentinel is not the admit plane", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "a vault hold is not live_pin_ok" not in lede:
        raise IntegrityError("honest hold lede keeps a vault hold is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if "a catalog must not hold secret values" not in lede:
        raise IntegrityError("honest hold lede keeps a catalog must not hold secret values", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest hold" not in site:
        raise IntegrityError("honest hold site keeps honest hold", reason_code="CATALOG_REVIEW")
    if "not a /hold route" not in site:
        raise IntegrityError("honest hold site keeps not a /hold route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest hold site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest hold is not a complement", reason_code="CATALOG_REVIEW")
    owner = (catalog.get("plane_interface") or {}).get("gaps") or {}
    open_items = " ".join(str(item) for item in owner.get("owner_only_open") or [])
    for stem in ("Teams team and channel ids", "SHAREPOINT_SITE_ID", "Sentinel on the existing LAW", "seat B click"):
        if stem not in open_items:
            raise IntegrityError("honest hold cannot close " + stem, reason_code="GAP_OPEN")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("hold playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat a vault hold as LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    services = body.get("services") if isinstance(body.get("services"), dict) else {}
    if services.get("claimed_as_wired") is True:
        raise IntegrityError("honest hold services cannot claim wired", reason_code="CATALOG_REVIEW")
    vault = services.get("vault") if isinstance(services.get("vault"), dict) else {}
    if vault.get("values_in_tree") is True:
        raise IntegrityError("honest hold cannot put secret values in the tree", reason_code="CATALOG_REVIEW")
    sentinel = services.get("sentinel") if isinstance(services.get("sentinel"), dict) else {}
    if sentinel.get("is_admit_plane") is True:
        raise IntegrityError("honest hold cannot treat Sentinel as the admit plane", reason_code="CATALOG_REVIEW")
    if sentinel.get("from_this_plane") is True:
        raise IntegrityError("honest hold cannot claim Sentinel from this plane", reason_code="CATALOG_REVIEW")


def run_hold_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded honest hold. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_hold(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest hold", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "vault_as_live_pin": False,
        "names_as_wired": False,
        "secret_in_catalog": False,
        "sentinel_as_admit": False,
        "hold_as_seated": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_hold"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_hold_certification()
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
        "vault_as_live_pin": False,
        "names_as_wired": False,
        "secret_in_catalog": False,
        "sentinel_as_admit": False,
        "hold_as_seated": False,
        "created": False,
        "live": False,
        "live_pin_ok": False,
        "wired": False,
        "certified": False,
        "considered": True,
        "recorded": True,
        "honest": True,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "href": "#missing",
        "facts": [dict(item) for item in body.get("facts") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "services": dict(body.get("services") or {}),
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "secret_names": list(body.get("secret_names") or []),
        "probes": probes,
        "this_agent_cannot": [
            "Treat a vault hold as LIVE_PIN_OK.",
            "Treat secret names as wired notify.",
            "Put secret values in the catalog.",
            "Treat Sentinel as the admit plane.",
            "Treat a vault hold as a seated second human.",
        ],
    }
