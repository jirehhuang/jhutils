"""Configure shared test fixtures."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from jhutils.mealie import Mealie

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@pytest.fixture(name="mealie_shopping_list_id", scope="session")
def fixture_mealie_shopping_list_id():
    """Return Mealie shopping list ID."""
    return os.getenv("MEALIE_SHOPPING_LIST_ID", "")


@pytest.fixture(name="mealie", scope="function")
def fixture_mealie():
    """Return Mealie client object."""
    return Mealie(
        api_url=os.getenv("MEALIE_API_URL", ""),
        api_key=os.getenv("MEALIE_API_KEY", ""),
    )
