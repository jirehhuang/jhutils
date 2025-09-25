"""Toolset class for managing tools."""

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig

from ._tools import AVAILABLE_MODES, TOOLS, AvailableTools, ToolList


class Toolset:
    """Class for managing tools."""

    _all_tools: ToolList = TOOLS

    def __init__(self, mode: str = "default"):
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
                    f"{tool!s} is not available " f"in mode {self.mode}."
                )
        self._selected_tools = tools

    @property
    def mode(self):
        """Getter for the mode."""
        return self._mode

    @mode.setter
    def mode(self, mode: str):
        """Update the mode and the corresponding active tools."""
        available_tool_names = AVAILABLE_MODES.get(mode, None)
        if not available_tool_names:
            raise ValueError(
                f"Mode '{mode}' is not supported. "
                f"Available modes: {AVAILABLE_MODES.keys()}"
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

    def get_tool_by_schema(self, tool_schema: BaseIOSchema) -> BaseTool:
        """Get a tool by its input schema."""
        for tool in self._all_tools:
            if (
                isinstance(tool_schema, tool.input_schema)
                or tool.input_schema == tool_schema
            ):
                return tool
        raise ValueError(
            f"Tool with schema '{tool_schema}' not found in the toolset."
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


# Static instance of Toolset for internal use
_toolset = Toolset()
