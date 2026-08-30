from __future__ import annotations

from ainav.microsoft.dns import probe_dns


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
    assert main(["dns"]) == 0
    out = capsys.readouterr().out
    assert "ainav.dns.v1" in out
    assert "launch_ready" in out
