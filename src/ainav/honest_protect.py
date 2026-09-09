"""Honest protect. Recorded. An IP board is not a patent.

Insulation is not uncopyable. An L1 license is not an assignment of Job C.
Kit PASS is not a source license. This board does not close G12.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_PROTECT_FACT_IDS,
    HONEST_PROTECT_HREFS,
    HONEST_PROTECT_REFUSE_IDS,
    HONEST_PROTECT_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.protect.v1"
COMPLEMENT_COUNT = 8


def validate_honest_protect(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_protect")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest protect", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest protect kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "protect_as_patent",
        "protect_as_uncopyable",
        "client_license_as_assignment",
        "kit_pass_as_source",
        "g12_as_closed",
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
                "honest protect cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest protect stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest protect stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest protect stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#ip":
        raise IntegrityError("honest protect sits on #ip", reason_code="CATALOG_REVIEW")
    if body.get("protect_as_patent") is not False:
        raise IntegrityError("an IP board is not a patent", reason_code="CATALOG_REVIEW")
    if body.get("protect_as_uncopyable") is not False:
        raise IntegrityError("insulation is not uncopyable", reason_code="CATALOG_REVIEW")
    if body.get("client_license_as_assignment") is not False:
        raise IntegrityError("an L1 license is not an assignment of Job C", reason_code="CATALOG_REVIEW")
    if body.get("kit_pass_as_source") is not False:
        raise IntegrityError("kit PASS is not a source license", reason_code="CATALOG_REVIEW")
    if body.get("g12_as_closed") is not False:
        raise IntegrityError("this board does not close G12", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_PROTECT_FACT_IDS):
        raise IntegrityError("honest protect stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest protect facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_PROTECT_FACT_IDS):
        raise IntegrityError("honest protect facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest protect facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_PROTECT_REFUSE_IDS):
        raise IntegrityError("honest protect refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_PROTECT_REFUSE_TEXT[key] for key in HONEST_PROTECT_REFUSE_IDS}:
        raise IntegrityError("honest protect refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_PROTECT_HREFS[key] for key in HONEST_PROTECT_REFUSE_IDS}:
        raise IntegrityError("honest protect refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest protect refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest protect" not in note:
        raise IntegrityError("honest protect note keeps honest protect", reason_code="CATALOG_REVIEW")
    if "an ip board is not a patent" not in note:
        raise IntegrityError("honest protect note keeps an IP board is not a patent", reason_code="CATALOG_REVIEW")
    if "an l1 license is not an assignment of job c" not in note:
        raise IntegrityError("honest protect note keeps an L1 license is not an assignment of Job C", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "an ip board is not a patent" not in lede:
        raise IntegrityError("honest protect lede keeps an IP board is not a patent", reason_code="CATALOG_REVIEW")
    if "an l1 license is not an assignment of job c" not in lede:
        raise IntegrityError("honest protect lede keeps an L1 license is not an assignment of Job C", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest protect" not in site:
        raise IntegrityError("honest protect site keeps honest protect", reason_code="CATALOG_REVIEW")
    if "not a /protect route" not in site:
        raise IntegrityError("honest protect site keeps not a /protect route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest protect site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest protect is not a complement", reason_code="CATALOG_REVIEW")
    ip = catalog.get("ip") if isinstance(catalog.get("ip"), dict) else {}
    if ip.get("g12_open") is not True:
        raise IntegrityError("honest protect cannot close G12", reason_code="GAP_OPEN")
    if ip.get("no_patent_claim_in_this_tree") is not True:
        raise IntegrityError("honest protect cannot claim a patent", reason_code="IP_CLAIM")
    insulation = ip.get("insulation") if isinstance(ip.get("insulation"), dict) else {}
    if insulation.get("patent_claimed") is True or insulation.get("uncopyable") is True:
        raise IntegrityError("honest protect cannot mark patent or uncopyable", reason_code="IP_CLAIM")
    layers = {str(item.get("id") or "") for item in insulation.get("layers") or [] if isinstance(item, dict)}
    if "client" not in layers:
        raise IntegrityError("honest protect insulation must include the client layer", reason_code="CATALOG_IP")
    reserved = " ".join(str(item) for item in ip.get("reserved_work") or []).lower()
    if "client license is use" not in reserved:
        raise IntegrityError("reserved work must keep client license is use", reason_code="CATALOG_IP")
    protect = ip.get("client_protect") if isinstance(ip.get("client_protect"), dict) else {}
    for flag in (
        "license_is_assignment",
        "work_for_hire",
        "kit_pass_is_source",
        "client_owns_reserved_work",
        "seats_are_inventors",
        "hours_assign_copyright",
        "g12_closed_by_board",
    ):
        if protect.get(flag) is True:
            raise IntegrityError("client protect cannot claim " + flag.replace("_", " "), reason_code="CATALOG_IP")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("protect playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat an IP board as a patent", reason_code="CATALOG_REVIEW")
    services = body.get("services") if isinstance(body.get("services"), dict) else {}
    if services.get("claimed_as_assignment") is True:
        raise IntegrityError("honest protect services cannot claim assignment", reason_code="CATALOG_REVIEW")
    microsoft = services.get("microsoft") if isinstance(services.get("microsoft"), dict) else {}
    if microsoft.get("is_the_product") is True:
        raise IntegrityError("honest protect cannot treat Microsoft as the product", reason_code="CATALOG_REVIEW")
    client = services.get("client") if isinstance(services.get("client"), dict) else {}
    if client.get("license_is_assignment") is True:
        raise IntegrityError("honest protect cannot treat an L1 license as assignment", reason_code="CATALOG_REVIEW")
    counsel = services.get("counsel") if isinstance(services.get("counsel"), dict) else {}
    if counsel.get("g12_closed") is True:
        raise IntegrityError("honest protect cannot close G12 from counsel theater", reason_code="CATALOG_REVIEW")


def run_protect_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded honest protect. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_protect(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest protect", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "protect_as_patent": False,
        "protect_as_uncopyable": False,
        "client_license_as_assignment": False,
        "kit_pass_as_source": False,
        "g12_as_closed": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_protect"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_protect_certification()
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
        "protect_as_patent": False,
        "protect_as_uncopyable": False,
        "client_license_as_assignment": False,
        "kit_pass_as_source": False,
        "g12_as_closed": False,
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
        "href": "#ip",
        "facts": [dict(item) for item in body.get("facts") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "services": dict(body.get("services") or {}),
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat an IP board as a patent.",
            "Treat insulation as uncopyable.",
            "Treat an L1 license as an assignment of Job C.",
            "Treat kit PASS as a source license.",
            "Treat this board as closing G12.",
        ],
    }
