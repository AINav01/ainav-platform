from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import IPError, ProgramError
from ainav.ip import refuse_claim
from ainav.programs import (
    claim_membership,
    pitch,
    public_wedge_action,
    qualify,
    screen_public_copy,
)


def test_public_wedge_is_l1_not_custody():
    action = public_wedge_action()
    assert action["action_class"] == "bc.general_journal.post"
    assert "USDC" not in str(action)
    assert "custody" not in str(action)


def test_inception_qualify_is_unclaimed():
    rec = qualify("nvidia.inception")
    assert rec["membership_claimed"] is False
    assert rec["applied"] is False
    assert rec["eligible_to_prepare"] is True
    assert rec["ready_to_apply"] is False
    assert rec["public_wedge"] == "bc.general_journal.post"
    assert rec["live"] is False
    assert rec["apply_prerequisites"]
    with pytest.raises(ProgramError) as exc:
        claim_membership("nvidia.inception")
    assert exc.value.reason_code == "PROGRAM_NOT_CLAIMED"
    later = qualify("nvidia.connect")
    assert later["eligible_to_prepare"] is False
    hub = qualify("microsoft.founders_hub")
    assert hub["eligible_to_prepare"] is True
    assert hub["ready_to_apply"] is False
    complementary = qualify("nvidia.developer")
    assert complementary["eligible_to_prepare"] is False


def test_public_copy_refuses_crypto_lead_and_false_membership():
    with pytest.raises(ProgramError) as exc:
        screen_public_copy("AINav is a USDC custody control plane")
    assert exc.value.reason_code == "PROGRAM_CRYPTO"
    screen_public_copy("Not a cryptocurrency product. Business Central write-gate.")
    with pytest.raises(IPError):
        refuse_claim("NVIDIA Inception member")


def test_pitch_leads_with_erp():
    text = pitch()
    assert "Business Central" in text
    assert "not claimed" in text.lower() or "Not an acceptance" in text
    assert "USDC" not in text
    assert "NVIDIA Inception" in text
    assert "Microsoft for Startups" in text
    assert "GitHub for Startups" in text
    assert "Microsoft ISV Success" in text


def test_programs_catalog_cannot_claim_or_go_crypto():
    cat = load_catalog()
    claimed = copy.deepcopy(cat)
    claimed["programs"]["membership_claimed"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(claimed)
    assert exc.value.reason_code == "PROGRAM_NOT_CLAIMED"
    crypto = copy.deepcopy(cat)
    crypto["programs"]["crypto_associated"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(crypto)
    assert exc2.value.reason_code == "PROGRAM_CRYPTO"
    gpu = copy.deepcopy(cat)
    gpu["programs"]["gpu_workload_claimed"] = True
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(gpu)
    assert exc3.value.reason_code == "PROGRAM_NOT_CLAIMED"
    with pytest.raises(ProgramError):
        qualify("not.a.program")
