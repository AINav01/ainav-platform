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

Same plane, named 2.9.0 surface:

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
python -m ainav review
python -m ainav review --probe
python -m ainav proof-day
python -m ainav buyer
python -m ainav brief
python -m ainav next-pin
python -m ainav provision acme --packs L1
python -m ainav motherships
python -m ainav delivery
python -m ainav raci
python -m ainav twin-demo
python -m ainav ops-demo
```

Master mothership issues the lockfile and never writes the client SoR. A **cloud** mothership (Azure-declared) and a **local** mothership share one consume ledger and run AdmitClient against a Business Central **digital twin** (`bc.general_journal.post`). Paid U-DUAL deepens the same plane onto a Sales Enterprise twin. Industry packs, repositories, and fee-for-service hours are **not SKUs**. Teams is notify-only. Entra supplies seat object ids — we do not replace the IdP. Live SoR and `LIVE_PIN_OK` are **open**.

Institute site: `institute/index.html` (AINAV.Institute). Plan: `docs/BUSINESS_PLAN.md`. Company review: `docs/REVIEW.md` (`python -m ainav review`). IP hygiene: `LICENSE`, `NOTICE`, `TRADEMARKS.md`. Microsoft marks name integrations only — they are not the product. G12 legal stays **open**. Launch is held.

```bash
python -m ainav ip
python -m ainav org
python -m ainav review
python -m ainav programs
python -m ainav pitch
python -m ainav connections
python -m ainav dns
python -m ainav agent-tools
python -m ainav agent-tools --steps
python -m ainav stack-demo
python -m ainav company-demo
```

Microsoft for Startups is first; NVIDIA Inception is second. Both are **qualification targets**, not claimed memberships. Public pitch leads with `bc.general_journal.post`. Inception excludes crypto-associated companies — do not lead with gold-vector custody fixtures. Apply also needs a working public website, an incorporation date, and two unique human contacts (developer + business executive). This tree does not claim those. Pitch: `docs/PROGRAMS.md`. The operating organization is `python -m ainav org` — every department exists; Sales, Teams, Institute, legal, and programs are not claimed live.

Proof day is the sale: `python -m ainav proof-day`. The Institute buyer page generates a forwardable brief and does not invent a contact inbox. Next pin is the intended Business Central sandbox envelope (`sent=False`). Not `LIVE_PIN_OK`.

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

### 2.8.0 (this tree)

Proof day is an executable 90-minute runbook. Institute buyer page
generates a forwardable brief (no inbox). Next pin is the intended
Business Central sandbox envelope. Microsoft for Startups is first;
NVIDIA Inception is second. L1 copy is incident-framed. G12/G13 stay
open. No named design partner.

### 2.7.0

Acceptance Kit is a twin proof. Quotes/invoices are catalog-list
artifacts. Exits: LOST, KIT_FAIL, CHURN. P-ADM/U-DUAL can renew.
Honest missing stays listed.

### 2.6.0

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
