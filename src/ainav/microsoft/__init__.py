"""Microsoft integrations are identity, notify, SoR, and audit sink — not the product."""

from ainav.microsoft.bc import BusinessCentralAdapter
from ainav.microsoft.entra import EntraSeatVerifier
from ainav.microsoft.stack import MICROSOFT_STACK, assert_not_a_seat
from ainav.microsoft.teams import TeamsNotifier

__all__ = [
    "BusinessCentralAdapter",
    "EntraSeatVerifier",
    "MICROSOFT_STACK",
    "TeamsNotifier",
    "assert_not_a_seat",
]
