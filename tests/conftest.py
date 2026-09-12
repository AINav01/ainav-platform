from __future__ import annotations

import pytest

from agent_gov import reset_default_store

# Cursor may inject notify/kit/sentinel names. Gold asserts unbound/missing_env
# when a test does not set them. Host secrets must not change those assertions.
MICROSOFT_BIND_ENV = (
    "TEAMS_ENTERPRISE_TEAM_ID",
    "TEAMS_ENTERPRISE_CHANNEL_ID",
    "TEAMS_PREMIUM_TEAM_ID",
    "TEAMS_PREMIUM_CHANNEL_ID",
    "SHAREPOINT_SITE_ID",
    "AZURE_SENTINEL_WORKSPACE_ID",
)


@pytest.fixture(autouse=True)
def _isolated_default_store():
    reset_default_store()
    yield
    reset_default_store()


@pytest.fixture(autouse=True)
def _isolate_microsoft_bind_env(monkeypatch):
    for name in MICROSOFT_BIND_ENV:
        monkeypatch.delenv(name, raising=False)
