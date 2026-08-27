"""Master mothership issues lockfiles and provisions local motherships."""

from __future__ import annotations

from typing import Any

from agent_gov import AdmitClient, FileAuthorityStore, MemoryAuthorityStore, default_lockfile
from agent_gov.store import AuthorityStore
from ainav.catalog import action_classes_for, load_catalog, modules_for
from ainav.errors import ProvisionError
from ainav.microsoft.bc import BusinessCentralAdapter
from ainav.microsoft.entra import EntraSeatVerifier
from ainav.microsoft.teams import TeamsNotifier


class LocalMothership:
    """Client-local Job C plane. Same admit law as master. No second product."""

    def __init__(
        self,
        client_id: str,
        *,
        packs: tuple[str, ...] = ("L1",),
        store: AuthorityStore | None = None,
    ) -> None:
        if not client_id.strip():
            raise ProvisionError("client_id is required")
        unknown = [p for p in packs if p not in {"L1", "P-ADM", "U-DUAL"}]
        if unknown:
            raise ProvisionError(f"invented pack {unknown!r}", reason_code="CATALOG_SKU")
        if "U-DUAL" in packs and "L1" not in packs:
            raise ProvisionError("U-DUAL cannot be provisioned without L1")
        self.client_id = client_id
        self.packs = packs
        self.store = store or MemoryAuthorityStore()
        self.lockfile = default_lockfile()
        self.verifier = EntraSeatVerifier(allow_lab_oids=True)
        self.client = AdmitClient(
            lockfile=self.lockfile,
            store=self.store,
            verifier=self.verifier,
        )
        self.bc = BusinessCentralAdapter()
        self.teams = TeamsNotifier()
        self.allowed_actions = self._allowed_actions()

    def _allowed_actions(self) -> frozenset[str]:
        allowed: set[str] = set()
        for pack in self.packs:
            allowed.update(action_classes_for(pack))
        return frozenset(allowed)

    def modules(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for pack in self.packs:
            out.extend(modules_for(pack))
        return out

    def run_and_apply(self, action: dict[str, Any], *, seat_a: str, seat_b: str) -> dict[str, Any]:
        action_class = action.get("action_class")
        if action_class not in self.allowed_actions:
            raise ProvisionError(
                f"action_class {action_class!r} is not on this mothership",
                reason_code="PACK_SCOPE",
            )
        return self.client.run_and_apply(
            action,
            seat_a=seat_a,
            seat_b=seat_b,
            apply=self.bc.apply,
        )

    def audit(self) -> dict[str, Any]:
        body = self.client.audit()
        body["client_id"] = self.client_id
        body["packs"] = list(self.packs)
        body["live"] = False
        return body


class MasterMothership:
    """AINav, Inc. control plane. Issues lockfiles. Does not write client SoR."""

    def __init__(self) -> None:
        self.catalog = load_catalog()
        self.lockfile = default_lockfile()
        self.locals: dict[str, LocalMothership] = {}

    def issue_lockfile(self):
        return self.lockfile

    def provision(
        self,
        client_id: str,
        *,
        packs: tuple[str, ...] = ("L1",),
        ledger_path: str | None = None,
    ) -> LocalMothership:
        if "U-DUAL" in packs and "P-ADM" in packs:
            # Allowed together only as paid attach — never as a free bundle flag.
            pass
        store = FileAuthorityStore(ledger_path) if ledger_path else MemoryAuthorityStore()
        local = LocalMothership(client_id, packs=packs, store=store)
        self.locals[client_id] = local
        return local

    def standard_l1_pack(self, client_id: str) -> LocalMothership:
        return self.provision(client_id, packs=("L1",))
