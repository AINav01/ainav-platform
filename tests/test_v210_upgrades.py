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


def test_owner_is_james_and_cynthia_mailbox_is_recorded():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.66.0"
    edge = cat["microsoft_stack"]["edge"]
    assert edge["id"] == "cloudflare.dns"
    assert edge["sku"] is False
    assert edge["full"] is True
    assert edge["is_admit_plane"] is False
    assert edge["complement"] is False
    assert edge["missing"] == []
    assert "sip" in " ".join(edge["already"]).lower()
    assert "lync" in " ".join(edge["already"]).lower()
    assert {item["id"] for item in cat["plane_interface"]["floor"]["not_the_gate"]} >= {
        "vendor_native",
        "teams",
        "pim",
        "copilot",
        "bc_workflow",
        "in_harness",
    }
    glance = cat["plane_interface"]["floor"]["first_glance"]
    assert glance["skus"] == ["L1", "P-ADM", "U-DUAL"]
    assert [item["id"] for item in glance["write_rail"]] == ["seat_a", "seat_b", "hash", "write"]
    assert "gate" in glance["rail_kicker"].lower()
    dash_glance = cat["plane_interface"]["dashboard"]["first_glance"]
    assert dash_glance["same_as"] == "client_dashboard"
    assert dash_glance["uses"] == "write_rail"
    assert [item["id"] for item in dash_glance["write_rail"]] == [item["id"] for item in glance["write_rail"]]
    assert "one dashboard" in dash_glance["lede"].lower()
    face = cat["plane_interface"]["floor"]["public_face"]
    assert face["cms"] is False
    assert face["application"] is True
    assert face["app"]["href"] == "app.html"
    assert face["launch"] is False
    assert [item["label"] for item in face["primary"]] == [
        "The write",
        "Proof day",
        "Bake-off",
        "Dashboard",
        "Owner",
    ]
    assert glance["uses"] == "not_the_gate"
    floor_success = cat["plane_interface"]["floor"]["success"]
    assert floor_success["uses"] == "expert_review.success"
    assert floor_success["lede"] == cat["expert_review"]["success"]["thesis"]
    assert glance["sku"] is False
    assert "substitute" in glance["lede"].lower()
    assert "not agent inventory" in glance["job_c"].lower()
    seat_note = next(
        item["note"] for item in cat["plane_interface"]["authorizations"] if item["id"] == "seat"
    )
    assert "1 mailbox" in seat_note.lower()
    assert "0 oid" in seat_note.lower()
    assert "invited, not recorded" not in seat_note.lower()
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
    assert "paid" in integrate["items"][0]["note"].lower()
    assert "e7" in integrate["items"][0]["note"].lower()
    assert "teams premium" in integrate["items"][0]["note"].lower()
    assert "not a seat" in integrate["items"][0]["note"].lower()
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
    assert "view assignment" in cat["equations"]["interface"]
    assert "MFA identify" in cat["equations"]["interface"]
    floor_must = cat["plane_interface"]["floor"]["must_have"]
    assert floor_must["mandated"] is False
    assert floor_must["certified"] is False
    assert floor_must["sku"] is False
    assert floor_must["why"] == cat["governance"]["must_have"]["why"]
    assert floor_must["incident"] == cat["l1_incident_copy"]
    assert "must-have" in cat["plane_interface"]["floor"]["lede"].lower()
    assert cat["plane_interface"]["client_dashboard"]["included_with"] == "L1"
    assert cat["plane_interface"]["client_dashboard"]["upsell"] is False
    offer = cat["plane_interface"]["included_and_upsells"]
    assert offer["sku"] is False
    assert offer["fourth_sku"] is False
    assert offer["included_means_free"] is False
    assert offer["u_dual_never_free"] is True
    assert [item["id"] for item in offer["first_glance"]["columns"]] == [
        "included_with_l1",
        "upsell_band",
    ]
    assert "not a gift" in offer["first_glance"]["lede"].lower()
    assert "included means free" in [item.lower() for item in offer["refuse"]]
    board = cat["plane_interface"]["client_dashboard"]["executive_board"]
    assert board["default_view"] == "client"
    assert board["sku"] is False
    assert [item["id"] for item in board["sections"]] == [
        "write_rail",
        "attention",
        "seats",
        "keep",
        "offer",
    ]
    assign = cat["plane_interface"]["view_assignment"]
    assert assign["sku"] is False
    assert assign["same_dashboard"] is True
    assert assign["included_with"] == "L1"
    assert assign["named_assignments"] == []
    assert assign["assignment_live"] is False
    assert assign["mfa"]["mfa_live"] is False
    assert assign["mfa"]["is_admit"] is False
    assert assign["disclaimers"]["legal"] == "AINav, Inc."
    assert assign["authorize"]["fail_closed"] is True
    assert assign["deauthorize"]["fail_closed"] is True
    assert {row["org_nodes"][0] for row in assign["matrix"]} == {
        item["id"] for item in cat["client_org"]["departments"]
    }
    assert cat["plane_interface"]["dashboard"]["upsell"] is False
    assert "catalog list" in cat["equations"]["investor"]
    assert cat["investor"]["priced_round"] is False
    assert cat["investor"]["equity_offered"] is False
    summary = cat["investor"]["executive_summary"]
    assert summary["sku"] is False
    assert summary["certified"] is False
    assert summary["mandated"] is False
    assert summary["proof"] == cat["buyer"]["proof_day"]
    assert "second human" in cat["investor"]["letter_open"].lower()
    assert "i am writing" in cat["investor"]["letter_open"].lower()
    assert cat["investor"]["letter_voice"] == "first_person"
    assert [item["id"] for item in cat["investor"]["executive_summary"]["items"]] == [
        "job_c",
        "proof",
        "skus",
        "tiles",
        "microsoft",
        "must_have",
        "opens",
        "ask",
    ]
    assert "seat b" in cat["investor"]["letter_body"].lower()
    assert "mailbox is now recorded" in cat["investor"]["letter_body"].lower()
    assert "chodnett@ainav.institute" in cat["investor"]["letter_body"].lower()
    assert "i will not ask" in cat["investor"]["letter_body"].lower()
    assert "i trust" in cat["investor"]["letter_body"].lower()
    assert "delaware" not in cat["investor"]["letter_body"].lower()
    assert "board packet" in cat["investor"]["executive_summary"]["lede"].lower()
    assert "sole owner" in cat["investor"]["letter_close"].lower()
    assert "$0" in summary["tiles"]
    assert "not the product" in summary["microsoft"].lower()
    assert "live_pin_ok cannot be marked" in summary["opens"].lower()
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
    assert invited["agreed"] is True
    assert invited["recorded"] is True
    assert invited["email"] == "chodnett@ainav.institute"
    assert invited["entra_oid"] is None
    assert invited["seat_clicked"] is False
    assert invited["second_unique_human"] is False
    assert invited["equity"] is False
    assert invited["officer"] is False
    assert invited["number_two"] is True
    assert invited["all_aspects"] is False
    assert cat["organization"]["number_two"]["scope"] == "other_aspects"
    assert cat["organization"]["number_two"]["all_aspects"] is False
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
    assert pub["invited"]["email"] == "chodnett@ainav.institute"
    assert pub["invited"]["recorded"] is True
    assert pub["invited"]["agreed"] is True
    assert pub["invited"]["entra_oid"] is None
    assert pub["invited"]["seat_clicked"] is False
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
    assert "executive summary" in md.lower()
    assert "a letter to cynthia hodnett" in md.lower()
    assert md.lower().index("executive summary") < md.lower().index("a letter to cynthia")
    assert md.lower().index("a letter to cynthia") < md.lower().index("why we need you")
    assert md.lower().index("why we need you") < md.lower().index("why a client must have this")
    assert md.lower().index("what a tuesday looks like") < md.lower().index("why a client must have this")
    assert md.lower().index("a letter to cynthia") < md.lower().index("why a client must have this")
    assert "dear cynthia" in md.lower()
    assert "i am writing" in md.lower()
    assert "item" in md.lower() and "what it is" in md.lower()
    assert "chodnett@ainav.institute" in md.lower()
    assert "mailbox recorded" in md.lower()
    assert md.lower().index("why a client must have this") < md.lower().index("investor packet")
    assert md.lower().index("already have") < md.lower().index("investor packet")
    assert "owner, board, examiner" in md.lower()
    assert md.lower().index("not the gate") < md.lower().index("investor packet")
    assert md.lower().index("the product is the admit plane") < md.lower().index("investor packet")
    assert md.lower().index("who may admit, freeze, keep") < md.lower().index("investor packet")
    assert md.lower().index("why a client must have this") < md.lower().index("the write that must not happen")
    assert "appendix — the plane" in md.lower()
    assert md.lower().index("a letter to cynthia") < md.lower().index("appendix — the plane")
    assert md.lower().index("appendix — the plane") < md.lower().index("complete the stack")
    assert "| step | what the owner clicks | link |" in md.lower()
    assert "admin.microsoft.com" in md
    assert "lab oids are not two named" in md.lower()
    assert "sealed decisionrecord" in md.lower()
    assert "ninety minutes" in md
    assert "Tuesday" in md
    assert "Where we actually are" in md
    assert "Financial model" in md or "catalog list" in md.lower()
    assert "Success upgrades" in md or "Bake-off" in md
    assert "Named dual seats" in md
    assert "not recorded as an officer" in md.lower()
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


def test_recorded_mailbox_refuses_oid_click_and_wrong_inbox():
    import copy

    cat = load_catalog()
    oid = copy.deepcopy(cat)
    oid["organization"]["contacts"]["invited"]["entra_oid"] = "invented-oid"
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(oid)
    assert exc.value.reason_code == "ORG_SECOND_OFFICER"
    clicked = copy.deepcopy(cat)
    clicked["organization"]["contacts"]["invited"]["seat_clicked"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(clicked)
    assert exc2.value.reason_code == "ORG_SECOND_OFFICER"
    gmail = copy.deepcopy(cat)
    gmail["organization"]["contacts"]["invited"]["email"] = "chodnett@gmail.com"
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(gmail)
    assert exc3.value.reason_code == "ORG_SECOND_OFFICER"
    alias = copy.deepcopy(cat)
    alias["organization"]["contacts"]["invited"]["email"] = "james@ainav.institute"
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(alias)
    assert exc4.value.reason_code == "ORG_SECOND_OFFICER"
    human = copy.deepcopy(cat)
    human["organization"]["contacts"]["invited"]["second_unique_human"] = True
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(human)
    assert exc5.value.reason_code == "ORG_SECOND_OFFICER"
    agreed_only = copy.deepcopy(cat)
    agreed_only["organization"]["contacts"]["invited"]["recorded"] = False
    agreed_only["organization"]["contacts"]["invited"]["email"] = None
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(agreed_only)
    assert exc6.value.reason_code == "ORG_SECOND_OFFICER"
