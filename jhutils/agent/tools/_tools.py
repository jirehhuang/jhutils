"""Available tools."""

from typing import TypeAlias

from atomic_agents import BaseTool

from ._add_shopping_items import AddShoppingItemsTool
from ._add_tasks import AddTasksTool
from ._respond import RespondTool

TOOLS = [AddTasksTool, AddShoppingItemsTool, RespondTool]
TOOL_NAMES = [tool.__qualname__ for tool in TOOLS]

AVAILABLE_MODES = {
    "default": ["AddTasksTool", "AddShoppingItemsTool", "RespondTool"],
    "shopping": ["AddShoppingItemsTool", "RespondTool"],
}

ToolList: TypeAlias = list[BaseTool]
