"""Test the agent tools module."""

import pytest
from pydantic import ValidationError

from jhutils.agents.tools import (
    AddShoppingItemsTool,
    AddTasksTool,
    MakeChainToolOutputSchema,
    RespondTool,
)

REMAINDER = "Unaddressed part of the user query."


@pytest.fixture(name="add_tasks_tool", scope="module")
def fixture_add_tasks_tool():
    """Return an instance of AddTasksTool."""
    return AddTasksTool()


@pytest.fixture(name="add_tasks_input", scope="module")
def fixture_add_tasks_input(add_tasks_tool):
    """Return an instance of the AddTasksTool input schema."""
    return add_tasks_tool.input_schema(tasks=["Test the schema"])


def test_add_shopping_items_tool():
    """Test that running the AddShoppingItemsTool returns the expected
    result."""
    items = ["milk", "eggs", "bread"]
    expected_result = {
        "result": f"Successfully added item(s): {', '.join(items)}"
    }
    tool = AddShoppingItemsTool()
    input_data = tool.input_schema(items=items)
    result = tool.run(input_data)
    assert result.model_dump() == expected_result


def test_add_tasks_tool():
    """Test that running the AddTasksTool returns the expected result."""
    tasks = ["Do laundry", "Buy groceries", "Clean room"]
    expected_result = {
        "result": f"Successfully added task(s): {', '.join(tasks)}"
    }
    tool = AddTasksTool()
    input_data = tool.input_schema(tasks=tasks)
    result = tool.run(input_data)
    assert result.model_dump() == expected_result


@pytest.mark.parametrize(
    "response",
    [
        "All tasks have been added successfully.",
        "Added milk, eggs, and bread to the shopping list.",
    ],
)
def test_respond_tool(response):
    """Test that running the RespondTool returns the expected result."""
    expected_result = {"response": response}
    tool = RespondTool()
    input_data = tool.input_schema(response=response)
    result = tool.run(input_data)
    assert result.model_dump() == expected_result


def test_schema_error_if_invalid_tool(add_tasks_input):
    """Test that a ValidationError is raised if an invalid tool is provided."""
    with pytest.raises(ValidationError):
        MakeChainToolOutputSchema()(
            tool_input=add_tasks_input,
            remainder=REMAINDER,
            next_tool="InvalidTool",
        )


def test_schema_none_valid_tool(add_tasks_input):
    """Test that None is a valid value for the next_tool field."""
    schema = MakeChainToolOutputSchema()(
        tool_input=add_tasks_input,
        remainder=REMAINDER,
        next_tool=None,
    )
    assert schema.next_tool is None
