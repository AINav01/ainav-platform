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
        f"- [Application]({HOST}/app.html): floor, capital, programs",
        f"- [Floor]({HOST}/app.html#floor): one dashboard, same write rail",
        f"- [Capital]({HOST}/app.html#capital): outside investor room, not a priced round",
        f"- [Business]({HOST}/app.html#business): if-then catalog list, bake-off, commercial close",
        f"- [Programs]({HOST}/app.html#programs): qualify, not claimed",
        f"- [Deep floor]({HOST}/control-plane.html): command console",
        f"- [Kit]({HOST}/kit.html): licensed complements, not a CMS",
        f"- [Identify]({HOST}/identify.html): Entra identify is not admit",
        "",
        "## Law",
        "",
        face["thesis"],
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
            "text": "Operating company. Commercial close open. If-then catalog list. Not a priced round. Not a forecast. Walk-away not recorded.",
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
