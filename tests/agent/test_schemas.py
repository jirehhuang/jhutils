"""Test the agents schemas module."""

import pytest
from pydantic import ValidationError

from jhutils.agent.tools import (
    MakeChainToolOutputSchema,
    RespondTool,
)

REMAINDER = "Unaddressed part of the user query."


@pytest.fixture(name="add_tasks_input", scope="module")
def fixture_add_tasks_input(add_tasks_tool):
    """Return an instance of the AddTasksTool input schema."""
    return add_tasks_tool.input_schema(tasks=["Test the schema"])


@pytest.fixture(name="chain_tool_output_schema", scope="function")
def fixture_chain_tool_output_schema(toolset):
    """Return an instance of MakeChainToolOutputSchema."""
    return MakeChainToolOutputSchema(toolset=toolset)


def test_chain_schema_error_if_invalid_tool(
    add_tasks_input, chain_tool_output_schema
):
    """Test that a ValidationError is raised if an invalid tool is provided."""
    with pytest.raises(ValidationError):
        chain_tool_output_schema(
            called_tool_input=add_tasks_input,
            remainder=REMAINDER,
            next_tool="InvalidTool",
        )


def test_chain_schema_none_valid_tool_input(chain_tool_output_schema):
    """Test that None is a valid value for the tool_input field."""
    schema = chain_tool_output_schema(
        called_tool_input=None,
        remainder=REMAINDER,
        next_tool="AddTasksTool",
    )
    assert schema.called_tool_input is None


def test_chain_schema_none_valid_next_tool(
    add_tasks_input, chain_tool_output_schema
):
    """Test that None is a valid value for the next_tool field."""
    schema = chain_tool_output_schema(
        called_tool_input=add_tasks_input,
        remainder="",
        next_tool=None,
    )
    assert schema.next_tool is None


def test_chain_schema_error_if_remainder_and_no_next_tool(
    add_tasks_input, chain_tool_output_schema
):
    """Test that a ValueError is raised if there is a remainder and next_tool
    is None."""
    msg = "If `remainder` is not empty, `next_tool` must not be `None`."
    with pytest.raises(ValueError, match=msg):
        chain_tool_output_schema(
            called_tool_input=add_tasks_input,
            remainder=REMAINDER,
            next_tool=None,
        )


def test_chain_schema_error_if_no_remainder_and_next_tool(
    add_tasks_input, chain_tool_output_schema
):
    """Test that a ValueError is raised if there is no remainder and next_tool
    is not None."""
    msg = "If `remainder` is empty, `next_tool` must be `None`."
    with pytest.raises(ValueError, match=msg):
        chain_tool_output_schema(
            called_tool_input=add_tasks_input,
            remainder="",
            next_tool="RespondTool",
        )


def test_chain_schema_error_if_respond_not_last_tool(chain_tool_output_schema):
    """Test that a ValueError is raised if called_tool_input is
    RespondInputSchema and next_tool is not None."""
    respond_input = RespondTool().input_schema(response="This is a response.")
    msg = (
        "If `called_tool_input` calls `RespondTool`, `REMAINDER` must "
        "be empty and `next_tool` must be `None`."
    )
    with pytest.raises(ValueError, match=msg):
        chain_tool_output_schema(
            called_tool_input=respond_input,
            remainder=REMAINDER,
            next_tool="AddTasksTool",
        )
