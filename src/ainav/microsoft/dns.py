"""Read-only DNS for ainav.institute. Never claims the custom domain. Never publishes."""

from __future__ import annotations

import subprocess
from typing import Any

APEX = "ainav.institute"
SWA_HOST = "blue-river-010091a0f.7.azurestaticapps.net"
E7_ON_CLOUDFLARE_CHECKS = (
    "cloudflare_nameservers",
    "mx_outlook",
    "spf_outlook",
    "entra_txt",
    "autodiscover",
    "enterpriseenrollment",
    "enterpriseregistration",
    "dkim",
    "dmarc",
    "teams_sip",
    "teams_lyncdiscover",
    "teams_sip_srv",
    "teams_federation_srv",
)
TEAMS_CHECK_KEYS = (
    "teams_sip",
    "teams_lyncdiscover",
    "teams_sip_srv",
    "teams_federation_srv",
)


def _dig(name: str, rtype: str) -> list[str]:
    try:
        out = subprocess.run(
            ["dig", "+short", rtype, name],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    lines = []
    for raw in (out.stdout or "").splitlines():
        line = raw.strip().strip(".")
        if line:
            lines.append(line)
    return lines


def probe_dns() -> dict[str, Any]:
    ns = _dig(APEX, "NS")
    a = _dig(APEX, "A")
    mx = _dig(APEX, "MX")
    txt = [item.strip('"') for item in _dig(APEX, "TXT")]
    asuid = _dig(f"asuid.{APEX}", "TXT")
    autodiscover = _dig(f"autodiscover.{APEX}", "CNAME")
    enrollment = _dig(f"enterpriseenrollment.{APEX}", "CNAME")
    registration = _dig(f"enterpriseregistration.{APEX}", "CNAME")
    dkim1 = _dig(f"selector1._domainkey.{APEX}", "CNAME")
    dkim2 = _dig(f"selector2._domainkey.{APEX}", "CNAME")
    dmarc = [item.strip('"') for item in _dig(f"_dmarc.{APEX}", "TXT")]
    sip = _dig(f"sip.{APEX}", "CNAME")
    lyncdiscover = _dig(f"lyncdiscover.{APEX}", "CNAME")
    sip_srv = _dig(f"_sip._tls.{APEX}", "SRV")
    fed_srv = _dig(f"_sipfederationtls._tcp.{APEX}", "SRV")
    cloudflare_ns = all("cloudflare.com" in item.lower() for item in ns) if ns else False
    outlook_mx = any("protection.outlook.com" in item.lower() for item in mx)
    outlook_spf = any("spf.protection.outlook.com" in item.lower() for item in txt)
    ms_verify = any(item.startswith("MS=") for item in txt)
    swa_txt = any("azurestaticapps" in item.lower() for item in asuid)
    teams_sip = bool(sip)
    body = {
        "kind": "ainav.dns.v1",
        "apex": APEX,
        "live": False,
        "live_pin_ok": False,
        "custom_domain_claimed": False,
        "launch_ready": False,
        "nameservers": ns,
        "cloudflare_nameservers": cloudflare_ns,
        "website": {
            "a": a,
            "asuid": asuid,
            "swa_asuid_present": swa_txt,
            "azure_swa_hostname": SWA_HOST,
            "azure_swa_bound": False,
            "note": "Apex still resolves through Cloudflare. It is not bound to Azure Static Web Apps.",
        },
        "microsoft_365": {
            "mx": mx,
            "mx_outlook": outlook_mx,
            "spf_outlook": outlook_spf,
            "entra_txt": ms_verify,
            "autodiscover": autodiscover,
            "enterpriseenrollment": enrollment,
            "enterpriseregistration": registration,
            "dkim": bool(dkim1 and dkim2),
            "dmarc": dmarc,
            "teams_sip": teams_sip,
            "lyncdiscover": lyncdiscover,
            "sip_srv": sip_srv,
            "federation_srv": fed_srv,
            "note": (
                "Mail, Entra, Teams SIP, and lync SRV are pointed at Microsoft. "
                "This is not a website launch."
                if teams_sip
                else "Mail and Entra records are pointed at Microsoft. "
                "Teams SIP/lync SRV is not present. This is not a website launch."
            ),
        },
    }
    body["e7_on_cloudflare"] = score_e7_on_cloudflare(body)
    return body


def score_e7_on_cloudflare(dns: dict[str, Any]) -> dict[str, Any]:
    """Live DNS scoreboard. Mail can be on Cloudflare while Teams records are missing."""
    m365 = dns.get("microsoft_365") or {}
    checks = {
        "cloudflare_nameservers": bool(dns.get("cloudflare_nameservers")),
        "mx_outlook": bool(m365.get("mx_outlook")),
        "spf_outlook": bool(m365.get("spf_outlook")),
        "entra_txt": bool(m365.get("entra_txt")),
        "autodiscover": bool(m365.get("autodiscover")),
        "enterpriseenrollment": bool(m365.get("enterpriseenrollment")),
        "enterpriseregistration": bool(m365.get("enterpriseregistration")),
        "dkim": bool(m365.get("dkim")),
        "dmarc": bool(m365.get("dmarc")),
        "teams_sip": bool(m365.get("teams_sip")),
        "teams_lyncdiscover": bool(m365.get("lyncdiscover")),
        "teams_sip_srv": bool(m365.get("sip_srv")),
        "teams_federation_srv": bool(m365.get("federation_srv")),
    }
    missing = [name for name in E7_ON_CLOUDFLARE_CHECKS if not checks[name]]
    mail_keys = [name for name in E7_ON_CLOUDFLARE_CHECKS if name not in TEAMS_CHECK_KEYS]
    mail_on = all(checks[name] for name in mail_keys)
    full = all(checks[name] for name in E7_ON_CLOUDFLARE_CHECKS)
    if full:
        note = (
            "DNS is full. Mail, Entra, Teams SIP, and lync SRV point through Cloudflare. "
            "Cloudflare is not the product, not a seat, not dual admit. "
            "This is not Institute launch."
        )
    else:
        note = (
            "Mail and Entra already point through Cloudflare nameservers. "
            f"Missing: {', '.join(missing) or 'none'}. "
            "Full is false while any check is missing. "
            "Cloudflare is not the product, not a seat, not dual admit. "
            "This is not Institute launch."
        )
    return {
        "kind": "ainav.e7_cloudflare.v1",
        "sku": False,
        "live": False,
        "live_pin_ok": False,
        "is_admit_plane": False,
        "full": full,
        "mail_on_cloudflare": mail_on,
        "checks": checks,
        "missing": missing,
        "note": note,
    }


def catalog_edge() -> dict[str, Any]:
    """Catalog-honest edge. Not a live probe. Never LIVE_PIN_OK."""
    from ainav.catalog import load_catalog

    edge = dict(load_catalog()["microsoft_stack"]["edge"])
    return {
        "id": edge["id"],
        "product": edge["product"],
        "role": edge["role"],
        "sku": False,
        "connection": False,
        "complement": False,
        "live": False,
        "live_pin_ok": False,
        "is_admit_plane": False,
        "full": bool(edge.get("full")),
        "apex": edge["apex"],
        "dashboard_url": edge["dashboard_url"],
        "already": list(edge["already"]),
        "missing": list(edge.get("missing") or []),
        "not": list(edge["not"]),
        "note": edge["note"],
    }
