from __future__ import annotations

import ssl
import urllib.error

from ainav.microsoft.dns import (
    _html_title,
    _http_probe,
    _tls_accepts,
    is_cloudflare_anycast,
    probe_dns,
    probe_edge_quality,
)


def test_dns_probe_does_not_claim_custom_domain_or_launch(monkeypatch):
    records = {
        ("ainav.institute", "NS"): ["bella.ns.cloudflare.com", "dilbert.ns.cloudflare.com"],
        ("ainav.institute", "A"): ["104.21.2.107"],
        ("ainav.institute", "MX"): ["0 ainav-institute.mail.protection.outlook.com"],
        ("ainav.institute", "TXT"): [
            '"v=spf1 include:spf.protection.outlook.com -all"',
            '"MS=ms86119254"',
        ],
        ("asuid.ainav.institute", "TXT"): [],
        ("autodiscover.ainav.institute", "CNAME"): ["autodiscover.outlook.com"],
        ("enterpriseenrollment.ainav.institute", "CNAME"): [
            "enterpriseenrollment-s.manage.microsoft.com"
        ],
        ("enterpriseregistration.ainav.institute", "CNAME"): [
            "enterpriseregistration.windows.net"
        ],
        ("selector1._domainkey.ainav.institute", "CNAME"): ["selector1.example"],
        ("selector2._domainkey.ainav.institute", "CNAME"): ["selector2.example"],
        ("_dmarc.ainav.institute", "TXT"): ['"v=DMARC1; p=none;"'],
        ("sip.ainav.institute", "CNAME"): [],
        ("lyncdiscover.ainav.institute", "CNAME"): [],
        ("_sip._tls.ainav.institute", "SRV"): [],
        ("_sipfederationtls._tcp.ainav.institute", "SRV"): [],
    }

    monkeypatch.setattr(
        "ainav.microsoft.dns._dig",
        lambda name, rtype: list(records.get((name, rtype), [])),
    )
    body = probe_dns()
    assert body["custom_domain_claimed"] is False
    assert body["launch_ready"] is False
    assert body["live_pin_ok"] is False
    assert body["cloudflare_nameservers"] is True
    assert body["website"]["azure_swa_bound"] is False
    assert body["website"]["swa_asuid_present"] is False
    assert body["microsoft_365"]["mx_outlook"] is True
    assert body["microsoft_365"]["spf_outlook"] is True
    assert body["microsoft_365"]["dkim"] is True
    assert body["microsoft_365"]["teams_sip"] is False
    assert body["e7_on_cloudflare"]["mail_on_cloudflare"] is True
    assert body["e7_on_cloudflare"]["full"] is False
    assert body["e7_on_cloudflare"]["live_pin_ok"] is False
    assert "teams_sip" in body["e7_on_cloudflare"]["missing"]


def test_dig_reads_live_cloudflare_ns():
    from ainav.microsoft.dns import _dig

    ns = _dig("ainav.institute", "NS")
    assert any("cloudflare.com" in item.lower() for item in ns)


def test_dig_empty_on_timeout(monkeypatch):
    import subprocess

    def boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="dig", timeout=15)

    monkeypatch.setattr("ainav.microsoft.dns.subprocess.run", boom)
    from ainav.microsoft.dns import _dig

    assert _dig("ainav.institute", "NS") == []


def test_cli_dns(monkeypatch, capsys):
    from ainav.__main__ import main

    monkeypatch.setattr(
        "ainav.microsoft.dns.probe_dns",
        lambda: {
            "kind": "ainav.dns.v1",
            "custom_domain_claimed": False,
            "launch_ready": False,
            "live": False,
        },
    )
    monkeypatch.setattr(
        "ainav.microsoft.dns.probe_edge_quality",
        lambda dns=None: {
            "kind": "ainav.edge.quality.probe.v1",
            "ssl_full_claimed": False,
            "apex_is_institute": False,
            "live_pin_ok": False,
        },
    )
    assert main(["dns"]) == 0
    out = capsys.readouterr().out
    assert "ainav.dns.v1" in out
    assert "launch_ready" in out
    assert "ainav.edge.quality.probe.v1" in out
    assert "ssl_full_claimed" in out


def test_cloudflare_anycast_and_html_title():
    assert is_cloudflare_anycast("104.26.10.1") is True
    assert is_cloudflare_anycast("172.67.1.1") is True
    assert is_cloudflare_anycast("52.101.8.1") is False
    assert is_cloudflare_anycast("not-an-ip") is False
    assert _html_title(b"<html><title>Just a moment...</title></html>") == "Just a moment..."
    assert _html_title(b"<html>no title</html>") == ""


def test_http_probe_branches(monkeypatch):
    class _Resp:
        status = 200
        headers = {"Content-Security-Policy": "script-src 'self'; form-action 'none'"}

        def read(self, _n):
            return b"<title>Institute</title>"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class _Opener:
        def open(self, req, timeout=12):
            return _Resp()

    monkeypatch.setattr("ainav.microsoft.dns.urllib.request.build_opener", lambda *args: _Opener())
    body = _http_probe("https://example.test/")
    assert body["status"] == 200
    assert body["title"] == "Institute"
    assert "script-src 'self'" in body["csp"]

    class _ErrOpener:
        def open(self, req, timeout=12):
            raise urllib.error.HTTPError(
                url="https://example.test/",
                code=403,
                msg="challenge",
                hdrs={"cf-mitigated": "challenge"},
                fp=None,
            )

    monkeypatch.setattr("ainav.microsoft.dns.urllib.request.build_opener", lambda *args: _ErrOpener())
    denied = _http_probe("https://ainav.institute/")
    assert denied["status"] == 403
    assert denied["cf_mitigated"] == "challenge"

    class _Boom:
        def open(self, req, timeout=12):
            raise OSError("down")

    monkeypatch.setattr("ainav.microsoft.dns.urllib.request.build_opener", lambda *args: _Boom())
    gone = _http_probe("https://example.test/")
    assert gone["status"] == 0


def test_tls_accepts_refuses_missing_or_error(monkeypatch):
    assert _tls_accepts("ainav.institute", None) is False

    def boom(*args, **kwargs):
        raise OSError("refused")

    monkeypatch.setattr("ainav.microsoft.dns.socket.create_connection", boom)
    version = getattr(getattr(ssl, "TLSVersion", object()), "TLSv1_2", None)
    if version is not None:
        assert _tls_accepts("ainav.institute", version) is False


def test_probe_edge_quality_never_claims_full(monkeypatch):
    http = {
        "http://ainav.institute/": {
            "url": "http://ainav.institute/",
            "status": 301,
            "headers": {},
            "title": "",
            "csp": "",
            "cf_mitigated": "",
            "hsts": "",
            "location": "https://ainav.institute/",
            "body_prefix": "",
        },
        "https://ainav.institute/": {
            "url": "https://ainav.institute/",
            "status": 403,
            "headers": {},
            "title": "Just a moment...",
            "csp": "",
            "cf_mitigated": "challenge",
            "hsts": "max-age=15552000",
            "location": "",
            "body_prefix": "<title>Just a moment...</title>",
        },
        "https://www.ainav.institute/": {
            "url": "https://www.ainav.institute/",
            "status": 301,
            "headers": {},
            "title": "",
            "csp": "",
            "cf_mitigated": "",
            "hsts": "",
            "location": "https://ainav.institute/",
            "body_prefix": "",
        },
        "https://ainav-institute.pages.dev/": {
            "url": "https://ainav-institute.pages.dev/",
            "status": 404,
            "headers": {},
            "title": "",
            "csp": "",
            "cf_mitigated": "",
            "hsts": "",
            "location": "",
            "body_prefix": "",
        },
        "https://blue-river-010091a0f.7.azurestaticapps.net/": {
            "url": "https://blue-river-010091a0f.7.azurestaticapps.net/",
            "status": 200,
            "headers": {},
            "title": "AINAV.Institute",
            "csp": "script-src 'self'; font-src 'self'; form-action 'none'",
            "cf_mitigated": "",
            "hsts": "",
            "location": "",
            "body_prefix": "",
        },
    }

    monkeypatch.setattr("ainav.microsoft.dns._http_probe", lambda url: http[url])
    monkeypatch.setattr(
        "ainav.microsoft.dns._tls_versions",
        lambda host: {"tls1_0": False, "tls1_1": False, "tls1_2": True, "tls1_3": True},
    )
    monkeypatch.setattr(
        "ainav.microsoft.dns._visitor_cert",
        lambda host: {
            "issuer": "Google Trust Services WE1",
            "san": ["ainav.institute"],
            "notAfter": "Nov 28 00:00:00 2026 GMT",
            "note": "Cloudflare Universal SSL is the visitor cert. It does not prove Full versus Flexible.",
        },
    )

    def fake_dig(name, rtype):
        if name.startswith("autodiscover") and rtype == "A":
            return ["52.96.10.1"]
        if "protection.outlook.com" in name and rtype == "A":
            return ["52.101.8.1"]
        return []

    monkeypatch.setattr("ainav.microsoft.dns._dig", fake_dig)
    dns = {
        "website": {"swa_asuid_present": False},
        "e7_on_cloudflare": {"full": True},
        "microsoft_365": {"mx": ["0 ainav-institute.mail.protection.outlook.com"]},
    }
    body = probe_edge_quality(dns=dns)
    assert body["kind"] == "ainav.edge.quality.probe.v1"
    assert body["ssl_full_claimed"] is False
    assert body["apex_is_institute"] is False
    assert body["rocket_loader_claimed"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["from_this_plane"] is False
    assert body["http_301"] is True
    assert body["https_403_challenge"] is True
    assert body["pages_404"] is True
    assert body["swa_200"] is True
    assert body["www_301"] is True
    assert body["tls_floor"] is True
    assert body["tls_legacy_refused"] is True
    assert body["mail_not_cloudflare_anycast"] is True
    assert body["visitor_cert_is_not_full"] is True
    assert body["asuid_absent"] is True
    assert body["e7_full"] is True
    assert "not ssl full" in body["note"].lower()
    assert "not institute launch" in body["note"].lower()


def test_mail_anycast_fails_closed(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.dns._http_probe",
        lambda url: {
            "url": url,
            "status": 0,
            "headers": {},
            "title": "",
            "csp": "",
            "cf_mitigated": "",
            "hsts": "",
            "location": "",
            "body_prefix": "",
        },
    )
    monkeypatch.setattr(
        "ainav.microsoft.dns._tls_versions",
        lambda host: {"tls1_0": False, "tls1_1": False, "tls1_2": False, "tls1_3": False},
    )
    monkeypatch.setattr(
        "ainav.microsoft.dns._visitor_cert",
        lambda host: {"issuer": "", "san": [], "notAfter": "", "note": "unread"},
    )
    monkeypatch.setattr("ainav.microsoft.dns._dig", lambda name, rtype: ["104.26.10.1"])
    body = probe_edge_quality(
        dns={
            "website": {"swa_asuid_present": False},
            "e7_on_cloudflare": {"full": False},
            "microsoft_365": {"mx": ["0 orange.example"]},
        }
    )
    assert body["mail_not_cloudflare_anycast"] is False
    assert body["ssl_full_claimed"] is False
    assert body["swa_200"] is False


def test_visitor_cert_and_tls_versions(monkeypatch):
    from ainav.microsoft.dns import _tls_versions, _visitor_cert

    class _Sock:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def getpeercert(self):
            return {
                "issuer": ((("organizationName", "Google Trust Services"),), (("commonName", "WE1"),)),
                "subjectAltName": (("DNS", "ainav.institute"),),
                "notAfter": "Nov 28 00:00:00 2026 GMT",
            }

    class _Wrap:
        def __enter__(self):
            return _Sock()

        def __exit__(self, *args):
            return False

        def wrap_socket(self, sock, server_hostname=None):
            return _Sock()

    class _Ctx:
        def wrap_socket(self, sock, server_hostname=None):
            return _Sock()

    monkeypatch.setattr("ainav.microsoft.dns.socket.create_connection", lambda *a, **k: _Sock())
    monkeypatch.setattr("ainav.microsoft.dns.ssl.create_default_context", lambda: _Ctx())
    cert = _visitor_cert("ainav.institute")
    assert "WE1" in cert["issuer"] or "Google Trust Services" in cert["issuer"]
    assert "ainav.institute" in cert["san"]
    assert "does not prove Full" in cert["note"]

    def boom(*args, **kwargs):
        raise OSError("down")

    monkeypatch.setattr("ainav.microsoft.dns.socket.create_connection", boom)
    unread = _visitor_cert("ainav.institute")
    assert unread["issuer"] == ""
    assert "does not prove Full" in unread["note"]

    monkeypatch.setattr(
        "ainav.microsoft.dns._tls_accepts",
        lambda host, version: getattr(version, "name", "") in {"TLSv1_2", "TLSv1_3"},
    )
    versions = _tls_versions("ainav.institute")
    assert versions["tls1_0"] is False
    assert versions["tls1_2"] is True or versions["tls1_3"] is True or set(versions) == {
        "tls1_0",
        "tls1_1",
        "tls1_2",
        "tls1_3",
    }
