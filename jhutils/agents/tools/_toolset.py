"""Toolset class for managing tools."""

from typing import Literal, TypeAlias, get_args

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig

from ._add_shopping_items import AddShoppingItemsTool
from ._add_tasks import AddTasksTool
from ._respond import RespondTool

TOOLS = [AddShoppingItemsTool, AddTasksTool, RespondTool]

TOOL_NAMES = [tool.__qualname__ for tool in TOOLS]
DEFAULT_TOOL_NAMES = ["AddShoppingItemsTool", "AddTasksTool", "RespondTool"]
SHOPPING_TOOL_NAMES = ["AddShoppingItemsTool"]

AvailableTools = Literal["AddShoppingItemsTool", "AddTasksTool", "RespondTool"]
AvailableModes = Literal["default", "shopping"]
ToolList: TypeAlias = list[BaseTool]

AVAILABLE_MODES = list(get_args(AvailableModes))


class Toolset:
    """Class for managing tools."""

    _all_tools: ToolList = TOOLS

    def __init__(self, mode: AvailableModes = "default"):
        """Initialize the Toolset with a list of tools."""
        self.mode = mode

    @property
    def all_tools(self):
        """Getter for all tools."""
        return self._all_tools

    @property
    def tools(self):
        """Getter and setter for the tools."""
        return self._tools

    @tools.setter
    def tools(self, tools: ToolList):
        self._tools = tools

    @property
    def mode(self):
        """Getter and setter for the mode."""
        return self._mode

    @mode.setter
    def mode(self, mode: AvailableModes):
        """Update the mode and the corresponding active tools."""
        self._mode = mode
        if mode == "shopping":
            self._tools = [
                tool
                for tool in self._tools
                if tool.__qualname__ in SHOPPING_TOOL_NAMES
            ]
        else:  # mode == "default"
            self._tools = self._all_tools

    @property
    def tool_names(self) -> list[AvailableTools]:
        """Get the names of all tools in the toolset."""
        return [tool.__qualname__ for tool in self._tools]

    def get_tool(self, name: AvailableTools) -> BaseTool:
        """Get a tool by its name."""
        for tool in self._tools:
            if tool.__qualname__ == name:
                return tool
        raise ValueError(f"Tool with name {name} not found in the toolset.")

    def get_input_schema(self, name: AvailableTools) -> BaseIOSchema:
        """Get the input schema constructor for a tool by its name."""
        return self.get_tool(name).input_schema

    def get_output_schema(self, name: AvailableTools) -> BaseIOSchema:
        """Get the output schema constructor for a tool by its name."""
        return self.get_tool(name).output_schema

    def get_config(self, name: AvailableTools) -> BaseToolConfig:
        """Get the config constructor for a tool by its name."""
        return self.get_tool(name).config_cls


toolset = Toolset()
