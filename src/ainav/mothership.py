"""Master mothership issues lockfiles and provisions local motherships."""

from __future__ import annotations

from typing import Any

from agent_gov import AdmitClient, FileAuthorityStore, MemoryAuthorityStore, default_lockfile
from agent_gov.store import AuthorityStore
from ainav.catalog import ALLOWED_SKUS, action_classes_for, l1_action_classes, load_catalog, modules_for
from ainav.errors import ProvisionError
from ainav.ip import screen_pack_label
from ainav.microsoft.azure import AzureHost
from ainav.microsoft.bc import BusinessCentralAdapter
from ainav.microsoft.compliance import ComplianceSink
from ainav.microsoft.connections import StackPlane
from ainav.microsoft.entra import EntraSeatVerifier
from ainav.microsoft.sales import SalesEnterpriseAdapter
from ainav.microsoft.teams import TeamsNotifier
from ainav.packs import book_service, pack_manifest, require_industry, require_library
from ainav.twin import SandboxRouter


HOST_MODES = ("master", "cloud", "local")


class LocalMothership:
    """Client Job C plane. Same admit law as master. No second product."""

    host_mode = "local"

    def __init__(
        self,
        client_id: str,
        *,
        packs: tuple[str, ...] = ("L1",),
        industry: tuple[str, ...] = (),
        libraries: tuple[str, ...] = (),
        store: AuthorityStore | None = None,
        kit_pass: bool = False,
    ) -> None:
        if not client_id.strip():
            raise ProvisionError("client_id is required")
        for pack in packs:
            screen_pack_label(pack)
        unknown = [p for p in packs if p not in ALLOWED_SKUS]
        if unknown:
            raise ProvisionError(f"invented pack {unknown!r}", reason_code="CATALOG_SKU")
        if ("P-ADM" in packs or "U-DUAL" in packs) and "L1" not in packs:
            raise ProvisionError("P-ADM and U-DUAL require L1", reason_code="PACK_SCOPE")
        if ("P-ADM" in packs or "U-DUAL" in packs) and not kit_pass:
            raise ProvisionError(
                "P-ADM and U-DUAL attach only after kit PASS",
                reason_code="ATTACH_GATE",
            )
        self.client_id = client_id
        self.packs = packs
        self.industry: tuple[str, ...] = ()
        self.libraries: tuple[str, ...] = ()
        self.kit_pass = kit_pass
        self.store = store or MemoryAuthorityStore()
        self.lockfile = default_lockfile()
        self.verifier = EntraSeatVerifier(allow_lab_oids=True)
        self.client = AdmitClient(
            lockfile=self.lockfile,
            store=self.store,
            verifier=self.verifier,
        )
        self.bc = BusinessCentralAdapter()
        self.sales = SalesEnterpriseAdapter()
        self.bc.twin.sealed = True
        self.sales.twin.sealed = True
        self.router = SandboxRouter(bc=self.bc.twin, sales=self.sales.twin, sealed=True)
        self.teams = TeamsNotifier()
        self.compliance = ComplianceSink()
        self.azure = AzureHost()
        self.stack = StackPlane()
        self.last_sor_connection: str | None = None
        self.allowed_actions = self._allowed_actions()
        for pack_id in industry:
            self.attach_industry(pack_id)
        for lib_id in libraries:
            self.attach_library(lib_id)

    def _allowed_actions(self) -> frozenset[str]:
        allowed: set[str] = set()
        for pack in self.packs:
            allowed.update(action_classes_for(pack))
        return frozenset(allowed)

    def attach_pack(self, sku_id: str) -> None:
        screen_pack_label(sku_id)
        if sku_id not in ALLOWED_SKUS:
            raise ProvisionError(f"invented pack {sku_id!r}", reason_code="CATALOG_SKU")
        if sku_id in {"P-ADM", "U-DUAL"} and "L1" not in self.packs:
            raise ProvisionError(f"{sku_id} cannot be provisioned without L1", reason_code="PACK_SCOPE")
        if sku_id in {"P-ADM", "U-DUAL"} and not self.kit_pass:
            raise ProvisionError(
                f"{sku_id} attaches only after kit PASS",
                reason_code="ATTACH_GATE",
            )
        if sku_id in self.packs:
            return
        self.packs = (*self.packs, sku_id)
        self.allowed_actions = self._allowed_actions()

    def attach_industry(self, pack_id: str) -> dict[str, Any]:
        pack = require_industry(pack_id, skus=self.packs)
        if pack_id not in self.industry:
            self.industry = (*self.industry, pack_id)
        return pack

    def attach_library(self, library_id: str) -> dict[str, Any]:
        lib = require_library(library_id, skus=self.packs)
        if library_id not in self.libraries:
            self.libraries = (*self.libraries, library_id)
        return lib

    def modules(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for pack in self.packs:
            out.extend(modules_for(pack))
        return out

    def book_service(self, service_id: str) -> dict[str, Any]:
        return book_service(service_id, skus=self.packs)

    def run_and_apply(self, action: dict[str, Any], *, seat_a: str, seat_b: str) -> dict[str, Any]:
        action_class = action.get("action_class")
        if action_class not in self.allowed_actions:
            raise ProvisionError(
                f"action_class {action_class!r} is not on this mothership",
                reason_code="PACK_SCOPE",
            )
        out = self.client.run_and_apply(
            action,
            seat_a=seat_a,
            seat_b=seat_b,
            apply=lambda grant: self.router.apply(grant, trusted=True),
        )
        if action.get("action_class") in l1_action_classes():
            self.last_sor_connection = "bc.premium"
        else:
            self.last_sor_connection = "sales.enterprise"
        self.stack.after_effect(
            self,
            {
                "record_type": out.get("record_type"),
                "request_id": out.get("request_id"),
                "action_hash": out.get("action_hash"),
            },
        )
        return out

    def export_audit(self) -> dict[str, Any]:
        if "P-ADM" not in self.packs:
            raise ProvisionError(
                "Purview export is a P-ADM module",
                reason_code="PACK_SCOPE",
            )
        return self.compliance.export_audit(self.audit())

    def manifest(self) -> dict[str, Any]:
        return pack_manifest(
            client_id=self.client_id,
            skus=self.packs,
            industry=self.industry,
            libraries=self.libraries,
            allowed_actions=self.allowed_actions,
            modules=self.modules(),
            host_mode=self.host_mode,
            lockfile_digest=self.lockfile.digest(),
        )

    def audit(self) -> dict[str, Any]:
        body = self.client.audit()
        body["client_id"] = self.client_id
        body["packs"] = list(self.packs)
        body["industry"] = list(self.industry)
        body["libraries"] = list(self.libraries)
        body["host_mode"] = self.host_mode
        body["lockfile_digest"] = self.lockfile.digest()
        body["live"] = False
        return body


class CloudMothership(LocalMothership):
    """Azure-declared client plane. Same Job C law and ledger. Not LIVE_PIN_OK."""

    host_mode = "cloud"


class MasterMothership:
    """AINav, Inc. control plane. Issues lockfiles. Does not write client SoR."""

    def __init__(self) -> None:
        self.catalog = load_catalog()
        self.lockfile = default_lockfile()
        self.locals: dict[str, LocalMothership] = {}
        self.clouds: dict[str, CloudMothership] = {}
        self.host = AzureHost()
        self.stack = StackPlane()
        self.teams = TeamsNotifier()
        self.compliance = ComplianceSink()

    def issue_lockfile(self):
        return self.lockfile

    def provision(
        self,
        client_id: str,
        *,
        packs: tuple[str, ...] = ("L1",),
        industry: tuple[str, ...] = (),
        libraries: tuple[str, ...] = (),
        ledger_path: str | None = None,
        store: AuthorityStore | None = None,
        kit_pass: bool = False,
    ) -> LocalMothership:
        if store is None:
            store = FileAuthorityStore(ledger_path) if ledger_path else MemoryAuthorityStore()
        local = LocalMothership(
            client_id,
            packs=packs,
            industry=industry,
            libraries=libraries,
            store=store,
            kit_pass=kit_pass,
        )
        self.locals[client_id] = local
        return local

    def provision_cloud(
        self,
        client_id: str,
        *,
        packs: tuple[str, ...] = ("L1",),
        industry: tuple[str, ...] = (),
        libraries: tuple[str, ...] = (),
        store: AuthorityStore | None = None,
        kit_pass: bool = False,
    ) -> CloudMothership:
        cloud = CloudMothership(
            client_id,
            packs=packs,
            industry=industry,
            libraries=libraries,
            store=store or MemoryAuthorityStore(),
            kit_pass=kit_pass,
        )
        self.clouds[client_id] = cloud
        return cloud

    def provision_pair(
        self,
        client_id: str,
        *,
        packs: tuple[str, ...] = ("L1",),
        industry: tuple[str, ...] = (),
        libraries: tuple[str, ...] = (),
        store: AuthorityStore | None = None,
        kit_pass: bool = False,
    ) -> dict[str, LocalMothership]:
        """One client, cloud + local motherships, one consume ledger."""
        shared = store or MemoryAuthorityStore()
        local = self.provision(
            client_id,
            packs=packs,
            industry=industry,
            libraries=libraries,
            store=shared,
            kit_pass=kit_pass,
        )
        cloud = self.provision_cloud(
            client_id,
            packs=packs,
            industry=industry,
            libraries=libraries,
            store=shared,
            kit_pass=kit_pass,
        )
        if local.lockfile.digest() != cloud.lockfile.digest():
            raise ProvisionError("pair lockfiles must match", reason_code="LOCKFILE_HASH_MISMATCH")
        return {"local": local, "cloud": cloud}

    def company_surface(self) -> dict[str, Any]:
        """AINav, Inc. + Institute + product stack. Deploy is not claimed."""
        return {
            "entity": "AINav, Inc.",
            "product": "AINav Control Plane",
            "institute": "AINAV.Institute",
            "live": False,
            "host_mode": "master",
            "writes_client_sor": False,
            "azure": self.host.describe(),
            "master_plan": self.host.plan_master(),
            "institute_plan": self.host.plan_institute(),
            "stack": self.stack.describe(),
            "motherships": list(load_catalog()["motherships"]["hosts"]),
        }

    def standard_l1_pack(self, client_id: str) -> LocalMothership:
        spec = self.catalog["provisioning"]["standard_l1"]
        return self.provision(
            client_id,
            packs=tuple(spec["skus"]),
            industry=tuple(spec["industry"]),
            libraries=tuple(spec.get("libraries") or ()),
        )
