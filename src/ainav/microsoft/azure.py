"""Azure hosts the master mothership and Institute static site. Not a live pin."""

from __future__ import annotations

from typing import Any

from ainav.errors import LivePinError
from ainav.microsoft.connections import intended_request, spec
from ainav.microsoft.stack import MICROSOFT_STACK


class AzureHost:
    """Declared Azure hosting for AINav, Inc. and AINAV.Institute."""

    def __init__(self, *, live: bool = False) -> None:
        if live:
            raise LivePinError(
                "Live Azure deploy is not claimed. G1 LIVE_PIN_OK is open.",
                reason_code="LIVE_PIN_NOT_CLAIMED",
            )
        self.live = False
        self.region = "declared"
        self.spec = spec("azure.host")

    def describe(self) -> dict[str, Any]:
        return {
            "connection": "azure.host",
            "hosting": MICROSOFT_STACK["hosting"],
            "live": False,
            "region": self.region,
            "role": "master mothership and Institute static host",
            "surfaces": list(self.spec["surfaces"]),
        }

    def plan_master(self) -> dict[str, Any]:
        return intended_request(
            "azure.host",
            method="PUT",
            path="/subscriptions/{sub}/resourceGroups/ainav-inc/providers/Microsoft.App/containerApps/master",
            payload={"name": "ainav-master", "live": False},
        )

    def plan_institute(self) -> dict[str, Any]:
        return intended_request(
            "azure.host",
            method="PUT",
            path="/subscriptions/{sub}/resourceGroups/ainav-inc/providers/Microsoft.Web/staticSites/institute",
            payload={
                "name": "ainav-institute",
                "appLocation": "institute",
                "config": "institute/staticwebapp.config.json",
                "live": False,
            },
        )

    def deploy_master(self) -> None:
        raise LivePinError(
            "Azure deploy of the master mothership is not claimed.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )

    def deploy_institute(self) -> None:
        raise LivePinError(
            "Azure deploy of AINAV.Institute is not claimed. Website files exist in-repo only.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )
