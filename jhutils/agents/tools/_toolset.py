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
AvailableModes = Literal["default", "shopping", None]
ToolList: TypeAlias = list[BaseTool]

AVAILABLE_MODES = list(get_args(AvailableModes))


class Toolset:
    """Class for managing tools."""

    _all_tools: ToolList = TOOLS

    def __init__(self, mode: AvailableModes = "default"):
        """Initialize the Toolset with a list of tools."""
        self.mode = mode  # This sets _available_tools
        self._selected_tools: ToolList = self._all_tools

    @property
    def all_tools(self):
        """Getter for all tools."""
        return self._all_tools

    @property
    def available_tools(self):
        """Getter for the available tools, determined by the mode."""
        return self._available_tools

    @property
    def selected_tools(self):
        """Getter for the selected tools."""
        return self._selected_tools

    @selected_tools.setter
    def selected_tools(self, tools: ToolList):
        """Setter for the selected tools."""
        for tool in tools:
            if tool not in self._available_tools:
                raise ValueError(
                    f"{tool.__qualname__} is not available "
                    f"in mode {self.mode}."
                )
        self._selected_tools = tools

    @property
    def mode(self):
        """Getter for the mode."""
        return self._mode

    @mode.setter
    def mode(self, mode: AvailableModes):
        """Update the mode and the corresponding active tools."""
        if mode not in AVAILABLE_MODES:
            raise ValueError(
                f"Mode '{mode}' is not supported. "
                f"Available modes: {AVAILABLE_MODES}"
            )
        available_tool_names = (
            SHOPPING_TOOL_NAMES if mode == "shopping" else DEFAULT_TOOL_NAMES
        )
        self._available_tools = [
            tool
            for tool in self._all_tools
            if tool.__qualname__ in available_tool_names
        ]
        self._mode = mode

    @property
    def all_tool_names(self) -> list[AvailableTools]:
        """Get the names of all tools in the toolset."""
        return [tool.__qualname__ for tool in self._all_tools]

    @property
    def available_tool_names(self) -> list[AvailableTools]:
        """Get the names of available tools in the toolset."""
        return [tool.__qualname__ for tool in self._available_tools]

    @property
    def selected_tool_names(self) -> list[AvailableTools]:
        """Get the names of selected tools in the toolset."""
        return [tool.__qualname__ for tool in self._selected_tools]

    def get_tool(self, tool_name: AvailableTools) -> BaseTool:
        """Get a tool by its name."""
        for tool in self._all_tools:
            if tool.__qualname__ == tool_name:
                return tool
        raise ValueError(
            f"Tool with name '{tool_name}' not found in the toolset."
        )

    def get_input_schema(self, tool_name: AvailableTools) -> BaseIOSchema:
        """Get the input schema constructor for a tool by its name."""
        return self.get_tool(tool_name).input_schema

    def get_output_schema(self, tool_name: AvailableTools) -> BaseIOSchema:
        """Get the output schema constructor for a tool by its name."""
        return self.get_tool(tool_name).output_schema

    def get_config(self, tool_name: AvailableTools) -> BaseToolConfig:
        """Get the config constructor for a tool by its name."""
        return self.get_tool(tool_name).config_cls


# Static instance of Toolset
_toolset = Toolset()
