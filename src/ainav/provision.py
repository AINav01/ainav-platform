"""Standard L1 provisioning pack. Deepens the same admit plane."""

from __future__ import annotations

from ainav.mothership import LocalMothership, MasterMothership


def provision_l1(client_id: str) -> LocalMothership:
    return MasterMothership().standard_l1_pack(client_id)


def provision_l1_with_udual(client_id: str) -> LocalMothership:
    """Paid U-DUAL attach. Not free with P-ADM — caller must have sold both."""
    return MasterMothership().provision(
        client_id,
        packs=("L1", "U-DUAL"),
        industry=("industry.treasury", "industry.sales"),
    )


def provision_l1_padm(client_id: str) -> LocalMothership:
    """Coverage after kit PASS. Does not include U-DUAL."""
    return MasterMothership().provision(
        client_id,
        packs=("L1", "P-ADM"),
        industry=("industry.treasury",),
    )
