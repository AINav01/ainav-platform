# Security

This repository is private. The Job C admit plane is fail-closed: denials, replays, and gate failures raise.

## Report a vulnerability

Open a **private** GitHub security advisory on `AINav01/ainav-platform`. Do not file a public issue for an integrity bypass, grant-bind hole, or consume-ledger race.

## Do not send

- Customer lockfiles, ledgers, or Entra/Azure secrets
- A request to mark `LIVE_PIN_OK`, signed L1, or product HA without evidence

## Out of scope for “we are secure now”

Live Graph, live Business Central, live Sales, multi-host Redis HA, and G12 legal remain **open**. Gold CI (`.github/workflows/gold.yml`, `make gold`) is in the tree and has run green. Checkout and setup-python are pinned by commit SHA. A green check is not live security and is not `LIVE_PIN_OK`.
