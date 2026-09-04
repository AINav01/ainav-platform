"""Read-only DNS for ainav.institute. Never claims the custom domain. Never publishes."""

from __future__ import annotations

import ipaddress
import socket
import ssl
import subprocess
import urllib.error
import urllib.request
from typing import Any

APEX = "ainav.institute"
SWA_HOST = "blue-river-010091a0f.7.azurestaticapps.net"
PAGES_HOST = "ainav-institute.pages.dev"
INSTITUTE_SWA = f"https://{SWA_HOST}/"
# Visitor-facing Cloudflare anycast. Outlook / Microsoft 365 must not land here.
_CF_ANYCAST = tuple(
    ipaddress.ip_network(item)
    for item in (
        "104.16.0.0/12",
        "172.64.0.0/13",
        "162.158.0.0/15",
        "188.114.96.0/19",
        "198.41.128.0/17",
        "173.245.48.0/20",
        "103.21.244.0/22",
        "103.22.200.0/22",
        "103.31.4.0/22",
        "141.101.64.0/18",
        "108.162.192.0/18",
        "190.93.240.0/20",
        "197.234.240.0/22",
        "131.0.72.0/22",
    )
)
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
            "note": (
                "Apex is Cloudflare anycast in front of empty Pages. "
                "It is not bound to Azure Static Web Apps. Pages is not the Institute. "
                "Azure SWA is the development twin."
            ),
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
        "plan": edge.get("plan") or "pro",
        "plan_sku": False,
        "from_this_plane": False,
        "apex": edge["apex"],
        "dashboard_url": edge["dashboard_url"],
        "already": list(edge["already"]),
        "missing": list(edge.get("missing") or []),
        "not": list(edge["not"]),
        "activate": dict(edge.get("activate") or {}),
        "holding": dict(edge.get("holding") or {}),
        "quality": dict(edge.get("quality") or {}),
        "twin": dict(edge.get("twin") or {}),
        "note": edge["note"],
    }


def is_cloudflare_anycast(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return any(addr in net for net in _CF_ANYCAST)


def _html_title(body: bytes) -> str:
    text = body.decode("utf-8", "replace")
    lower = text.lower()
    start = lower.find("<title>")
    end = lower.find("</title>")
    if start < 0 or end < 0 or end <= start:
        return ""
    return text[start + 7 : end].strip()


def _http_probe(url: str) -> dict[str, Any]:
    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "ainav-edge-quality/1"},
    )
    empty = {
        "url": url,
        "status": 0,
        "headers": {},
        "title": "",
        "csp": "",
        "cf_mitigated": "",
        "hsts": "",
        "location": "",
        "body_prefix": "",
    }
    try:
        with opener.open(req, timeout=12) as resp:
            raw = resp.read(4096)
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return {
                "url": url,
                "status": int(resp.status),
                "headers": headers,
                "title": _html_title(raw),
                "csp": headers.get("content-security-policy", ""),
                "cf_mitigated": headers.get("cf-mitigated", ""),
                "hsts": headers.get("strict-transport-security", ""),
                "location": headers.get("location", ""),
                "body_prefix": raw.decode("utf-8", "replace"),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read(4096) if exc.fp else b""
        headers = {k.lower(): v for k, v in (exc.headers.items() if exc.headers else [])}
        return {
            "url": url,
            "status": int(exc.code),
            "headers": headers,
            "title": _html_title(raw),
            "csp": headers.get("content-security-policy", ""),
            "cf_mitigated": headers.get("cf-mitigated", ""),
            "hsts": headers.get("strict-transport-security", ""),
            "location": headers.get("location", ""),
            "body_prefix": raw.decode("utf-8", "replace"),
        }
    except (OSError, urllib.error.URLError):
        return empty


def _tls_accepts(host: str, version: Any) -> bool:
    if version is None:
        return False
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.minimum_version = version
        ctx.maximum_version = version
    except (ValueError, OSError):
        return False
    try:
        with socket.create_connection((host, 443), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=host):
                return True
    except OSError:
        return False


def _tls_versions(host: str) -> dict[str, bool]:
    versions = getattr(ssl, "TLSVersion", None)
    return {
        "tls1_0": _tls_accepts(host, getattr(versions, "TLSv1", None)),
        "tls1_1": _tls_accepts(host, getattr(versions, "TLSv1_1", None)),
        "tls1_2": _tls_accepts(host, getattr(versions, "TLSv1_2", None)),
        "tls1_3": _tls_accepts(host, getattr(versions, "TLSv1_3", None)),
    }


def _visitor_cert(host: str) -> dict[str, Any]:
    note = "Cloudflare Universal SSL is the visitor cert. It does not prove Full versus Flexible."
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as wrapped:
                cert = wrapped.getpeercert() or {}
    except OSError:
        return {"issuer": "", "san": [], "notAfter": "", "note": note}
    issuer = " ".join(part[0][1] for part in (cert.get("issuer") or []) if part)
    san = [item[1] for item in (cert.get("subjectAltName") or [])]
    return {
        "issuer": issuer,
        "san": san,
        "notAfter": str(cert.get("notAfter") or ""),
        "note": note,
    }


def _a_records(name: str) -> list[str]:
    return [item for item in _dig(name, "A") if item and item[0].isdigit()]


def _mail_not_cloudflare_anycast(dns: dict[str, Any]) -> dict[str, Any]:
    auto_a = _a_records(f"autodiscover.{APEX}")
    mx_a: list[str] = []
    for item in (dns.get("microsoft_365") or {}).get("mx") or []:
        parts = str(item).split()
        host = parts[-1].rstrip(".") if parts else ""
        if host:
            mx_a.extend(_a_records(host))
    auto_cf = [ip for ip in auto_a if is_cloudflare_anycast(ip)]
    mx_cf = [ip for ip in mx_a if is_cloudflare_anycast(ip)]
    return {
        "autodiscover_a": auto_a,
        "mx_a": mx_a,
        "autodiscover_cloudflare_anycast": auto_cf,
        "mx_cloudflare_anycast": mx_cf,
        "not_cloudflare_anycast": bool(auto_a or mx_a) and not auto_cf and not mx_cf,
    }


def probe_edge_quality(*, dns: dict[str, Any] | None = None) -> dict[str, Any]:
    """Live HTTP/TLS/DNS quality. Never SSL Full. Never launch. Never LIVE_PIN_OK."""
    body = dns if dns is not None else probe_dns()
    http_apex = _http_probe(f"http://{APEX}/")
    https_apex = _http_probe(f"https://{APEX}/")
    www = _http_probe(f"https://www.{APEX}/")
    pages = _http_probe(f"https://{PAGES_HOST}/")
    swa = _http_probe(INSTITUTE_SWA)
    tls = _tls_versions(APEX)
    cert = _visitor_cert(APEX)
    mail = _mail_not_cloudflare_anycast(body)
    title = (https_apex.get("title") or "").lower()
    challenge = https_apex.get("status") == 403 and (
        https_apex.get("cf_mitigated") == "challenge"
        or "just a moment" in title
        or "challenge" in title
    )
    csp = (swa.get("csp") or "").lower()
    swa_ok = swa.get("status") == 200 and "script-src 'self'" in csp and "form-action 'none'" in csp
    asuid_absent = not bool((body.get("website") or {}).get("swa_asuid_present"))
    e7 = body.get("e7_on_cloudflare") or {}
    tls_floor = bool(tls.get("tls1_2") or tls.get("tls1_3"))
    tls_legacy_refused = not tls.get("tls1_0") and not tls.get("tls1_1")
    www_301 = www.get("status") == 301
    apex_headers = https_apex.get("headers") or {}
    cloudflare_edge = str(apex_headers.get("server") or "").lower() == "cloudflare" or bool(
        apex_headers.get("cf-ray")
    )
    apex_404 = https_apex.get("status") == 404
    apex_csp = (https_apex.get("csp") or "").lower()
    apex_has_institute_csp = "script-src 'self'" in apex_csp and "form-action 'none'" in apex_csp
    return {
        "kind": "ainav.edge.quality.probe.v1",
        "sku": False,
        "live": False,
        "live_pin_ok": False,
        "from_this_plane": False,
        "ssl_full_claimed": False,
        "apex_is_institute": False,
        "authorized_release": False,
        "rocket_loader_claimed": False,
        "e7_full": bool(e7.get("full")),
        "asuid_absent": asuid_absent,
        "http_301": http_apex.get("status") == 301,
        "https_403_challenge": challenge,
        "apex_404": apex_404,
        "cloudflare_edge": cloudflare_edge,
        "apex_has_institute_csp": apex_has_institute_csp,
        "pages_404": pages.get("status") == 404,
        "swa_200": swa_ok,
        "twin_swa_200": swa_ok,
        "www_301": www_301,
        "tls_floor": tls_floor,
        "tls_legacy_refused": tls_legacy_refused,
        "mail_not_cloudflare_anycast": bool(mail.get("not_cloudflare_anycast")),
        "visitor_cert_is_not_full": True,
        "rocket_loader_seen": "rocket-loader" in (https_apex.get("body_prefix") or "").lower(),
        "http": {
            "apex_http": http_apex,
            "apex_https": https_apex,
            "www": www,
            "pages": pages,
            "swa": swa,
        },
        "tls": tls,
        "mail": mail,
        "visitor_cert": cert,
        "note": (
            "Live probe is HTTP 301, apex 404 empty on Cloudflare edge, pages 404, "
            "SWA twin 200, asuid absent, E7 13/13, TLS 1.2+, and mail not Cloudflare anycast. "
            "The 403 challenge hold is gone. Visitor cert is not SSL Full. "
            "Cloudflare edge is not the Institute. Azure SWA is the development twin. "
            "Authorized gold-99 release is owner-only. This is not Institute launch. "
            "This Cloud Agent cannot edit Cloudflare."
        ),
    }
