"""Schemas that are composed dynamically based on the tools available."""

from typing import Literal, Type, Union, cast

from atomic_agents import BaseIOSchema, BaseTool
from pydantic import Field, model_validator

from ._toolset import Toolset


# pylint: disable=invalid-name
def MakeChainToolOutputSchema(  # noqa: N802
    toolset: Toolset,
) -> Type[BaseIOSchema]:
    """Construct a ChainToolOutputSchema for a given set of tools.

    Parameters
    ----------
    toolset
        Toolset whose tools' input schemas will be unioned.

    Returns
    -------
    type[BaseIOSchema]
        A dynamically created Pydantic schema class where `called_tool_input`
        is a Union of the tools' input schemas.
    """
    tool_input_schemas = tuple(
        cast(type[BaseTool], tool).input_schema
        for tool in toolset.selected_tools
    )
    tool_input_type = (
        (Union[tool_input_schemas[0], None] if tool_input_schemas else None)
        if len(tool_input_schemas) == 1
        else Union[(*tool_input_schemas, None)]
    )

    tool_name_literals = tuple(
        Literal[tool_name] for tool_name in toolset.available_tool_names
    )
    next_tool_type = (
        (Union[tool_name_literals[0], None] if tool_name_literals else None)
        if len(tool_name_literals) == 1
        else Union[(*tool_name_literals, None)]
    )

    @model_validator(mode="after")
    def _validate(self):
        called_tool_input = getattr(self, "called_tool_input", None)
        remainder = getattr(self, "remainder", None)
        next_tool = getattr(self, "next_tool", None)

        if remainder != "" and next_tool is None:
            raise ValueError(
                "If `remainder` is not empty, `next_tool` must not be `None`."
            )

        if remainder == "" and next_tool is not None:
            raise ValueError(
                "If `remainder` is empty, `next_tool` must be `None`."
            )

        if isinstance(
            called_tool_input, toolset.get_input_schema("RespondTool")
        ) and (remainder != "" or next_tool is not None):
            raise ValueError(
                "If `called_tool_input` calls `RespondTool`, `REMAINDER` must "
                "be empty and `next_tool` must be `None`."
            )

        return self

    annotations = {
        "called_tool_input": tool_input_type,
        "remainder": str,
        "next_tool": next_tool_type,
    }
    class_dict = {
        "__annotations__": annotations,
        "called_tool_input": Field(
            ...,
            description=(
                "The input parameters used to call one of the Selected "
                "Tool(s)."
            ),
        ),
        "remainder": Field(
            ...,
            description=(
                "ALL remaining text from the user query that has NOT been "
                "addressed by the called tool in `called_tool_input`. "
                "The format should be maintained as a text query with "
                "instructions as if provided by the user."
            ),
        ),
        "next_tool": Field(
            ...,
            description=(
                "The next tool to select and call in the next iteration to "
                "address some or all of the remainder of the user query in "
                "`remainder`. "
                "Can be one of any of the Available Tool(s)."
            ),
        ),
        "__doc__": (
            "Output schema for calling a tool and chaining to the next tool."
            "\n\n"
            "Some specific scenarios include:\n"
            "- *Skip tool call and select next tool:* "
            "If (a) no tool from the Selected Tool(s) is applicable to "
            "address the user query, AND "
            "if (b) a tool from the Available Tool(s) is applicable, then "
            "*skip* with `called_tool_input=None` and select the next tool "
            "with `next_tool`.\n"
            "- *Trigger exit with explanation*: "
            "If no tool from the Available Tool(s) is applicable to "
            "specifically address the user query, use `RespondTool` to "
            "respond to the remainder.\n"
            "- *Exit with successful completion:* "
            "If `remainder=''` (is blank), then `next_tool` MUST be `None` to "
            "signal successful completion and exit.\n"
        ),
        "_validate": _validate,
    }
    ChainToolOutputSchema = type(  # noqa: N806
        "ChainToolOutputSchema", (BaseIOSchema,), class_dict
    )
    return ChainToolOutputSchema


# pylint: disable=invalid-name
def MakeParseQueryOutputSchema(  # noqa: N802
    toolset: Toolset,
) -> Type[BaseIOSchema]:  # pragma: no cover
    """Construct a ParseQueryOutputSchema for a given set of tools.

    Parameters
    ----------
    toolset
        Toolset whose tools' names will be used to define the `queries` field.

    Returns
    -------
    type[BaseIOSchema]
        A dynamically created Pydantic schema class where `queries` is a dict
        with keys as the tools' names and values as the corresponding queries.
    """
    tool_name_literals = tuple(
        Literal[tool_name] for tool_name in toolset.available_tool_names
    )
    queries_type = (
        dict[tool_name_literals[0], str]  # type: ignore
        if len(tool_name_literals) == 1
        else (
            dict[Union[*tool_name_literals], str]  # type: ignore
            if len(tool_name_literals) > 1
            else dict[str, str]
        )
    )

    annotations = {
        "queries": queries_type,
    }
    class_dict = {
        "__annotations__": annotations,
        "queries": Field(
            ...,
            description=(
                "Parsed queries organized by relevant tool. "
                "If no query is applicable for a tool, omit that tool from "
                "the dictionary."
            ),
        ),
        "__doc__": (
            "Output schema for parsing a user query into individual queries "
            "organized by relevant tool."
        ),
    }
    ParseQueryOutputSchema = type(  # noqa: N806
        "ParseQueryOutputSchema", (BaseIOSchema,), class_dict
    )
    raise NotImplementedError
    # pylint: disable=unreachable
    return ParseQueryOutputSchema  # pragma: no cover
