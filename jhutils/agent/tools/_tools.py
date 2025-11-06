"""Available tools."""

import textwrap
from typing import TypeAlias

from atomic_agents import BaseTool

from ._add_shopping_items import AddShoppingItemsTool
from ._add_tasks import AddTasksTool
from ._respond import RespondTool

TOOLS = [AddTasksTool, AddShoppingItemsTool, RespondTool]
TOOL_NAMES = [tool.__qualname__ for tool in TOOLS]

AVAILABLE_MODES = {
    "general": ["AddTasksTool", "AddShoppingItemsTool", "RespondTool"],
    "shopping": ["AddShoppingItemsTool", "RespondTool"],
}

# System prompts for manager agent. See Obsidian.prompts_path docstring.
SYSTEM_PROMPTS = {
    "general": textwrap.dedent(
        """
        You are a helpful general assistant.
        Respond as concisely and completely as possible.
        """
    ),
    "shopping": textwrap.dedent(
        """
        You are a helpful shopping assistant.
        Respond as concisely and completely as possible.
        """
    ),
}

ToolList: TypeAlias = list[BaseTool]
