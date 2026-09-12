"""Honest better. Recorded. A much better build and business is not launch.

A systems review is not a wired firm. A 10/10 is not a seated second human.
A polish pass is not production. Interpretability is not LIVE_PIN_OK.
Making better is not launch. Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_BETTER_FACT_IDS,
    HONEST_BETTER_HOP_HREFS,
    HONEST_BETTER_HOP_IDS,
    HONEST_BETTER_HREFS,
    HONEST_BETTER_REFUSE_IDS,
    HONEST_BETTER_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.better.v1"
COMPLEMENT_COUNT = 8


def validate_honest_better(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_better")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest better", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest better kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "better_as_launch",
        "ten_as_seated",
        "systems_as_wired",
        "polish_as_production",
        "interpret_as_live_pin",
        "make_as_launch",
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
        "recognized_revenue",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest better cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest better stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest better stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest better stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#success":
        raise IntegrityError("honest better sits on #success", reason_code="CATALOG_REVIEW")
    if body.get("better_as_launch") is not False:
        raise IntegrityError("a much better build and business is not launch", reason_code="CATALOG_REVIEW")
    if body.get("ten_as_seated") is not False:
        raise IntegrityError("a 10/10 is not a seated second human", reason_code="CATALOG_REVIEW")
    if body.get("systems_as_wired") is not False:
        raise IntegrityError("a systems review is not a wired firm", reason_code="CATALOG_REVIEW")
    if body.get("polish_as_production") is not False:
        raise IntegrityError("a polish pass is not production", reason_code="CATALOG_REVIEW")
    if body.get("interpret_as_live_pin") is not False:
        raise IntegrityError("interpretability is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if body.get("make_as_launch") is not False:
        raise IntegrityError("making better is not launch", reason_code="CATALOG_REVIEW")
    hops = body.get("hops") or []
    if not isinstance(hops, list) or [item.get("id") for item in hops if isinstance(item, dict)] != list(
        HONEST_BETTER_HOP_IDS
    ):
        raise IntegrityError("honest better hops stay catalog law", reason_code="CATALOG_REVIEW")
    hop_hrefs = {item.get("id"): item.get("href") for item in hops if isinstance(item, dict)}
    if hop_hrefs != {key: HONEST_BETTER_HOP_HREFS[key] for key in HONEST_BETTER_HOP_IDS}:
        raise IntegrityError("honest better hop hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("closed") is True or item.get("live") is True for item in hops if isinstance(item, dict)):
        raise IntegrityError("honest better hops are not closed or live", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_BETTER_FACT_IDS):
        raise IntegrityError("honest better stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest better facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_BETTER_FACT_IDS):
        raise IntegrityError("honest better facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest better facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_BETTER_REFUSE_IDS):
        raise IntegrityError("honest better refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_BETTER_REFUSE_TEXT[key] for key in HONEST_BETTER_REFUSE_IDS}:
        raise IntegrityError("honest better refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_BETTER_HREFS[key] for key in HONEST_BETTER_REFUSE_IDS}:
        raise IntegrityError("honest better refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest better refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest better" not in note:
        raise IntegrityError("honest better note keeps honest better", reason_code="CATALOG_REVIEW")
    if "a much better build and business is not launch" not in note:
        raise IntegrityError("honest better note keeps a much better build and business is not launch", reason_code="CATALOG_REVIEW")
    if "interpretability is not live_pin_ok" not in note:
        raise IntegrityError("honest better note keeps interpretability is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if "making better is not launch" not in note:
        raise IntegrityError("honest better note keeps making better is not launch", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "a much better build and business is not launch" not in lede:
        raise IntegrityError("honest better lede keeps a much better build and business is not launch", reason_code="CATALOG_REVIEW")
    if "a systems review is not a wired firm" not in lede:
        raise IntegrityError("honest better lede keeps a systems review is not a wired firm", reason_code="CATALOG_REVIEW")
    if "a 10/10 is not a seated second human" not in lede:
        raise IntegrityError("honest better lede keeps a 10/10 is not a seated second human", reason_code="CATALOG_REVIEW")
    if "making better is not launch" not in lede:
        raise IntegrityError("honest better lede keeps making better is not launch", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest better" not in site:
        raise IntegrityError("honest better site keeps honest better", reason_code="CATALOG_REVIEW")
    if "not a /better route" not in site:
        raise IntegrityError("honest better site keeps not a /better route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest better site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    if "making better is not launch" not in site:
        raise IntegrityError("honest better site keeps making better is not launch", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest better is not a complement", reason_code="CATALOG_REVIEW")
    owner = (catalog.get("plane_interface") or {}).get("gaps") or {}
    open_items = " ".join(str(item) for item in owner.get("owner_only_open") or [])
    for stem in ("seat B click", "G12/G13", "billing", "launch"):
        if stem not in open_items:
            raise IntegrityError("honest better cannot close " + stem, reason_code="GAP_OPEN")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("better playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat a much better build and business as launch", reason_code="CATALOG_REVIEW")


def run_better_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded honest better. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_better(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest better", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "better_as_launch": False,
        "ten_as_seated": False,
        "systems_as_wired": False,
        "polish_as_production": False,
        "interpret_as_live_pin": False,
        "make_as_launch": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_better"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_better_certification()
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
        "better_as_launch": False,
        "ten_as_seated": False,
        "systems_as_wired": False,
        "polish_as_production": False,
        "interpret_as_live_pin": False,
        "make_as_launch": False,
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
        "href": "#success",
        "facts": [dict(item) for item in body.get("facts") or []],
        "hops": [dict(item) for item in body.get("hops") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat a much better build and business as launch.",
            "Treat a 10/10 as a seated second human.",
            "Treat a systems review as a wired firm.",
            "Treat a polish pass as production.",
            "Treat interpretability as LIVE_PIN_OK.",
            "Treat making better as launch.",
        ],
    }
