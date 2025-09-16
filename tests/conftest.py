"""Configure shared test fixtures."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from smolagents import LiteLLMModel

from jhutils import Mealie, Obsidian

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


@pytest.fixture(name="obsidian", scope="function")
def fixture_obsidian():
    """Return Obsidian client object."""
    return Obsidian(
        owner=os.getenv("OBSIDIAN_VAULT_OWNER", ""),
        repository=os.getenv("OBSIDIAN_VAULT_REPOSITORY", ""),
        branch=os.getenv("OBSIDIAN_VAULT_BRANCH", ""),
        github_token=os.getenv("OBSIDIAN_VAULT_TOKEN", ""),
    )


@pytest.fixture(name="llm", scope="module")
def fixture_llm():
    """Return fixture for the LLM instance."""
    return LiteLLMModel(
        model_id="openrouter/openai/gpt-4o-mini",
        token=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.0,
    )
