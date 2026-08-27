from __future__ import annotations

import pytest

from agent_gov import reset_default_store


@pytest.fixture(autouse=True)
def _isolated_default_store():
    reset_default_store()
    yield
    reset_default_store()
