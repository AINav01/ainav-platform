# AINav, Inc. — ultimate control plane interface

Release 2.25.0. Not a SKU. Not LIVE_PIN_OK. Not a certificate.

**Humans sit on the plane from the top of the client's existing org chart. Owner and board oversee. Treasury and controller admit. Departments draft or keep. Department AI is not a seat. Internal and remote use the same Entra object id. Hierarchical views are the same plane seen from owner, seats, examiner, remote, and IT. The write path is draft, bind, two admits, first record, second record, keep. The executive dashboard tiles the admit ledger and freeze state. It does not invent live P&L. AI compliance is a map, not a certificate. The interface is not a fourth SKU.**

Equation: humans from the top × one admit plane × hierarchical access × fail-closed tiles.
Plane: failsafe × off-switch × reset × rollback × two-human control.
Org: client org chart × existing SOD × one admit plane.

## Seating cascade — from the top

- **Oversee** — Owner / executive, Board
- **Keep** — Internal audit / examiner
- **Admit** — Treasury — seat A, Controller — seat B
- **Draft** — Payables / sales
- **Host** — IT / identity
- **Counsel** — Legal
- **Same plane** — Remote human
- **Not a seat** — Cloud Agent / client AI

## Hierarchical views — one plane

- **Entire plane** — Anyone on the tenant. Can: See the ledger and the freeze state. Cannot: A view is not a seat.
- **Owner / board** — Oversee. Can: Institute the plane. Request a freeze. Cannot: Click both admits. One title cannot be both seats.
- **Seat A / seat B** — Treasury and controller. Can: Bind the action_hash. Refuse the write. Cannot: Be both seats. Let AI click.
- **Examiner** — Internal audit. Can: Read first and second records and the seating map. Cannot: Admit. File. Certify.
- **Remote human** — Same Entra object id. Can: Whatever their seat already allows, from any network. Cannot: Open a second plane. Use a VPN SKU.
- **IT / identity** — Host. Can: Host Copilot, Agent 365, BYO MCP. Block bypass tools. Cannot: Admit. Treat PIM as dual.

## Write path

| Step | By | State | Note |
| --- | --- | --- | --- |
| Draft | Department AI / payables / sales | idle | Not a seat. |
| Bind | The plane | none | action_hash. No live bind. |
| Seat A | treasury_approver | 0 | Own Entra object id. Own click. |
| Seat B | treasury_controller | 0 | Cynthia Hodnett invited, not recorded. |
| First record | SoR after dual admit | 1 sandbox | AINAV-L1 lab oids. 0 production. |
| Second record | Sealed DecisionRecord | 0 | P-ADM keep not attached. |
| Keep | Examiner / board | none | Weekly export after kit PASS. |

## Three lines of defense

- **1LOD** — Dual admit on the write. Seat A and seat B. In force: true. Claimed: false.
- **2LOD** — P-ADM keep / second record. Compliance keep after kit PASS. In force: false. Claimed: false.
- **3LOD** — Independent assurance. Internal audit reads; not a named auditor. In force: false. Claimed: false.

## How humans sit from the top

The ultimate control plane interface is not a fourth product. It is how humans sit on the plane from the top of the client's existing org chart down to every drafting AI.

Owner and board oversee. They institute the plane and can ask for a freeze. They are not seats. One title cannot click both admits. Treasury (seat A) and controller (seat B) are the only two humans who bind the action_hash. Payables and sales may draft. IT hosts Copilot and agents. Those AIs are not seats. Compliance and internal audit keep the second record. Legal is not replaced. Department AI is not a seat. Do not invent named heads.

Hierarchical access is segregation of duties, not a new identity provider. Internal and remote use the same Entra object id on the same plane. Remote is not a second control plane and not a VPN SKU. Microsoft Conditional Access may identify the human. It does not admit the write. The Cloud Agent may operate the host. It is not a seat.

The executive dashboard is that same plane, tiled. Real-time here means the admit ledger and the freeze state: pending binds, admits, refuses, frozen, last sealed keep. It does not invent a live P&L, forecast ARR, or Production Business Central metrics. Until signed L1, business tiles stay zero and the sandbox journal AINAV-L1 is labeled lab operator identities. AI compliance tiles map NIST, SOX, EU AI Act, ISO 42001, books-and-records, and three lines of defense with claimed=false. The dashboard is not a certificate and not a SKU.

The floor is one plane with hierarchical views. Owner and board see freeze and the off switch. They are not seats. Seat A and seat B see pending binds and refuse. The examiner sees the first record, the second record, and the maps. Remote is the same Entra object id — Conditional Access may identify; it does not admit. IT hosts Copilot and agents. Views are not SKUs and not a second product.

The write path is the same for every privileged class: draft, bind an action_hash, seat A, seat B, first record on the SoR, second record as the sealed DecisionRecord, keep. Off switch is fail-closed. Reset is the last sealed keep. Rollback is a compensating write that itself requires dual admit. Coverage is every action class on L1, P-ADM, and U-DUAL. None of those classes are live. Three lines of defense: 1LOD is dual admit, 2LOD is P-ADM keep, 3LOD is not claimed.

## Hierarchy

| Level | Role | Admit | Freeze | Keep | Note |
| --- | --- | --- | --- | --- | --- |
| Owner / executive | oversee | False | request | view | Institutes the plane. One title cannot be both seats. Do not invent a name. |
| Board | oversee | False | request | view | Fiduciary oversight. Board keep after P-ADM. Do not invent a director. |
| Internal audit / examiner | keep | False | False | second_record | Second record and seating map. Not a named auditor. Not a filing. |
| Treasury — seat A | admit | True | refuse | view | treasury_approver. Own Entra object id. Own click. |
| Controller — seat B | admit | True | refuse | view | treasury_controller. Cynthia Hodnett if she agrees. Invited, not recorded. |
| Payables / sales | draft | False | False | False | May draft. Same two humans admit. Department AI is not a seat. |
| IT / identity | host | False | False | False | Hosts Copilot, Agent 365, BYO MCP. Not a seat. |
| Legal | counsel | False | False | False | Not replaced. G12 stays open. |
| Remote human | same_plane | if_seated | if_seated | if_role | Same Entra object id. Not a second plane. Not a VPN SKU. |
| Cloud Agent / client AI | not_a_seat | False | False | False | May draft or operate the host. Cannot bind an action_hash. |

## Throughout the client organization

| Department | Role | Seat | AI | Note |
| --- | --- | --- | --- | --- |
| Treasury | admit | treasury_approver | May draft cash and bank journals. Not a seat. | Usually seat A. Existing two-person SOD. Not a SKU. |
| Controller / accounting | admit | treasury_controller | May draft the books. Not a seat. | Usually seat B. First record is the admitted SoR write. Not a SKU. |
| Payables | draft | — | AP Copilot may draft invoices and payments. Not a seat. | Same two treasury humans admit. Not a fourth SKU. |
| Sales / quote desk | draft | — | Sales Copilot may draft quotes and orders. Not a seat. | Paid U-DUAL deepens the same plane. Not a second product. |
| IT / identity | host | — | Owns Copilot, Agent 365, BYO MCP. Not a seat. | Hosts identity. Blocks bypass tools. PIM activation is not dual admit. |
| Security / compliance | keep | — | May draft risk memos. Not a seat. | 2LOD keep. Second record after P-ADM. Not a certificate. |
| Internal audit | keep | — | Not a seat. | Reads first and second records. Do not invent an audit partner. |
| Legal / counsel | counsel | — | Not a seat. | AINav does not replace counsel. G12 stays open on our side. Do not invent a firm. |
| Owner / executive | oversee | — | Not a seat unless they are one of the two named humans. | Institutes AINav. Can ask for freeze. One title cannot be both seats. |
| Board | oversee | — | Not a seat. | Fiduciary oversight. Inventory of models is not a control. Do not invent a director. |

## Internal and remote access

- Internal: Entra ID on the client tenant. Same action_hash. Same consume ledger.
- Remote: Same Entra object id from any network. Conditional Access may identify. It does not admit.
- Same plane: true. Second remote plane: false. VPN SKU: false.
- Entra required: true. PIM is not dual. Teams is not a seat.

## Executive dashboard — honest tiles

Admit ledger and freeze state. Not invented P&L. Not live Production BC.

| Tile | Value | Note |
| --- | --- | --- |
| Plane state | OPEN | Not frozen. Fail-closed if thrown. Not LIVE_PIN_OK. |
| Pending dual admits | 0 | No named treasury pair has a live bind. |
| First record (SoR) | 1 sandbox / 0 production | AINAV-L1 lab oids. Not two named humans. |
| Second record | 0 | P-ADM keep not attached. Not live Purview. |
| Off switch | READY | Fail-closed freeze. Does not power down Copilot. |
| Last sealed keep | none | Weekly DecisionRecord export after kit PASS. |
| Recognized revenue | $0 | Not booked. No billing provider. |
| Named customers | 0 | Do not invent a buyer. |
| Signed L1 | 0 | Counsel pack G13 stays open. |
| Year-one if all three | $88,000–$135,000 | Catalog list. Not a forecast. |
| Seats recorded | 0 recorded / 1 invited | Cynthia Hodnett invited, not recorded. Email none. |
| AI compliance maps | 11 instruments / claimed=false | NIST, SOX, EU AI Act, ISO 42001. Not certified. |

## AI compliance maps (claimed = false)

- **NIST AI Risk Management Framework** — Govern and Measure via sealed DecisionRecords on the admit plane Claimed: false.
- **OMB M-24-10 (federal agency AI)** — Human authority before consequential action. ICP is not a federal agency unless they buy. Claimed: false.
- **SOX / internal control over financial reporting** — Unauthorized general-journal post is the L1 incident. Dual admit is a control. Not a SOX opinion. Claimed: false.
- **FTC and state AI / automated-decision laws** — Refuse undeclared automated SoR writes. Not a state-law opinion. Claimed: false.
- **EU AI Act** — AINav is a write-gate failsafe, not the client's high-risk system. No conformity assessment is claimed. Claimed: false.
- **ISO/IEC 42001 AI management system** — Catalog and DecisionRecords can feed an AIMS. Certification is not claimed. Claimed: false.
- **OECD AI Principles** — Accountability and human agency before the write. Not a membership. Claimed: false.
- **Books and records (first / second record)** — First record is the admitted SoR write. Second record is the sealed DecisionRecord. Not a 17a-4 opinion. Claimed: false.
- **Three lines of defense** — 1LOD is dual admit on the write. 2LOD is P-ADM keep / second record. 3LOD is not claimed. Claimed: false.
- **Board fiduciary oversight of material AI write risk** — One human plane over every AI that can draft a book write. Not a legal opinion. Not a mandate. Claimed: false.
- **COSO internal control** — Dual admit is a control activity. Off switch is fail-closed. Not a COSO opinion. Claimed: false.

## Action coverage — same plane, none live

| Class | SKU | Wedge | Live | Note |
| --- | --- | --- | --- | --- |
| bc.general_journal.post | L1 | true | false | Wedge. |
| d365.quote.discount_override | U-DUAL | true | false | Wedge. |
| d365.order.submit | U-DUAL | true | false | Wedge. |
| bc.payment_journal.post | L1 | false | false | A la carte L1. Vendor or customer payment journal. Same admit plane. Not a SKU. |
| bc.bank_reconciliation.post | L1 | false | false | A la carte L1. Bank reconciliation that hits the GL. Not a SKU. |
| bc.purchase_invoice.post | L1 | false | false | A la carte L1. Purchase invoice post. Not a SKU. |
| d365.invoice.post | U-DUAL | false | false | A la carte U-DUAL. Invoice post on the Sales twin until G14. Not a fourth SKU. |
| d365.creditmemo.issue | U-DUAL | false | false | A la carte U-DUAL. Credit memo issue. Never free with P-ADM. |
| bc.cash_receipt.post | L1 | false | false | A la carte L1. Cash receipt that hits the GL. Not a SKU. |
| bc.sales_invoice.post | L1 | false | false | A la carte L1. Sales invoice post on the BC twin. Not a SKU. |
| bc.fixed_asset.post | L1 | false | false | A la carte L1. Fixed-asset journal. Same admit plane. Not a SKU. |
| bc.inventory.adjust | L1 | false | false | A la carte L1. Inventory adjustment that hits the GL. Not a SKU. |
| d365.return.authorize | U-DUAL | false | false | A la carte U-DUAL. Return authorization. Never free with P-ADM. |
| d365.price.override | U-DUAL | false | false | A la carte U-DUAL. List-price override. Never free with P-ADM. |
| d365.quote.void | U-DUAL | false | false | A la carte U-DUAL. Void an issued quote. Never free with P-ADM. |

## Mechanics

- **Off switch** — Fail-closed. No dual admit, no write. Humans freeze new grants. Inference may continue. Consequence does not. Does not: Power down Copilot, Agent 365, or the client's model.
- **Reset** — Return the admit plane to the last sealed DecisionRecord / Merkle root as the keep. Does not: Wipe production Business Central or Sales.
- **Rollback** — A compensating SoR write that itself requires dual admit. The second record shows the rollback was admitted. Does not: Silent undo or a time machine.

## Refuse

- fourth SKU
- invented live P&L
- forecast ARR
- LIVE_PIN_OK
- EU AI Act certified
- named department heads
- remote second plane
- Cloud Agent as seat

Interface seating of the three SKUs. Not a product. Not LIVE_PIN_OK.
