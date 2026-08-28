"""Read-only DNS for ainav.institute. Never claims the custom domain. Never publishes."""

from __future__ import annotations

import subprocess
from typing import Any

APEX = "ainav.institute"
SWA_HOST = "blue-river-010091a0f.7.azurestaticapps.net"


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
    cloudflare_ns = all("cloudflare.com" in item.lower() for item in ns) if ns else False
    outlook_mx = any("protection.outlook.com" in item.lower() for item in mx)
    outlook_spf = any("spf.protection.outlook.com" in item.lower() for item in txt)
    ms_verify = any(item.startswith("MS=") for item in txt)
    swa_txt = any("azurestaticapps" in item.lower() for item in asuid)
    return {
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
            "teams_sip": bool(sip),
            "note": "Mail and Entra records are pointed at Microsoft. Teams SIP/lync SRV is not present. This is not a website launch.",
        },
    }
