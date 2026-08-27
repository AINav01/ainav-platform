# ainav-platform

Private engineering repository for AINav platform development.

Job C admit plane: **dual-admitted effect authority** before a privileged system-of-record write.

```python
from agent_gov import admit, ConsumeLedger, default_lockfile, EffectLedger

rec = admit(action, default_lockfile(), ledger=ConsumeLedger(),
            seat_a="oid-1", seat_b="oid-2")
EffectLedger().effect(rec["request_id"], rec["action_hash"])
```

`admit` binds two distinct human seats to an `action_hash` and consumes that slot once. The grant ticket (`grant_id`) binds seats + hash + policy. `EffectLedger.effect` is the fail-closed gate: reserve → optional SoR `apply` → `effect_applied`. A failed apply is `effect_apply_failed` (never a fake success). Sealed DecisionRecords are immutable and hash-chained (`seq` + `prev_receipt_hash`).

Same plane, named 2.1.0 surface:

```python
from agent_gov import DualSession

session = DualSession("oid-1", "oid-2")
rec = session.admit(action)
session.effect(rec["request_id"], rec["action_hash"])
```

## Invariants (must not change)

- Dual distinct principals (`seat_a != seat_b`)
- `action_hash` is SHA-256 of canonical JSON (sorted keys, no whitespace)
- Privileged actions require `action_class`
- Single-use consume — second admit of the same hash is `ConsumeReplay`
- Fail-closed — deny, replay, and gate failures raise; they never return ok
- SoR / effect only after admit ok
- Lockfiles cannot weaken those invariants
- DecisionRecords are hash-chained (`prev_receipt_hash` + `seq`) and verifiable
- Sealed receipts are immutable
- `grant_id` binds seats to the action and policy
- Frozen gold vectors pin `action_hash` (breaking change if they move)

## Install and gold

```bash
python -m pip install -e ".[dev]"
make gold
python -m agent_gov demo
python -m agent_gov audit
```

Offline gold covers dual seats, single-use consume, H9 (exactly one concurrent admit **and** effect), the Lua / Redis-shaped consume adapter, file-ledger reload, and integrity verification. Live Redis multi-host HA and `LIVE_PIN_OK` are **not** claimed here.

## Package

| Export | Role |
|--------|------|
| `admit` / `AdmitClient` / `DualSession` | Dual-seat admission |
| `ConsumeLedger` | Single-use slot ledger |
| `EffectLedger` | Effect gate / SoR apply |
| `FileAuthorityStore` | Append-only JSONL ledger |
| `RedisDualConsume` | EVAL of `dual_consume.lua` (bring your client) |
| `default_lockfile` | Pinned Job C policy |
| `verify_record` / `verify_chain` | Tamper check |
| `audit` / `prove` | Verified counts + Merkle inclusion proof |
