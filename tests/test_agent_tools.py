"""Tests for the agent tools module."""

from jhutils.agent_tools import (
    AddShoppingItemsInputSchema,
    AddShoppingItemsTool,
)


def test_add_shopping_items_tool():
    """Test that running the AddShoppingItemsTool returns the expected
    result."""
    expected_result = {
        "result": "Successfully added item(s): milk, eggs, bread"
    }
    tool = AddShoppingItemsTool()
    input_data = AddShoppingItemsInputSchema(items=["milk", "eggs", "bread"])
    result = tool.run(input_data)
    assert result.model_dump() == expected_result
