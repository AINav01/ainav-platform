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

Same plane, named 2.6.0 surface:

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

## Mothership and commercial spine

Three SKUs only — **L1** ($28–40k), **P-ADM** ($40–60k/yr), **U-DUAL** ($20–35k/yr). U-DUAL is never free with P-ADM. Packs deepen this admit plane.

```bash
python -m ainav plan
python -m ainav provision acme --packs L1
python -m ainav twin-demo
python -m ainav ops-demo
```

Master mothership issues the lockfile. A local mothership runs AdmitClient against a Business Central **digital twin** (`bc.general_journal.post`). Paid U-DUAL deepens the same plane onto a Sales Enterprise twin. Industry packs and fee-for-service hours are **not SKUs**. Teams is notify-only. Entra supplies seat object ids — we do not replace the IdP. Live SoR and `LIVE_PIN_OK` are **open**.

Institute site: `institute/index.html` (AINAV.Institute). Plan: `docs/BUSINESS_PLAN.md`. IP hygiene: `LICENSE`, `NOTICE`, `TRADEMARKS.md`. Microsoft marks name integrations only — they are not the product. G12 legal stays **open**.

```bash
python -m ainav ip
python -m ainav programs
python -m ainav pitch
python -m ainav connections
python -m ainav stack-demo
python -m ainav company-demo
```

NVIDIA Inception and Microsoft for Startups are **qualification targets**, not claimed memberships. Public pitch leads with `bc.general_journal.post`. Inception excludes crypto-associated companies — do not lead with gold-vector custody fixtures. A working public website and incorporation date are apply prerequisites; this tree does not claim either. Pitch: `docs/PROGRAMS.md`.

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

### 2.6.0 (this tree)

Company operating system: pipeline, kit board, delivery runbook, catalog
economics (not recognized revenue). Complements: Entra, Key Vault, Monitor,
SharePoint kit evidence, Defender XDR. Industry controller / quote desk
and QBR / mothership-ops hours are not SKUs.

### 2.5.0

Microsoft stack connections: Azure, Microsoft 365 E7, Teams Enterprise,
Teams Premium, Business Central Premium, Sales Enterprise. Wired on the
mothership in sandbox mode. Live deploy and live SoR stay unclaimed.

### 2.4.0

NVIDIA Inception / Microsoft for Startups qualification doctrine.
Public wedge is `bc.general_journal.post`. Membership, credits, and a
public website deploy are not claimed. Gold `custody.withdraw.execute`
is a frozen lab fixture only.
