"""Configure shared test fixtures."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from jhutils.mealie import Mealie

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@pytest.fixture(name="mealie_api_url", scope="session")
def fixture_mealie_api_url():
    """Return Mealie API URL."""
    return os.getenv("MEALIE_API_URL", "")


@pytest.fixture(name="mealie_api_key", scope="session")
def fixture_mealie_api_key():
    """Return Mealie API key."""
    return os.getenv("MEALIE_API_KEY", "")


@pytest.fixture(name="mealie_shopping_list_id", scope="session")
def fixture_mealie_shopping_list_id():
    """Return Mealie shopping list ID."""
    return os.getenv("MEALIE_SHOPPING_LIST_ID", "")


@pytest.fixture(name="mealie", scope="session")
def fixture_mealie(mealie_api_url, mealie_api_key):
    """Return Mealie client object."""
    return Mealie(
        api_url=mealie_api_url,
        api_key=mealie_api_key,
    )
