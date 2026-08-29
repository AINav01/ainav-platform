# AINav, Inc. — deep-dive review

Catalog-honest. Not a live pin. Not a launch. Not recognized revenue.

## Verdict

AINav, Inc. has a running Job C admit plane, a Microsoft sandbox twin, and an Azure-hosted Institute that is **held until launch**. The company can prove the L1 write-gate on Business Central Sandbox. It cannot yet sell a signed L1, attach P-ADM, or mark LIVE_PIN_OK.

**Success still open:** LIVE_PIN_OK × proof day × signed L1 × P-ADM attach
**Commercial close:** named dual seats × proof day × signed L1 × P-ADM attach
**Lab pin:** LIVE_PIN_OK — never marked from sales.
**Owner:** James Hodnett (handle DayTradingMarkets). **Operator:** cursor.cloud_agent (not a seat, not dual admit).
**Second officer:** none. **Invited:** Cynthia Hodnett (not recorded, no email stored). **Named customers:** none. **Recognized revenue:** none.
**Launch ready:** false. **Custom domain claimed:** false.

## Success equation scorecard

The product equation is a lab pin times a sale. Controllers buy the commercial equation.

- **Commercial close** — named dual seats × proof day × signed L1 × P-ADM attach. Closed: false.
- **LIVE_PIN_OK** — false. Never marked from this plane.
- **Proof day** — executable (`python -m ainav proof-day`, 90 minutes). Sold: false.
- **Signed L1** — false. G13. Sandbox journal AINAV-L1 used lab operator oids, not two named treasury humans.
- **P-ADM attach** — 0. Attaches only after L1 Acceptance Kit PASS.
- **Closed:** false.

## How the pieces fit

One company. Three SKUs. Ten departments. Six Microsoft connections. Eight complements. The Cloud Agent operates the host. It is not a seat.

Azure hosts → Microsoft 365 E7 / Entra identifies → AINav admits → Business Central (L1 SoR) and Sales (U-DUAL SoR) receive the write → Teams notifies. Complements hold secrets, evidence, policy, and audit.

- **Owner / operator** — `sole_owner`. Owner James Hodnett. Operator cursor.cloud_agent is not a seat and not dual admit. Second officer: none.
- **Job C admit plane** — `running_code`. AINav Control Plane. Two distinct humans bind one action_hash. Then the write. Cloud Agent is not seat_a or seat_b.
- **L1 / Business Central** — `sandbox_journal`. Sandbox company AINav document `AINAV-L1` on 2026-08-28 for 250.00. Wedge `bc.general_journal.post`. lab operator oids — not two named treasury humans. Production stays blocked. Not LIVE_PIN_OK.
- **P-ADM attach** — `unattached`. Attaches after L1 Acceptance Kit PASS. Attached=0. Never bundles free U-DUAL.
- **U-DUAL / Sales** — `licensed_not_wired`. Sales Enterprise is licensed. Global Discovery returned zero instances. Attached=0. Twin only until G14.
- **Institute / DNS** — `azure_hosted_not_custom`. ainav-institute on eastus2. launch_ready=false. Apex still Squarespace. No asuid. Do not publish until launch.
- **Programs** — `qualify_not_claimed`. Microsoft for Startups first. NVIDIA Inception second. Membership claimed: false. Crypto-associated: false. GPU production: false.
- **Commercial spine** — `catalog_list_not_revenue`. Year-one catalog list if one controller buys all three: $88,000–$135,000. Signed L1=0. Named customers: none. Recognized revenue: none.

Refuse: Teams vote as dual; Copilot as the admit plane; free U-DUAL; LIVE_PIN_OK; named design partner; invented contact inbox.

## First principles

Dual-admitted effect authority before privileged system-of-record writes.
A privileged write is allowed only when two distinct humans bind the same `action_hash`,
that grant is consumed once, and the effect gate is fail-closed.
Microsoft is identity, notify, SoR, and audit sink. The product is the admit plane.

Must not change:

- Job C only — not agent inventory (Job A), not IdP replacement (Job B)
- Dual distinct principals
- action_hash bound
- Single-use consume
- Fail-closed
- SoR only after admit ok
- No free U-DUAL with P-ADM or U-SOR
- No soft HITL as dual
- No invented SKUs
- No LIVE_PIN_OK / product HA / signed L1 without evidence

## The sale

The unauthorized general-journal post that two humans did not admit. L1 is the week you prove that write cannot land without two seats.
- Proof day: 90 minutes. `python -m ainav proof-day`
- Seats: treasury_approver / treasury_controller
- Door: Generate a proof-day brief a controller can forward. Do not invent a contact inbox.
- Refuse: Teams vote as dual, Copilot as the admit plane, free U-DUAL, LIVE_PIN_OK, named design partner, invented contact inbox.

## Commercial spine

**L1 FIRST_OFFER** — $28,000–$40,000 (2–4 weeks) — prove.
**P-ADM ADMIT_COVERAGE** — $40,000–$60,000 (annual) — keep after L1 Acceptance Kit PASS. Never bundles free U-DUAL.
**U-DUAL DEPTH_PACK** — $20,000–$35,000 (annual) — deepen. Never free with P-ADM or U-SOR.
A la carte packs attach after the required SKU. They are not SKUs.

Year-one catalog list if one controller buys all three: $88,000–$135,000. Catalog list if one controller buys L1, then attaches P-ADM, then pays for U-DUAL. Not recognized revenue.
Pipeline attached: L1=0, P-ADM=0, U-DUAL=0. Signed L1=0.

Price L1 against the unauthorized journal that two humans did not admit. Prove it in ninety minutes. Keep with P-ADM. Deepen with paid U-DUAL.
- Motion: qualify → proof day → sell L1 that week → kit PASS → attach P-ADM → offer paid U-DUAL
- Economics: Pipeline math uses catalog list prices. It is not recognized revenue.

## Digital twin and Microsoft sandbox

Three layers. They are not interchangeable.

1. **In-process twin** — `bc.sandbox` and `d365.sales.sandbox` only. `python -m ainav twin-demo`. Institute `#twin` bench is browser-only. Graph, Dataverse, and Production are not called.
2. **Business Central Sandbox (real)** — company AINav (`9b8d1202-be8f-f111-8327-7ced8db3712c`). Document `AINAV-L1` on 2026-08-28 for 250.00. Wedge `bc.general_journal.post`. Sandbox journal exists. Production is blocked. This is not LIVE_PIN_OK. Seats: lab operator oids — not two named treasury humans.
3. **Sales twin only** — Dynamics 365 Sales Enterprise is licensed. No Dataverse instance. Quote override stays on the twin until G14.

Next pin: `bc.sandbox` → `bc.microsoft.sandbox` on bc.premium. sent=False. Process twin → Microsoft Business Central sandbox envelope. Not production. Not LIVE_PIN_OK.

## Microsoft fabric

Path: Azure hosts → Microsoft 365 E7 / Entra identifies → AINav admits → Business Central (L1 SoR) and Sales (U-DUAL SoR) receive the write → Teams notifies. Complements hold secrets, evidence, policy, and audit.

Fabric path (sandbox, not SKUs):

- **azure.host** — Microsoft Azure (`host`, hosted_sandbox). ainav-institute on eastus2. Custom domain not bound.
- **m365.e7** — Microsoft 365 E7 / Microsoft Entra ID (`identity`, connected_sandbox). Seat object ids. Copilot is not a seat. PIM is not dual admit.
- **admit** — AINav Control Plane (`admit`, running_code). Two distinct humans. One action hash. Then the write.
- **bc.premium** — Dynamics 365 Business Central Premium (`sor`, sandbox_journal). sandbox · AINav · bc.general_journal.post. Production blocked.
- **sales.enterprise** — Dynamics 365 Sales Enterprise (`sor`, licensed_not_wired). License exists. No Dataverse instance. Twin only until G14.
- **teams.enterprise** — Microsoft Teams Enterprise (`notify`, licensed_not_wired). Effect notify. A chat is not a seat.
- **teams.premium** — Microsoft Teams Premium (`notify`, licensed_not_wired). Protected notify. A meeting is not a seat.

Six connections (sandbox, not SKUs):

- **azure.host** — Microsoft Azure (hosting). binds: master mothership target, AINAV.Institute static site.
- **m365.e7** — Microsoft 365 E7 (tenant). binds: Entra Suite seat ids, Purview/Sentinel audit sink, Teams licensing.
- **teams.enterprise** — Microsoft Teams Enterprise (notify). binds: effect notify.
- **teams.premium** — Microsoft Teams Premium (notify). binds: protected effect notify.
- **bc.premium** — Dynamics 365 Business Central Premium (sor). binds: bc.general_journal.post.
- **sales.enterprise** — Dynamics 365 Sales Enterprise (sor). binds: d365.quote.discount_override, d365.order.submit.

Eight complements (not SKUs, not live, PIM is not dual, LAW is not Sentinel):

- **entra.id** — Microsoft Entra ID (identity). binds: seat object ids. Seat object ids. Not an IdP replacement. Copilot is not the admit plane.
- **azure.keyvault** — Azure Key Vault (secrets). binds: connection secret hold. Connection secret hold on the host. Not a live pin.
- **azure.monitor** — Azure Monitor (observe). binds: mothership health. Mothership health. LAW is not Sentinel. Not a live pin.
- **sharepoint.kit** — SharePoint (evidence). binds: Acceptance Kit evidence. Kit evidence store. Not a seat. Graph is not called from this page.
- **defender.xdr** — Microsoft Defender XDR (security). binds: E7 security sink. E7 security sink. SecurityIncident.Read.All is not granted. Not the admit plane.
- **entra.pim** — Microsoft Entra Privileged Identity Management (seat_eligibility). binds: eligible dual seats. Eligible seats. A PIM activation is not dual admit.
- **sentinel.siem** — Microsoft Sentinel (siem). binds: DecisionRecord export sink. DecisionRecord export sink. The mothership LAW is not a Sentinel workspace.
- **azure.policy** — Azure Policy (host_policy). binds: lockfile host constraints. Host policy. West Europe is blocked. Cannot weaken Job C.

E7 ships Copilot and Agent 365. They are not the admit plane.
Agent Tools admin: https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all
Leave Available (owner Unblocks if Blocked; this Cloud Agent cannot):

- **Work IQ User** — Seat object ids. Not a seat.
- **Work IQ Teams** — Notify. A chat is not a seat.
- **Work IQ SharePoint** — Kit evidence. Not dual.
- **Work IQ Mail** — Notify only. A mailbox is not a seat.
- **Microsoft MCP Management** — Governs tools. Cannot weaken Job C.

Owner steps:

1. Sign in to the Microsoft 365 admin center as James Hodnett. Use a role that can manage Agent Tools. https://admin.microsoft.com
2. Open Agents > Tools > Registry. The Cloud admin deep link lands on the tools list. https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all
3. For each Leave Available tool: search the Name, open the row, and leave Status = Available. If it is Blocked, choose Unblock. Available is not a seat. https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all
4. Confirm these five show Status Available and Publisher Microsoft: Work IQ User, Work IQ Teams, Work IQ SharePoint, Work IQ Mail, Microsoft MCP Management. https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all
5. Do not bind Microsoft 365 Copilot, Work IQ Copilot, Agent 365, or Work IQ Calendar as seat_a or seat_b. A tool invocation is not dual admit. https://learn.microsoft.com/en-us/microsoft-agent-365/tooling-servers-overview
6. Find Dataverse MCP Server. If Status is Available, choose Block. Keep it blocked until paid U-DUAL and dual admit exist. https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all
7. Open the Requests tab. Reject any BYO MCP that writes Business Central or Sales or claims dual admit. Do not register an AINav admit MCP that posts journals. https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all
8. Stop. This does not publish the Institute, write a SoR, or mark LIVE_PIN_OK. This Cloud Agent cannot click Unblock or Block.

Block until dual: Dataverse MCP Server, Any BYO MCP that writes Business Central or Sales.
Never as admit: Microsoft 365 Copilot, Work IQ Copilot, Agent 365, Work IQ Calendar.
This Cloud Agent cannot approve tools.

## Institute and DNS

- Azure hostname: https://blue-river-010091a0f.7.azurestaticapps.net
- Site: ainav-institute in eastus2
- public_deploy_claimed=False custom_domain_claimed=False launch_ready=False
- Nameservers stay on Cloudflare. Apex still serves Squarespace Coming Soon.
- Microsoft 365 mail is pointed (MX, SPF, DKIM, autodiscover, Entra enrollment).
- No Azure SWA `asuid`. Custom domain list on the Static Web App is empty.
- `--publish-institute` returns `launch_not_ready` and does not upload.
- Do not bind `ainav.institute` until the owner says launch.

## Operating organization

Departments are the operating company, not SKUs. Out-of-gate means the map is complete. It does not mean Sales, Teams, Institute, legal, or programs are live.
- Owner James Hodnett. Operator is not a seat.
- Second unique human: false. Incorporation date: not stored in this tree.

- **Treasury / Finance** — running_sandbox. systems: bc.premium. Business Central Sandbox company AINav. Production stays blocked. Not LIVE_PIN_OK. Blocked by: BC Production app not Enabled; signed L1 / two named treasury humans.
- **Identity / IT / Host** — running_sandbox. systems: m365.e7, entra.id, azure.host, azure.keyvault, azure.monitor, azure.policy. Same Entra app. Azure host in eastus. West Europe is blocked by policy. Blocked by: LIVE_PIN_OK.
- **Sales / Revenue** — licensed_not_wired. systems: sales.enterprise. Sales Enterprise license exists. Global Discovery returned zero instances. Blocked by: Power Platform environment with Dataverse; DATAVERSE_URL.
- **People / Notify** — licensed_not_wired. systems: teams.enterprise, teams.premium. Teams is licensed. A chat is not a seat. Graph notify is not wired. Blocked by: Team.ReadBasic.All on the same Entra app.
- **Security / Compliance** — licensed_not_wired. systems: defender.xdr, entra.pim, sentinel.siem, sharepoint.kit. E7 licenses exist. Complements are not SKUs. PIM activation is not dual admit. LAW is not Sentinel. Blocked by: SecurityIncident.Read.All; RoleEligibilitySchedule.Read.Directory; Sites.Read.All; Sentinel on the existing LAW.
- **Institute / GTM** — azure_hosted_not_custom. systems: repo.institute, azure.host. Azure hostname is published. ainav.institute coming-soon is not bound. Not LIVE_PIN_OK. Blocked by: ainav.institute custom domain.
- **Legal / Counsel** — open_gap. systems: catalog.legal. IP hygiene lives in this tree. Counsel pack is not signed. Blocked by: G12 legal; G13 signed L1.
- **Product / Engineering** — running_code. systems: repo.agent_gov, repo.catalog. Job C admit plane and catalog. Three SKUs only. Not a live pin. Blocked by: product HA.
- **Delivery / Customer Success** — running_code. systems: delivery. Master / cloud / local motherships and week-one runbook. Do not invent a customer. Blocked by: named customer; LIVE_PIN_OK.
- **Programs / Partnerships** — qualify_not_claimed. systems: programs. Microsoft for Startups first. NVIDIA Inception second. Membership is not claimed. Blocked by: public website; incorporation date; second unique human contact.

## Delivery

Same Job C lockfile. One consume ledger per client. Master never writes the client SoR.
- Master: Azure-declared master mothership issues lockfile, catalog, gold. Never writes client SoR.
- Cloud: Azure-declared client mothership. Same ledger as local. Sandbox twin.
- Local: Client-local mothership. Same ledger as cloud. AdmitClient + twin + Teams notify.
- Week one: provision master lockfile → provision cloud + local pair on one ledger → proof day or Acceptance Kit on the BC twin → notify Teams Enterprise and Premium → store kit evidence in SharePoint sandbox → refuse live pin.

## Programs

Job C: dual-admitted effect authority before Dynamics 365 Business Central privileged writes. Not a cryptocurrency product. Not an IdP. Not agent inventory.
- Public wedge: `bc.general_journal.post`
- Order: microsoft.founders_hub → nvidia.inception → nvidia.developer → github.for_startups → microsoft.isv_success → nvidia.connect.
- Membership claimed: false. Ready to apply: false. GPU workload claimed: false. Crypto-associated: false.

## Human gates (owner only)

- Ask Cynthia Hodnett to be the second unique human. If she agrees, create her own @ainav.institute mailbox and Entra user. Do not use an alias or Gmail. Do not record her in this tree until you send the address and say record it.
- Confirm her Entra object id is different from James Hodnett. She signs in once. She is treasury_controller / Inception business executive. She clicks seat B. You do not click both seats.
- Leave Available: Work IQ User, Work IQ Teams, Work IQ SharePoint, Work IQ Mail, Microsoft MCP Management. Block Dataverse MCP until paid U-DUAL.
- On the same Entra app AINav Cloud Agent1 ([REDACTED]), grant admin consent for Team.ReadBasic.All, Sites.Read.All, SecurityIncident.Read.All, and RoleEligibilitySchedule.Read.Directory. Do not use Write roles. Do not create a new app.
- Create a US Power Platform environment with Dataverse. Then start a new Cloud Agent with DATAVERSE_URL. This unblocks the Sales twin, not live SoR.
- Record the Delaware C-corp incorporation date outside this tree for Microsoft for Startups and NVIDIA Inception. Do not commit the date here.
- Apply to Microsoft for Startups first, only after you say launch and the public site is the custom domain. Membership is not claimed.
- Say launch only when you want ainav.institute bound. Then add SWA asuid TXT and point DNS. A Coming Soon page is not the custom domain. Do not publish until you say launch.
- Enable the same Entra app in Business Central Production only when you explicitly authorize a Production write. Sandbox journal AINAV-L1 is not Production.

## Financial model (catalog list)

Pipeline math uses catalog list prices. It is not booked. It is not recognized revenue.
Recognized revenue: 0. Signed L1: 0. Named customers: 0. Billing provider: false.

- **One controller — L1 only** — $28,000–$40,000. One controller buys L1 and stops.
- **One controller — L1 then P-ADM** — $68,000–$100,000. One controller buys L1, kit PASS, then attaches P-ADM.
- **One controller — all three SKUs** — $88,000–$135,000. One controller buys L1, attaches P-ADM, then pays for U-DUAL.
- **Three controllers — L1 + P-ADM each** — $204,000–$300,000. Three controllers each buy L1 and attach P-ADM. No named buyers exist.
- **One L1 plus four FFS days** — $42,000–$54,000. One controller buys L1 and four billable days on the same plane.
- **One L1 plus payables and bank desks** — $40,000–$60,000. One controller buys L1 then attaches industry.payables and industry.bank.
- **All three SKUs plus invoice and credit desks** — $100,000–$155,000. One controller buys all three SKUs then attaches industry.invoice_desk and industry.credit.

## Expert review — working well

- Job C invariants hold in gold: dual seats, single-use consume, fail-closed effect, hash-chained DecisionRecords.
- Three SKUs only. Packs, libraries, FFS, and Microsoft licenses are not products.
- Catalog is law. Probe cannot publish, write a SoR, or mark LIVE_PIN_OK.
- AINAV.Institute is hosted and launch is held. Coming Soon is not claimed as the custom domain.
- Microsoft fabric path is correct: Azure hosts, Entra identifies, AINav admits, BC/Sales receive, Teams notifies.
- Business Central Sandbox journal AINAV-L1 exists. Production stays blocked.
- Cynthia Hodnett is invited by name and not recorded. The Cloud Agent is not a seat.
- Proof day is an executable ninety-minute runbook. Buyer brief does not invent an inbox.
- A la carte desks are pack-gated. Extra Business Central and Sales writes stay off the wedge until attach.

## Expert review — could be improved

- AINAV-L1 used lab operator oids. That is a sandbox write, not two named treasury humans.
- One human cannot close dual admit, Inception contacts, or signed L1.
- Sales Enterprise is licensed with zero Dataverse instances. U-DUAL cannot leave the twin.
- Cloud and local motherships are Azure-declared in catalog and still in-process on one ledger — not two deployed planes.
- Apex ainav.institute is Squarespace Coming Soon while Azure hosts the real site. The public face is split.
- Graph read roles are missing. Teams, SharePoint, Defender, and PIM complements stay 403.
- No billing provider. Catalog list cannot become recognized revenue.
- Ten departments are mapped. Most are licensed_not_wired. The map is not the company running.

## Fifteen upgrades

- **1. [owner] Named dual seats** — Ask Cynthia. Create her @ainav.institute user. She clicks seat B. James does not click both.
- **2. [owner] Proof day on named humans** — Run python -m ainav proof-day with two distinct Entra object ids. Stop telling the AINAV-L1 lab-oid story as the sale.
- **3. [owner] Graph read on the same app** — Admin-consent Team.ReadBasic.All, Sites.Read.All, SecurityIncident.Read.All, RoleEligibilitySchedule.Read.Directory. No Write. No new app.
- **4. [owner] US Dataverse** — Create a US Power Platform environment with Dataverse. New Cloud Agent with DATAVERSE_URL. Unblocks the Sales twin, not live SoR.
- **5. [tree] One door, no inbox** — Keep the Institute buyer page as a forwardable proof-day brief. Do not invent a contact inbox or a design-partner name.
- **6. [tree] Price the incident, not hours** — Sell L1 against the unauthorized journal. FFS days deepen the same plane and never mint a SKU.
- **7. [tree] Hold launch** — Do not bind ainav.institute or publish until James says launch. --publish-institute stays launch_not_ready.
- **8. [owner] Startups then Inception** — Apply to Microsoft for Startups only after launch and the custom domain. Inception second. Membership is not claimed.
- **9. [tree] P-ADM weekly keep object** — Weekly sealed DecisionRecord export the treasurer can open. Not live Purview.
- **10. [tree] FFS requires L1** — Billable days refuse without L1. They cannot attach U-DUAL.
- **11. [tree] Catalog financial model** — Talk if-then catalog list. Never invent ARR, bookings, or recognized revenue.
- **12. [tree] Commercial equation ≠ lab pin** — Controllers buy named dual seats × proof day × signed L1 × P-ADM attach. LIVE_PIN_OK stays a lab pin.
- **13. [owner] Counsel pack** — G12 hygiene then G13 signed L1. Unsigned order form and MSA skeleton are not a signature.
- **14. [tree] Product HA is not a sale** — Redis multi-host and LIVE_PIN_OK stay engineering. Do not mark them from a contract.
- **15. [owner] Leave Available / Block Dataverse MCP** — Leave five Microsoft tools Available. Block Dataverse MCP until paid U-DUAL. Tools are not seats.

## Still missing

- Second unique human (Inception contacts and signed L1 seats)
- ainav.institute custom domain and incorporation date
- Power Platform / Dataverse environment for Sales
- Graph roles on the same Entra app for Teams, SharePoint, Defender, PIM
- Recognized revenue / external billing provider
- Signed L1 counsel pack (G13)
- Multi-host product HA

## OPEN (do not mark closed)

- G1/G10 LIVE_PIN_OK
- G12 legal
- G13 signed L1
- G14 live SoR
- Product HA

## Read the company

Catalog wins. `--probe` overlays live Microsoft and DNS health. Probe does not publish, write a SoR, or mark LIVE_PIN_OK.

- `python -m ainav review`
- `python -m ainav review --probe`
- `python -m ainav org [--probe]`
- `python -m ainav connect --probe`
- `python -m ainav dns`
- `python -m ainav agent-tools [--probe]`
- `python -m ainav proof-day`
- `python -m ainav twin-demo`
- `python -m ainav programs`
- `python -m ainav finance`
- `python -m ainav brief-pdf`
