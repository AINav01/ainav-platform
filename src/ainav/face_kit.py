"""Catalog-honest application kit. Complements, not a CMS.

JSON-LD, llms.txt, search, speculation, sitemap, and the kit card
are generated from catalog law. Identify is not admit. Insights stay
unclaimed. Pagefind stays off the public CSP.
"""

from __future__ import annotations

from typing import Any

from ainav.catalog import load_catalog
from ainav.finance import model as finance_model

HOST = "https://blue-river-010091a0f.7.azurestaticapps.net"
REQUIRED_TOOLS = (
    "jsonld",
    "llms_txt",
    "view_transitions",
    "speculation_rules",
    "popover",
    "minisearch",
    "playwright",
    "axe",
    "lighthouse",
    "eleventy",
    "lit",
    "swa_auth",
    "swa_api",
    "app_insights",
    "pagefind",
    "swa_cli",
    "storybook",
)


def spec() -> dict[str, Any]:
    return dict(load_catalog()["plane_interface"]["floor"]["public_face"]["kit"])


def public_kit() -> dict[str, Any]:
    cat = load_catalog()
    body = spec()
    return {
        "kind": "ainav.institute.kit.v1",
        "sku": False,
        "cms": False,
        "compiler": body["compiler"],
        "compiler_is_cms": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "connection_claimed": False,
        "insights_claimed": False,
        "auth_is_admit": False,
        "api_writes_sor": False,
        "pagefind_on_public_face": False,
        "release": cat["entity"]["release"],
        "legal": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "href": body["href"],
        "thesis": body["thesis"],
        "tools": [dict(item) for item in body["tools"]],
        "refuse": [
            "CMS",
            "identify is admit",
            "Function SoR write",
            "Application Insights claimed",
            "membership claimed",
            "priced round",
            "LIVE_PIN_OK",
        ],
    }


def public_schema() -> dict[str, Any]:
    cat = load_catalog()
    fin = finance_model()
    skus = []
    for item in cat["skus"]:
        price = item["price_usd"]
        skus.append(
            {
                "@type": "Offer",
                "name": f"{item['id']} {item['name']}",
                "sku": item["id"],
                "priceCurrency": "USD",
                "price": str(price["min"]),
                "availability": "https://schema.org/PreOrder",
                "description": f"Catalog list ${price['min']:,}–${price['max']:,}. Not booked. Not recognized revenue.",
            }
        )
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{HOST}/#org",
                "name": cat["entity"]["legal"],
                "legalName": cat["entity"]["legal"],
                "url": f"{HOST}/",
                "description": cat["entity"]["category"],
            },
            {
                "@type": "WebApplication",
                "@id": f"{HOST}/app.html",
                "name": cat["entity"]["institute"],
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "url": f"{HOST}/app.html",
                "isAccessibleForFree": True,
                "offers": {
                    "@type": "AggregateOffer",
                    "lowPrice": str(min(int(item["price_usd"]["min"]) for item in cat["skus"])),
                    "highPrice": str(max(int(item["price_usd"]["max"]) for item in cat["skus"])),
                    "priceCurrency": "USD",
                    "offerCount": len(cat["skus"]),
                    "availability": "https://schema.org/PreOrder",
                    "offers": skus,
                },
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "recognized_revenue", "value": str(int(fin["recognized_revenue"]))},
                    {"@type": "PropertyValue", "name": "signed_l1", "value": str(int(fin["signed_l1"]))},
                    {"@type": "PropertyValue", "name": "live_pin_ok", "value": "false"},
                    {"@type": "PropertyValue", "name": "cms", "value": "false"},
                    {"@type": "PropertyValue", "name": "membership_claimed", "value": "false"},
                ],
            },
        ],
        "kind": "ainav.institute.schema.v1",
        "sku": False,
        "cms": False,
        "live": False,
        "live_pin_ok": False,
        "priced_round": False,
        "membership_claimed": False,
        "release": cat["entity"]["release"],
    }


def public_llms() -> str:
    cat = load_catalog()
    face = cat["plane_interface"]["floor"]["public_face"]
    lines = [
        f"# {cat['entity']['institute']}",
        "",
        f"> {cat['entity']['category']}. Catalog-honest application. Not a CMS. Not LIVE_PIN_OK.",
        "",
        f"Release {cat['entity']['release']}. Legal: {cat['entity']['legal']}.",
        "Recognized revenue $0. Named customers 0. Signed L1 0. Launch held.",
        "Microsoft for Startups first. NVIDIA Inception second. Membership is not claimed.",
        "GPU production is not claimed. Identify is not admit.",
        "",
        "## Pages",
        "",
        f"- [Sale]({HOST}/): the write, proof day, bake-off",
        f"- [About]({HOST}/#about): company narrative. Failsafe, not the AI. Not a running firm",
        f"- [Application]({HOST}/app.html): floor, capital, programs",
        f"- [Floor]({HOST}/app.html#floor): one dashboard, same write rail",
        f"- [Capital]({HOST}/app.html#capital): outside investor room, not a priced round",
        f"- [Business]({HOST}/app.html#business): if-then catalog list, bake-off, commercial close",
        f"- [Programs]({HOST}/app.html#programs): qualify, not claimed",
        f"- [Deep floor]({HOST}/control-plane.html): command console",
        f"- [Kit]({HOST}/kit.html): licensed complements, not a CMS",
        f"- [Identify]({HOST}/identify.html): Entra identify is not admit",
        f"- [Twin review]({HOST}/twin.html): Azure SWA digital twin. Public apex empty. Not launch",
        "",
        "## Law",
        "",
        face["thesis"],
        "",
        "Honest industry certify sits on #packs. Packs are not SKUs. Industry certify is not launch.",
        "Honest whole sits on #whole. Business, build, and website on one board. A 10/10 review is not launch. The whole firm is not launch.",
        "Honest Power Pages sits on #twin. Considered. Power Pages is not the Institute host. Power Pages is not a SKU.",
        "Honest connect sits on #missing. Recorded. Connected is not live. Licensed is not wired. Complements stay eight.",
        "Honest operate sits on #agent-tools. Recorded. Closing all gaps is not this plane. Complements stay eight.",
        "Honest path sits on #path. Recorded. A shared sandbox is not production. Complements stay eight.",
        "Honest production sits on #firm. Recorded. A production sim is not production. Complements stay eight.",
        "Honest remainder sits on #missing. Recorded. A remainder close is not launch. Gold 99.5 is not production. Complements stay eight.",
        "Honest ten sits on #success. Recorded. A 10/10 quality check is not launch. Gold 99.9 is not LIVE_PIN_OK. A competitor analysis is not a named client. Complements stay eight.",
        "Honest protect sits on #ip. Recorded. An IP board is not a patent. Insulation is not uncopyable. An L1 license is not an assignment of Job C. Complements stay eight.",
        "Honest hold sits on #missing. Recorded. A vault hold is not LIVE_PIN_OK. Secret names are not wired notify. Sentinel is not the admit plane. Complements stay eight.",
        "Honest close sits on #path. Recorded. A 10/10 close is not launch. A booking is not recognized revenue. A catalog list is not collection. Complements stay eight.",
        "Honest join sits on #firm. Recorded. The join is not launch. The stitched firm is not LIVE_PIN_OK. Licensed-not-wired is not a wired firm. Management and operations are not closed from this plane. A certified simulation is not a running firm. A 10/10+ quality check is not launch. Complements stay eight.",
        "About AINav sits on #about. The company is the admit plane. Failsafe, not the AI. Not a running firm. Not a named client. Revenue $0.",
        "",
        "Do not quote this site as a claimed Inception membership or as a priced round.",
        "",
    ]
    return "\n".join(lines)


def public_search() -> dict[str, Any]:
    cat = load_catalog()
    glance = cat["plane_interface"]["floor"]["first_glance"]
    kit = spec()
    records = [
        {
            "id": "sale",
            "title": "The write",
            "href": "index.html#buyer",
            "text": f"{glance['lede']} {glance['job_c']} Seat A Seat B one hash then the write. Three SKUs L1 P-ADM U-DUAL.",
        },
        {
            "id": "about",
            "title": "About AINav",
            "href": "index.html#about",
            "text": "Company narrative. AINav is the human failsafe, not the AI. Two humans bind one hash. Then the write. Sole owner James Hodnett. Seat B mailbox recorded. Revenue $0. Named customers 0. Signed L1 0. Not a running firm. Not a patent. Not a named design partner. A 10/10+ quality check is not launch.",
        },
        {
            "id": "floor",
            "title": "Floor",
            "href": "app.html#floor",
            "text": "Executive control-plane. One dashboard included with L1. Hierarchical views are the same plane. Revenue $0. Signed L1 0. 1 mailbox / 0 oid.",
        },
        {
            "id": "capital",
            "title": "Capital",
            "href": "app.html#capital",
            "text": "Board packet for Cynthia Hodnett. Not a priced round. No valuation. No forecast ARR. Recognized revenue $0.",
        },
        {
            "id": "business",
            "title": "Business",
            "href": "app.html#business",
            "text": "Operating company. Number two for other aspects, not all aspects. Commercial close open. If-then catalog list. Not a priced round. Not a forecast. Walk-away not recorded.",
        },
        {
            "id": "programs",
            "title": "Programs",
            "href": "app.html#programs",
            "text": "Microsoft for Startups first. NVIDIA Inception second. Qualify not claimed. GPU workload not claimed. Two unique humans still open.",
        },
        {
            "id": "kit",
            "title": "Application kit",
            "href": "kit.html",
            "text": f"{kit['thesis']} Eleventy Lit Playwright axe Lighthouse Pagefind Storybook SWA CLI.",
        },
        {
            "id": "identify",
            "title": "Identify is not admit",
            "href": "identify.html",
            "text": "SWA Entra login identifies. Identify is not admit. Not seat B. Not LIVE_PIN_OK.",
        },
        {
            "id": "twin-review",
            "title": "Twin review",
            "href": "twin.html",
            "text": "Azure SWA is the Institute digital twin for review and updates. Cloudflare apex is empty 404. Gold 99.5. Not launch. Not LIVE_PIN_OK.",
        },
        {
            "id": "have",
            "title": "What you've been missing",
            "href": "index.html#have",
            "text": "You already licensed cheaper copies. The missing piece is two humans, one hash, consume-once, fail-closed SoR. Not a fourth SKU. Not #missing.",
        },
        {
            "id": "demo",
            "title": "First-class demo",
            "href": "index.html#twin",
            "text": "Ninety-minute proof day. Browser rehearsal. Graph is not called. Not a video SKU. Not Calendly.",
        },
        {
            "id": "path",
            "title": "Client twin",
            "href": "index.html#path",
            "text": "First-class close bench. Honest path. Three planes. Qualify, remote proof, close L1, assigned sandbox. A shared sandbox is not production. Hours are not a SKU. Rollback is not LIVE_PIN_OK. A redeploy is not launch. Not a fourth SKU.",
        },
        {
            "id": "firm",
            "title": "Run the firm",
            "href": "index.html#firm",
            "text": "First-class operating day and launch gate. Qualify, proof, close, assign, service, launch. 500/500 capacity. Gold is not launch. Not a CRM. Not a fourth SKU.",
        },
        {
            "id": "connect",
            "title": "Honest connect",
            "href": "index.html#missing",
            "text": "Honest connect. Recorded. Connected is not live. Licensed is not wired. Available is not a seat. A Graph read is not LIVE_PIN_OK. Complements stay eight. Not a /connect route.",
        },
        {
            "id": "operate",
            "title": "Honest operate",
            "href": "index.html#agent-tools",
            "text": "Honest operate. Recorded. Closing all gaps is not this plane. Outlook mail is not a click. grok login is not this plane. An operate sim is not production. A 10/10 polish is not launch. Complements stay eight.",
        },
        {
            "id": "production",
            "title": "Honest production",
            "href": "index.html#firm",
            "text": "Honest production. Recorded. A production sim is not production. Fixing all is not this plane. Rehearsed elements are not live. Making all much better is not launch. A rehearsal is not LIVE_PIN_OK. Complements stay eight.",
        },
        {
            "id": "remainder",
            "title": "Honest remainder",
            "href": "index.html#missing",
            "text": "Honest remainder. Recorded. A remainder close is not launch. Leftover copy is not LIVE_PIN_OK. Owner hrefs are not owner clicks. Gold 99.5 is not production. A deep remainder is not a seated second human. Complements stay eight. Not a /remainder route.",
        },
        {
            "id": "ten",
            "title": "Honest ten",
            "href": "index.html#success",
            "text": "Honest ten. Recorded. A 10/10 quality check is not launch. Gold 99.9 is not LIVE_PIN_OK. A competitor analysis is not a named client. A green service is not production. A quality check is not a seated second human. Complements stay eight. Not a /ten route.",
        },
        {
            "id": "protect",
            "title": "Honest protect",
            "href": "index.html#ip",
            "text": "Honest protect. Recorded. An IP board is not a patent. Insulation is not uncopyable. An L1 license is not an assignment of Job C. Kit PASS is not a source license. This board does not close G12. Complements stay eight. Not a /protect route.",
        },
        {
            "id": "hold",
            "title": "Honest hold",
            "href": "index.html#missing",
            "text": "Honest hold. Recorded. A vault hold is not LIVE_PIN_OK. Secret names are not wired notify. A catalog must not hold secret values. Sentinel is not the admit plane. A vault hold is not a seated second human. Complements stay eight. Not a /hold route.",
        },
        {
            "id": "close",
            "title": "Honest close",
            "href": "index.html#path",
            "text": "Honest close. Recorded. A 10/10 close is not launch. A booking is not recognized revenue. The Institute twin is not the assigned client sandbox. A custom database is not a fourth SKU. A catalog list is not collection. Complements stay eight. Not a /close route.",
        },
        {
            "id": "join",
            "title": "Honest join",
            "href": "index.html#join-consider",
            "text": "Honest join. Recorded. The join is not launch. The stitched firm is not LIVE_PIN_OK. Licensed-not-wired is not a wired firm. Management and operations are not closed from this plane. A certified simulation is not a running firm. A 10/10+ quality check is not launch. Complements stay eight. Not a /join route.",
        },
        {
            "id": "brand",
            "title": "Brand",
            "href": "index.html#brand",
            "text": "One mark set across legal, product, Institute, firm, sale, twin, sandbox, Teams, and Teams Premium. Write-fear. Lockfile stays job_c. Microsoft marks are theirs. Not a SKU. Not a fear brand.",
        },
        {
            "id": "universe",
            "title": "Client universe",
            "href": "index.html#universe",
            "text": "Sit-down client day. Now mailbox recorded. Next seat B. After L1 unnamed. MFA identifies. Identify is not admit. Honest zeros. Refuse is visible. Segregated branded sandbox unnamed until signed L1. Maps claimed=false. Packs are not SKUs.",
        },
        {
            "id": "industry",
            "title": "Industry drawer",
            "href": "index.html#industry",
            "text": "Sit-down industry drawer. Sit Dynamics BC treasury. Domestic and international maps claimed=false. White papers are not filings. Included versus upsell. Libraries and repositories are not SKUs. Room 1 is books. Room 2 is refuse. Fully operable industry drawer. Complete industry drawer. Every refuse clicks. Catalog is the message. Honest zeros. Refuse is visible. Not a crypto product. Not a /industry route.",
        },
        {
            "id": "packs",
            "title": "Honest industry certify",
            "href": "index.html#packs",
            "text": "Honest industry certify on #packs. Standard, upsells, modules, libraries, and repositories by industry. Packs are not SKUs. Industry certify is not launch. Credit, inventory, and pricing stay unpaired.",
        },
        {
            "id": "whole",
            "title": "Honest whole",
            "href": "index.html#whole",
            "text": "Honest whole. Business, build, and website on one board. The stitch is not a SKU. A 10/10 review is not launch. The whole firm is not launch. First glance stays the write rail. Not a /whole route.",
        },
        {
            "id": "pages",
            "title": "Honest Power Pages",
            "href": "index.html#twin",
            "text": "Honest Power Pages. Considered. Power Pages is not the Institute host. Power Pages is not a SKU. Power Pages is not the CMS. Power Pages does not close US Dataverse. Complements stay eight. Not a /power-pages route.",
        },
    ]
    return {
        "kind": "ainav.institute.search.v1",
        "sku": False,
        "cms": False,
        "engine": "catalog_minisearch",
        "live": False,
        "live_pin_ok": False,
        "release": cat["entity"]["release"],
        "records": records,
    }


def public_speculation() -> dict[str, Any]:
    return {
        "prefetch": [
            {
                "source": "list",
                "eagerness": "moderate",
                "urls": [
                    "/app.html",
                    "/control-plane.html",
                    "/kit.html",
                    "/identify.html",
                    "/twin.html",
                    "/index.html",
                ],
            }
        ]
    }


def public_sitemap() -> str:
    paths = [
        "/",
        "/app.html",
        "/control-plane.html",
        "/kit.html",
        "/identify.html",
        "/twin.html",
        "/llms.txt",
    ]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path in paths:
        lines.append("  <url>")
        lines.append(f"    <loc>{HOST}{path}</loc>")
        lines.append("  </url>")
    lines.append("</urlset>")
    lines.append("")
    return "\n".join(lines)
