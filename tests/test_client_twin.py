from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.buyer import success_program
from ainav.catalog import load_catalog, validate_catalog


def test_client_twin_is_catalog_law_and_on_the_sale_site():
    cat = load_catalog()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "client-assigned" in blob
    assert "segregated" in blob
    assert "client twin" in blob
    twin = cat["expert_review"]["success"]["client_twin"]
    assert twin["kind"] == "ainav.client_twin.v1"
    assert twin["sku"] is False
    assert twin["fourth_sku"] is False
    assert twin["assigned"] is False
    assert twin["production"] is False
    assert twin["launch"] is False
    assert twin["live_pin_ok"] is False
    assert twin["named_client"] is None
    assert twin["do_not_invent_names"] is True
    stages = " ".join(twin["stages"]).lower()
    for stem in ("qualify", "remote proof", "close l1", "assigned sandbox", "paid enhance"):
        assert stem in stages
    exported = success_program()["client_twin"]
    assert exported["lede"] == twin["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin_html = Path("institute/twin.html").read_text(encoding="utf-8")
    assert 'id="path"' in html
    assert 'id="path-console"' in html
    assert "paintClientTwin" in js
    assert 'href="#path">Client twin</a>' in html
    assert "Close on a client twin" in html
    assert 'id="close-console"' in html
    assert "Assigned sandbox" in html
    assert "fourth SKU" in html
    assert 'href="/path"' not in html
    assert html.index('id="product"') < html.index('id="path"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#path"' not in nav
    assert "index.html#path" in twin_html
    walk = cat["expert_review"]["success"]["qualify"]["walk_away"]
    assert len(walk) == 20
    assert any("calendly" in item.lower() and "client twin" in item.lower() for item in walk)
    objections = {item["id"] for item in cat["expert_review"]["success"]["objections"]}
    assert "path" in objections
    sale = cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
    assert [item["href"] for item in sale][-1] == "#join-consider"
    assert [item["href"] for item in sale][-2] == "#firm"
    assert [item["href"] for item in sale][-3] == "#close-consider"
    assert 'id="twin-use"' in html
    assert 'id="twin-use-hops"' in html
    assert 'id="twin-use-lede"' in html
    assert "The Institute twin is not the assigned client sandbox" in html
    assert "Assigned stays 0" in html
    assert 'href="#demo-console"' in html[html.index('id="twin-use-hops"') : html.index('id="twin-use-walk"')]
    assert 'href="#client-planes"' in html[html.index('id="twin-use-hops"') : html.index('id="twin-use-walk"')]
    assert 'href="#firm"' in html[html.index('id="twin-use-hops"') : html.index('id="twin-use-walk"')]
    assert "index.html#twin-use" in twin_html
    hops = html[html.index('id="join-hops"') : html.index("</ol>", html.index('id="join-hops"'))]
    assert hops.count("<li") == 11
    assert 'id="client-proof"' in html
    assert 'id="client-proof-hops"' in html
    assert 'id="client-proof-lede"' in html
    assert 'id="client-proof-need"' in html
    assert 'id="client-proof-why"' in html
    assert 'id="client-proof-zeros"' in html
    assert 'id="client-proof-facts"' in html
    assert 'id="client-proof-cut"' in html
    assert "client-proof-lede" not in js
    assert "A 10/10 client is not a live client" in html
    assert "A certified client simulation is not a named client" in html
    assert "Walk the client 10/10" in html
    assert 'id="client-proof-is-named">none' in html
    assert 'id="client-proof-is-assigned">no' in html
    assert 'id="client-proof-is-launch">no' in html
    assert 'id="client-proof-is-sim">no' in html
    assert 'id="client-proof-is-assign">no' in html
    assert 'href="/client"' not in html
    assert html.index('id="life-proof"') < html.index('id="client-proof"') < html.index('id="close-console"')
    client_proof = html[html.index('id="client-proof-hops"') : html.index("</ol>", html.index('id="client-proof-hops"'))]
    assert client_proof.count("Need:") == 6
    assert client_proof.count("Why:") == 6
    assert client_proof.count("<li") == 6
    assert 'href="#life-proof"' in client_proof
    assert 'href="#success"' in client_proof
    assert 'href="#client-planes"' in client_proof
    assert 'href="#twin-proof"' in client_proof
    assert 'href="#close-console"' in client_proof
    assert 'href="#missing"' in client_proof
    assert 'href="#client-proof"' in html[html.index('id="life-proof-walk"') : html.index("</p>", html.index('id="life-proof-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="client-planes-walk"') : html.index("</p>", html.index('id="client-planes-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="ten-proof-walk"') : html.index("</p>", html.index('id="ten-proof-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="twin-proof-walk"') : html.index("</p>", html.index('id="twin-proof-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="eco-proof-walk"') : html.index("</p>", html.index('id="eco-proof-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="path-join-walk"') : html.index("</p>", html.index('id="path-join-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="close-join-walk"') : html.index("</p>", html.index('id="close-join-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="twin-use-walk"') : html.index("</p>", html.index('id="twin-use-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="firm-proof-walk"') : html.index("</p>", html.index('id="firm-proof-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="sale-tools-walk"') : html.index("</p>", html.index('id="sale-tools-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="bc-tools-walk"') : html.index("</p>", html.index('id="bc-tools-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="ms-proof-walk"') : html.index("</p>", html.index('id="ms-proof-walk"'))]
    assert 'href="#client-proof"' in html[html.index('id="close-console-walk"') : html.index("</p>", html.index('id="close-console-walk"'))]
    assert "index.html#client-proof" in twin_html
    assert hops.count("<li") == 11
    assert 'id="client-planes"' in html
    assert 'id="client-plane-hops"' in html
    assert "one live client, one sandbox" in html.lower()
    plane = html[html.index('id="client-plane-hops"') : html.index("</ol>", html.index('id="client-plane-hops"'))]
    assert plane.count("Need:") == 6
    assert plane.count("Why:") == 6
    assert plane.count("<li") == 6
    assert 'href="#success"' in plane
    assert 'href="#demo-console"' in plane
    assert 'href="#close-consider"' in plane
    assert 'href="#close-console"' in plane
    assert 'href="#ops"' in plane
    assert 'href="#firm"' in plane
    assert 'href="#twin-use"' in html[html.index('id="path-planes"') : html.index("</ol>", html.index('id="path-planes"'))]
    assert "Walk the segregated planes" in html
    assert "index.html#client-planes" in twin_html
    assert "index.html#client-planes" in Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="client-planes-need"' in html
    assert 'id="client-planes-why"' in html
    assert 'id="client-planes-zeros"' in html
    assert 'id="client-planes-facts"' in html
    assert 'id="client-planes-cut"' in html
    assert 'id="close-console-need"' in html
    assert 'id="close-console-why"' in html
    assert 'id="close-console-walk"' in html
    assert "close-console-lede" not in js
    assert "client-planes-lede" not in js
    assert "twin-use-lede" not in js
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    assert ".plane-island" in css
    assert "#client-planes.is-landed" in css
    assert "#client-proof-hops { grid-template-columns: repeat(3" in css
    assert "#client-proof.is-landed" in css
    assert "#close-console.is-landed" in css
    assert 'id="client-planes-cut"' in html
    assert 'id="twin-proof"' in html
    assert 'id="twin-proof-hops"' in html
    assert 'id="twin-proof-cut"' in html
    assert "twin-proof-lede" not in js
    assert "Named-human proof day" in html
    assert "Twin certified is not launch day" in html
    proof = html[html.index('id="twin-proof-hops"') : html.index("</ol>", html.index('id="twin-proof-hops"'))]
    assert proof.count("Need:") == 6
    assert proof.count("Why:") == 6
    assert proof.count("<li") == 6
    assert 'href="#buyer"' in proof
    assert 'href="#demo-console"' in proof
    assert 'href="kit.html"' in proof
    assert 'href="#ready-lanes"' in proof
    assert 'href="#client-planes"' in proof
    assert 'href="#missing"' in proof
    assert "#twin-proof-hops { grid-template-columns: repeat(3" in css
    assert "#twin-proof.is-landed" in css
    assert "index.html#twin-proof" in twin_html
    assert 'id="life-proof"' in html
    assert 'id="life-proof-hops"' in html
    assert 'id="life-proof-lede"' in html
    assert 'id="life-proof-need"' in html
    assert 'id="life-proof-why"' in html
    assert 'id="life-proof-zeros"' in html
    assert 'id="life-proof-facts"' in html
    assert 'id="life-proof-cut"' in html
    assert "life-proof-lede" not in js
    assert "A walked lifecycle is not a live client" in html
    assert "Walk the client lifecycle" in html
    life = html[html.index('id="life-proof-hops"') : html.index("</ol>", html.index('id="life-proof-hops"'))]
    assert life.count("Need:") == 6
    assert life.count("Why:") == 6
    assert life.count("<li") == 6
    assert 'href="#success"' in life
    assert 'href="#demo-console"' in life
    assert 'href="#close-consider"' in life
    assert 'href="#close-console"' in life
    assert 'href="#ops"' in life
    assert 'href="#firm"' in life
    assert 'href="#life-proof"' in html[html.index('id="twin-proof-walk"') : html.index("</p>", html.index('id="twin-proof-walk"'))]
    assert 'href="#life-proof"' in html[html.index('id="client-planes-walk"') : html.index("</p>", html.index('id="client-planes-walk"'))]
    assert "#life-proof-hops { grid-template-columns: repeat(3" in css
    assert "#life-proof.is-landed" in css
    assert "index.html#life-proof" in twin_html
    assert 'id="eco-proof"' in html
    assert 'id="eco-proof-hops"' in html
    assert 'id="eco-proof-lede"' in html
    assert 'id="eco-proof-need"' in html
    assert 'id="eco-proof-why"' in html
    assert 'id="eco-proof-zeros"' in html
    assert 'id="eco-proof-facts"' in html
    assert 'id="eco-proof-cut"' in html
    assert "eco-proof-lede" not in js
    assert "The stitched ecosystem is not a running firm" in html
    assert "Walk the ecosystem proof" in html
    eco = html[html.index('id="eco-proof-hops"') : html.index("</ol>", html.index('id="eco-proof-hops"'))]
    assert eco.count("Need:") == 6
    assert eco.count("Why:") == 6
    assert eco.count("<li") == 6
    assert 'href="#whole"' in eco
    assert 'href="#buyer"' in eco
    assert 'href="#twin-proof"' in eco
    assert 'href="#life-proof"' in eco
    assert 'href="#firm-ms"' in eco
    assert 'href="#missing"' in eco
    assert 'href="#eco-proof"' in html[html.index('id="twin-proof-walk"') : html.index("</p>", html.index('id="twin-proof-walk"'))]
    assert 'href="#eco-proof"' in html[html.index('id="life-proof-walk"') : html.index("</p>", html.index('id="life-proof-walk"'))]
    assert 'href="#eco-proof"' in html[html.index('id="whole-join-walk"') : html.index("</p>", html.index('id="whole-join-walk"'))]
    assert "#eco-proof-hops { grid-template-columns: repeat(3" in css
    assert "#eco-proof.is-landed" in css
    assert "index.html#eco-proof" in twin_html
    assert 'id="firm-proof"' in html
    assert 'id="firm-proof-hops"' in html
    assert 'id="firm-proof-lede"' in html
    assert 'id="firm-proof-need"' in html
    assert 'id="firm-proof-why"' in html
    assert 'id="firm-proof-zeros"' in html
    assert 'id="firm-proof-facts"' in html
    assert "firm-proof-lede" not in js
    assert "Walk the operating company" in html
    assert "Teams Premium is not a seat" in html
    assert "Co-brand stays unnamed until signed L1" in html
    assert 'id="firm-proof-cut"' in html
    assert html.index('id="firm-lede"') < html.index('id="firm-proof"') < html.index('id="firm-rails"')
    firm_proof = html[html.index('id="firm-proof-hops"') : html.index("</ol>", html.index('id="firm-proof-hops"'))]
    assert firm_proof.count("Need:") == 6
    assert firm_proof.count("Why:") == 6
    assert firm_proof.count("<li") == 6
    assert 'href="#business"' in firm_proof
    assert 'href="#success"' in firm_proof
    assert 'href="#firm-ms"' in firm_proof
    assert 'href="#finance"' in firm_proof
    assert 'href="#brand"' in firm_proof
    assert 'href="#universe"' in firm_proof
    assert 'href="#firm-proof"' in html[html.index('id="eco-proof-walk"') : html.index("</p>", html.index('id="eco-proof-walk"'))]
    assert 'href="#firm-proof"' in html[html.index('id="firm-join-walk"') : html.index("</p>", html.index('id="firm-join-walk"'))]
    assert 'href="#firm-proof"' in html[html.index('id="ops-join-walk"') : html.index("</p>", html.index('id="ops-join-walk"'))]
    assert 'href="#firm-proof"' in html[html.index('id="brand-join-walk"') : html.index("</p>", html.index('id="brand-join-walk"'))]
    assert 'href="#firm-proof"' in html[html.index('id="finance-join-walk"') : html.index("</p>", html.index('id="finance-join-walk"'))]
    assert 'href="#firm-proof"' in html[html.index('id="universe-join-walk"') : html.index("</p>", html.index('id="universe-join-walk"'))]
    assert "#firm-proof-hops { grid-template-columns: repeat(3" in css
    assert "#firm-proof.is-landed" in css
    assert "index.html#firm-proof" in twin_html
    assert 'id="sale-tools"' in html
    assert 'id="sale-tools-hops"' in html
    assert 'id="sale-tools-lede"' in html
    assert 'id="sale-tools-need"' in html
    assert 'id="sale-tools-why"' in html
    assert 'id="sale-tools-zeros"' in html
    assert 'id="sale-tools-facts"' in html
    assert "sale-tools-lede" not in js
    assert "Walk the sales tools" in html
    assert "Sales Enterprise is not the firm CRM" in html
    assert "Microsoft marks are theirs" in html
    assert "Microsoft is not the product" in html
    assert 'id="sale-tools-cut"' in html
    assert 'id="sale-tools-is-crm">no' in html
    assert 'id="sale-tools-is-seat">no' in html
    assert 'id="sale-tools-is-sku">no' in html
    assert 'id="sale-tools-is-wired">no' in html
    assert 'id="sale-tools-is-hubspot">no' in html
    assert html.index('id="firm-lede"') < html.index('id="firm-proof"') < html.index('id="sale-tools"') < html.index('id="bc-tools"') < html.index('id="ms-proof"') < html.index('id="ms-universe"') < html.index('id="firm-rails"')
    sale_tools = html[html.index('id="sale-tools-hops"') : html.index("</ol>", html.index('id="sale-tools-hops"'))]
    assert sale_tools.count("Need:") == 6
    assert sale_tools.count("Why:") == 6
    assert sale_tools.count("<li") == 6
    assert 'href="#ms-sales"' in sale_tools
    assert 'href="#ms-teams-premium"' in sale_tools
    assert 'href="#ms-teams"' in sale_tools
    assert 'href="#ms-e7"' in sale_tools
    assert 'href="#success"' in sale_tools
    assert 'href="#brand"' in sale_tools
    assert 'href="#sale-tools"' in html[html.index('id="firm-proof-walk"') : html.index("</p>", html.index('id="firm-proof-walk"'))]
    assert 'href="#sale-tools"' in html[html.index('id="firm-join-walk"') : html.index("</p>", html.index('id="firm-join-walk"'))]
    assert 'href="#sale-tools"' in html[html.index('id="firm-ms-join-walk"') : html.index("</p>", html.index('id="firm-ms-join-walk"'))]
    assert 'href="#sale-tools"' in html[html.index('id="brand-join-walk"') : html.index("</p>", html.index('id="brand-join-walk"'))]
    assert "#sale-tools-hops { grid-template-columns: repeat(3" in css
    assert "#sale-tools.is-landed" in css
    assert "index.html#sale-tools" in twin_html
    assert '"sales.enterprise": "ms-sales"' in js
    assert '"teams.premium": "ms-teams-premium"' in js
    assert 'id="ms-sales"' in html
    assert 'id="ms-teams-premium"' in html
    assert 'id="ms-teams"' in html
    assert 'id="ms-e7"' in html
    assert 'id="bc-tools"' in html
    assert 'id="bc-tools-hops"' in html
    assert 'id="bc-tools-lede"' in html
    assert 'id="bc-tools-need"' in html
    assert 'id="bc-tools-why"' in html
    assert 'id="bc-tools-zeros"' in html
    assert 'id="bc-tools-facts"' in html
    assert "bc-tools-lede" not in js
    assert "Walk Business Central" in html
    assert "A sandbox journal is not production" in html
    assert "Lab AINAV-L1 is not two named treasury humans" in html
    assert "Controllers already have Business Central" in html
    assert 'id="bc-tools-cut"' in html
    assert 'id="bc-tools-is-prod">no' in html
    assert 'id="bc-tools-is-close">no' in html
    assert 'id="bc-tools-is-wired">no' in html
    assert 'id="bc-tools-is-named">no' in html
    assert 'id="bc-tools-is-sku">no' in html
    assert 'href="/bc"' not in html
    bc_tools = html[html.index('id="bc-tools-hops"') : html.index("</ol>", html.index('id="bc-tools-hops"'))]
    assert bc_tools.count("Need:") == 6
    assert bc_tools.count("Why:") == 6
    assert bc_tools.count("<li") == 6
    assert 'href="#ms-bc"' in bc_tools
    assert 'href="#product"' in bc_tools
    assert 'href="#ms-entra"' in bc_tools
    assert 'href="#ms-azure"' in bc_tools
    assert 'href="#brand"' in bc_tools
    assert 'href="#missing"' in bc_tools
    assert 'href="#bc-tools"' in html[html.index('id="sale-tools-walk"') : html.index("</p>", html.index('id="sale-tools-walk"'))]
    assert 'href="#bc-tools"' in html[html.index('id="firm-proof-walk"') : html.index("</p>", html.index('id="firm-proof-walk"'))]
    assert 'href="#bc-tools"' in html[html.index('id="firm-join-walk"') : html.index("</p>", html.index('id="firm-join-walk"'))]
    assert 'href="#bc-tools"' in html[html.index('id="firm-ms-join-walk"') : html.index("</p>", html.index('id="firm-ms-join-walk"'))]
    assert 'href="#bc-tools"' in html[html.index('id="brand-join-walk"') : html.index("</p>", html.index('id="brand-join-walk"'))]
    assert 'href="#bc-tools"' in html[html.index('id="product-walk"') : html.index("</p>", html.index('id="product-walk"'))]
    assert "#bc-tools-hops { grid-template-columns: repeat(3" in css
    assert "#bc-tools.is-landed" in css
    assert "index.html#bc-tools" in twin_html
    assert '"bc.premium": "ms-bc"' in js
    assert '"azure.host": "ms-azure"' in js
    assert '"entra.id": "ms-entra"' in js
    assert 'id="ms-bc"' in html
    assert 'id="ms-azure"' in html
    assert 'id="ms-entra"' in html
    assert 'id="ten-proof"' in html
    assert 'id="ten-proof-hops"' in html
    assert 'id="ten-proof-lede"' in html
    assert 'id="ten-proof-need"' in html
    assert 'id="ten-proof-why"' in html
    assert 'id="ten-proof-zeros"' in html
    assert 'id="ten-proof-facts"' in html
    assert 'id="ten-proof-cut"' in html
    assert "ten-proof-lede" not in js
    assert "Walk the 10/10" in html
    assert "Making all much better is not launch" in html
    assert "A 10/10+ quality check is not launch" in html
    assert 'id="ten-proof-is-launch">no' in html
    assert 'id="ten-proof-is-gold">no' in html
    assert 'id="ten-proof-is-wired">no' in html
    assert 'id="ten-proof-is-sim">no' in html
    assert 'id="ten-proof-is-seated">no' in html
    assert 'href="/ten"' not in html
    assert html.index('id="ten-lede"') < html.index('id="ten-proof"') < html.index('id="ten-zeros"')
    ten_proof = html[html.index('id="ten-proof-hops"') : html.index("</ol>", html.index('id="ten-proof-hops"'))]
    assert ten_proof.count("Need:") == 6
    assert ten_proof.count("Why:") == 6
    assert ten_proof.count("<li") == 6
    assert 'href="#whole"' in ten_proof
    assert 'href="#eco-proof"' in ten_proof
    assert 'href="#firm-ms"' in ten_proof
    assert 'href="#twin-proof"' in ten_proof
    assert 'href="#bc-tools"' in ten_proof
    assert 'href="#ten-consider"' in ten_proof
    assert 'href="#ten-proof"' in html[html.index('id="ten-join-walk"') : html.index("</p>", html.index('id="ten-join-walk"'))]
    assert 'href="#ten-proof"' in html[html.index('id="eco-proof-walk"') : html.index("</p>", html.index('id="eco-proof-walk"'))]
    assert 'href="#ten-proof"' in html[html.index('id="twin-proof-walk"') : html.index("</p>", html.index('id="twin-proof-walk"'))]
    assert 'href="#ten-proof"' in html[html.index('id="life-proof-walk"') : html.index("</p>", html.index('id="life-proof-walk"'))]
    assert 'href="#ten-proof"' in html[html.index('id="firm-proof-walk"') : html.index("</p>", html.index('id="firm-proof-walk"'))]
    assert 'href="#ten-proof"' in html[html.index('id="sale-tools-walk"') : html.index("</p>", html.index('id="sale-tools-walk"'))]
    assert 'href="#ten-proof"' in html[html.index('id="bc-tools-walk"') : html.index("</p>", html.index('id="bc-tools-walk"'))]
    assert "#ten-proof-hops { grid-template-columns: repeat(3" in css
    assert "#ten-proof.is-landed" in css
    assert "index.html#ten-proof" in twin_html
    assert 'id="ten-need"' in html
    assert 'id="ten-why"' in html
    assert "ten-need" not in js
    assert "ten-lede" not in js
    assert "Walk honest ten" in html
    assert html.index('id="ten-lede"') < html.index('id="ten-need"') < html.index('id="ten-proof"') < html.index('id="ten-zeros"')
    assert 'href="#ten-consider"' in html[html.index('id="ten-proof-walk"') : html.index("</p>", html.index('id="ten-proof-walk"'))]
    assert 'href="#ten-consider"' in html[html.index('id="ten-join-walk"') : html.index("</p>", html.index('id="ten-join-walk"'))]
    assert "Walk the industry" in html[html.index('id="ten-join-walk"') : html.index("</p>", html.index('id="ten-join-walk"'))]
    assert "Walk Agent Intent" in html[html.index('id="ten-join-walk"') : html.index("</p>", html.index('id="ten-join-walk"'))]
    assert "#ten-consider.is-landed" in css
    assert 'href="/ten"' not in html
    assert 'id="ms-proof"' in html
    assert 'id="ms-proof-hops"' in html
    assert 'id="ms-proof-lede"' in html
    assert 'id="ms-proof-need"' in html
    assert 'id="ms-proof-why"' in html
    assert 'id="ms-proof-zeros"' in html
    assert 'id="ms-proof-facts"' in html
    assert 'id="ms-proof-cut"' in html
    assert "ms-proof-lede" not in js
    assert "Walk the Microsoft 10/10" in html
    assert "A 10/10 Microsoft estate is not launch" in html
    assert "Licensed-not-wired is not a wired firm" in html
    assert 'id="ms-proof-is-wired">no' in html
    assert 'id="ms-proof-is-ninth">no' in html
    assert 'id="ms-proof-is-product">no' in html
    assert 'id="ms-proof-is-launch">no' in html
    assert 'id="ms-proof-is-write">revoked' in html
    assert 'href="/ms"' not in html
    ms_proof = html[html.index('id="ms-proof-hops"') : html.index("</ol>", html.index('id="ms-proof-hops"'))]
    assert ms_proof.count("Need:") == 6
    assert ms_proof.count("Why:") == 6
    assert ms_proof.count("<li") == 6
    assert 'href="#ms-azure"' in ms_proof
    assert 'href="#ms-entra"' in ms_proof
    assert 'href="#ms-bc"' in ms_proof
    assert 'href="#ms-sales"' in ms_proof
    assert 'href="#ms-teams-premium"' in ms_proof
    assert 'href="#firm-ms"' in ms_proof
    assert 'href="#ms-proof"' in html[html.index('id="ten-proof-walk"') : html.index("</p>", html.index('id="ten-proof-walk"'))]
    assert 'href="#ms-proof"' in html[html.index('id="sale-tools-walk"') : html.index("</p>", html.index('id="sale-tools-walk"'))]
    assert 'href="#ms-proof"' in html[html.index('id="bc-tools-walk"') : html.index("</p>", html.index('id="bc-tools-walk"'))]
    assert 'href="#ms-proof"' in html[html.index('id="firm-proof-walk"') : html.index("</p>", html.index('id="firm-proof-walk"'))]
    assert 'href="#ms-proof"' in html[html.index('id="firm-ms-join-walk"') : html.index("</p>", html.index('id="firm-ms-join-walk"'))]
    assert 'href="#ms-proof"' in html[html.index('id="firm-join-walk"') : html.index("</p>", html.index('id="firm-join-walk"'))]
    assert 'href="#ms-proof"' in html[html.index('id="brand-join-walk"') : html.index("</p>", html.index('id="brand-join-walk"'))]
    assert 'href="#ms-proof"' in html[html.index('id="eco-proof-walk"') : html.index("</p>", html.index('id="eco-proof-walk"'))]
    assert "#ms-proof-hops { grid-template-columns: repeat(3" in css
    assert "#ms-proof.is-landed" in css
    assert "index.html#ms-proof" in twin_html
    assert 'id="ms-universe"' in html
    assert 'id="ms-universe-hops"' in html
    assert 'id="ms-universe-lede"' in html
    assert 'id="ms-universe-need"' in html
    assert 'id="ms-universe-why"' in html
    assert 'id="ms-universe-zeros"' in html
    assert 'id="ms-universe-facts"' in html
    assert 'id="ms-universe-cut"' in html
    assert "ms-universe-lede" not in js
    assert "Walk the Microsoft universe" in html
    assert "Temporary access is not LIVE_PIN_OK" in html
    assert "A 10/10 Microsoft universe is not launch" in html
    assert 'id="ms-universe-is-wired">no' in html
    assert 'id="ms-universe-is-ninth">no' in html
    assert 'id="ms-universe-is-pin">no' in html
    assert 'id="ms-universe-is-seat">no' in html
    assert 'id="ms-universe-is-write">revoked' in html
    assert 'href="/ms"' not in html
    assert html.index('id="ms-proof"') < html.index('id="ms-universe"') < html.index('id="firm-rails"')
    ms_universe = html[html.index('id="ms-universe-hops"') : html.index("</ol>", html.index('id="ms-universe-hops"'))]
    assert ms_universe.count("Need:") == 6
    assert ms_universe.count("Why:") == 6
    assert ms_universe.count("<li") == 6
    assert 'href="#ms-azure"' in ms_universe
    assert 'href="#ms-e7"' in ms_universe
    assert 'href="#ms-bc"' in ms_universe
    assert 'href="#ms-sales"' in ms_universe
    assert 'href="#ms-teams-premium"' in ms_universe
    assert 'href="#hold-consider"' in ms_universe
    assert 'href="#ms-universe"' in html[html.index('id="ms-proof-walk"') : html.index("</p>", html.index('id="ms-proof-walk"'))]
    assert 'href="#ms-universe"' in html[html.index('id="ten-proof-walk"') : html.index("</p>", html.index('id="ten-proof-walk"'))]
    assert 'href="#ms-universe"' in html[html.index('id="offer-proof-walk"') : html.index("</p>", html.index('id="offer-proof-walk"'))]
    assert 'href="#ms-universe"' in html[html.index('id="firm-ms-join-walk"') : html.index("</p>", html.index('id="firm-ms-join-walk"'))]
    assert 'href="#ms-universe"' in html[html.index('id="firm-join-walk"') : html.index("</p>", html.index('id="firm-join-walk"'))]
    assert 'href="#ms-universe"' in html[html.index('id="eco-proof-walk"') : html.index("</p>", html.index('id="eco-proof-walk"'))]
    assert "Walk the industry" in html[html.index('id="firm-ms-join-walk"') : html.index("</p>", html.index('id="firm-ms-join-walk"'))]
    assert "Walk Agent Intent" in html[html.index('id="firm-ms-join-walk"') : html.index("</p>", html.index('id="firm-ms-join-walk"'))]
    assert "#ms-universe-hops { grid-template-columns: repeat(3" in css
    assert "#ms-universe.is-landed" in css
    assert "index.html#ms-universe" in twin_html
    assert 'id="firm-ms-need"' in html
    assert 'id="firm-ms-why"' in html
    assert 'id="hold-need"' in html
    assert 'id="hold-why"' in html
    assert 'id="hold-join-walk"' in html
    assert "firm-ms-need" not in js
    assert "hold-need" not in js
    assert "Walk the honest hold" in html
    assert 'href="#hold-consider"' in html[html.index('id="ms-universe-walk"') : html.index("</p>", html.index('id="ms-universe-walk"'))]
    assert 'href="#ms-universe"' in html[html.index('id="hold-join-walk"') : html.index("</p>", html.index('id="hold-join-walk"'))]
    assert "Walk the industry" in html[html.index('id="firm-ms-join-walk"') : html.index("</p>", html.index('id="firm-ms-join-walk"'))]
    assert "Walk Agent Intent" in html[html.index('id="firm-ms-join-walk"') : html.index("</p>", html.index('id="firm-ms-join-walk"'))]
    assert "#firm-ms.is-landed" in css
    assert "#hold-consider.is-landed" in css
    assert "#close-console.is-landed" in css
    assert 'background: color-mix(in srgb, var(--gold) 10%, var(--paper))' in css[css.index("#hold-consider.is-landed") : css.index("#hold-consider.is-landed") + 400]
    firm_ms_gold = css[css.index("#firm-ms.is-landed") : css.index("#firm-ms.is-landed") + 280]
    assert "var(--paper)" not in firm_ms_gold
    assert 'id="offer-proof"' in html
    assert 'id="offer-proof-hops"' in html
    assert 'id="offer-proof-lede"' in html
    assert 'id="offer-proof-need"' in html
    assert 'id="offer-proof-why"' in html
    assert 'id="offer-proof-zeros"' in html
    assert 'id="offer-proof-facts"' in html
    assert 'id="offer-proof-cut"' in html
    assert "offer-proof-lede" not in js
    assert "Walk the offer 10/10" in html
    assert "A 10/10 offer is not a fourth SKU" in html
    assert "Packs, modules, and repositories are not SKUs" in html
    assert 'id="offer-proof-is-pack">no' in html
    assert 'id="offer-proof-is-free">no' in html
    assert 'id="offer-proof-is-hours">no' in html
    assert 'id="offer-proof-is-cert">no' in html
    assert 'id="offer-proof-is-trial">no' in html
    assert 'href="/offer"' not in html
    assert html.index('id="packs"') < html.index('id="offer-proof"') < html.index('id="industry-narratives"')
    offer_proof = html[html.index('id="offer-proof-hops"') : html.index("</ol>", html.index('id="offer-proof-hops"'))]
    assert offer_proof.count("Need:") == 6
    assert offer_proof.count("Why:") == 6
    assert offer_proof.count("<li") == 6
    assert 'href="#ten-proof"' in offer_proof
    assert 'href="#included-upsells"' in offer_proof
    assert 'href="#industry-narratives"' in offer_proof
    assert 'href="#industry-area-libraries"' in offer_proof
    assert 'href="#ops"' in offer_proof
    assert 'href="#missing"' in offer_proof
    assert 'href="#offer-proof"' in html[html.index('id="ten-proof-walk"') : html.index("</p>", html.index('id="ten-proof-walk"'))]
    assert 'href="#offer-proof"' in html[html.index('id="client-proof-walk"') : html.index("</p>", html.index('id="client-proof-walk"'))]
    assert 'href="#offer-proof"' in html[html.index('id="eco-proof-walk"') : html.index("</p>", html.index('id="eco-proof-walk"'))]
    assert 'href="#offer-proof"' in html[html.index('id="industry-narr-walk"') : html.index("</p>", html.index('id="industry-narr-walk"'))]
    assert 'href="#offer-proof"' in html[html.index('id="industry-narr-return"') : html.index("</p>", html.index('id="industry-narr-return"'))]
    assert 'href="#offer-proof"' in html[html.index('id="ops-join-walk"') : html.index("</p>", html.index('id="ops-join-walk"'))]
    assert 'href="#offer-proof"' in html[html.index('id="finance-join-walk"') : html.index("</p>", html.index('id="finance-join-walk"'))]
    assert 'href="#offer-proof"' in html[html.index('id="commercial-walk"') : html.index("</p>", html.index('id="commercial-walk"'))]
    assert "#offer-proof-hops { grid-template-columns: repeat(3" in css
    assert "#offer-proof.is-landed" in css
    assert "#included-upsells.is-landed" in css
    assert "index.html#offer-proof" in twin_html
    assert hops.count("<li") == 11


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_client_twin_fail_closed():
    def sku(cat):
        cat["expert_review"]["success"]["client_twin"]["sku"] = True

    def fourth(cat):
        cat["expert_review"]["success"]["client_twin"]["fourth_sku"] = True

    def assigned(cat):
        cat["expert_review"]["success"]["client_twin"]["assigned"] = True

    def production(cat):
        cat["expert_review"]["success"]["client_twin"]["production"] = True

    def launch(cat):
        cat["expert_review"]["success"]["client_twin"]["launch"] = True

    def named(cat):
        cat["expert_review"]["success"]["client_twin"]["named_client"] = "Acme"

    def live(cat):
        cat["expert_review"]["success"]["client_twin"]["live"] = True

    def pin(cat):
        cat["expert_review"]["success"]["client_twin"]["live_pin_ok"] = True

    def kind(cat):
        cat["expert_review"]["success"]["client_twin"]["kind"] = "ainav.fourth.sku.v1"

    def stages(cat):
        cat["expert_review"]["success"]["client_twin"]["stages"] = ["Demo only"]

    def count(cat):
        cat["expert_review"]["success"]["client_twin"]["count"] = 1

    def invent(cat):
        cat["expert_review"]["success"]["client_twin"]["do_not_invent_names"] = False

    def lede(cat):
        cat["expert_review"]["success"]["client_twin"]["lede"] = "A shared demo tenant."

    def is_yes(cat):
        cat["expert_review"]["success"]["client_twin"]["is"] = ["A product"]

    def is_not(cat):
        cat["expert_review"]["success"]["client_twin"]["is_not"] = ["A blog"]

    def enhance(cat):
        cat["expert_review"]["success"]["client_twin"]["enhance"] = "Free extras."

    def deploy(cat):
        cat["expert_review"]["success"]["client_twin"]["deploy"] = "Auto-promote."

    def site(cat):
        cat["expert_review"]["success"]["client_twin"]["site"] = "A /demo route."

    def note(cat):
        cat["expert_review"]["success"]["client_twin"]["note"] = "Assigned later."

    def walk(cat):
        cat["expert_review"]["success"]["qualify"]["walk_away"][-1] = "Calendly as the demo"

    def objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item for item in cat["expert_review"]["success"]["objections"] if item.get("id") != "path"
        ]

    def ciso_prod(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "institute twin" not in item.lower() and "client production" not in item.lower()
        ]

    def ciso_sku(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            "A fourth SKU as the sandbox" if "client twin" in item.lower() else item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
        ]

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "client-assigned" not in item.lower()
        ]

    def book(cat):
        cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"] = [
            item
            for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
            if item.get("href") != "#path"
        ]

    def upgrade(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 55:
                item["do"] = "Ship a sandbox demo."

    for mutator in (
        sku,
        fourth,
        assigned,
        production,
        launch,
        named,
        live,
        pin,
        kind,
        stages,
        count,
        invent,
        lede,
        is_yes,
        is_not,
        enhance,
        deploy,
        site,
        note,
        walk,
        objection,
        ciso_prod,
        ciso_sku,
        principles,
        book,
        upgrade,
    ):
        _reject(mutator)
