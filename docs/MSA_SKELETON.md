# AINav, Inc. — MSA skeleton (unsigned)

Hygiene skeleton. G12 legal is not signed. Not a patent. Not LIVE_PIN_OK.
Product: AINav Control Plane (Job C).

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
- AINav is a separate failsafe from client AI
- No invented compliance certification
- Client utilizes AI; AINav is the human-control failsafe
- Client's customers utilizing AI still require the client's two humans
- First record is the SoR write; second record is the DecisionRecord
- One human plane sits over every client AI that can draft a write
- Off switch is fail-closed, not powering down Copilot
- Rollback is a dual-admitted compensating write, not a time machine
- Client departments are not SKUs; department AI is not a seat
- Do not invent named department heads
- Microsoft is not the product; lockfile stays job_c
- No patent claimed in this tree; insulation is not uncopyable
