from __future__ import annotations

import pytest

from agent_gov import (
    ConsumeLedger,
    EffectBlocked,
    EffectLedger,
    MemoryAuthorityStore,
    admit,
    default_lockfile,
    run_and_apply,
)

from tests.helpers import sample_action


def test_effect_requires_matching_admit():
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    with pytest.raises(EffectBlocked) as exc:
        EffectLedger().effect(rec["request_id"], "0" * 64)
    assert exc.value.reason_code == "EFFECT_HASH_MISMATCH"


def test_effect_without_admit_is_blocked():
    with pytest.raises(EffectBlocked) as exc:
        EffectLedger().effect("req_missing", "a" * 64)
    assert exc.value.reason_code == "EFFECT_NO_ADMIT"


def test_second_effect_is_replay_blocked():
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    EffectLedger().effect(rec["request_id"], rec["action_hash"])
    with pytest.raises(EffectBlocked) as exc:
        EffectLedger().effect(rec["request_id"], rec["action_hash"])
    assert exc.value.reason_code == "EFFECT_REPLAY"


def test_isolated_effect_store_cannot_see_default_admit():
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    isolated = EffectLedger(store=MemoryAuthorityStore())
    with pytest.raises(EffectBlocked) as exc:
        isolated.effect(rec["request_id"], rec["action_hash"])
    assert exc.value.reason_code == "EFFECT_NO_ADMIT"


def test_run_and_apply_invokes_sor_only_after_ok():
    seen: list[dict] = []

    def apply(grant):
        seen.append(grant)
        return {"posted": True}

    out = run_and_apply(
        sample_action(),
        default_lockfile(),
        seat_a="oid-1",
        seat_b="oid-2",
        apply=apply,
    )
    assert out["record_type"] == "effect_applied"
    assert out["apply_result"] == {"posted": True}
    assert seen[0]["record_type"] == "admit_ok"


def test_apply_failure_is_fail_closed_and_not_retryable():
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(),
        seat_a="oid-1",
        seat_b="oid-2",
    )

    def boom(_grant):
        raise RuntimeError("bc timeout")

    with pytest.raises(EffectBlocked) as exc:
        EffectLedger().effect(rec["request_id"], rec["action_hash"], apply=boom)
    assert exc.value.reason_code == "EFFECT_APPLY_FAILED"
    with pytest.raises(EffectBlocked) as exc2:
        EffectLedger().effect(rec["request_id"], rec["action_hash"])
    assert exc2.value.reason_code == "EFFECT_REPLAY"


def test_effect_rejects_empty_ids():
    with pytest.raises(EffectBlocked):
        EffectLedger().effect("", "a" * 64)
    with pytest.raises(EffectBlocked):
        EffectLedger().effect("req_x", "")
