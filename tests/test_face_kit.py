from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.face_kit import (
    REQUIRED_TOOLS,
    public_kit,
    public_llms,
    public_schema,
    public_search,
    public_sitemap,
    public_speculation,
)


def test_public_kit_is_fail_closed():
    body = public_kit()
    assert body["kind"] == "ainav.institute.kit.v1"
    assert body["cms"] is False
    assert body["compiler_is_cms"] is False
    assert body["auth_is_admit"] is False
    assert body["api_writes_sor"] is False
    assert body["insights_claimed"] is False
    assert body["pagefind_on_public_face"] is False
    assert body["live_pin_ok"] is False
    assert {item["id"] for item in body["tools"]} >= set(REQUIRED_TOOLS)
    schema = public_schema()
    assert schema["membership_claimed"] is False
    assert schema["priced_round"] is False
    assert schema["live_pin_ok"] is False
    blob = json.dumps(schema).lower()
    assert "nvidia inception member" not in blob
    llms = public_llms().lower()
    assert "microsoft for startups first" in llms
    assert "nvidia inception second" in llms
    assert "nvidia inception member" not in llms
    search = public_search()
    assert search["engine"] == "catalog_minisearch"
    assert {item["id"] for item in search["records"]} >= {"floor", "capital", "business", "programs", "kit"}
    assert public_speculation()["prefetch"][0]["urls"]
    assert "/app.html" in public_sitemap()
    assert "/llms.txt" in public_sitemap()


def test_kit_files_and_csp_stay_honest():
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    swa = json.loads(Path("institute/staticwebapp.config.json").read_text(encoding="utf-8"))
    assert "ainav-elements.js" in kit
    assert "speculate.js" in kit
    assert "ainav-honest" in app
    assert "app-search" in app
    assert "Owner book" in app
    assert app.count("Owner book") == 1
    assert "@view-transition" in css
    assert "--gold-ink: #7a5d26" in css
    assert "Identify is not admit" in identify
    assert 'aria-label="Menu"' in app
    assert "nvidia inception member" not in kit.lower()
    assert "href=\"mailto:" not in kit
    assert swa["globalHeaders"]["Content-Security-Policy"].find("wasm-unsafe-eval") < 0
    assert swa["globalHeaders"]["Content-Security-Policy"].find("form-action 'none'") >= 0
    pagefind = next(item for item in swa["routes"] if item.get("route") == "/pagefind/*")
    assert "wasm-unsafe-eval" in pagefind["headers"]["Content-Security-Policy"]
    owner = next(item for item in swa["routes"] if item.get("route") == "/owner-gate.html")
    assert owner["allowedRoles"] == ["authenticated"]
    api = Path("api/src/read.js").read_text(encoding="utf-8")
    assert "405" in api
    assert "API_READ_ONLY" in api
    assert "writes_sor: false" in api or "writes_sor" in api
    insights = Path("institute/insights.js").read_text(encoding="utf-8")
    assert "claimed: false" in insights
    assert Path("web/eleventy/index.md").exists()
    assert Path("web/e2e/app.spec.js").exists()
    assert Path("web/stories/rail.stories.js").exists()
    assert Path(".github/workflows/kit.yml").exists()


def test_catalog_refuses_kit_fiction():
    cat = load_catalog()
    cms = copy.deepcopy(cat)
    cms["plane_interface"]["floor"]["public_face"]["kit"]["cms"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cms)
    assert exc.value.reason_code == "CATALOG_PLANE"
    admit = copy.deepcopy(cat)
    admit["plane_interface"]["floor"]["public_face"]["kit"]["auth_is_admit"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(admit)
    assert exc2.value.reason_code == "CATALOG_PLANE"
    write = copy.deepcopy(cat)
    write["plane_interface"]["floor"]["public_face"]["kit"]["api_writes_sor"] = True
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(write)
    assert exc3.value.reason_code == "CATALOG_PLANE"
    insights = copy.deepcopy(cat)
    insights["plane_interface"]["floor"]["public_face"]["kit"]["insights_claimed"] = True
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(insights)
    assert exc4.value.reason_code == "CATALOG_PLANE"
    pagefind = copy.deepcopy(cat)
    pagefind["plane_interface"]["floor"]["public_face"]["kit"]["pagefind_on_public_face"] = True
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(pagefind)
    assert exc5.value.reason_code == "CATALOG_PLANE"
