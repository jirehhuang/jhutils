"""Available tools."""

import textwrap
from typing import TypeAlias

from atomic_agents import BaseTool

from ._add_shopping_items import AddShoppingItemsTool
from ._add_tasks import AddTasksTool
from ._read_recipe import ReadRecipeTool
from ._respond import RespondTool

TOOLS = [AddTasksTool, AddShoppingItemsTool, ReadRecipeTool, RespondTool]
TOOL_NAMES = [tool.__qualname__ for tool in TOOLS]

AVAILABLE_MODES = {
    "general": ["AddTasksTool", "AddShoppingItemsTool", "RespondTool"],
    "shopping": ["AddShoppingItemsTool", "RespondTool"],
    "cooking": ["AddShoppingItemsTool", "ReadRecipeTool"],
    "review": [],
    "theology": [],
    "testing": [],
}

ToolList: TypeAlias = list[BaseTool]


def _get_default_system_prompt(mode: str) -> str:
    """Get the default system prompt for a given mode.

    Get the default system prompt for a given mode for the manager agent.
    See Obsidian.prompts_path docstring for details.

    Parameters
    ----------
    mode
        The mode to get the system prompt for.

    Returns
    -------
    str
        The default system prompt for the given mode.
    """
    return textwrap.dedent(
        f"""
        You are a helpful {mode} assistant.
        Respond as concisely and completely as possible.
        """
    )
