# AINav, Inc. — stack walk

Release 2.54.0. Catalog-honest. Not LIVE_PIN_OK. Not a launch.
Microsoft is identity, notify, SoR, and audit sink. The product is the admit plane.

**Azure hosts. Entra identifies. AINav admits. Business Central and Sales receive. Teams notifies. Complements hold secrets, evidence, policy, and audit. Cloudflare is DNS/edge, not a hop on the privileged write.**

Implementation: Job C gold invariants plus fail-closed probes in ainav.microsoft.health, dns, host_bind, bc_sandbox, and institute_publish. Probe never writes a SoR and never marks LIVE_PIN_OK.
CLI: `python -m ainav stack`. Probe is read-only: `python -m ainav connect --probe`.

This Cloud Agent cannot: create users; grant Graph roles; edit Cloudflare; bind ainav.institute; mark LIVE_PIN_OK.

## Privileged-write path

1. **Cloudflare DNS / edge** — `full`. probe_dns. Cloudflare Pro is the edge plan, not a SKU. E7 mail, Entra, Teams SIP, and lync SRV already point. Missing: none. DNS full is not Institute launch.
   Owner: Confirm Pro: SSL Full not Flexible, WAF managed on, Rocket Loader off. Do not orange-cloud MX or autodiscover. Do not bind ainav.institute until the transfer is Active and you say launch. This Cloud Agent cannot edit Cloudflare. [Cloudflare dashboard](https://dash.cloudflare.com) · [Cloudflare DNS docs](https://developers.cloudflare.com/dns/)

2. **Azure host** — `hosted_not_custom`. Institute is on Azure Static Web Apps eastus2. host_bind and institute_publish stay fail-closed. Custom domain is not bound.
   Owner: Say launch only when you want ainav.institute bound. Then add SWA asuid TXT and point DNS. [Azure Static Web Apps](https://portal.azure.com/#view/Microsoft_Azure_StaticApps) · [SWA custom domain](https://learn.microsoft.com/en-us/azure/static-web-apps/custom-domain-external)

3. **Entra identify** — `mailbox_recorded_oid_open`. Cynthia Hodnett mailbox chodnett@ainav.institute is recorded. Mailbox is not an Entra oid and not a click. probe_graph reads org and users when the same app has User.Read.All.
   Owner: Create or confirm her Entra user. Confirm a distinct object id. She signs in once. You do not click both seats. [Entra users](https://entra.microsoft.com/#view/Microsoft_AAD_UsersAndTenants/UserManagementMenuBlade/~/AllUsers) · [Entra users](https://learn.microsoft.com/en-us/entra/identity/users/users-overview)

4. **AINav Control Plane** — `running_code`. Job C gold: two distinct humans bind one action_hash, consume-once, fail-closed EffectLedger, hash-chained DecisionRecords. Cloud Agent is not a seat.
   Owner: She clicks seat B with her own object id. Lab oids are not two named treasury humans. [Azure-hosted Institute](https://blue-river-010091a0f.7.azurestaticapps.net/) · [ainav-platform](https://github.com/AINav01/ainav-platform)

5. **Business Central Premium** — `sandbox_journal`. Sandbox company AINav. Document AINAV-L1. Wedge bc.general_journal.post. Production stays blocked. Not LIVE_PIN_OK.
   Owner: Enable the same Entra app in Business Central Production only when you explicitly authorize a Production write. [Business Central Sandbox](https://businesscentral.dynamics.com/ainav.institute/Sandbox) · [BC companies](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/new-company)

6. **Sales Enterprise** — `licensed_not_wired`. Sales Enterprise is licensed. Global Discovery returned zero instances. U-DUAL stays on the twin until G14.
   Owner: Create a US Power Platform environment with Dataverse. Then start a new Cloud Agent with DATAVERSE_URL. This unblocks the Sales twin, not live SoR. [Power Platform environments](https://admin.powerplatform.microsoft.com/environments) · [Create an environment](https://learn.microsoft.com/en-us/power-platform/admin/create-environment)

7. **Teams notify** — `dns_full_graph_open`. SIP and lync SRV already point through Cloudflare. DNS is not the Teams Graph connection. A chat is not a seat.
   Owner: Admin-consent Team.ReadBasic.All on the same Entra app. Do not use Write. Do not create a new app. [Microsoft 365 admin](https://admin.cloud.microsoft/?source=applauncher#/homepage) · [Teams overview](https://learn.microsoft.com/en-us/microsoftteams/teams-overview)

8. **Graph Read on the same app** — `owner_consent_open`. Health probes report 403 without Team.ReadBasic.All, Sites.Read.All, SecurityIncident.Read.All, and RoleEligibilitySchedule.Read.Directory. No Graph Write from this plane.
   Owner: On the same Entra app AINav Cloud Agent1, grant those four Read roles. Do not use Write. Do not create a new app. [Entra app registrations](https://entra.microsoft.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade) · [Graph permissions](https://learn.microsoft.com/en-us/graph/permissions-reference)

9. **Agent Tools registry** — `owner_leave_available`. Catalog playbook. A tool invocation is not dual admit. This Cloud Agent cannot click Unblock or Block.
   Owner: Leave five Work IQ / MCP Management tools Available. Block Dataverse MCP until paid U-DUAL. Reject BYO SoR writers. [Agents > Tools registry](https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all) · [Manage tools for agents](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-tools-for-agent)

10. **Institute launch** — `held`. --publish-institute stays launch_not_ready. Apex is Squarespace Coming Soon. Azure hostname is hosted.
   Owner: Say launch only when you want ainav.institute bound. A Coming Soon page is not the custom domain. [Azure Static Web Apps](https://portal.azure.com/#view/Microsoft_Azure_StaticApps) · [Bind a custom domain](https://learn.microsoft.com/en-us/azure/static-web-apps/custom-domain-external)


## Complements (not hops on the write)

- **Azure Key Vault** — `declared_sandbox`. host_bind can create a vault. Secrets are not LIVE_PIN_OK.
   Owner: Hold connection secrets here. Do not paste them into the catalog. [Key Vaults](https://portal.azure.com/#browse/Microsoft.KeyVault%2Fvaults) · [Key Vault overview](https://learn.microsoft.com/en-us/azure/key-vault/general/overview)

- **Azure Monitor** — `declared_sandbox`. Mothership health. LAW is not Sentinel. Not a live pin.
   Owner: Read host health. Do not treat Monitor as the admit plane. [Azure Monitor](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/overview) · [Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/overview)

- **SharePoint kit** — `graph_read_open`. Kit evidence store. Graph Write is not consented from this plane. Sites.Read.All is the owner gate.
   Owner: Grant Sites.Read.All on the same app. Do not grant Write from this plane. [SharePoint](https://www.office.com/launch/sharepoint) · [SharePoint Graph](https://learn.microsoft.com/en-us/graph/api/resources/sharepoint)

- **Defender XDR** — `graph_read_open`. E7 security sink. SecurityIncident.Read.All stays owner-consent. Not the admit plane.
   Owner: Grant SecurityIncident.Read.All on the same app. No Write. [Microsoft Defender portal](https://security.microsoft.com) · [Defender XDR](https://learn.microsoft.com/en-us/defender-xdr/)

- **Entra PIM** — `not_dual`. Eligible seats. A PIM activation is not dual admit. RoleEligibilitySchedule.Read.Directory stays owner-consent.
   Owner: Grant the Read Directory role on the same app. Do not treat PIM as seat B. [Entra PIM](https://entra.microsoft.com/#view/Microsoft_Azure_PIMCommon/CommonMenuBlade/~/quickStart) · [PIM configure](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)

- **Microsoft Sentinel** — `declared_sandbox`. DecisionRecord export sink after P-ADM. The mothership LAW is not a Sentinel workspace.
   Owner: Do not treat Sentinel as the admit plane. Keep is the sealed DecisionRecord. [Microsoft Sentinel](https://portal.azure.com/#view/Microsoft_Azure_Security_Insights) · [Sentinel overview](https://learn.microsoft.com/en-us/azure/sentinel/overview)

- **Azure Policy** — `cannot_weaken`. Host policy. Cannot weaken Job C invariants. LIVE_PIN_OK cannot be marked from this plane.
   Owner: Keep West Europe blocked if that is the host rule. Do not loosen Job C from Policy. [Azure Policy](https://portal.azure.com/#view/Microsoft_Azure_Policy/PolicyMenuBlade/~/Overview) · [Azure Policy](https://learn.microsoft.com/en-us/azure/governance/policy/overview)


## Stop

A green health probe is not LIVE_PIN_OK. DNS full is not Institute launch. Sandbox AINAV-L1 is not Production. Mailbox recorded is not a seat B click.
