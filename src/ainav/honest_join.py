"""Honest join. Recorded. The join is not launch.

The stitched firm is not LIVE_PIN_OK. Licensed-not-wired is not a wired firm.
Management and operations are not closed from this plane.
A certified simulation is not a running firm.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_JOIN_FACT_IDS,
    HONEST_JOIN_HOP_HREFS,
    HONEST_JOIN_HOP_IDS,
    HONEST_JOIN_HREFS,
    HONEST_JOIN_REFUSE_IDS,
    HONEST_JOIN_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.join.v1"
COMPLEMENT_COUNT = 8


def validate_honest_join(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_join")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest join", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest join kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "join_as_launch",
        "stitch_as_live_pin",
        "licensed_as_wired_firm",
        "manage_ops_as_closed",
        "certify_as_running",
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
        "signed_l1",
        "named_client",
        "billing_provider",
        "running_firm",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest join cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest join stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest join stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest join stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#firm":
        raise IntegrityError("honest join sits on #firm", reason_code="CATALOG_REVIEW")
    if body.get("join_as_launch") is not False:
        raise IntegrityError("the join is not launch", reason_code="CATALOG_REVIEW")
    if body.get("stitch_as_live_pin") is not False:
        raise IntegrityError("the stitched firm is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if body.get("licensed_as_wired_firm") is not False:
        raise IntegrityError("licensed-not-wired is not a wired firm", reason_code="CATALOG_REVIEW")
    if body.get("manage_ops_as_closed") is not False:
        raise IntegrityError("management and operations are not closed from this plane", reason_code="CATALOG_REVIEW")
    if body.get("certify_as_running") is not False:
        raise IntegrityError("a certified simulation is not a running firm", reason_code="CATALOG_REVIEW")
    hops = body.get("hops") or []
    if not isinstance(hops, list) or [item.get("id") for item in hops if isinstance(item, dict)] != list(
        HONEST_JOIN_HOP_IDS
    ):
        raise IntegrityError("honest join hops stay catalog law", reason_code="CATALOG_REVIEW")
    hop_hrefs = {item.get("id"): item.get("href") for item in hops if isinstance(item, dict)}
    if hop_hrefs != {key: HONEST_JOIN_HOP_HREFS[key] for key in HONEST_JOIN_HOP_IDS}:
        raise IntegrityError("honest join hop hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("closed") is True or item.get("live") is True for item in hops if isinstance(item, dict)):
        raise IntegrityError("honest join hops are not closed or live", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_JOIN_FACT_IDS):
        raise IntegrityError("honest join stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest join facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_JOIN_FACT_IDS):
        raise IntegrityError("honest join facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest join facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_JOIN_REFUSE_IDS):
        raise IntegrityError("honest join refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_JOIN_REFUSE_TEXT[key] for key in HONEST_JOIN_REFUSE_IDS}:
        raise IntegrityError("honest join refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_JOIN_HREFS[key] for key in HONEST_JOIN_REFUSE_IDS}:
        raise IntegrityError("honest join refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest join refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest join" not in note:
        raise IntegrityError("honest join note keeps honest join", reason_code="CATALOG_REVIEW")
    if "the join is not launch" not in note:
        raise IntegrityError("honest join note keeps the join is not launch", reason_code="CATALOG_REVIEW")
    if "a certified simulation is not a running firm" not in note:
        raise IntegrityError("honest join note keeps a certified simulation is not a running firm", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "the join is not launch" not in lede:
        raise IntegrityError("honest join lede keeps the join is not launch", reason_code="CATALOG_REVIEW")
    if "licensed-not-wired is not a wired firm" not in lede:
        raise IntegrityError("honest join lede keeps licensed-not-wired is not a wired firm", reason_code="CATALOG_REVIEW")
    if "a 10/10+ quality check is not launch" not in lede:
        raise IntegrityError("honest join lede keeps a 10/10+ quality check is not launch", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest join" not in site:
        raise IntegrityError("honest join site keeps honest join", reason_code="CATALOG_REVIEW")
    if "not a /join route" not in site:
        raise IntegrityError("honest join site keeps not a /join route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest join site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest join is not a complement", reason_code="CATALOG_REVIEW")
    owner = (catalog.get("plane_interface") or {}).get("gaps") or {}
    open_items = " ".join(str(item) for item in owner.get("owner_only_open") or [])
    for stem in ("seat B click", "G12/G13", "billing", "launch"):
        if stem not in open_items:
            raise IntegrityError("honest join cannot close " + stem, reason_code="GAP_OPEN")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("join playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat the join as launch", reason_code="CATALOG_REVIEW")


def run_join_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded honest join. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_join(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest join", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "join_as_launch": False,
        "stitch_as_live_pin": False,
        "licensed_as_wired_firm": False,
        "manage_ops_as_closed": False,
        "certify_as_running": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_join"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_join_certification()
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
        "join_as_launch": False,
        "stitch_as_live_pin": False,
        "licensed_as_wired_firm": False,
        "manage_ops_as_closed": False,
        "certify_as_running": False,
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
        "href": "#firm",
        "facts": [dict(item) for item in body.get("facts") or []],
        "hops": [dict(item) for item in body.get("hops") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat the join as launch.",
            "Treat the stitched firm as LIVE_PIN_OK.",
            "Treat licensed-not-wired as a wired firm.",
            "Treat management and operations as closed from this plane.",
            "Treat a certified simulation as a running firm.",
        ],
    }
