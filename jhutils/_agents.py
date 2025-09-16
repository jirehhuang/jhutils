"""Non-working version of agent with tool scheduling and testing support."""

import functools
import inspect
from typing import Any, Callable

import makefun
from smolagents import ToolCallingAgent
from smolagents import tool as tool_decorator

from jhutils._utils import _convert_docstring

# Shared instructions common to all managed agents
MANAGED_INSTRUCTIONS = """
Read the descriptions of the tools carefully and follow them exactly.

Do NOT perform duplicate actions that have already been done. Before executing
an action, check to see if it has already been done, whether in the same step
or in a previous step. If it has, do NOT perform it again. Assume you were
successful unless you receive an error or failure message.

After each step, check to see if the previous step addressed all remaining
parts of your assignment. If it did, you can stop and stop using the
`final_answer` tool.
"""

# Description for shopping agent to help manager agent decide when to use it
SHOPPING_DESCRIPTION = """
I manage the shopping list and shopping activities. Consult me if you need to:
1. Know what is on the shopping list
2. Add item(s) to the shopping list
"""

# Instructions specific to shopping agent
SHOPPING_INSTRUCTIONS = f"""
{MANAGED_INSTRUCTIONS}
"""

SCRIBE_DESCRIPTION = """
I manage tasks and notes. Consult me if you need to:
1. Add an independent task or action item
2. Write a note organizing information or thoughts
"""

SCRIBE_INSTRUCTIONS = f"""
{MANAGED_INSTRUCTIONS}
"""

# Instructions for manager agent to govern delegating to managed agents
MANAGER_INSTRUCTIONS = """
The provided text may contain dictation or transcription errors. Clean up
obvious errors, filler words, and repeated content.

Read the descriptions of the managed agents carefully and follow them exactly.

Make sure that ALL provided text is either delegated to a managed agent or
addressed by a tool. Do NOT leave text to the final answer unless you are
asked a specific question, such as "What is on my shopping list?".

The `final_answer` tool should ONLY be used for responding to the user in a
concise way. Ask clarifying questions if needed. Do NOT include a complete
summary of all actions taken.
"""


QUERY = (
    "I need to pick up milk and eggs. "
    "I should call John tomorrow. "
    "Also, remind me about the meeting next week. "
    "My wife's favorite food is sushi. "
    "I wonder if she likes KBBQ more or Fogo de Chao. "
)


class ToolSchedulingAgent(ToolCallingAgent):
    """Agent with extended support for scheduling and testing tool calls."""

    def __init__(
        self,
        *args: Any,
        tools: list,
        mock_registry: dict[str, Callable] | None = None,
        **kwargs: Any,
    ):
        self._tools = tools
        self._actions: list[dict[str, Any]] = []
        self._prepared_tools = [self._prepare_tool(tool) for tool in tools]
        self._mock_registry = mock_registry or {}
        super().__init__(*args, tools=self._prepared_tools, **kwargs)

    def _prepare_tool(self, tool: Callable):
        """Prepare a tool for use by the agent.

        This involves inspecting the tool's signature and docstring, and
        wrapping it to add action logging, deferred execution, and mock support
        for testing.
        """
        doc = tool.__doc__ = _convert_docstring(inspect.getdoc(tool) or "")
        has_returns = "Returns" in doc
        sig = inspect.signature(tool)

        if has_returns:
            return_annotation = (
                sig.return_annotation
                if sig.return_annotation is not inspect.Signature.empty
                else Any
            )
        else:
            return_annotation = None

        # Wrap body with mock support
        def wrapper_body(*args, **kwargs):
            self._add_action(tool, args, kwargs, executed=has_returns)

            # If a mock exists, use it instead of real tool
            if tool.__name__ in self._mock_registry:
                mock_tool = self._mock_registry[tool.__name__]

                # Ensure mock_tool is callable
                if not callable(mock_tool):
                    raise TypeError(
                        f"Mock tool '{tool.__name__}' is not callable."
                    )

                # Ensure return type matches the tool's signature
                mock_return_annotation = inspect.signature(
                    mock_tool
                ).return_annotation
                if mock_return_annotation is not return_annotation:
                    raise TypeError(
                        f"Return type of mock tool for '{tool.__name__}' "
                        f"({mock_return_annotation}) does not match "
                        f"the tool's return type ({return_annotation})."
                    )

                return mock_tool(*args, **kwargs)

            # If the tool has a return value, execute it immediately
            if has_returns:
                return tool(*args, **kwargs)
            return None

        wrapper = makefun.create_function(
            sig.replace(return_annotation=return_annotation),
            wrapper_body,
            doc=doc,
            func_name=tool.__name__,
        )
        functools.update_wrapper(wrapper, tool)

        return tool_decorator(wrapper)

    def _add_action(
        self,
        tool: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        executed: bool = False,
    ):
        """Add an action to the queue."""
        self._actions.append(
            {
                "tool": tool,
                "args": args,
                "kwargs": kwargs,
                "executed": executed,
            }
        )

    def _run_actions(self) -> None:
        """Run all queued actions."""
        # Batch functions if in batch registry
        for action in self._actions:
            _ = action["tool"](*action["args"], **action["kwargs"])
        self._actions.clear()
