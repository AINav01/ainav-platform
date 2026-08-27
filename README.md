# ainav-platform

Private engineering repository for AINav platform development.

This tree hosts the Job C admit plane: **dual-admitted effect authority** before a privileged system-of-record write.

```python
from agent_gov import admit, ConsumeLedger, default_lockfile, EffectLedger

rec = admit(action, default_lockfile(), ledger=ConsumeLedger(),
            seat_a="oid-1", seat_b="oid-2")
EffectLedger().effect(rec["request_id"], rec["action_hash"])
```

`admit` binds two distinct human seats to an `action_hash`, then atomically consumes that slot once. `EffectLedger.effect` is the fail-closed gate: no matching `admit_ok` (or a hash mismatch, or a replay) means the SoR write does not happen.

## Invariants (must not change)

- Dual distinct principals (`seat_a != seat_b`)
- `action_hash` is SHA-256 of canonical JSON (sorted keys, no whitespace)
- Single-use consume — second admit of the same hash is `ConsumeReplay`
- Fail-closed — deny, replay, and gate failures raise; they never return ok
- SoR / effect only after admit ok
- Lockfiles cannot weaken those invariants

## Install and gold

```bash
python -m pip install -e ".[dev]"
make gold
```

Offline gold covers dual seats, single-use consume, H9 (exactly one concurrent ok), the Lua validate-all-then-write-all simulator, and the effect gate. Live Redis multi-host HA and `LIVE_PIN_OK` are **not** claimed here.

## Package

| Export | Role |
|--------|------|
| `admit` | Dual-seat admission + consume |
| `ConsumeLedger` | Single-use slot ledger |
| `EffectLedger` | Effect gate / SoR apply |
| `default_lockfile` | Pinned Job C policy |
| `run_and_apply` | Admit then effect in one call |

Version `2.1.0` matches the lab admit-plane surface (`AdmitClient` / Redis consume live in the private control-plane monorepo).
