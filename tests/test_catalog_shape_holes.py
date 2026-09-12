from __future__ import annotations

import json

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog


def _set_path(root, path, value):
    cursor = root
    for step in path[:-1]:
        cursor = cursor[step]
    cursor[path[-1]] = value


HOLES = [
    (("microsoft_stack",), None),
    (("microsoft_stack",), "x"),
    (("microsoft_stack", "edge"), None),
    (("microsoft_stack", "edge"), "x"),
    (("microsoft_stack", "edge", "quality"), None),
    (("microsoft_stack", "edge", "quality"), "x"),
    (("microsoft_stack", "edge", "quality", "host_freshness"), "x"),
    (("microsoft_stack", "edge", "quality", "owner_ssl"), "x"),
    (("microsoft_stack", "edge", "quality", "owner_ssl", "automatic"), False),
    (("microsoft_stack", "edge", "quality", "owner_ssl", "visitor_cert_is_not_proof"), False),
    (("microsoft_stack", "edge", "quality", "owner_recorded"), []),
    (("microsoft_stack", "edge", "quality", "verified"), ["tls"]),
    (("microsoft_stack", "walk"), None),
    (("microsoft_stack", "walk"), "x"),
    (("microsoft_stack", "graph"), "x"),
    (("microsoft_stack", "graph", "remove_before_grant"), []),
    (("microsoft_stack", "graph", "four_reads"), []),
    (("microsoft_stack", "graph", "owner_recorded"), []),
    (("investor",), None),
    (("investor",), "x"),
    (("investor", "executive_summary"), None),
    (("investor", "letter_body"), "Seat B mailbox recorded. Not stock. Not a priced round. chodnett@ainav.institute. Number two. Not all aspects. I trust. I will not ask."),
    (("investor", "control_plane"), "The control plane is independence from the vendor."),
    (("engineering",), None),
    (("engineering", "gold_ci"), None),
    (("engineering", "formal"), "x"),
    (("plane_interface",), None),
    (("plane_interface",), "x"),
    (("plane_interface", "gaps"), None),
    (("plane_interface", "gaps"), "x"),
    (("plane_interface", "proof_day_floor"), "x"),
    (("plane_interface", "pending_bind"), None),
    (("plane_interface", "examiner_walk"), None),
    (("plane_interface", "view_assignment", "entra_groups"), None),
    (("plane_interface", "motions"), None),
    (("plane_interface", "hostname_rehearsal"), None),
    (("plane_interface", "competitive"), None),
    (("plane_interface", "client_dashboard"), None),
    (("plane_interface", "floor", "must_have"), None),
    (("plane_interface", "floor", "first_glance"), None),
    (("plane_interface", "floor", "success"), None),
    (("plane_interface", "floor", "first_glance", "write_rail"), []),
    (("organization", "contacts", "invited", "seat_role"), "owner"),
    (("organization", "contacts", "invited", "inception_role"), "developer"),
    (("expert_review", "success"), None),
    (("expert_review", "success", "ciso", "does_not"), ["inbox"]),
    (("expert_review", "first_principles"), []),
    (("expert_review", "first_principles"), ["identify is not admit"]),
    (("expert_review", "working_well"), ["gold floor 95"]),
    (("plane_interface", "gaps", "in_tree_closed"), ["gold floor 95", "client offer"]),
]


@pytest.mark.parametrize("path,value", HOLES, ids=lambda item: ".".join(str(part) for part in item) if isinstance(item, tuple) else str(item))
def test_catalog_shape_holes_fail_closed(path, value):
    cat = json.loads(json.dumps(load_catalog()))
    _set_path(cat, path, value)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
