from __future__ import annotations


def sample_action(**overrides):
    action = {
        "action_class": "custody.withdraw.execute",
        "payload": {"amount": "100", "asset": "USDC", "dest": "0xabc"},
        "proposal_id": "prp-1",
        "sor_target": "custody.core",
        "policy_id": "dual-admit-v1",
    }
    action.update(overrides)
    return action
