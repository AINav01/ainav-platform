from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog

REFUSE_TRUE = (
    "sku",
    "live",
    "live_pin_ok",
    "certified",
    "mandated",
    "cms",
    "launch",
    "assignment_live",
    "graph_write_claimed",
    "ssl_full_claimed",
    "apex_is_institute",
    "ninth_complement",
    "crypto_associated",
    "marks_live_pin",
    "from_this_plane",
    "is_admit_plane",
    "second_remote_plane",
    "vpn_sku",
    "forecast",
    "real_time_claimed",
    "all_wired_claimed",
    "claimed",
    "seventeen_a4",
    "worm",
)


def _paths(obj, prefix=()):
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = prefix + (key,)
            if key in REFUSE_TRUE and value is False:
                yield path
            yield from _paths(value, path)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            yield from _paths(item, prefix + (index,))


def _set_path(root, path, value):
    cursor = root
    for step in path[:-1]:
        cursor = cursor[step]
    cursor[path[-1]] = value


def _refuse_paths():
    cat = load_catalog()
    return [path for path in _paths(cat) if path[-1] in REFUSE_TRUE]


@pytest.mark.parametrize("path", _refuse_paths())
def test_catalog_refuses_true_on_honest_false_flags(path):
    cat = copy.deepcopy(load_catalog())
    _set_path(cat, path, True)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)
