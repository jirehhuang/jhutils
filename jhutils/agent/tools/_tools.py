"""Available tools."""

from typing import Literal, TypeAlias

from atomic_agents import BaseTool

from ._add_shopping_items import AddShoppingItemsTool
from ._add_tasks import AddTasksTool
from ._respond import RespondTool

TOOLS = [AddTasksTool, AddShoppingItemsTool, RespondTool]
TOOL_NAMES = [tool.__qualname__ for tool in TOOLS]

AvailableTools = Literal["AddTasksTool", "AddShoppingItemsTool", "RespondTool"]
ToolList: TypeAlias = list[BaseTool]

AVAILABLE_MODES = {
    "default": ["AddTasksTool", "AddShoppingItemsTool", "RespondTool"],
    "shopping": ["AddShoppingItemsTool", "RespondTool"],
}
