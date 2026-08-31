from __future__ import annotations

import copy

import pytest

from agent_gov import ConsumeReplay
from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.delivery import DeliverySystem, public_delivery, raci, week_one
from ainav.errors import LivePinError
from ainav.mothership import CloudMothership
from ainav.ops import ClientAccount
from ainav.provision import provision_pair


def _journal(memo: str = "pair") -> dict:
    return {
        "action_class": "bc.general_journal.post",
        "payload": {"account": "1000", "amount": "1.00", "memo": memo},
        "proposal_id": "prp-pair-shared",
        "sor_target": "bc.sandbox",
        "policy_id": "dual-admit-v1",
    }


def test_catalog_delivery_law():
    cat = load_catalog()
    assert cat["motherships"]["hosts"] == ["master", "cloud", "local"]
    assert cat["motherships"]["shared_ledger"] is True
    assert cat["motherships"]["master"]["writes_client_sor"] is False
    assert set(raci()) == {"master", "cloud", "local", "buyer", "owner", "operator"}
    assert "Not a seat" in raci()["operator"]
    assert "refuse live pin" in week_one()
    ids = [item["id"] for item in cat["repositories"]]
    assert ids[:3] == ["repo.agent_gov", "repo.catalog", "repo.institute"]
    assert {"repo.finance", "repo.brief", "repo.review"} <= set(ids)


def test_pair_shares_lockfile_and_consume_ledger():
    pair = provision_pair("acme")
    local, cloud = pair["local"], pair["cloud"]
    assert isinstance(cloud, CloudMothership)
    assert local.host_mode == "local"
    assert cloud.host_mode == "cloud"
    assert local.lockfile.digest() == cloud.lockfile.digest()
    assert local.client.store is cloud.client.store
    out = local.run_and_apply(_journal(), seat_a="oid-1", seat_b="oid-2")
    assert out["record_type"] == "effect_applied"
    with pytest.raises(ConsumeReplay):
        cloud.run_and_apply(_journal(), seat_a="oid-1", seat_b="oid-2")


def test_delivery_system_snapshot_and_runbook():
    system = DeliverySystem()
    system.provision_pair("acme")
    snap = system.snapshot("acme")
    assert snap["live"] is False
    assert snap["shared_ledger"] is True
    assert snap["hosts"]["cloud"]["host_mode"] == "cloud"
    assert snap["hosts"]["local"]["host_mode"] == "local"
    assert snap["hosts"]["master"]["writes_client_sor"] is False
    runbook = system.runbook("acme")
    assert runbook["cloud"]
    assert "provision cloud + local pair on one ledger" in runbook["steps"]
    with pytest.raises(LivePinError):
        system.claim_live_pin()


def test_sold_l1_provisions_cloud_and_local():
    account = ClientAccount("acme")
    account.sell_l1()
    assert account.local is not None
    assert account.cloud is not None
    assert account.local.client.store is account.cloud.client.store
    snap = account.snapshot()
    assert snap["hosts"]["cloud"] == "cloud"


def test_public_delivery_is_sandbox():
    body = public_delivery()
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["hosts"] == ["master", "cloud", "local"]
    assert body["bd"]["no_inbox"] is True


def test_catalog_rejects_split_ledger():
    cat = load_catalog()
    broken = copy.deepcopy(cat)
    broken["motherships"]["shared_ledger"] = False
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(broken)
    assert exc.value.reason_code == "CATALOG_DELIVERY"
    hosts = copy.deepcopy(cat)
    hosts["motherships"]["hosts"] = ["master", "cloud"]
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(hosts)
    assert exc2.value.reason_code == "CATALOG_DELIVERY"
    master = copy.deepcopy(cat)
    master["motherships"]["master"]["writes_client_sor"] = True
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(master)
    assert exc3.value.reason_code == "CATALOG_DELIVERY"
    live = copy.deepcopy(cat)
    live["motherships"]["cloud"]["live"] = True
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(live)
    assert exc4.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    pair = copy.deepcopy(cat)
    pair["delivery"]["shared_ledger"] = False
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(pair)
    assert exc5.value.reason_code == "CATALOG_DELIVERY"
    raci_missing = copy.deepcopy(cat)
    raci_missing["delivery"]["raci"] = {"master": "issues law"}
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(raci_missing)
    assert exc6.value.reason_code == "CATALOG_DELIVERY"
    repo = copy.deepcopy(cat)
    repo["repositories"][0]["sku"] = "L1"
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(repo)
    assert exc7.value.reason_code == "CATALOG_SKU"


def test_delivery_system_refuses_unknown_pair():
    from ainav.errors import ProvisionError

    with pytest.raises(ProvisionError) as exc:
        DeliverySystem().snapshot("missing-client")
    assert exc.value.reason_code == "DELIVERY"


def test_cli_motherships_and_raci(capsys):
    from ainav.__main__ import main

    assert main(["raci"]) == 0
    assert main(["delivery"]) == 0
    assert main(["motherships", "--client-id", "cli-pair"]) == 0
    out = capsys.readouterr().out
    assert "ConsumeReplay" in out or "cloud_replay" in out
    assert "shared_digest" in out
    assert "week_one" in out
