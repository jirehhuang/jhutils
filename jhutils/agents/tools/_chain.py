"""Schemas for chaining multiple tool calls together."""

from typing import Literal, Union

from atomic_agents import BaseIOSchema, BaseTool
from pydantic import Field

from ._add_shopping_items import AddShoppingItemsTool
from ._add_tasks import AddTasksTool
from ._respond import RespondTool

ALL_TOOLS = [AddShoppingItemsTool, AddTasksTool, RespondTool]
QUICK_TOOLS = ALL_TOOLS


class QueryInputSchema(BaseIOSchema):
    """Input schema providing the user's query."""

    query: str = Field(
        ...,
        description=("The user's input query to be analyzed and addressed."),
    )


# pylint: disable=invalid-name
def MakeChainToolOutputSchema(tools: list[BaseTool]):  # noqa: N802
    """Construct a ChainToolOutputSchema for a given set of tools.

    Parameters
    ----------
    tools
        List of tools whose input schemas will be unioned.

    Returns
    -------
    type[BaseIOSchema]
        A dynamically created Pydantic schema class where `tool_input`
        is a Union of the tools' input schemas.
    """
    tool_input_schemas = tuple(tool.input_schema for tool in tools)
    tool_input_type = (
        tool_input_schemas[0]
        if len(tool_input_schemas) == 1
        else Union[*tool_input_schemas]
    )

    tool_name_literals = tuple(
        Literal[str(tool.__qualname__)] for tool in tools
    )
    next_tool_type = (
        Union[(*tool_name_literals, None)]
        if len(tool_name_literals) > 1
        else (
            Union[tool_name_literals[0], None] if tool_name_literals else None
        )
    )

    annotations = {
        "tool_input": tool_input_type,
        "remainder": str,
        "next_tool": next_tool_type,
    }
    class_dict = {
        "__annotations__": annotations,
        "tool_input": Field(
            ..., description="The input parameters for the selected tool."
        ),
        "remainder": Field(
            ...,
            description=(
                "The remaining text from the user's request that has not been "
                "addressed by the tool. Maintain the format as instructions "
                "from the user."
            ),
        ),
        "next_tool": Field(
            ...,
            description=(
                "The next tool to call to address the remainder of the user's "
                "request. If there are no remaining tasks, this should be "
                "None."
            ),
        ),
        "__doc__": "Output schema for the tool chaining agent.",
    }
    ChainToolOutputSchema = type(  # noqa: N806
        "ChainToolOutputSchema", (BaseIOSchema,), class_dict
    )
    return ChainToolOutputSchema
