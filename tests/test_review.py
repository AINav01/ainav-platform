from __future__ import annotations

from pathlib import Path

from ainav.review import deep_dive, public_card, review_json, review_model


def test_deep_dive_is_catalog_honest():
    body = deep_dive()
    assert "AINav, Inc." in body
    assert "Job C" in body
    assert "LIVE_PIN_OK × proof day × signed L1 × P-ADM attach" in body
    assert "Launch ready:** false" in body
    assert "AINAV-L1" in body
    assert "bc.general_journal.post" in body
    assert "Dataverse" in body
    assert "Squarespace registrar transfer" in body
    assert "empty Cloudflare Pages" in body
    assert "Pages is not the Institute" in body
    assert "Squarespace Coming Soon" not in body
    assert "launch_not_ready" in body
    assert "E7 on Cloudflare" in body
    assert "full=true" in body
    assert "dash.cloudflare.com" in body
    assert "E7 DNS is full" in body or "dns is full" in body.lower()
    assert "Gold CI" in body
    assert ".github/workflows/gold.yml" in body
    assert "make gold" in body
    assert "observed_green=true" in body
    assert "Closed in this tree" in body
    assert "Work IQ User" in body
    assert "Seat object ids. Not a seat." in body
    assert "Owner steps:" in body
    assert "https://admin.microsoft.com" in body
    assert "James Hodnett" in body
    assert "DayTradingMarkets" in body
    assert "Cynthia Hodnett" in body
    assert "named dual seats" in body
    assert "Named customers:** none" in body
    assert "Success equation scorecard" in body
    assert "How the pieces fit" in body
    assert "Read the company" in body
    assert "## Owner — James must click" in body
    assert "G1/G10 LIVE_PIN_OK" in body
    assert "## Competitive field (honest)" in body
    assert "## Success program — bake-off, qualify, walk away" in body
    assert "## Stack walk" in body
    assert "dash.cloudflare.com" in body
    assert "python -m ainav stack" in body
    assert "## Success upgrades" in body
    assert "licensed substitute" in body.lower()
    assert "Workflow User Groups" in body
    assert "One seat missing" in body or "write does not land" in body.lower()
    assert "Workflow User Group" in body
    assert "Copilot Studio" in body
    assert "not a patent" in body.lower()
    assert "Closed:** false" in body
    assert "Live probe overlay" not in body
    on_disk = Path("docs/REVIEW.md").read_text(encoding="utf-8")
    assert on_disk == body


def test_review_json_cannot_claim_live():
    body = review_json()
    assert body["kind"] == "ainav.review.v1"
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["launch_ready"] is False
    assert body["signed_l1"] is False
    assert body["recognized_revenue"] is None
    assert body["named_customers"] == []
    assert body["second_officer"] is None
    assert body["operator_is_seat"] is False
    assert body["equation"]["closed"] is False
    assert body["equation"]["p_adm_attached"] == 0
    assert body["attached"] == {"L1": 0, "P-ADM": 0, "U-DUAL": 0}
    assert body["agent_tools_is_admit_plane"] is False
    assert "markdown" in body
    card = public_card()
    assert "markdown" not in card
    assert card["live"] is False
    assert card["probed"] is False
    assert card["expert_review"]["success"]["live_pin_ok"] is False
    assert len(card["expert_review"]["upgrades"]) == 40


def test_review_model_fit_covers_the_company():
    model = review_model()
    ids = [item["id"] for item in model["fit"]]
    assert ids == [
        "owner",
        "admit",
        "l1",
        "p_adm",
        "u_dual",
        "institute",
        "programs",
        "pipeline",
    ]
    assert all(item["note"] for item in model["fit"])
    assert model["cli"][0] == "python -m ainav review"


def test_probe_overlay_is_read_only(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.health.stack_health",
        lambda probe=None: {"connected": ["bc.premium"], "blocked": ["sales.enterprise"]},
    )
    monkeypatch.setattr(
        "ainav.microsoft.dns.probe_dns",
        lambda: {
            "cloudflare_nameservers": True,
            "website": {"swa_asuid_present": False},
            "microsoft_365": {"mx_outlook": True, "teams_sip": False},
        },
    )
    body = deep_dive(probe=True)
    assert "Live probe overlay" in body
    assert "bc.premium" in body
    assert "Not LIVE_PIN_OK" in body
    assert "Departments wired now" in body
    assert "does not promote blocked" in body.lower() or "Does not promote blocked" in body
    probed = review_model(probe=True)
    assert probed["probed"] is True
    assert probed["probe"]["live"] is False
    assert probed["probe"]["live_pin_ok"] is False
    assert probed["probe"]["launch_ready"] is False
    assert probed["probe"]["custom_domain_claimed"] is False
    assert "bc.premium" in probed["probe"]["connected"]


def test_cli_review(capsys):
    from ainav.__main__ import main

    assert main(["review"]) == 0
    out = capsys.readouterr().out
    assert "deep-dive review" in out
    assert "not a seat" in out.lower() or "Operator:** cursor.cloud_agent" in out
    assert "How the pieces fit" in out
