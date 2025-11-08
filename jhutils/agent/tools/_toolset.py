"""Toolset class for managing tools."""

import inspect
import os

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from atomic_agents.context import (
    BaseDynamicContextProvider,
)
from docstring_parser import parse

from jhutils._utils import _match_phrase

from ..._mealie import Mealie
from ..._obsidian import Obsidian
from ._tools import (
    AVAILABLE_MODES,
    TOOLS,
    ToolList,
    _get_default_system_prompt,
)


class Toolset:
    """Class for managing tools.

    Parameters
    ----------
    mode
        The mode to initialize the toolset with. Determines the available
        tools.
    kwargs
        Additional keyword arguments to pass to tool constructors.
    """

    def __init__(self, mode: str = "general", **kwargs):
        """Initialize the Toolset with a list of tools and tool arguments."""
        self._all_tools: ToolList = TOOLS.copy()
        self._kwargs = kwargs
        self.mode = mode  # Sets _available_tools and _system_prompt
        self._selected_tools: ToolList = self._available_tools
        self._system_prompt: str | None = None

    @classmethod
    def from_environ(cls, mode: str = "general", **kwargs) -> "Toolset":
        """Create a Toolset instance from environment variables."""
        if not isinstance(kwargs.get("mealie"), Mealie):
            kwargs["mealie"] = Mealie.from_environ()
        if not isinstance(kwargs.get("obsidian"), Obsidian):
            kwargs["obsidian"] = Obsidian.from_environ()
        return cls(mode=mode, **kwargs)

    @property
    def system_prompt(self):
        """Get the prompt for the toolset based on the mode."""
        return self._system_prompt or self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """Retrieve the system prompt based on the current mode.

        Attempts to retrieve the Obsidian object from the toolset kwargs.
        If successful and contains a non-empty prompts_path, attempts to read
        the prompt file for the current mode from the Obsidian vault. Falls
        back to the default system prompt if any step fails.
        """
        prompt = None

        obsidian = self.kwargs.get("obsidian", None)
        if isinstance(obsidian, Obsidian):
            prompts_path = obsidian.prompts_path

            if prompts_path:
                prompt_path = os.path.join(prompts_path, f"{self.mode}.md")
                prompt = obsidian.read_file(prompt_path).get("content", None)

        self._system_prompt = prompt or _get_default_system_prompt(self.mode)
        return self._system_prompt

    @property
    def kwargs(self):
        """Getter for all tool constructor arguments."""
        return self._kwargs

    @property
    def all_tools(self):
        """Getter for all tools."""
        return self._all_tools

    @property
    def available_tools(self):
        """Getter for the available tools.

        The available tools are determined by the current mode.
        """
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
        if available_tool_names is None:
            raise ValueError(
                f"Mode '{mode}' is not supported. "
                f"Available modes: {AVAILABLE_MODES.keys()}"
            )
        self._available_tools = [
            tool
            for tool in self.all_tools
            if tool.__qualname__ in available_tool_names
        ]
        self._mode = mode
        self._get_system_prompt()

    def match_mode(self, query: str) -> str | None:
        """Match query to available modes to identify and update mode.

        Convenience method to match a user query to available modes using
        ``_match_phrase``, and update the mode if a match is found.

        Parameters
        ----------
        query
            The query phrase to match against available modes.

        Returns
        -------
        str | None
            The matched mode name, or None if no match is found.
        """
        available_modes = list(AVAILABLE_MODES.keys())
        mode = _match_phrase(
            query, phrases=available_modes, min_score=85, as_index=False
        )

        if isinstance(mode, str) and mode in set(available_modes):
            self.mode = mode

        # Type checker does not infer that mode cannot be int
        return mode  # type: ignore[return-value]

    @property
    def all_tool_names(self) -> list[str]:
        """Get the names of all tools in the toolset."""
        return [tool.__qualname__ for tool in self.all_tools]

    @property
    def available_tool_names(self) -> list[str]:
        """Get the names of available tools in the toolset."""
        return [tool.__qualname__ for tool in self._available_tools]

    @property
    def selected_tool_names(self) -> list[str]:
        """Get the names of selected tools in the toolset."""
        return [tool.__qualname__ for tool in self._selected_tools]

    def get_tool(
        self,
        tool_name: str | None = None,
        tool_schema: BaseIOSchema | None = None,
    ) -> BaseTool:
        """Get a tool by its name, input schema, or input.

        Parameters
        ----------
        tool_name
            The name of the tool to retrieve.
        tool_schema
            The input schema of the tool to retrieve, or an instance of it.

        Returns
        -------
        BaseTool
            The tool class corresponding to the provided name or schema.
        """
        if not tool_name and not tool_schema:
            raise ValueError(
                'Either "tool_name" or "tool_schema" must be provided.'
            )
        for tool in self.all_tools:
            if tool_name is not None and tool.__qualname__ == tool_name:
                return tool
            if tool_schema is not None and (
                isinstance(tool_schema, tool.input_schema)
                or tool.input_schema == tool_schema
            ):
                return tool

        if tool_name is None:
            if hasattr(tool_schema, "__name__"):
                tool_name = tool_schema.__name__  # type: ignore
            else:
                tool_name = tool_schema.__class__.__name__
        raise ValueError(
            f'Tool with name "{tool_name}" not found in the toolset.'
        )

    def get_kwargs(
        self,
        tool_name: str | None = None,
        tool_schema: BaseIOSchema | None = None,
    ) -> dict:
        """Retrieve the keyword arguments for a tool.

        Filtered to only those that are named arguments in the tool's __init__
        method.
        """
        tool = self.get_tool(tool_name=tool_name, tool_schema=tool_schema)
        sig = inspect.signature(tool.__init__)
        valid_args = [
            p.name
            for p in sig.parameters.values()
            if p.name not in {"self", "config"}
        ]
        return {k: v for k, v in self._kwargs.items() if k in valid_args}

    def initialize_tool(
        self,
        tool_name: str | None = None,
        tool_schema: BaseIOSchema | None = None,
    ) -> BaseTool:
        """Instantiate a tool by its name or schema."""
        tool = self.get_tool(tool_name=tool_name, tool_schema=tool_schema)
        tool_config = tool.config_cls()
        tool_kwargs = self.get_kwargs(
            tool_name=tool_name, tool_schema=tool_schema
        )
        return tool(config=tool_config, **tool_kwargs)

    def get_input_schema(
        self,
        tool_name: str | None = None,
        tool_schema: BaseIOSchema | None = None,
    ) -> BaseIOSchema:
        """Get the input schema constructor for a tool."""
        return self.get_tool(
            tool_name=tool_name, tool_schema=tool_schema
        ).input_schema  # type: ignore

    def get_output_schema(
        self,
        tool_name: str | None = None,
        tool_schema: BaseIOSchema | None = None,
    ) -> BaseIOSchema:
        """Get the output schema constructor for a tool."""
        return self.get_tool(
            tool_name=tool_name, tool_schema=tool_schema
        ).output_schema  # type: ignore

    def get_config(
        self,
        tool_name: str | None = None,
        tool_schema: BaseIOSchema | None = None,
    ) -> BaseToolConfig:
        """Get the config constructor for a tool."""
        return self.get_tool(
            tool_name=tool_name, tool_schema=tool_schema
        ).config_cls  # type: ignore

    def reset_selected_tools(self):
        """Reset the selected tools to available tools.

        To avoid carrying over states between runs.
        """
        self._selected_tools = self._available_tools


# pylint: disable=too-few-public-methods
class AvailableToolsProvider(BaseDynamicContextProvider):
    """Dynamic context provider for Available Tool(s)."""

    def __init__(self, toolset: Toolset, title: str = "Available Tool(s)"):
        super().__init__(title)
        self._toolset = toolset

    def get_info(self) -> str:
        """Get information."""
        return "\n".join(
            [
                (
                    f"- {tool.__qualname__}: "
                    f"{parse(tool.__doc__).short_description}"  # type: ignore
                )
                for tool in self._toolset.available_tools
            ]
        )


# pylint: disable=too-few-public-methods
class SelectedToolsProvider(BaseDynamicContextProvider):
    """Dynamic context provider for Selected Tool(s)."""

    def __init__(self, toolset: Toolset, title: str = "Selected Tool(s)"):
        super().__init__(title)
        self._title = title
        self._toolset = toolset

    def get_info(self) -> str:
        """Get information."""
        return ", ".join(
            [f"- {tool.__qualname__}" for tool in self._toolset.selected_tools]
        )
