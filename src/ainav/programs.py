"""Startup program qualification. Catalog wins. Membership is not claimed.

NVIDIA Inception excludes companies associated with cryptocurrency.
Public materials lead with the Business Central write-gate.
Frozen gold vectors may still contain lab custody fixtures — that is not
the commercial or Inception story.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog
from ainav.errors import ProgramError
from ainav.ip import refuse_claim

CRYPTO_STEMS = (
    "usdc",
    "usdt",
    "bitcoin",
    "stablecoin",
    "cryptocurrency",
    "crypto associated",
    "custody.withdraw",
    "0xabc",
)

ALLOWED_STATUSES = frozenset(
    {"qualify_not_claimed", "later_not_first", "complementary_not_claimed"}
)
FIRST_IDS = frozenset({"nvidia.inception", "microsoft.founders_hub"})
APPLY_FIRST = ("microsoft.founders_hub", "nvidia.inception")


def programs() -> dict[str, Any]:
    return dict(load_catalog()["programs"])


def validate_programs(catalog: dict[str, Any]) -> None:
    body = catalog.get("programs")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing programs doctrine", reason_code="CATALOG_PROGRAM")
    if body.get("membership_claimed") is True or body.get("applied") is True:
        raise IntegrityError("program membership cannot be claimed here", reason_code="PROGRAM_NOT_CLAIMED")
    if body.get("crypto_associated") is not False:
        raise IntegrityError(
            "Inception requires crypto_associated=false; lead with the BC wedge",
            reason_code="PROGRAM_CRYPTO",
        )
    if body.get("gpu_workload_claimed") is True:
        raise IntegrityError("GPU production workload is not claimed", reason_code="PROGRAM_NOT_CLAIMED")
    if body.get("website", {}).get("public_deploy_claimed") is True:
        raise IntegrityError("public website deploy is not claimed", reason_code="PROGRAM_NOT_CLAIMED")
    if body.get("website", {}).get("custom_domain_claimed") is True:
        raise IntegrityError("ainav.institute custom domain is not claimed", reason_code="PROGRAM_NOT_CLAIMED")
    if body.get("website", {}).get("launch_ready") is True:
        raise IntegrityError(
            "Institute launch is held. Do not publish until the owner says launch.",
            reason_code="PROGRAM_NOT_CLAIMED",
        )
    if body.get("website", {}).get("pages_is_host") is True:
        raise IntegrityError("Cloudflare Pages is not the Institute host", reason_code="PROGRAM_NOT_CLAIMED")
    if str(body.get("website", {}).get("apex_origin") or "") != "ainav-institute.pages.dev":
        raise IntegrityError(
            "apex origin is empty Cloudflare Pages",
            reason_code="PROGRAM_NOT_CLAIMED",
        )
    wedge = body.get("public_wedge")
    l1_actions = {
        m["id"]
        for m in catalog.get("modules", [])
        if m.get("sku") == "L1" and m.get("kind") == "action"
    }
    if wedge not in l1_actions:
        raise IntegrityError("public_wedge must be the L1 action class", reason_code="PROGRAM_WEDGE")
    ids = {item.get("id") for item in body.get("targets", [])}
    if not FIRST_IDS.issubset(ids):
        raise IntegrityError("catalog must list Inception and Microsoft for Startups")
    order = list(body.get("application_order") or [])
    if order[:2] != list(APPLY_FIRST):
        raise IntegrityError(
            "Microsoft for Startups is first; NVIDIA Inception is second",
            reason_code="PROGRAM_ORDER",
        )
    if set(order) != ids:
        raise IntegrityError("application_order must list every program target", reason_code="PROGRAM_ORDER")
    for item in body.get("targets", []):
        if item.get("status") not in ALLOWED_STATUSES:
            raise IntegrityError(
                f"unknown program status {item.get('status')!r}",
                reason_code="CATALOG_PROGRAM",
            )


def public_programs() -> dict[str, Any]:
    """Fail-closed Institute feed. Membership stays unclaimed."""
    cat = load_catalog()
    body = programs()
    contacts = cat["organization"]["contacts"]
    invited = contacts["invited"]
    by_id = {item["id"]: item for item in body["targets"]}
    ladder = []
    for program_id in application_order():
        rec = qualify(program_id)
        target = by_id[program_id]
        ladder.append(
            {
                "id": rec["id"],
                "name": rec["name"],
                "status": rec["status"],
                "priority": target.get("priority"),
                "apply_order": rec["apply_order"],
                "eligible_to_prepare": rec["eligible_to_prepare"],
                "ready_to_apply": False,
                "membership_claimed": False,
                "applied": False,
                "url": target.get("url"),
                "cost": target.get("cost"),
                "must": list(target.get("must") or []),
                "must_not": list(target.get("must_not") or []),
                "benefits": list(target.get("benefits") or []),
                "note": target.get("note"),
                "pitch_rule": target.get("pitch_rule"),
                "apply": rec["apply"],
                "blockers": list(rec.get("blockers") or []),
            }
        )
    return {
        "kind": "ainav.institute.programs.v1",
        "sku": False,
        "cms": False,
        "live": False,
        "live_pin_ok": False,
        "membership_claimed": False,
        "applied": False,
        "gpu_workload_claimed": False,
        "crypto_associated": False,
        "priced_round": False,
        "raise_claimed": False,
        "release": cat["entity"]["release"],
        "legal": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "owner": cat["operating"]["owner_principal"],
        "lead_narrative": body["lead_narrative"],
        "public_wedge": body["public_wedge"],
        "application_order": list(body["application_order"]),
        "apply_first": APPLY_FIRST[0],
        "apply_second": APPLY_FIRST[1],
        "apply_prerequisites": list(body.get("apply_prerequisites") or []),
        "website": dict(body["website"]),
        "ladder": ladder,
        "contacts": {
            "owner": contacts["owner"],
            "developer": contacts.get("developer"),
            "business_executive": contacts.get("business_executive"),
            "second_unique_human": False,
            "developer_intended": contacts["owner"],
            "invited": {
                "name": invited["name"],
                "email": invited.get("email"),
                "recorded": bool(invited.get("recorded")),
                "agreed": bool(invited.get("agreed")),
                "entra_oid": invited.get("entra_oid"),
                "seat_clicked": bool(invited.get("seat_clicked")),
                "inception_role": invited.get("inception_role"),
                "equity": bool(invited.get("equity")),
                "second_unique_human": bool(invited.get("second_unique_human")),
            },
        },
        "refuse": [
            "priced round",
            "membership claimed",
            "GPU production workload",
            "LIVE_PIN_OK",
            "CMS",
        ],
    }


def application_order() -> list[str]:
    body = programs()
    return list(body.get("application_order") or [item["id"] for item in body["targets"]])


def public_wedge_action() -> dict[str, Any]:
    """Inception-safe L1 action. Not a custody / USDC fixture."""
    return {
        "action_class": "bc.general_journal.post",
        "payload": {"account": "1000", "amount": "250.00", "memo": "sandbox journal"},
        "proposal_id": "prp-public-wedge",
        "sor_target": "bc.sandbox",
        "policy_id": "dual-admit-v1",
    }


def screen_public_copy(text: str) -> None:
    refuse_claim(text)
    lowered = text.lower()
    for stem in CRYPTO_STEMS:
        idx = lowered.find(stem)
        if idx < 0:
            continue
        prefix = lowered[max(0, idx - 8) : idx]
        if "not " in prefix or "not a " in prefix:
            continue
        raise ProgramError(
            "public program copy cannot lead with crypto or gold-vector custody fixtures",
            reason_code="PROGRAM_CRYPTO",
        )


def qualify(program_id: str) -> dict[str, Any]:
    body = programs()
    target = None
    for item in body["targets"]:
        if item["id"] == program_id:
            target = dict(item)
            break
    if target is None:
        raise ProgramError(f"unknown program {program_id}", reason_code="PROGRAM_UNKNOWN")
    blockers: list[str] = []
    if body["membership_claimed"] or body.get("applied"):
        blockers.append("membership must not be claimed from this plane")
    if body["crypto_associated"]:
        blockers.append("crypto association blocks NVIDIA Inception")
    if body.get("gpu_workload_claimed"):
        blockers.append("do not invent a GPU production workload")
    if not body.get("website", {}).get("in_repo"):
        blockers.append("working website materials missing")
    if body.get("website", {}).get("public_deploy_claimed"):
        blockers.append("do not claim a live public deploy without evidence")
    status = target.get("status")
    if status == "later_not_first":
        blockers.append("not the first application")
    if status == "complementary_not_claimed":
        blockers.append("complementary developer program — not a grant membership")
    apply_blockers = list(body.get("apply_prerequisites") or [])
    if not body.get("website", {}).get("public_deploy_claimed"):
        apply_blockers = list(dict.fromkeys(apply_blockers))
    order = list(body.get("application_order") or [item["id"] for item in body["targets"]])
    return {
        "id": program_id,
        "name": target.get("name"),
        "status": status,
        "eligible_to_prepare": not blockers and status == "qualify_not_claimed",
        "ready_to_apply": False,
        "membership_claimed": False,
        "applied": False,
        "public_wedge": body["public_wedge"],
        "lead_narrative": body["lead_narrative"],
        "blockers": blockers,
        "apply_prerequisites": apply_blockers,
        "apply": target.get("apply") or target.get("url"),
        "apply_order": order.index(program_id) + 1 if program_id in order else None,
        "apply_first": APPLY_FIRST[0],
        "live": False,
    }


def claim_membership(program_id: str) -> None:
    qualify(program_id)
    raise ProgramError(
        f"{program_id} membership is not claimed. G1/G10 and program acceptance stay open.",
        reason_code="PROGRAM_NOT_CLAIMED",
    )


def pitch() -> str:
    cat = load_catalog()
    body = cat["programs"]
    screen_public_copy(body["lead_narrative"])
    for item in body["targets"]:
        if item.get("pitch_rule"):
            screen_public_copy(item["pitch_rule"])
    lines = [
        f"# {cat['entity']['legal']} — program pitch (not an acceptance)",
        "",
        body["lead_narrative"],
        "",
        f"**Public wedge:** `{body['public_wedge']}` on a Business Central digital twin.",
        "**Not:** cryptocurrency, agent inventory (Job A), IdP replacement (Job B), Teams vote.",
        f"**Azure hostname:** {body.get('website', {}).get('azure_url') or 'not published'}",
        "**Not claimed:** membership, credits, badges, GPU production, ainav.institute custom domain.",
        "",
        "## Apply order",
        "",
        "Microsoft for Startups first. NVIDIA Inception second.",
        "Do not apply until the custom domain, incorporation date, and two unique human contacts exist.",
        "Do not lead any deck with lab custody fixtures.",
        "",
        "## Commercial spine",
        "",
    ]
    for sku_item in cat["skus"]:
        price = sku_item["price_usd"]
        lines.append(
            f"- **{sku_item['id']} {sku_item['name']}** — "
            f"${price['min']:,}–${price['max']:,} ({sku_item['term']})"
        )
    lines += [
        "",
        "## Apply prerequisites (still open)",
        "",
    ]
    for item in body.get("apply_prerequisites", []):
        lines.append(f"- {item}")
    lines += [
        "",
        "## Programs to prepare (not claimed)",
        "",
    ]
    by_id = {item["id"]: item for item in body["targets"]}
    for program_id in body.get("application_order") or [item["id"] for item in body["targets"]]:
        item = by_id[program_id]
        status = item.get("status")
        lines.append(f"- **{item['name']}** — {status}. {item.get('url', '')}")
        if item.get("pitch_rule"):
            lines.append(f"  - {item['pitch_rule']}")
        if item.get("note"):
            lines.append(f"  - {item['note']}")
    lines += [
        "",
        "## NVIDIA Inception constraints",
        "",
        "Inception excludes companies associated with cryptocurrency, consultancies,",
        "cloud service providers, resellers, and public companies. Lead with ERP",
        "write-gate. Frozen gold vectors are lab interop fixtures only; they are",
        "not the product story and must not appear on the application deck.",
        "",
        "Official FAQ: a startup may join before using NVIDIA GPUs or SDKs.",
        "Do not invent an H100 / DGX production workload.",
        "",
        "The application portal also requires two unique contacts — one",
        "developer and one business executive — with business emails.",
        "Aliases and gmail are refused. A sole founder does not collapse",
        "that rule. The Cloud Agent is not a contact.",
        "",
        "Membership, signed L1, awarded cloud credits, and a public",
        "production website deploy are **not** claimed in this tree.",
        "",
    ]
    return "\n".join(lines)
