"""IP and competitor boundaries. Catalog wins. G12 legal stays open.

This is executable hygiene: refuse rebrands, competitor SKUs, and
Microsoft-as-product claims. It is not a patent filing and not counsel sign-off.
"""

from __future__ import annotations

import re
from typing import Any

from agent_gov.errors import IntegrityError, LockfileError
from ainav.catalog import ALLOWED_SKUS
from ainav.errors import IPError

_SPLIT = re.compile(r"[^a-z0-9]+")


def normalize_label(value: str) -> str:
    return _SPLIT.sub("_", value.strip().lower()).strip("_")


def _alias_set(catalog: dict[str, Any]) -> set[str]:
    return {normalize_label(item) for item in catalog.get("ip", {}).get("competitor_aliases", [])}


def _microsoft_mark_set(catalog: dict[str, Any]) -> set[str]:
    return {normalize_label(item) for item in catalog.get("ip", {}).get("microsoft_marks", [])}


def validate_ip_doctrine(catalog: dict[str, Any]) -> None:
    ip = catalog.get("ip")
    if not isinstance(ip, dict):
        raise IntegrityError("catalog missing ip doctrine", reason_code="CATALOG_IP")
    if ip.get("g12_open") is not True:
        raise IntegrityError("G12 legal cannot be marked closed", reason_code="GAP_OPEN")
    if ip.get("owner") != catalog.get("entity", {}).get("legal"):
        raise IntegrityError("ip.owner must match the legal entity", reason_code="IP_REBRAND")
    if catalog.get("entity", {}).get("product") != ip.get("product_mark"):
        raise IntegrityError("entity.product cannot be rebranded", reason_code="IP_REBRAND")
    if ip.get("no_patent_claim_in_this_tree") is not True:
        raise IntegrityError("this tree must not claim a filed patent", reason_code="IP_CLAIM")
    aliases = _alias_set(catalog)
    if aliases & {normalize_label(s) for s in ALLOWED_SKUS}:
        raise IntegrityError("competitor aliases cannot collide with SKUs", reason_code="CATALOG_SKU")
    for sku_item in catalog.get("skus", []):
        _refuse_label(str(sku_item["id"]), catalog, kind="SKU")
    for pack in catalog.get("industry_packs", []):
        _refuse_label(str(pack.get("id")), catalog, kind="industry pack")
    for lib in catalog.get("libraries", []):
        _refuse_label(str(lib.get("id")), catalog, kind="library")
    _validate_insulation(ip)


def screen_pack_label(label: str, *, catalog: dict[str, Any] | None = None) -> None:
    """Refuse competitor or Microsoft-as-product pack names. Allowed SKUs pass."""
    if label in ALLOWED_SKUS:
        return
    if catalog is None:
        from ainav.catalog import load_catalog

        catalog = load_catalog()
    _refuse_label(label, catalog, kind="pack")


def refuse_claim(text: str, *, catalog: dict[str, Any] | None = None) -> None:
    if catalog is None:
        from ainav.catalog import load_catalog

        catalog = load_catalog()
    lowered = " ".join(normalize_label(text).split("_"))
    for claim in catalog.get("ip", {}).get("forbidden_claims", []):
        stem = " ".join(normalize_label(claim).split("_"))
        if stem and stem in lowered:
            raise IPError(
                f"forbidden competitive claim: {claim}",
                reason_code="IP_CLAIM",
            )


def refuse_lockfile_rebrand(product: str) -> None:
    if product != "job_c":
        raise LockfileError(
            "lockfile product must remain job_c — competitor rebrand refused",
            reason_code="LOCKFILE_PRODUCT",
        )


def notice(catalog: dict[str, Any] | None = None) -> str:
    if catalog is None:
        from ainav.catalog import load_catalog

        catalog = load_catalog()
    ip = catalog["ip"]
    lines = [
        ip["copyright"],
        "",
        f"Owner: {ip['owner']}",
        f"Product mark: {ip['product_mark']}",
        f"Institute mark: {ip['institute_mark']}",
        "",
        "Reserved work:",
    ]
    for item in ip.get("reserved_work", []):
        lines.append(f"- {item}")
    lines += [
        "",
        "Microsoft marks (theirs): " + ", ".join(ip.get("microsoft_marks", [])),
        ip.get("microsoft_use", ""),
        "",
        "G12 legal is OPEN. This notice is hygiene, not a signed opinion.",
        "No patent is claimed in this tree.",
        "Insulation is not uncopyable.",
        "",
        (ip.get("insulation") or {}).get("thesis") or "",
        "",
    ]
    return "\n".join(lines)


def public_insulation() -> dict[str, Any]:
    from ainav.catalog import load_catalog

    cat = load_catalog()
    body = dict(cat["ip"]["insulation"])
    return {
        "kind": "ainav.ip.insulation.v1",
        "sku": False,
        "patent_claimed": False,
        "uncopyable": False,
        "g12_open": True,
        "live": False,
        "live_pin_ok": False,
        "thesis": body["thesis"],
        "equation": cat["equations"].get("insulation"),
        "why_microsoft_is_not_the_failsafe": body.get("why_microsoft_is_not_the_failsafe"),
        "what_they_can_copy": list(body.get("what_they_can_copy") or []),
        "what_the_build_pins": list(body.get("what_the_build_pins") or []),
        "layers": [dict(item) for item in body.get("layers") or []],
        "others": list(body.get("others") or []),
        "refuse": list(body.get("refuse") or []),
        "reserved_work": list(cat["ip"].get("reserved_work") or []),
        "microsoft_use": cat["ip"].get("microsoft_use"),
        "note": "Hygiene. Not a patent. Not uncopyable. G12 stays open. Microsoft is not the product.",
    }


def insulation_markdown() -> str:
    from ainav.catalog import load_catalog

    body = public_insulation()
    lines = [
        f"# {load_catalog()['entity']['legal']} — insulation (not a patent)",
        "",
        body["thesis"],
        f"Equation: {body.get('equation')}.",
        "SKU: false. Patent claimed: false. Uncopyable: false. G12: open. LIVE_PIN_OK: false.",
        "",
        "## Why Microsoft is not the failsafe",
        "",
        body.get("why_microsoft_is_not_the_failsafe") or "",
        "",
        "## What they can copy",
        "",
    ]
    for item in body["what_they_can_copy"]:
        lines.append(f"- {item}")
    lines += ["", "## What the build pins", ""]
    for item in body["what_the_build_pins"]:
        lines.append(f"- {item}")
    lines += ["", "## Layers", ""]
    for item in body["layers"]:
        lines.append(f"- **{item['id']}** — {item.get('does')}")
    lines += ["", "## Others (same conflict)", ""]
    for item in body["others"]:
        lines.append(f"- {item}")
    lines += ["", "## Refuse", ""]
    for item in body["refuse"]:
        lines.append(f"- {item}")
    lines += ["", body.get("note") or "", ""]
    return "\n".join(lines)


def _validate_insulation(ip: dict[str, Any]) -> None:
    body = ip.get("insulation")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing ip.insulation", reason_code="CATALOG_IP")
    if body.get("sku") is True:
        raise IntegrityError("insulation is not a SKU", reason_code="CATALOG_SKU")
    if body.get("patent_claimed") is True:
        raise IntegrityError("this tree must not claim a patent", reason_code="IP_CLAIM")
    if body.get("uncopyable") is True:
        raise IntegrityError("insulation is not uncopyable", reason_code="IP_CLAIM")
    if body.get("g12_open") is not True:
        raise IntegrityError("G12 legal cannot be marked closed", reason_code="GAP_OPEN")
    thesis = str(body.get("thesis") or "").lower()
    if "independen" not in thesis:
        raise IntegrityError("insulation thesis must keep independence", reason_code="CATALOG_IP")
    if "not a patent" not in thesis:
        raise IntegrityError("insulation thesis must say this is not a patent", reason_code="IP_CLAIM")
    refuse = " ".join(body.get("refuse") or []).lower()
    for stem in ("uncopyable", "patent granted", "cannot legally copy"):
        if stem not in refuse:
            raise IntegrityError(f"insulation must refuse {stem}", reason_code="IP_CLAIM")
    claims = " ".join(ip.get("forbidden_claims") or []).lower()
    for stem in ("uncopyable", "patent granted", "cannot legally copy"):
        if stem not in claims:
            raise IntegrityError(f"forbidden claims must include {stem}", reason_code="IP_CLAIM")
    layers = {str(item.get("id") or "") for item in body.get("layers") or []}
    for needed in ("independence", "job_c", "fail_closed", "gold", "catalog_law"):
        if needed not in layers:
            raise IntegrityError(f"insulation layers must include {needed}", reason_code="CATALOG_IP")
    if not body.get("what_they_can_copy") or not body.get("what_the_build_pins"):
        raise IntegrityError("insulation must name what they can copy and what the build pins", reason_code="CATALOG_IP")


def _refuse_label(label: str, catalog: dict[str, Any], *, kind: str) -> None:
    if label in ALLOWED_SKUS:
        return
    norm = normalize_label(label)
    if not norm:
        return
    aliases = _alias_set(catalog)
    tokens = set(norm.split("_")) | {norm}
    if tokens & aliases or norm in aliases:
        if tokens & _microsoft_mark_set(catalog) or any(
            token in {"copilot", "purview", "sentinel", "entra", "azure", "dynamics", "teams"}
            for token in tokens
        ):
            raise IPError(
                f"{kind} {label!r} treats a Microsoft mark as the product",
                reason_code="MICROSOFT_PRODUCT",
            )
        raise IPError(
            f"{kind} {label!r} is a competitor alias, not an AINav SKU",
            reason_code="COMPETITOR_SKU",
        )
