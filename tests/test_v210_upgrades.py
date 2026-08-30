from __future__ import annotations

from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.brief_pdf import render_pdf, write_brief
from ainav.catalog import load_catalog, validate_catalog
from ainav.counsel import msa_markdown, msa_skeleton, order_form, order_form_markdown
from ainav.keep import weekly_keep
from ainav.owner_steps import owner_steps_markdown, public_owner_steps
from ainav.packs import book_service
from ainav.proof_day import run_proof_day
from ainav.runbooks import all_runbooks


def test_owner_is_james_and_cynthia_is_invited_not_recorded():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.36.0"
    assert {item["id"] for item in cat["plane_interface"]["floor"]["not_the_gate"]} >= {
        "vendor_native",
        "teams",
        "pim",
        "copilot",
    }
    assert cat["plane_interface"]["floor"]["proof_close"]["walk_out"] == cat["proof_day"]["walk_out"]
    page = cat["plane_interface"]["floor"]["page"]
    assert page["product_first"] is True
    assert page["twin_heading"] == "Proof day"
    assert page["twin_is"] == cat["microsoft_stack"]["not_the_product"]
    assert page["sale"] == cat["plane_interface"]["floor"]["proof_close"]["sale"]
    assert page["product_path"] == ["buyer", "twin", "product"]
    assert page["company_after"] == "about"
    acc = cat["plane_interface"]["floor"]["accountable"]
    assert "duty matrix" in acc["lede"].lower()
    assert {item["id"] for item in acc["items"]} >= {"admit", "freeze", "keep", "not_a_seat"}
    assert acc["items"][2]["note"] == cat["plane_interface"]["floor"]["must_have"]["for"]["examiner"]
    assert "lab oids are not two named" in " ".join(item["note"] for item in acc["items"]).lower()
    protect = cat["plane_interface"]["floor"]["protect"]
    assert "not counsel" in protect["lede"].lower()
    assert {item["id"] for item in protect["items"]} >= {
        "disclaimer",
        "attest",
        "policy",
        "update",
    }
    assert protect["items"][1]["note"] == cat["governance"]["records"]["second"]["what"]
    assert "does not certify" in protect["items"][0]["note"].lower()
    assert "not a signature" in protect["items"][0]["note"].lower()
    assert "cannot weaken job c" in protect["items"][2]["note"].lower()
    assert "a rebrand breaks gold" in protect["items"][3]["note"].lower()
    memory = cat["plane_interface"]["floor"]["memory"]
    assert "two records and a keep" in memory["lede"].lower()
    assert {item["id"] for item in memory["items"]} >= {"first", "keep", "reset", "rollback"}
    assert memory["items"][0]["note"] == cat["governance"]["records"]["first"]["what"]
    assert memory["items"][1]["note"] == next(
        item["note"] for item in cat["plane_interface"]["write_path"] if item["id"] == "keep"
    )
    assert memory["items"][2]["note"] == cat["governance"]["plane"]["reset"]["does"]
    assert "not a time machine" in memory["items"][3]["note"].lower()
    integrate = cat["plane_interface"]["floor"]["integrate"]
    assert "cannot create users" in integrate["lede"].lower()
    assert [item["id"] for item in integrate["items"]] == [
        item["id"] for item in cat["owner_gates"]
    ]
    assert all(item["url"].startswith("https://") for item in integrate["items"])
    assert integrate["items"][0]["url"].startswith("https://admin.microsoft.com")
    assert integrate["items"][2]["url"].startswith("https://admin.cloud.microsoft")
    assert "2ad041b8" not in integrate["items"][3]["url"]
    assert "write does not land" in cat["plane_interface"]["floor"]["no_means"]["fail_closed"].lower()
    assert "business central" in cat["plane_interface"]["floor"]["already_have"].lower()
    assert "gate" in cat["plane_interface"]["floor"]["still_lack"].lower()
    assert set(cat["plane_interface"]["floor"]["must_have"]["for"]) >= {"owner", "board", "examiner"}
    assert "must-have" in cat["equations"]["interface"]
    assert "humans from the top" in cat["equations"]["interface"]
    assert "walkable rehearsal" in cat["equations"]["interface"]
    assert "authorization lifecycle" in cat["equations"]["interface"]
    assert "sealed records" in cat["equations"]["interface"]
    assert "provision bands" in cat["equations"]["interface"]
    floor_must = cat["plane_interface"]["floor"]["must_have"]
    assert floor_must["mandated"] is False
    assert floor_must["certified"] is False
    assert floor_must["sku"] is False
    assert floor_must["why"] == cat["governance"]["must_have"]["why"]
    assert floor_must["incident"] == cat["l1_incident_copy"]
    assert "must-have" in cat["plane_interface"]["floor"]["lede"].lower()
    assert cat["plane_interface"]["client_dashboard"]["included_with"] == "L1"
    assert cat["plane_interface"]["client_dashboard"]["upsell"] is False
    assert cat["plane_interface"]["dashboard"]["upsell"] is False
    assert "catalog list" in cat["equations"]["investor"]
    assert cat["investor"]["priced_round"] is False
    assert cat["investor"]["equity_offered"] is False
    assert "client utilizes AI" in cat["equations"]["control"]
    assert "institutes AINav" in cat["equations"]["cascade"]
    assert "one admit plane" in cat["equations"]["umbrella"]
    assert "off-switch" in cat["equations"]["plane"]
    assert "org chart" in cat["equations"]["org"]
    assert "independence" in cat["equations"]["insulation"]
    assert cat["icp"]["independent_of_microsoft"] is True
    assert cat["icp"]["counterparties_utilize_ai"] is True
    assert cat["icp"]["sits_over_client_ai"] is True
    assert cat["icp"]["org_chart"] is True
    assert "institutes" in cat["icp"]["institutes_ainav"].lower()
    assert cat["operating"]["owner_principal"] == "James Hodnett"
    invited = cat["organization"]["contacts"]["invited"]
    assert invited["name"] == "Cynthia Hodnett"
    assert invited["recorded"] is False
    assert invited["email"] is None
    assert invited["equity"] is False
    assert cat["organization"]["second_officer"] is None
    assert cat["organization"]["contacts"]["second_unique_human"] is False


def test_commercial_equation_is_not_the_lab_pin():
    cat = load_catalog()
    assert "named dual seats" in cat["equations"]["commercial"]
    assert cat["equations"]["lab_pin"] == "LIVE_PIN_OK"
    assert cat["counsel"]["signed"] is False
    assert order_form()["unsigned"] is True
    assert msa_skeleton()["g12_open"] is True
    assert "unsigned" in order_form_markdown().lower()
    assert "MSA skeleton" in msa_markdown()


def test_billable_ffs_requires_l1():
    with pytest.raises(Exception) as exc:
        book_service("ffs.replay_workshop", skus=())
    assert exc.value.reason_code == "FFS_SCOPE"


def test_keep_artifact_is_not_live():
    body = weekly_keep(client_id="keep-test")
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wired"] is False
    assert body["effect"] == "effect_applied"


def test_proof_day_rejects_one_human():
    with pytest.raises(Exception) as exc:
        run_proof_day("pd", seat_a="oid-james", seat_b="oid-james")
    assert exc.value.reason_code == "SEAT_DISTINCT"


def test_proof_day_can_bind_named_oids():
    body = run_proof_day("pd-named", seat_a="oid-james", seat_b="oid-cynthia")
    assert body["seats"]["named_humans"] is True
    assert body["seats"]["seat_b"]["bound"] == "oid-cynthia"
    assert body["signed_l1"] is False


def test_runbooks_are_not_skus():
    body = all_runbooks()
    assert all(item["sku"] is False for item in body["items"])
    assert any(item["id"] == "industry.controller" for item in body["items"])


def test_owner_steps_have_links():
    md = owner_steps_markdown()
    assert "admin.microsoft.com" in md
    assert "Cynthia Hodnett" in md
    assert "James Hodnett" in md
    pub = public_owner_steps()
    assert pub["invited"]["email"] is None
    assert pub["live_pin_ok"] is False


def test_printable_brief_is_a_pdf():
    from ainav.brief_pdf import brief_html, brief_markdown

    raw = render_pdf()
    assert raw.startswith(b"%PDF-1.4")
    assert b"Cynthia" in raw or b"AINAV" in raw
    md = brief_markdown()
    assert "Cynthia Hodnett" in md
    assert "treasury_controller" in md
    assert "not a contract" in md.lower()
    assert "unauthorized general-journal" in md
    assert "why a client must have this" in md.lower()
    assert md.lower().index("why a client must have this") < md.lower().index("investor packet")
    assert md.lower().index("already have") < md.lower().index("investor packet")
    assert "owner, board, examiner" in md.lower()
    assert md.lower().index("not the gate") < md.lower().index("investor packet")
    assert md.lower().index("the product is the admit plane") < md.lower().index("investor packet")
    assert md.lower().index("who may admit, freeze, keep") < md.lower().index("investor packet")
    assert "lab oids are not two named" in md.lower()
    assert "sealed decisionrecord" in md.lower()
    assert "ninety minutes" in md
    assert "Tuesday" in md
    assert "Where we actually are" in md
    assert "Financial model" in md or "catalog list" in md.lower()
    assert "Fifteen" in md or "15" in md
    assert "Named dual seats" in md
    assert "not recorded" in md.lower()
    assert "Investor executive summary" in md or "Investor packet" in md
    assert "priced round" in md.lower()
    assert "industry.payables" in md or "Upsell catalog" in md
    html = brief_html()
    assert "Executive brief" in html
    assert "Cynthia Hodnett" in html
    assert "<table>" in html
    from ainav.brief_pdf import brief_sections

    sections = brief_sections()
    assert any(title for title, _ in sections)
    path = write_brief(Path("docs/CYNTHIA_HODNETT_BRIEF.pdf"))
    assert path.exists()
    assert path.read_bytes().startswith(b"%PDF")
    assert Path("docs/CYNTHIA_HODNETT_BRIEF.md").exists()
    assert Path("docs/CYNTHIA_HODNETT_BRIEF.html").exists()


def test_cli_owner_and_counsel(capsys):
    from ainav.__main__ import main

    assert main(["owner-steps"]) == 0
    assert "Cynthia Hodnett" in capsys.readouterr().out
    assert main(["order-form"]) == 0
    assert "L1" in capsys.readouterr().out
    assert main(["msa"]) == 0
    assert "unsigned" in capsys.readouterr().out.lower()
    assert main(["runbooks"]) == 0
    assert "industry.treasury" in capsys.readouterr().out
    assert main(["finance"]) == 0
    assert "catalog" in capsys.readouterr().out.lower()
    assert main(["governance"]) == 0
    assert "failsafe" in capsys.readouterr().out.lower()
    assert main(["control-plane"]) == 0
    assert "dashboard" in capsys.readouterr().out.lower()
    assert main(["dashboard"]) == 0
    assert "CONTROL_PLANE" in capsys.readouterr().out
    assert main(["ip"]) == 0
    assert "not uncopyable" in capsys.readouterr().out.lower()
    assert main(["investor"]) == 0
    assert "priced round" in capsys.readouterr().out.lower()
    assert main(["investor-pdf"]) == 0
    assert "INVESTOR" in capsys.readouterr().out
    assert main(["keep-artifact"]) == 0
    assert "live_pin_ok" in capsys.readouterr().out
    assert main(["brief-pdf"]) == 0
    assert "CYNTHIA" in capsys.readouterr().out
    assert main(["proof-day", "--seat-a", "oid-a", "--seat-b", "oid-b"]) == 0
    assert "named_humans" in capsys.readouterr().out


def test_cannot_record_invited_human(monkeypatch):
    import copy

    cat = copy.deepcopy(load_catalog())
    cat["organization"]["contacts"]["invited"]["recorded"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
