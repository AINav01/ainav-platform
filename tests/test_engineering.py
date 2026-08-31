from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import catalog_engineering, load_catalog, validate_catalog
from ainav.institute_status import public_status
from ainav.review import review_model


def test_catalog_engineering_records_gold_ci_not_launch():
    body = catalog_engineering()
    assert body["kind"] == "ainav.engineering.v1"
    assert body["sku"] is False
    assert body["connection"] is False
    assert body["complement"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["launch"] is False
    assert body["is_admit_plane"] is False
    gold = body["gold_ci"]
    assert gold["id"] == "github.actions.gold"
    assert gold["exists"] is True
    assert gold["observed_green"] is True
    assert gold["workflow"] == ".github/workflows/gold.yml"
    assert gold["command"] == "make gold"
    assert gold["coverage_floor"] == 90
    assert gold["marks_live_pin"] is False
    assert gold["is_admit_plane"] is False
    assert "not live_pin_ok" in gold["note"].lower()
    assert "green check" in gold["note"].lower()
    assert any("gold" in item.lower() or "github" in item.lower() for item in body["closed_in_tree"])
    assert any("live_pin" in item.lower() for item in body["cannot_close"])
    assert any("cynthia" in item.lower() or "second unique" in item.lower() for item in body["cannot_close"])
    assert "not a sku" in body["note"].lower()


def test_gold_workflow_exists_and_refuses_live_pin():
    text = Path(".github/workflows/gold.yml").read_text(encoding="utf-8")
    assert "make gold" in text
    assert "LIVE_PIN_OK" in text
    assert "not signed L1" in text
    assert "permissions:" in text
    assert "contents: read" in text
    assert "actions/checkout@11d5960a326750d5838078e36cf38b85af677262" in text
    assert "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065" in text
    assert Path(".github/dependabot.yml").is_file()
    dependabot = Path(".github/dependabot.yml").read_text(encoding="utf-8")
    assert "package-ecosystem: github-actions" in dependabot
    assert "package-ecosystem: pip" in dependabot
    assert Path(".github/CODEOWNERS").is_file()
    assert "@DayTradingMarkets" in Path(".github/CODEOWNERS").read_text(encoding="utf-8")


def test_package_version_matches_catalog_release():
    release = load_catalog()["entity"]["release"]
    assert release == "2.50.0"
    assert f'version = "{release}"' in Path("pyproject.toml").read_text(encoding="utf-8")


def test_catalog_rejects_engineering_sku_live_or_missing_gold_file():
    sku = copy.deepcopy(load_catalog())
    sku["engineering"]["sku"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(sku)
    assert exc.value.reason_code == "CATALOG_ENGINEERING"

    live = copy.deepcopy(load_catalog())
    live["engineering"]["live_pin_ok"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(live)
    assert exc2.value.reason_code == "CATALOG_ENGINEERING"

    launch = copy.deepcopy(load_catalog())
    launch["engineering"]["launch"] = True
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(launch)
    assert exc3.value.reason_code == "CATALOG_ENGINEERING"

    missing = copy.deepcopy(load_catalog())
    missing["engineering"]["gold_ci"]["exists"] = True
    missing["engineering"]["gold_ci"]["workflow"] = ".github/workflows/missing.yml"
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(missing)
    assert exc4.value.reason_code == "CATALOG_ENGINEERING"


def test_catalog_allows_recorded_missing_gold_workflow():
    cat = copy.deepcopy(load_catalog())
    gold = cat["engineering"]["gold_ci"]
    gold["exists"] = False
    gold["observed_green"] = False
    gold["note"] = (
        "Gold CI is missing. Not in the tree. A green check is not LIVE_PIN_OK. "
        "This Cloud Agent has not written the workflow."
    )
    cat["engineering"]["closed_in_tree"] = [
        item for item in cat["engineering"]["closed_in_tree"] if "gold" not in item.lower()
    ]
    validate_catalog(cat)


def test_catalog_rejects_missing_gold_without_honesty(monkeypatch):
    cat = copy.deepcopy(load_catalog())
    cat["engineering"]["gold_ci"]["exists"] = False
    cat["engineering"]["gold_ci"]["observed_green"] = False
    cat["engineering"]["gold_ci"]["note"] = "Gold CI. A green check is not LIVE_PIN_OK."
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "CATALOG_ENGINEERING"

    none = copy.deepcopy(load_catalog())
    none["engineering"]["gold_ci"]["exists"] = None
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(none)
    assert exc2.value.reason_code == "CATALOG_ENGINEERING"

    no_human = copy.deepcopy(load_catalog())
    no_human["engineering"]["cannot_close"] = ["LIVE_PIN_OK"]
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(no_human)
    assert exc3.value.reason_code == "CATALOG_ENGINEERING"

    no_note = copy.deepcopy(load_catalog())
    no_note["engineering"]["note"] = "Engineering plane."
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(no_note)
    assert exc4.value.reason_code == "CATALOG_ENGINEERING"

    no_kind = copy.deepcopy(load_catalog())
    no_kind["engineering"]["kind"] = "invented"
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(no_kind)
    assert exc5.value.reason_code == "CATALOG_ENGINEERING"

    no_gold = copy.deepcopy(load_catalog())
    no_gold["engineering"]["gold_ci"] = None
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(no_gold)
    assert exc6.value.reason_code == "CATALOG_ENGINEERING"

    pin = copy.deepcopy(load_catalog())
    pin["engineering"]["gold_ci"]["marks_live_pin"] = True
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(pin)
    assert exc7.value.reason_code == "CATALOG_ENGINEERING"

    floor = copy.deepcopy(load_catalog())
    floor["engineering"]["gold_ci"]["coverage_floor"] = 80
    with pytest.raises(IntegrityError) as exc8:
        validate_catalog(floor)
    assert exc8.value.reason_code == "CATALOG_ENGINEERING"

    cmd = copy.deepcopy(load_catalog())
    cmd["engineering"]["gold_ci"]["command"] = "pytest"
    with pytest.raises(IntegrityError) as exc9:
        validate_catalog(cmd)
    assert exc9.value.reason_code == "CATALOG_ENGINEERING"

    plane = copy.deepcopy(load_catalog())
    plane["engineering"]["gold_ci"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError) as exc10:
        validate_catalog(plane)
    assert exc10.value.reason_code == "CATALOG_ENGINEERING"

    gone = copy.deepcopy(load_catalog())
    del gone["engineering"]
    with pytest.raises(IntegrityError) as exc11:
        validate_catalog(gone)
    assert exc11.value.reason_code == "CATALOG_ENGINEERING"

    bad_id = copy.deepcopy(load_catalog())
    bad_id["engineering"]["gold_ci"]["id"] = "invented.ci"
    with pytest.raises(IntegrityError) as exc12:
        validate_catalog(bad_id)
    assert exc12.value.reason_code == "CATALOG_ENGINEERING"

    quiet = copy.deepcopy(load_catalog())
    quiet["engineering"]["gold_ci"]["note"] = "Gold CI is in the tree. Green check."
    with pytest.raises(IntegrityError) as exc13:
        validate_catalog(quiet)
    assert exc13.value.reason_code == "CATALOG_ENGINEERING"

    empty = copy.deepcopy(load_catalog())
    empty["engineering"]["closed_in_tree"] = []
    with pytest.raises(IntegrityError) as exc14:
        validate_catalog(empty)
    assert exc14.value.reason_code == "CATALOG_ENGINEERING"

    no_pin = copy.deepcopy(load_catalog())
    no_pin["engineering"]["cannot_close"] = ["Second unique human Cynthia"]
    with pytest.raises(IntegrityError) as exc15:
        validate_catalog(no_pin)
    assert exc15.value.reason_code == "CATALOG_ENGINEERING"

    fiction = copy.deepcopy(load_catalog())
    fiction["engineering"]["closed_in_tree"] = ["LIVE_PIN_OK is marked"]
    with pytest.raises(IntegrityError) as exc16:
        validate_catalog(fiction)
    assert exc16.value.reason_code == "CATALOG_ENGINEERING"

    plane_note = copy.deepcopy(load_catalog())
    plane_note["engineering"]["note"] = "Not a SKU. Owner clicks stay owner clicks."
    with pytest.raises(IntegrityError) as exc17:
        validate_catalog(plane_note)
    assert exc17.value.reason_code == "CATALOG_ENGINEERING"

    no_green = copy.deepcopy(load_catalog())
    no_green["engineering"]["gold_ci"]["note"] = (
        "Gold CI is in the tree. A workflow is not LIVE_PIN_OK."
    )
    with pytest.raises(IntegrityError) as exc18:
        validate_catalog(no_green)
    assert exc18.value.reason_code == "CATALOG_ENGINEERING"

    no_record = copy.deepcopy(load_catalog())
    no_record["engineering"]["closed_in_tree"] = [
        "Job C invariants",
        "Catalog law — three SKUs only",
    ]
    with pytest.raises(IntegrityError) as exc19:
        validate_catalog(no_record)
    assert exc19.value.reason_code == "CATALOG_ENGINEERING"

    claimed = copy.deepcopy(load_catalog())
    claimed["engineering"]["gold_ci"]["exists"] = False
    claimed["engineering"]["gold_ci"]["observed_green"] = True
    claimed["engineering"]["gold_ci"]["note"] = (
        "Gold CI ran green. A green check is not LIVE_PIN_OK. Missing."
    )
    with pytest.raises(IntegrityError) as exc20:
        validate_catalog(claimed)
    assert exc20.value.reason_code == "CATALOG_ENGINEERING"

    no_ran = copy.deepcopy(load_catalog())
    no_ran["engineering"]["gold_ci"]["note"] = (
        "Gold CI is in the tree. A green check is not LIVE_PIN_OK."
    )
    with pytest.raises(IntegrityError) as exc21:
        validate_catalog(no_ran)
    assert exc21.value.reason_code == "CATALOG_ENGINEERING"

    fiction_green = copy.deepcopy(load_catalog())
    fiction_green["engineering"]["gold_ci"]["exists"] = False
    fiction_green["engineering"]["gold_ci"]["observed_green"] = False
    fiction_green["engineering"]["gold_ci"]["note"] = (
        "Gold CI is missing. Not in the tree. Ran green. A green check is not LIVE_PIN_OK."
    )
    with pytest.raises(IntegrityError) as exc22:
        validate_catalog(fiction_green)
    assert exc22.value.reason_code == "CATALOG_ENGINEERING"

    none_green = copy.deepcopy(load_catalog())
    none_green["engineering"]["gold_ci"]["observed_green"] = None
    with pytest.raises(IntegrityError) as exc23:
        validate_catalog(none_green)
    assert exc23.value.reason_code == "CATALOG_ENGINEERING"

    from ainav import catalog as catalog_mod

    real_is_file = catalog_mod.Path.is_file

    def missing_gold(self):
        if self.as_posix() == ".github/workflows/gold.yml":
            return False
        return real_is_file(self)

    gone_file = copy.deepcopy(load_catalog())
    monkeypatch.setattr(catalog_mod.Path, "is_file", missing_gold)
    with pytest.raises(IntegrityError) as exc24:
        validate_catalog(gone_file)
    assert exc24.value.reason_code == "CATALOG_ENGINEERING"
    monkeypatch.undo()

    def _workflow_text(body: str):
        real = catalog_mod.Path.read_text

        def fake(self, encoding="utf-8"):
            if self.as_posix() == ".github/workflows/gold.yml":
                return body
            return real(self, encoding=encoding)

        return fake

    no_make = copy.deepcopy(load_catalog())
    monkeypatch.setattr(catalog_mod.Path, "read_text", _workflow_text("LIVE_PIN_OK\nactions/checkout@11d5960a326750d5838078e36cf38b85af677262\n"))
    with pytest.raises(IntegrityError) as exc25:
        validate_catalog(no_make)
    assert exc25.value.reason_code == "CATALOG_ENGINEERING"
    monkeypatch.undo()

    no_pin_word = copy.deepcopy(load_catalog())
    monkeypatch.setattr(
        catalog_mod.Path,
        "read_text",
        _workflow_text("make gold\nactions/checkout@11d5960a326750d5838078e36cf38b85af677262\n"),
    )
    with pytest.raises(IntegrityError) as exc26:
        validate_catalog(no_pin_word)
    assert exc26.value.reason_code == "CATALOG_ENGINEERING"
    monkeypatch.undo()

    no_checkout = copy.deepcopy(load_catalog())
    monkeypatch.setattr(
        catalog_mod.Path,
        "read_text",
        _workflow_text("make gold\nLIVE_PIN_OK\nactions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065\n"),
    )
    with pytest.raises(IntegrityError) as exc27:
        validate_catalog(no_checkout)
    assert exc27.value.reason_code == "CATALOG_ENGINEERING"
    monkeypatch.undo()

    no_setup = copy.deepcopy(load_catalog())
    monkeypatch.setattr(
        catalog_mod.Path,
        "read_text",
        _workflow_text("make gold\nLIVE_PIN_OK\nactions/checkout@11d5960a326750d5838078e36cf38b85af677262\n"),
    )
    with pytest.raises(IntegrityError) as exc28:
        validate_catalog(no_setup)
    assert exc28.value.reason_code == "CATALOG_ENGINEERING"


def test_honest_missing_must_keep_live_pin_and_second_human():
    missing = load_catalog()["honest_missing"]
    assert any("LIVE_PIN_OK" in item for item in missing)
    assert any("Second unique" in item or "Cynthia" in item for item in missing)

    gone = copy.deepcopy(load_catalog())
    gone["honest_missing"] = []
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(gone)
    assert exc.value.reason_code == "CATALOG_HONEST"

    no_pin = copy.deepcopy(load_catalog())
    no_pin["honest_missing"] = [
        item for item in no_pin["honest_missing"] if "LIVE_PIN" not in item
    ]
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(no_pin)
    assert exc2.value.reason_code == "CATALOG_HONEST"

    no_human = copy.deepcopy(load_catalog())
    no_human["honest_missing"] = [
        item
        for item in no_human["honest_missing"]
        if "second unique" not in item.lower() and "cynthia" not in item.lower()
    ]
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(no_human)
    assert exc3.value.reason_code == "CATALOG_HONEST"

    claimed = copy.deepcopy(load_catalog())
    claimed["honest_missing"] = [
        "LIVE_PIN_OK is marked",
        "Second unique human (Inception contacts and signed L1 seats)",
    ]
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(claimed)
    assert exc4.value.reason_code == "CATALOG_HONEST"


def test_catalog_rejects_operating_and_equation_fiction():
    from ainav.catalog import _validate_operating

    def reject(reason: str, **patch: object) -> None:
        body = copy.deepcopy(load_catalog())
        for key, value in patch.items():
            if key == "operating" and value is None:
                body["operating"] = None
            elif "." in key:
                section, field = key.split(".", 1)
                body[section][field] = value
            else:
                body[key] = value
        with pytest.raises(IntegrityError) as exc:
            _validate_operating(body)
        assert exc.value.reason_code == reason

    reject("CATALOG_OPERATING", operating=None)
    reject("CATALOG_OPERATING", **{"operating.legal_entity": "Invented, Inc."})
    reject("CATALOG_OPERATING", **{"operating.sole_owner": False})
    reject("CATALOG_OPERATING", **{"operating.operator_is_seat": True})
    reject("CATALOG_OPERATING", **{"operating.agent_is_not_dual": False})
    reject("CATALOG_OPERATING", **{"operating.owner_principal": "  "})
    same = copy.deepcopy(load_catalog())
    same["operating"]["owner_principal"] = same["operating"]["operator"]
    with pytest.raises(IntegrityError) as exc:
        _validate_operating(same)
    assert exc.value.reason_code == "CATALOG_OPERATING"
    reject("CATALOG_EQUATION", **{"equations.commercial": "signed L1 only"})
    reject("CATALOG_EQUATION", **{"equations.lab_pin": "SIGNED_L1"})
    reject("CATALOG_EQUATION", **{"equations.control": "AI writes alone"})
    reject("CATALOG_EQUATION", **{"equations.cascade": "no client institutes"})
    reject("CATALOG_EQUATION", **{"equations.umbrella": "many planes"})
    reject("CATALOG_EQUATION", **{"equations.plane": "no fail-closed"})
    reject("CATALOG_EQUATION", **{"equations.org": "no chart"})
    reject("CATALOG_EQUATION", **{"equations.insulation": "independence × Job C"})
    reject("CATALOG_EQUATION", **{"equations.interface": "no humans from the top"})
    reject(
        "CATALOG_EQUATION",
        **{
            "equations.interface": (
                "humans from the top × hierarchical access × authorization lifecycle "
                "× sealed records × must-have"
            )
        },
    )
    reject(
        "CATALOG_EQUATION",
        **{
            "equations.interface": (
                "humans from the top × hierarchical access × walkable rehearsal × must-have"
            )
        },
    )
    reject(
        "CATALOG_EQUATION",
        **{
            "equations.interface": (
                "humans from the top × hierarchical access × walkable rehearsal "
                "× authorization lifecycle × sealed records"
            )
        },
    )
    reject("CATALOG_EQUATION", **{"equations.investor": "forecast booked"})
    reject(
        "CATALOG_EQUATION",
        **{"equations.investor": "catalog list × zero booked × one click"},
    )


def test_public_status_keeps_engineering_off_the_write_path():
    body = public_status()
    path_ids = [item["id"] for item in body["fabric"]["path"]]
    assert "github.actions.gold" not in path_ids
    eng = body["engineering"]
    assert eng["gold_ci"]["id"] == "github.actions.gold"
    assert eng["sku"] is False
    assert eng["live_pin_ok"] is False
    assert eng["launch"] is False
    assert eng["gold_ci"]["exists"] is True
    assert eng["gold_ci"]["observed_green"] is True


def test_review_model_carries_catalog_engineering():
    model = review_model()
    assert model["engineering"]["gold_ci"]["exists"] is True
    assert model["engineering"]["sku"] is False
    assert model["live_pin_ok"] is False
    assert model["launch_ready"] is False


def test_institute_paints_closed_and_gold_ci():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    makefile = Path("Makefile").read_text(encoding="utf-8")
    assert 'id="closed"' in html
    assert 'id="closed-in-tree"' in html
    assert 'id="cannot-close"' in html
    assert 'id="gold-ci-note"' in html
    assert 'id="honest-missing"' in html
    assert "G12 legal (counsel pack unsigned)" in html
    assert "make gold" in html
    assert "ran green" in html.lower()
    assert "href=\"#closed\"" in html
    assert html.index('href="#closed"') < html.index('href="#missing"')
    assert html.index('href="#missing"') < html.index('href="#open"')
    assert ">Owner<" in html
    assert "James must click" in html
    assert "<h2>Owner — James must click</h2>" in html
    assert "G1/G10 LIVE_PIN_OK" in html
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    assert 'href="index.html#closed"' in plane
    assert 'href="index.html#missing"' in plane
    assert plane.index('href="index.html#closed"') < plane.index('href="index.html#missing"')
    assert plane.index('href="index.html#missing"') < plane.index('href="index.html#open"')
    assert "observed_green" in js
    assert "refuse to paint a fiction scoreboard" in js
    assert "closed-in-tree" in js
    assert "honest-missing" in js
    assert "#closed" in css
    assert "regen:" in makefile
    assert "gold: plan-check" in makefile
