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
        "",
    ]
    return "\n".join(lines)


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
