"""Configure shared test fixtures."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from jhutils import Mealie, Obsidian
from jhutils.agent._assistant import make_openai_client_from_environ
from jhutils.agent.tools import Toolset
from jhutils.agent.tools._add_tasks import AddTasksTool

env_path = Path(__file__).resolve().parents[1]
dotenv_file = (
    env_path / ".env.test"
    if (env_path / ".env.test").exists()
    else env_path / ".env"
)
load_dotenv(dotenv_file, override=True)

TEST_RECIPE_NAME = "Complex Recipe"


def clear_shopping_list():
    """Clear all items from the Mealie shopping list."""
    mealie = Mealie.from_environ()
    items = mealie.load_shopping_items(force=True)
    mealie.delete_shopping_items([item["id"] for item in items])


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
def fixture_toolset(obsidian, mealie):
    """Return the dummy instance of Toolset that does not contain necessary
    clients for full execution of certain tools."""
    return Toolset(obsidian=obsidian, mealie=mealie)


@pytest.fixture(name="add_tasks_tool", scope="module")
def fixture_add_tasks_tool(obsidian):
    """Return an instance of AddTasksTool."""
    return AddTasksTool(obsidian=obsidian)


@pytest.fixture(scope="function", autouse=True)
def clear_shopping_list_before_test(request):
    """Clear the Mealie shopping list before tests marked with
    'clear_shopping_list'."""
    if request.node.get_closest_marker("clear_shopping_list"):
        clear_shopping_list()


@pytest.fixture(scope="session", autouse=True)
def mealie_startup():
    """Perform startup action for Mealie client."""
    clear_shopping_list()
