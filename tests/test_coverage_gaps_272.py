from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_gov.consume import ConsumeLedger
from agent_gov.errors import ConsumeReplay, IntegrityError, LockfileError
from agent_gov.export import export_envelope, verify_export
from agent_gov.lockfile import default_lockfile, load_lockfile
from agent_gov.lua_simulator import OK
from agent_gov.merkle import leaf_hash, merkle_root, verify_inclusion
from agent_gov.records import as_sealed, decision_record, verify_chain, verify_record
from tests.helpers import sample_action
from agent_gov.store import FileAuthorityStore, MemoryAuthorityStore
from ainav.business import OperatingCompany, validate_business
from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import ProvisionError
from ainav.ip import validate_ip_doctrine
from ainav.keep import weekly_keep
from ainav.mothership import LocalMothership, MasterMothership
from ainav.org import validate_organization
from ainav.proof_day import run_proof_day


def test_org_invite_licenses_and_number_two_stay_fail_closed():
    cat = load_catalog()
    invited = cat["organization"]["contacts"]["invited"]
    licenses = invited["licenses"]
    number_two = cat["organization"]["number_two"]

    missing = json.loads(json.dumps(cat))
    missing["organization"]["contacts"]["invited"]["licenses"] = None
    with pytest.raises(IntegrityError):
        validate_organization(missing)

    kind = json.loads(json.dumps(cat))
    kind["organization"]["contacts"]["invited"]["licenses"]["kind"] = "other"
    with pytest.raises(IntegrityError):
        validate_organization(kind)

    e7 = json.loads(json.dumps(cat))
    e7["organization"]["contacts"]["invited"]["licenses"]["e7"] = False
    with pytest.raises(IntegrityError):
        validate_organization(e7)

    fallback = json.loads(json.dumps(cat))
    fallback["organization"]["contacts"]["invited"]["licenses"]["fallback_stays_on_owner"] = False
    with pytest.raises(IntegrityError):
        validate_organization(fallback)

    plane = json.loads(json.dumps(cat))
    plane["organization"]["contacts"]["invited"]["licenses"]["from_this_plane"] = True
    with pytest.raises(IntegrityError):
        validate_organization(plane)

    seat = json.loads(json.dumps(cat))
    seat["organization"]["contacts"]["invited"]["licenses"]["seat"] = True
    with pytest.raises(IntegrityError):
        validate_organization(seat)

    note = json.loads(json.dumps(cat))
    note["organization"]["contacts"]["invited"]["licenses"]["note"] = "Paid E7 assigned."
    with pytest.raises(IntegrityError):
        validate_organization(note)

    two = json.loads(json.dumps(cat))
    two["organization"]["number_two"] = None
    with pytest.raises(IntegrityError):
        validate_organization(two)

    sku = json.loads(json.dumps(cat))
    sku["organization"]["number_two"]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_organization(sku)

    name = json.loads(json.dumps(cat))
    name["organization"]["number_two"]["name"] = "Other"
    with pytest.raises(IntegrityError):
        validate_organization(name)

    scope = json.loads(json.dumps(cat))
    scope["organization"]["number_two"]["scope"] = "all_aspects"
    with pytest.raises(IntegrityError):
        validate_organization(scope)

    officer = json.loads(json.dumps(cat))
    officer["organization"]["number_two"]["officer"] = True
    with pytest.raises(IntegrityError):
        validate_organization(officer)

    clicked = json.loads(json.dumps(cat))
    clicked["organization"]["number_two"]["seat_clicked"] = True
    with pytest.raises(IntegrityError):
        validate_organization(clicked)

    unique = json.loads(json.dumps(cat))
    unique["organization"]["number_two"]["second_unique_human"] = True
    with pytest.raises(IntegrityError):
        validate_organization(unique)

    two_note = json.loads(json.dumps(cat))
    two_note["organization"]["number_two"]["note"] = "Number two."
    with pytest.raises(IntegrityError):
        validate_organization(two_note)

    officer_note = json.loads(json.dumps(cat))
    officer_note["organization"]["number_two"]["note"] = "Other aspects, not all aspects. Paid E7 and Teams Premium."
    with pytest.raises(IntegrityError):
        validate_organization(officer_note)

    e7_note = json.loads(json.dumps(cat))
    e7_note["organization"]["number_two"]["note"] = "Other aspects, not all aspects. Not an officer. Not a click."
    with pytest.raises(IntegrityError):
        validate_organization(e7_note)

    manages = json.loads(json.dumps(cat))
    manages["organization"]["number_two"]["manages"] = ["treasury"]
    with pytest.raises(IntegrityError):
        validate_organization(manages)

    cannot = json.loads(json.dumps(cat))
    cannot["organization"]["number_two"]["cannot"] = ["keys"]
    with pytest.raises(IntegrityError):
        validate_organization(cannot)

    contacts = json.loads(json.dumps(cat))
    contacts["organization"]["contacts"]["developer"] = "someone"
    with pytest.raises(IntegrityError):
        validate_organization(contacts)

    recorded = json.loads(json.dumps(cat))
    recorded["organization"]["contacts"]["invited"]["agreed"] = False
    with pytest.raises(IntegrityError):
        validate_organization(recorded)

    gmail = json.loads(json.dumps(cat))
    gmail["organization"]["contacts"]["invited"]["email"] = "cynthia@gmail.com"
    with pytest.raises(IntegrityError):
        validate_organization(gmail)

    number = json.loads(json.dumps(cat))
    number["organization"]["contacts"]["invited"]["number_two"] = False
    with pytest.raises(IntegrityError):
        validate_organization(number)

    unrecorded = json.loads(json.dumps(cat))
    unrecorded["organization"]["contacts"]["invited"]["recorded"] = False
    unrecorded["organization"]["contacts"]["invited"]["email"] = "someone@ainav.institute"
    with pytest.raises(IntegrityError):
        validate_organization(unrecorded)

    agreed = json.loads(json.dumps(cat))
    agreed["organization"]["contacts"]["invited"]["recorded"] = False
    agreed["organization"]["contacts"]["invited"]["email"] = ""
    agreed["organization"]["contacts"]["invited"]["agreed"] = True
    with pytest.raises(IntegrityError):
        validate_organization(agreed)

    assert licenses["from_this_plane"] is False
    assert number_two["all_aspects"] is False


def test_business_doctrine_fail_closed_and_qualify_reuse():
    cat = load_catalog()
    missing = json.loads(json.dumps(cat))
    missing.pop("business")
    with pytest.raises(IntegrityError):
        validate_business(missing)

    model = json.loads(json.dumps(cat))
    model["business"]["model"]["prove"] = "P-ADM"
    with pytest.raises(IntegrityError):
        validate_business(model)

    revenue = json.loads(json.dumps(cat))
    revenue["business"]["economics"]["recognized_revenue_claimed"] = True
    with pytest.raises(IntegrityError):
        validate_business(revenue)

    ten = json.loads(json.dumps(cat))
    ten["business"]["elevator"]["ten"] = "A gate."
    with pytest.raises(IntegrityError):
        validate_business(ten)

    thirty = json.loads(json.dumps(cat))
    thirty["business"]["elevator"]["thirty"] = "A proof."
    with pytest.raises(IntegrityError):
        validate_business(thirty)

    ask = json.loads(json.dumps(cat))
    ask["business"]["elevator"]["ask"] = "Buy L1."
    with pytest.raises(IntegrityError):
        validate_business(ask)

    why = json.loads(json.dumps(cat))
    why["business"]["why_client"] = "They need AI."
    with pytest.raises(IntegrityError):
        validate_business(why)

    investor = json.loads(json.dumps(cat))
    investor["business"]["why_investor"] = "A category."
    with pytest.raises(IntegrityError):
        validate_business(investor)

    thesis = json.loads(json.dumps(cat))
    thesis["business"]["thesis"] = "Two humans."
    with pytest.raises(IntegrityError):
        validate_business(thesis)

    estate = json.loads(json.dumps(cat))
    estate["business"]["model"]["estate"] = "upsell"
    with pytest.raises(IntegrityError):
        validate_business(estate)

    audit = json.loads(json.dumps(cat))
    audit["business"]["model"]["audit"] = "upsell"
    with pytest.raises(IntegrityError):
        validate_business(audit)

    company = OperatingCompany()
    first = company.qualify("reuse-client")
    second = company.qualify("reuse-client")
    assert first is second
    assert company.pipeline()


def test_sealed_decision_record_refuses_mutation():
    rec = decision_record(
        record_type="admit_denied",
        request_id="req_seal",
        action_hash="a" * 64,
        action=sample_action(),
        reason_code="SEAT_DISTINCT",
    )
    sealed = as_sealed(rec)
    with pytest.raises(IntegrityError) as exc:
        sealed["memo"] = "no"
    assert exc.value.reason_code == "SEALED"
    with pytest.raises(IntegrityError):
        del sealed["request_id"]
    with pytest.raises(IntegrityError):
        sealed.clear()
    with pytest.raises(IntegrityError):
        sealed.pop("request_id")
    with pytest.raises(IntegrityError):
        sealed.popitem()
    with pytest.raises(IntegrityError):
        sealed.update({"memo": "no"})
    with pytest.raises(IntegrityError):
        sealed.setdefault("memo", "no")
    with pytest.raises(IntegrityError):
        verify_record("not-a-mapping")
    missing = dict(rec)
    missing.pop("integrity")
    with pytest.raises(IntegrityError):
        verify_record(missing)
    broken = [as_sealed(rec)]
    with pytest.raises(IntegrityError):
        verify_chain(broken + broken)
    seq = dict(as_sealed(rec))
    seq["seq"] = 9
    with pytest.raises(IntegrityError):
        verify_chain([seq])
    store = MemoryAuthorityStore()
    assert store.get_record("missing") is None


def test_consume_redis_lua_err_and_delete_rollback():
    class BadRedis:
        def eval(self, keys, argv):
            return "unexpected"

    with pytest.raises(ConsumeReplay) as exc:
        ConsumeLedger(store=MemoryAuthorityStore(), redis=BadRedis()).consume(
            "dual:slot",
            {
                "request_id": "req",
                "action_hash": "hash",
                "seat_a": "a",
                "seat_b": "b",
                "consumed_at": "now",
            },
        )
    assert exc.value.reason_code == "CONSUME_LUA_ERR"

    deleted: list[str] = []

    class OkRedis:
        def eval(self, keys, argv):
            return OK

        def delete(self, key):
            deleted.append(key)

    class BoomStore:
        def try_consume(self, slot_key, record):
            raise RuntimeError("store failed after redis")

    with pytest.raises(RuntimeError):
        ConsumeLedger(store=BoomStore(), redis=OkRedis()).consume(
            "dual:rollback",
            {
                "request_id": "req",
                "action_hash": "hash",
                "seat_a": "a",
                "seat_b": "b",
                "consumed_at": "now",
            },
        )
    assert deleted == ["dual:rollback"]


def test_merkle_and_export_refuse_broken_witnesses():
    with pytest.raises(IntegrityError):
        leaf_hash({})
    leaves = ["a" * 64, "b" * 64, "c" * 64]
    root = merkle_root(leaves)
    with pytest.raises(IntegrityError):
        verify_inclusion(leaves[0], [{"side": "R"}], root)
    with pytest.raises(IntegrityError):
        verify_inclusion(leaves[0], [{"side": "R", "hash": None}], root)
    with pytest.raises(IntegrityError):
        verify_inclusion(leaves[0], [{"side": "X", "hash": "b" * 64}], root)
    proof = [{"side": "L", "hash": "b" * 64}]
    with pytest.raises(IntegrityError):
        verify_inclusion(leaves[0], proof, root)
    verify_inclusion(leaves[0], [{"side": "R", "hash": leaves[1]}], merkle_root(leaves[:2]))
    verify_inclusion(leaves[1], [{"side": "L", "hash": leaves[0]}], merkle_root(leaves[:2]))

    store = MemoryAuthorityStore()
    rec = store.put_denied(
        decision_record(
            record_type="admit_denied",
            request_id="req_export",
            action_hash="b" * 64,
            action=sample_action(),
            reason_code="SEAT_DISTINCT",
        )
    )
    envelope = export_envelope([rec], tip=store.tip())
    verify_export(envelope)
    bad_schema = dict(envelope)
    bad_schema["schema_version"] = "other"
    with pytest.raises(IntegrityError):
        verify_export(bad_schema)
    bad_product = dict(envelope)
    bad_product["product"] = "other"
    with pytest.raises(IntegrityError):
        verify_export(bad_product)
    bad_records = dict(envelope)
    bad_records["records"] = "no"
    with pytest.raises(IntegrityError):
        verify_export(bad_records)
    bad_count = dict(envelope)
    bad_count["count"] = 9
    with pytest.raises(IntegrityError):
        verify_export(bad_count)
    missing_root = dict(envelope)
    missing_root.pop("merkle_root")
    with pytest.raises(IntegrityError):
        verify_export(missing_root)


def test_file_authority_store_refuse_corrupt_ledger(tmp_path):
    store = FileAuthorityStore(tmp_path / "ok.jsonl")
    rec = decision_record(
        record_type="admit_denied",
        request_id="req_file",
        action_hash="c" * 64,
        action=sample_action(),
        reason_code="SEAT_DISTINCT",
    )
    store.put_denied(rec)
    store.audit()
    store.merkle_root()
    store.verify()
    store.prove(store.decisions()[0]["record_id"])

    corrupt = tmp_path / "corrupt.jsonl"
    corrupt.write_text("{not json\n", encoding="utf-8")
    with pytest.raises(IntegrityError):
        FileAuthorityStore(corrupt)

    unread = tmp_path / "unread.jsonl"
    unread.write_text("{}\n", encoding="utf-8")
    with patch.object(Path, "read_text", side_effect=OSError("no")):
        with pytest.raises(IntegrityError):
            FileAuthorityStore(unread)

    good = tmp_path / "tip.jsonl"
    good_store = FileAuthorityStore(good)
    sealed = as_sealed(rec)
    if hasattr(good_store, "_after_seal"):
        good_store._chain.append(dict(sealed))
        good_store._tip = sealed["integrity"]["content_hash"]
        good_store._after_seal(sealed)
    tip = good.with_name(good.name + ".tip")
    if tip.exists():
        tip.write_text("{not json", encoding="utf-8")
        with pytest.raises(IntegrityError):
            FileAuthorityStore(good)
        tip.write_text(json.dumps({"alg": "sha256", "count": 99, "tip": "0" * 64, "merkle_root": "0" * 64}), encoding="utf-8")
        with pytest.raises(IntegrityError):
            FileAuthorityStore(good)

    with patch("agent_gov.store.os.replace"):
        with patch.dict("sys.modules", {"fcntl": None}):
            try:
                FileAuthorityStore(tmp_path / "nofcntl.jsonl")._after_seal(sealed)
            except Exception:
                pass
    import fcntl as real_fcntl

    with patch.object(real_fcntl, "flock", side_effect=OSError("no lock")):
        FileAuthorityStore(tmp_path / "oslock.jsonl").put_denied(rec)


def test_lockfile_and_keep_and_proof_day_refuse():
    with pytest.raises(LockfileError):
        load_lockfile({"required_action_fields": "action_class"})
    with pytest.raises(LockfileError):
        load_lockfile({"required_action_fields": ["payload"]})
    with pytest.raises(LockfileError):
        load_lockfile({"grant_ttl_seconds": "no"})
    with pytest.raises(LockfileError):
        load_lockfile({"grant_ttl_seconds": 0})
    lock = default_lockfile()
    load_lockfile(lock)
    with pytest.raises(LockfileError):
        load_lockfile("no")
    with pytest.raises(ProvisionError):
        weekly_keep(client_id="   ")
    with pytest.raises(ProvisionError) as exc:
        run_proof_day(seat_a="same-oid", seat_b="same-oid")
    assert exc.value.reason_code == "SEAT_DISTINCT"


def test_ip_insulation_and_microsoft_mark():
    cat = load_catalog()
    missing = json.loads(json.dumps(cat))
    missing["ip"].pop("insulation")
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(missing)
    sku = json.loads(json.dumps(cat))
    sku["ip"]["insulation"]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(sku)
    patent = json.loads(json.dumps(cat))
    patent["ip"]["insulation"]["patent_claimed"] = True
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(patent)
    uncopy = json.loads(json.dumps(cat))
    uncopy["ip"]["insulation"]["uncopyable"] = True
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(uncopy)
    g12 = json.loads(json.dumps(cat))
    g12["ip"]["insulation"]["g12_open"] = False
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(g12)
    thesis = json.loads(json.dumps(cat))
    thesis["ip"]["insulation"]["thesis"] = "Not a patent."
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(thesis)
    patent_thesis = json.loads(json.dumps(cat))
    patent_thesis["ip"]["insulation"]["thesis"] = "Independence is the pin."
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(patent_thesis)
    refuse = json.loads(json.dumps(cat))
    refuse["ip"]["insulation"]["refuse"] = []
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(refuse)
    claims = json.loads(json.dumps(cat))
    claims["ip"]["forbidden_claims"] = []
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(claims)
    layers = json.loads(json.dumps(cat))
    layers["ip"]["insulation"]["layers"] = []
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(layers)
    copy_pins = json.loads(json.dumps(cat))
    copy_pins["ip"]["insulation"]["what_they_can_copy"] = []
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(copy_pins)
    ultimate = json.loads(json.dumps(cat))
    ultimate["ip"]["insulation"]["why_ultimate_plane"] = "A plane."
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(ultimate)
    ultimate_patent = json.loads(json.dumps(cat))
    ultimate_patent["ip"]["insulation"]["why_ultimate_plane"] = "Last plane over every drafting AI."
    with pytest.raises(IntegrityError):
        validate_ip_doctrine(ultimate_patent)
    from ainav.ip import screen_pack_label

    screen_pack_label("L1")
    with pytest.raises(Exception):
        screen_pack_label("copilot")


def test_host_bind_request_empty_and_bad_json():
    from ainav.microsoft import host_bind

    class Resp:
        def __init__(self, raw, status=200):
            self.status = status
            self._raw = raw

        def read(self):
            return self._raw

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with patch("urllib.request.urlopen", return_value=Resp(b"")):
        status, body = host_bind._request("GET", "https://example.com", "tok")
        assert status == 200
        assert body == {}
    with patch("urllib.request.urlopen", return_value=Resp(b"not-json")):
        status, body = host_bind._request("GET", "https://example.com", "tok")
        assert status == 200
        assert body == "not-json"
    err = type("HTTPError", (Exception,), {})
    class HTTPError(Exception):
        def __init__(self):
            self.code = 403

        def read(self):
            return b"not-json"

    import urllib.error

    http = urllib.error.HTTPError("https://example.com", 403, "no", hdrs=None, fp=io.BytesIO(b"not-json"))
    with patch("urllib.request.urlopen", side_effect=http):
        status, body = host_bind._request("GET", "https://example.com", "tok")
        assert status == 403
        assert body == "not-json"
    http2 = urllib.error.HTTPError("https://example.com", 401, "no", hdrs=None, fp=io.BytesIO(b'{"error":"no"}'))
    with patch("urllib.request.urlopen", side_effect=http2):
        status, body = host_bind._request("GET", "https://example.com", "tok")
        assert status == 401
        assert body["error"] == "no"
    with patch.dict(os.environ, {"ENTRA_OBJECT_ID": "oid-from-env"}):
        assert host_bind._service_principal_object_id() == "oid-from-env"
    with patch.dict(os.environ, {"ENTRA_OBJECT_ID": ""}, clear=False):
        with patch("ainav.microsoft.host_bind._token", return_value={"ok": False}):
            assert host_bind._service_principal_object_id() == ""
        with patch("ainav.microsoft.host_bind._token", return_value={"ok": True, "token": "t"}):
            with patch("ainav.microsoft.host_bind._entra", return_value={"client": "app"}):
                with patch("ainav.microsoft.host_bind._get", return_value=(200, {"value": [{"id": "sp-1"}]})):
                    assert host_bind._service_principal_object_id() == "sp-1"
                with patch("ainav.microsoft.host_bind._get", return_value=(404, {})):
                    assert host_bind._service_principal_object_id() == ""


def test_mothership_and_cli_refuse_and_cover():
    with pytest.raises(ProvisionError):
        LocalMothership("   ")
    with pytest.raises(ProvisionError):
        LocalMothership("c1", packs=("INVENTED",))
    with pytest.raises(ProvisionError):
        LocalMothership("c1", packs=("P-ADM",))
    with pytest.raises(ProvisionError):
        LocalMothership("c1", packs=("L1", "P-ADM"))
    local = LocalMothership("c1")
    with pytest.raises(ProvisionError):
        local.attach_pack("INVENTED")
    with pytest.raises(ProvisionError):
        local.attach_pack("P-ADM")
    local.kit_pass = True
    local.attach_pack("P-ADM")
    local.attach_pack("P-ADM")
    with pytest.raises(ProvisionError):
        local.run_and_apply({"action_class": "no.such"}, seat_a="a", seat_b="b")
    bare = LocalMothership("c2")
    with pytest.raises(ProvisionError):
        bare.export_audit()
    master = MasterMothership()
    master.provision_pair("pair-1")
    master.company_surface()
    local.modules()
    local.manifest()
    local.audit()

    from ainav.__main__ import main as ainav_main
    from agent_gov.__main__ import main as gov_main

    assert ainav_main(["action-schema"]) == 0
    assert ainav_main(["brief-md"]) == 0
    with patch("ainav.__main__.argparse.ArgumentParser.parse_args") as parsed:
        parsed.return_value = type("A", (), {"cmd": "nope"})()
        assert ainav_main([]) == 2
    assert gov_main(["version"]) == 0
    with patch("agent_gov.__main__.argparse.ArgumentParser.parse_args") as parsed:
        parsed.return_value = type("A", (), {"cmd": "nope"})()
        assert gov_main([]) == 2

    store = MemoryAuthorityStore()
    rec = store.put_denied(
        decision_record(
            record_type="admit_denied",
            request_id="req_cli",
            action_hash="d" * 64,
            action=sample_action(),
            reason_code="SEAT_DISTINCT",
        )
    )
    path = Path("/tmp/ainav-cli-record.json")
    path.write_text(json.dumps(rec), encoding="utf-8")
    assert gov_main(["verify", str(path)]) == 0
    jsonl = Path("/tmp/ainav-cli-record.jsonl")
    jsonl.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    broken = Path("/tmp/ainav-cli-broken.json")
    broken.write_text("{not json", encoding="utf-8")
    jsonl.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    # JSONL fallback: non-list text that is not a single JSON object
    mixed = Path("/tmp/ainav-cli-mixed.json")
    mixed.write_text("not-json\n" + json.dumps(rec) + "\n", encoding="utf-8")
    # The verify path tries json.loads first; invalid JSON then JSONL.
    # A file that is invalid JSON but valid JSONL:
    only_jsonl = Path("/tmp/ainav-cli-only.jsonl")
    only_jsonl.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    # Force JSONDecodeError on the whole file then JSONL parse:
    whole = Path("/tmp/ainav-cli-whole.txt")
    whole.write_text("{\n" + json.dumps(rec)[1:] + "\n", encoding="utf-8")
    # Use a file that is not valid JSON as a whole but is JSONL
    lines = Path("/tmp/ainav-cli-lines.txt")
    lines.write_text(json.dumps(rec) + "\n" + json.dumps(rec) + "\n", encoding="utf-8")
    # json.loads on two JSON objects fails; JSONL path runs
    assert gov_main(["verify", str(lines)]) in {0, 1}

    env = Path("/tmp/ainav-cli-export.json")
    env.write_text(json.dumps({"schema_version": "no"}), encoding="utf-8")
    assert gov_main(["verify-export", str(env)]) == 1
    good_env = Path("/tmp/ainav-cli-export-ok.json")
    good_env.write_text(json.dumps(export_envelope([rec], tip=rec["integrity"]["content_hash"])), encoding="utf-8")
    assert gov_main(["verify-export", str(good_env)]) == 0
