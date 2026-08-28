from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.institute_status import public_status


def test_public_status_is_sandbox_and_unclaimed():
    body = public_status()
    assert body["kind"] == "ainav.institute.status.v1"
    assert body["live"] is False
    assert body["bc"]["wedge"] == "bc.general_journal.post"
    assert body["bc"]["sandbox_document"] == "AINAV-L1"
    assert body["sales"]["instances"] == 0
    assert body["custom_domain_claimed"] is False


def test_sandbox_evidence_cannot_claim_production():
    cat = copy.deepcopy(load_catalog())
    cat["sandbox_evidence"]["production"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    signed = copy.deepcopy(load_catalog())
    signed["sandbox_evidence"]["signed_l1"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(signed)
    assert exc2.value.reason_code == "SIGNED_L1_OPEN"
