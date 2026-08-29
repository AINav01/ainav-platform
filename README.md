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

Same plane, named 2.15.0 surface:

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
python -m ainav owner-steps
python -m ainav brief-pdf
python -m ainav order-form
python -m ainav keep-artifact
python -m ainav finance
python -m ainav governance
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

### 2.31.0 (this tree)

A named controller can now name the incident and the SOD they already
have. They still could not name what is not the gate, what they walk
out of proof day with, or what no does. Hero, buyer, Client console,
and the Cynthia brief now say: vendor-native approval, Teams, PIM, and
Copilot are not the plane; walk out is a sealed DecisionRecord and a
Merkle export; refusing is the product working; fail-closed means the
write does not land; the off switch freezes grants, not Copilot.

### 2.30.0

A named controller already has Business Central Premium, Entra, and
two-person journal SOD. They still lack a gate in front of the write.
Must-have is for owner, board, and examiner on the same plane —
inventory of models is not a control. Hero, buyer, Client console,
and the Cynthia brief now say that before SKUs or the scoreboard.
Proof day is the sale. Native approval is not the plane.

### 2.29.0

A named controller must see why this is must-have before SKUs, the
dashboard, or the scoreboard. The unauthorized general-journal post
the client's AI or the client's customer AI drafted and two humans
did not admit. Every new client AI is another unauthorized-write
surface unless one human plane sits over all of them. Hero, buyer,
floor Entire/Client, and the Cynthia brief now lead with that copy.
Job C in plain language is two humans before the write. Mandated:
false. Certified: false. Not a fourth SKU. One dashboard included
with L1. Standard and advanced stay provision bands.

### 2.28.3

The floor reads as three scopes a buyer can scan: week-one prove,
included with L1, advanced upsell. Client tab sits next to Entire
plane. Desk table is grouped. Band cards drop the SKU:false dump.
One dashboard, included with L1. Not a second dashboard product.

### 2.28.2

Desk-table bands no longer say bare "advanced" on included-with-SKU
rows. Labels are standard, advanced · priced, advanced · with P-ADM,
and advanced · with U-DUAL. L1 SKU includes now name included seating
and the dashboard. G12 sits in honest_missing with the other open
legal gap. Delivery week-one is the runbook after the standard_l1
prove — not a second week-one product.

### 2.28.1

Deep review of the 2.28.0 bands. included means included with the
required SKU when that SKU is attached — not free. Sales/quote desks
are included with paid U-DUAL, not with L1. Week-one prove stays
`provisioning.standard_l1` (treasury + wedge). Commercial standard
seating is every L1 pack and library with `included_in_sku=true`, plus
the one dashboard. Libraries now sit on the desk table. One dashboard
object (`dashboard` = `client_dashboard`). Not LIVE_PIN_OK.

### 2.28.0

Client executive dashboard is included with L1 — not an upsell and not
a SKU. One dashboard; do not sell Standard vs Advanced dashboard
products. Provisioning is two bands on the three SKUs: standard is
included seating (L1 packs, wedge, Entra, Teams notify, twin, proof
day, the dashboard); advanced is the upsell band (priced desks, P-ADM,
paid U-DUAL, hours). Neither band is a SKU. U-DUAL is never free.
Attached 0/0/0. Not LIVE_PIN_OK.

### 2.27.0

Executive floor adds zero-standing access (identify is not admit; not a
ZTNA SKU), authorization lifecycle and revocation, provisioning of the
three SKUs plus desks/hours (U-DUAL never free; attached 0/0/0),
notify-only inter-communication, sealed record keeping, and a
regulation/AI compliance matrix with claimed=false. Two more views:
Provision and Records. Not a fourth SKU. Not LIVE_PIN_OK.

### 2.26.0

Command-console floor: each hierarchical view has a deck (owner freeze,
seats rehearsal, examiner inspector, remote same-Entra, IT host).
Walkable sandbox rehearsal of `bc.general_journal.post` — not a live
bind, Microsoft is not called, production stays 0. Duty matrix is SOD.
Attention board is honest zeros plus one sandbox first record. Catalog
as-of clock, not a live Production clock. Not a fourth SKU. Not
LIVE_PIN_OK.

### 2.25.0

Deep control-plane floor: hierarchical views (owner, seats, examiner,
remote, IT), write path from draft to keep, three lines of defense,
action coverage (none live), fail-closed mechanics. Same honest ledger.
Not a fourth SKU. Not LIVE_PIN_OK.

### 2.24.0

Ultimate control plane interface: humans from the top of the client's
org chart, hierarchical access, same-Entra remote, executive dashboard
tiles (admit ledger — not invented P&L), AI compliance maps
claimed=false. Printed in the Cynthia letter and brief. Institute
`#control-plane`. Not a fourth SKU. Not LIVE_PIN_OK.

### 2.23.0

Why the ultimate control plane insulates: last human gate over every
drafting AI. The vendor of that AI cannot credibly be the failsafe.
A vendor-native button is not the category. Not a patent. Not
uncopyable. G12 stays open. Printed in the Cynthia letter and the
executive brief.

### 2.22.0

Full Cynthia Hodnett packet on GitHub: investor letter with priced
upsell catalog, longer personal brief, financial model, governance,
owner steps, and Institute `#investor` (desks + fee-for-service).
Not a priced round. Not a forecast. Owner gaps stay open.

| Packet | Path |
|--------|------|
| Investor letter (print) | `docs/CYNTHIA_HODNETT_INVESTOR.pdf` |
| Investor letter (HTML) | `docs/CYNTHIA_HODNETT_INVESTOR.html` |
| Investor letter (markdown) | `docs/CYNTHIA_HODNETT_INVESTOR.md` |
| Personal brief (print) | `docs/CYNTHIA_HODNETT_BRIEF.pdf` |
| Personal brief (HTML) | `docs/CYNTHIA_HODNETT_BRIEF.html` |
| Personal brief (markdown) | `docs/CYNTHIA_HODNETT_BRIEF.md` |
| Financial model | `docs/FINANCIAL_MODEL.md` |
| Governance | `docs/GOVERNANCE.md` |
| Owner steps | `docs/OWNER_STEPS.md` |
| One-page plan | `docs/BUSINESS_PLAN.md` |

### 2.21.0

Cynthia Hodnett investor letter: greeting, seat-B ask, what we will
not ask, attach math, and the full upsell catalog with list prices
(L1 desks, P-ADM keep, U-DUAL, fee-for-service, libraries). Packs are
not a fourth SKU. Not a priced round. Not a forecast. Print
`docs/CYNTHIA_HODNETT_INVESTOR.pdf`. Owner gaps stay open.

### 2.20.0

Cynthia Hodnett investor packet: letter pages with the three SKUs,
the full upsell catalog and list prices, sale motion, and Tuesday
role. Packs are not a fourth SKU. Not a priced round. Not a forecast.
Print `docs/CYNTHIA_HODNETT_INVESTOR.pdf`. Owner gaps stay open.

### 2.19.0

Investor executive summary for Cynthia Hodnett: catalog list, zero
booked, two-human close. Not a priced round. Not a forecast. Not an
equity grant. Owner gaps stay open.

### 2.18.0

The build insulates by staying independent of the AI vendor.
Microsoft sells Copilot and Agent 365; the vendor of the AI cannot
credibly sit over that AI as the human failsafe. Others can copy a
Teams vote. They do not copy Job C: lockfile stays `job_c`,
fail-closed gold, catalog law. Not a patent. Not uncopyable.
G12 stays open. Owner gaps stay open.

### 2.17.0

The plane sits on the client's existing org chart. Treasury and
controller hold the two admit seats. IT hosts Copilot. Department AI
is not a seat. Do not invent named heads. Departments are not SKUs.
Owner gaps stay open.

### 2.16.0

One human plane sits over every client AI that can draft a write.
Failsafe, off switch, reset, rollback, first and second records.
Off switch is fail-closed, not powering down Copilot. Rollback is a
compensating write, not a time machine. Must-have for owner, board,
and examiner is not a statute. Not a fourth SKU. Owner gaps stay open.

### 2.15.0

The client utilizes AI. The client's customers do too. The client
institutes AINav and its stable of offerings as the failsafe.
First record is the SoR write. Second record is the DecisionRecord.
Cascade desk and second-record keep are not SKUs. Not a certificate.
Owner gaps stay open.

### 2.14.0

AINav is a separate failsafe from client AI. Catalog maps NIST AI RMF,
SOX/ICFR, EU AI Act, and ISO 42001 without claiming certification.
`industry.governance` seats L1. `industry.oversight` is a priced P-ADM
keep. Owner gaps stay open. Cynthia still invited, not recorded.

### 2.13.0

Priced a-la-carte desks on the same three SKUs. Cash, fixed-asset,
inventory, returns, pricing, and retention attach with catalog-list
bands. Pack attach is a pricing model, not a fourth SKU. Order form,
finance, and Institute `#packs` list the desks. Owner gaps stay open.
Cynthia still invited, not recorded.

### 2.12.0

A la carte upsells on the same three SKUs: payables, bank, invoice,
and credit desks; quote-to-cash and P-ADM SIEM libraries; finance /
brief / review repositories. Extra actions stay pack-gated. Owner
gaps stay open. Cynthia still invited, not recorded.

### 2.11.0

Company executive packet: org, motherships, Microsoft fabric, products,
pricing models, catalog-list financial scenarios, expert review, and
15 upgrades. Print `docs/CYNTHIA_HODNETT_BRIEF.pdf`. Finance:
`python -m ainav finance`. Cynthia still invited, not recorded.

### 2.10.1

Deep executive brief for Cynthia Hodnett — incident, honest status,
Tuesday role, and a decision. Print `docs/CYNTHIA_HODNETT_BRIEF.pdf`.
Still invited, not recorded. Same commercial close. Launch is held.

### 2.10.0

James Hodnett is sole owner. Cynthia Hodnett is invited as seat B —
not recorded, no email stored. Commercial close is named dual seats ×
proof day × signed L1 × P-ADM attach. LIVE_PIN_OK stays a lab pin.
Unsigned order form and MSA skeleton. Owner steps with Microsoft
links. Printable brief: `python -m ainav brief-pdf`. Institute
primary path is the write, proof day, and open. Launch is held.

### 2.9.0

Proof day is an executable 90-minute runbook. Institute buyer page
generates a forwardable brief (no inbox). Next pin is the intended
Business Central sandbox envelope. Microsoft for Startups is first;
NVIDIA Inception is second. L1 copy is incident-framed. G12/G13 stay
open. No named design partner.

### 2.8.0

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
