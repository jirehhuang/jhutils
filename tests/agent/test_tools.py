"""Test the agent tools module."""

import pytest

from jhutils.agent.tools import (
    AddShoppingItemsTool,
    ReadRecipeTool,
    RespondTool,
)
from tests.conftest import TEST_RECIPE_NAME


@pytest.fixture(name="add_shopping_items_tool", scope="function")
def fixture_add_shopping_items_tool(mealie):
    """Return an instance of AddShoppingItemsTool."""
    return AddShoppingItemsTool(mealie=mealie)


def test_add_shopping_items_tool(add_shopping_items_tool):
    """Test that running the AddShoppingItemsTool returns the expected
    result."""
    items = ["milk", "bread"]
    expected_result = {
        "result": f"Added {len(items)} items: {', '.join(items)}"
    }
    input_data = add_shopping_items_tool.input_schema(items=items)
    result = add_shopping_items_tool.run(input_data)
    assert result.model_dump() == expected_result


def test_add_shopping_items_tool_parsed(add_shopping_items_tool):
    """Test that running the AddShoppingItemsTool correctly parses a food."""
    items = ["3 lb butternut squash, from Costco"]
    expected_result = {"result": "Added 1 item: butternut squash"}
    input_data = add_shopping_items_tool.input_schema(items=items)
    result = add_shopping_items_tool.run(input_data)
    assert result.model_dump() == expected_result


def test_read_recipe_tool(mealie):
    """Test that running the ReadRecipe correctly retrieves recipe."""
    expected_start = "# Complex Recipe\n\nThis recipe has a description."
    tool = ReadRecipeTool(mealie=mealie)
    input_data = tool.input_schema(recipe_name=TEST_RECIPE_NAME)
    result = tool.run(input_data)
    assert result.model_dump()["result"].startswith(expected_start)


def test_add_tasks_tool(add_tasks_tool):
    """Test that running the AddTasksTool returns the expected result."""
    tasks = ["Do laundry", "Buy groceries", "Clean room"]
    expected_result = {"result": f"Added 3 tasks: {', '.join(tasks)}"}
    input_data = add_tasks_tool.input_schema(tasks=tasks)
    result = add_tasks_tool.run(input_data)
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
