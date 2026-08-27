"""Microsoft integrations are identity, notify, SoR, and audit sink — not the product."""

from ainav.microsoft.azure import AzureHost
from ainav.microsoft.bc import BusinessCentralAdapter
from ainav.microsoft.compliance import ComplianceSink
from ainav.microsoft.entra import EntraSeatVerifier
from ainav.microsoft.sales import SalesEnterpriseAdapter
from ainav.microsoft.stack import MICROSOFT_STACK, assert_not_a_seat
from ainav.microsoft.teams import TeamsNotifier

__all__ = [
    "AzureHost",
    "BusinessCentralAdapter",
    "ComplianceSink",
    "EntraSeatVerifier",
    "MICROSOFT_STACK",
    "SalesEnterpriseAdapter",
    "TeamsNotifier",
    "assert_not_a_seat",
]
