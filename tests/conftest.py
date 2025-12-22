"""Configure shared test fixtures."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from jhutils import Mealie, Obsidian
from jhutils.agent._assistant import make_openai_client_from_environ
from jhutils.agent.tools import Toolset

env_path = Path(__file__).resolve().parents[1]
dotenv_file = (
    env_path / ".env.test"
    if (env_path / ".env.test").exists()
    else env_path / ".env"
)
load_dotenv(dotenv_file, override=True)

TEST_RECIPE_NAME = "Complex Recipe"


@pytest.fixture(name="mealie_shopping_list_id", scope="session")
def fixture_mealie_shopping_list_id():
    """Return Mealie shopping list ID."""
    return os.getenv("MEALIE_SHOPPING_LIST_ID", "")


@pytest.fixture(name="mealie", scope="function")
def fixture_mealie():
    """Return Mealie client object."""
    return Mealie.from_environ()


@pytest.fixture(name="obsidian", scope="module")
def fixture_obsidian():
    """Return Obsidian client object."""
    return Obsidian.from_environ()


@pytest.fixture(name="openai_client", scope="function")
def fixture_openai_client():
    """Return OpenAI client object."""
    return make_openai_client_from_environ()


@pytest.fixture(name="toolset", scope="function")
def fixture_toolset():
    """Return the dummy instance of Toolset that does not contain necessary
    clients for full execution of certain tools."""
    # This is useful for testing tool calling behavior without making actual
    # API calls during testing.
    return Toolset(obsidian=None, mealie=None)
