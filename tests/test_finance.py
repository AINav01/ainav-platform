from ainav.catalog import load_catalog
from ainav.finance import finance_markdown, model


def test_finance_is_catalog_list_not_revenue():
    body = model()
    assert body["recognized_revenue"] == 0
    assert body["signed_l1"] == 0
    assert body["named_customers"] == 0
    assert body["billing_provider"] is False
    assert body["live_pin_ok"] is False
    by_id = {row["id"]: row for row in body["scenarios"]}
    assert by_id["all_three"]["min"] == 88000
    assert by_id["all_three"]["max"] == 135000
    assert by_id["l1_padm"]["min"] == 68000
    assert by_id["three_l1_padm"]["min"] == 204000
    assert by_id["l1_plus_four_days"]["min"] == 42000
    assert by_id["l1_plus_two_desks"]["min"] == 40000
    assert by_id["l1_plus_two_desks"]["max"] == 60000
    assert by_id["all_three_plus_desks"]["min"] == 100000
    assert by_id["all_three_plus_desks"]["max"] == 155000
    assert by_id["l1_padm_oversight"]["min"] == 73000
    assert by_id["l1_padm_oversight"]["max"] == 108000
    assert by_id["l1_plus_cascade"]["min"] == 34000
    assert by_id["l1_plus_cascade"]["max"] == 50000
    assert by_id["l1_padm_second_record"]["min"] == 73000
    assert by_id["l1_padm_second_record"]["max"] == 108000
    assert by_id["l1_plus_off_switch"]["min"] == 34000
    assert by_id["l1_plus_off_switch"]["max"] == 50000
    assert by_id["l1_padm_board"]["min"] == 73000
    assert by_id["l1_padm_board"]["max"] == 108000
    assert by_id["l1_padm_internal_audit"]["min"] == 73000
    assert by_id["l1_padm_internal_audit"]["max"] == 108000
    assert by_id["l1_padm_ip_keep"]["min"] == 73000
    assert by_id["l1_padm_ip_keep"]["max"] == 108000
    md = finance_markdown()
    assert "Not recognized revenue" in md or "not recognized" in md.lower()
    assert "L1" in md


def test_expert_review_has_sixteen_upgrades():
    cat = load_catalog()
    upgrades = cat["expert_review"]["upgrades"]
    assert len(upgrades) == 16
    assert any(item.get("n") == 16 and item.get("done") is True for item in upgrades)
    assert all(item.get("marks_live_pin") is not True for item in upgrades)
    assert any(item["who"] == "owner" for item in upgrades)
    assert any(item["who"] == "tree" for item in upgrades)
