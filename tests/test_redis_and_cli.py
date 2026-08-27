from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_gov import (
    ConsumeLedger,
    ConsumeReplay,
    RedisDualConsume,
    SimulatorRedis,
    admit,
    default_lockfile,
)
from agent_gov.__main__ import main
from agent_gov.redis_consume import LUA_PATH

from tests.helpers import sample_action


def test_lua_script_on_disk_matches_contract():
    script = LUA_PATH.read_text(encoding="utf-8")
    assert "validate-all-then-write-all" in script
    assert "{ok}" in script
    assert "{err}" in script


def test_redis_dual_consume_via_simulator_client():
    redis = RedisDualConsume(SimulatorRedis())
    ledger = ConsumeLedger(redis=redis)
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ledger,
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert rec["consumed"] is True
    with pytest.raises(ConsumeReplay):
        admit(
            sample_action(),
            default_lockfile(),
            ledger=ledger,
            seat_a="oid-3",
            seat_b="oid-4",
        )


def test_cli_version_and_invariants(capsys):
    assert main(["version"]) == 0
    assert "2.1.0" in capsys.readouterr().out
    assert main(["invariants"]) == 0
    out = capsys.readouterr().out
    assert "dual-admit-v1" in out
    assert "fail_closed" in out
    assert main(["vectors"]) == 0
    assert "da4eeecbca9ce7fed28c062156295505eb3b4e978022452feb2b4a4162579fcd" in capsys.readouterr().out


def test_cli_demo_and_verify(tmp_path, capsys):
    assert main(["demo", "--seat-a", "oid-1", "--seat-b", "oid-2"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["admit"] == "admit_ok"
    assert payload["effect"] == "effect_applied"
    record = {
        "schema_version": "decision_record.v1",
        "record_id": "dr_x",
        "record_type": "admit_ok",
        "request_id": "req_x",
        "action_hash": "a" * 64,
        "prev_receipt_hash": "0" * 64,
    }
    from agent_gov.hashing import content_hash
    from agent_gov.records import hashable_body

    record["integrity"] = {
        "alg": "sha256",
        "content_hash": content_hash(hashable_body(record)),
        "prev_receipt_hash": "0" * 64,
    }
    path = tmp_path / "rec.json"
    path.write_text(json.dumps(record))
    assert main(["verify", str(path)]) == 0


def test_action_type_rejected():
    from agent_gov import AdmitDenied, action_hash

    with pytest.raises(AdmitDenied) as exc:
        action_hash(123)
    assert exc.value.reason_code == "ACTION_TYPE"


def test_cli_verify_jsonl(tmp_path):
    from agent_gov.hashing import content_hash
    from agent_gov.records import GENESIS_HASH, hashable_body

    rec = {
        "schema_version": "decision_record.v1",
        "record_id": "dr_y",
        "record_type": "admit_ok",
        "request_id": "req_y",
        "action_hash": "b" * 64,
        "prev_receipt_hash": GENESIS_HASH,
    }
    rec["integrity"] = {
        "alg": "sha256",
        "content_hash": content_hash(hashable_body(rec)),
        "prev_receipt_hash": GENESIS_HASH,
    }
    path = tmp_path / "chain.jsonl"
    path.write_text(json.dumps(rec) + "\n")
    assert main(["verify", str(path)]) == 0


def test_redis_bytes_and_bad_script():
    class _BytesClient:
        def eval(self, script, numkeys, *parts):
            return b"{ok}"

    assert RedisDualConsume(_BytesClient()).eval(["k"], ["a"]) == "{ok}"
    bad = SimulatorRedis()
    assert bad.eval("no-contract", 1, "k") == "{err}"
