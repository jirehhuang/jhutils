"""Tests for the agent tools module."""

from jhutils.agent_tools import (
    AddShoppingItemsInputSchema,
    AddShoppingItemsTool,
    AddTasksInputSchema,
    AddTasksTool,
)


def test_add_shopping_items_tool():
    """Test that running the AddShoppingItemsTool returns the expected
    result."""
    items = ["milk", "eggs", "bread"]
    expected_result = {
        "result": f"Successfully added item(s): {', '.join(items)}"
    }
    tool = AddShoppingItemsTool()
    input_data = AddShoppingItemsInputSchema(items=items)
    result = tool.run(input_data)
    assert result.model_dump() == expected_result


def test_add_tasks_tool():
    """Test that running the AddTasksTool returns the expected result."""
    tasks = ["Do laundry", "Buy groceries", "Clean room"]
    expected_result = {
        "result": f"Successfully added task(s): {', '.join(tasks)}"
    }
    tool = AddTasksTool()
    input_data = AddTasksInputSchema(tasks=tasks)
    result = tool.run(input_data)
    assert result.model_dump() == expected_result
