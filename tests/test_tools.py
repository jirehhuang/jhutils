"""Test the agent tools module."""

import numpy as np
import pytest
from pydantic import ValidationError

from jhutils.agents.tools import (
    AddShoppingItemsTool,
    AddTasksTool,
    MakeChainToolOutputSchema,
    RespondTool,
)
from jhutils.agents.tools._toolset import (
    DEFAULT_TOOL_NAMES,
    SHOPPING_TOOL_NAMES,
    TOOLS,
    _Toolset,
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


def test_schema_none_valid_tool_input():
    """Test that None is a valid value for the tool_input field."""
    schema = MakeChainToolOutputSchema()(
        tool_input=None,
        remainder=REMAINDER,
        next_tool="AddTasksTool",
    )
    assert schema.tool_input is None


def test_schema_none_valid_next_tool(add_tasks_input):
    """Test that None is a valid value for the next_tool field."""
    schema = MakeChainToolOutputSchema()(
        tool_input=add_tasks_input,
        remainder=REMAINDER,
        next_tool=None,
    )
    assert schema.next_tool is None


@pytest.fixture(name="toolset_", scope="function")
def fixture_toolset_():
    """Return the default instance of _Toolset."""
    return _Toolset()


@pytest.mark.parametrize(
    "mode, tool_names",
    [
        ("default", DEFAULT_TOOL_NAMES),
        ("shopping", SHOPPING_TOOL_NAMES),
    ],
)
def test_toolset_constructs_with_mode(mode, tool_names):
    """Test that _Toolset constructs correctly with different modes, as well
    as tool_names property."""
    toolset_ = _Toolset(mode=mode)
    assert toolset_.mode == mode
    assert np.all(toolset_.tool_names == tool_names)


def test_toolset_all_tools(toolset_):
    """Test that _Toolset.all_tools property getter correctly returns the
    expected list of tools."""
    assert np.all(toolset_.all_tools == TOOLS)


def test_toolset_tools_getter_setter(toolset_):
    """Test that the _Toolset.tools property getter and setter work as
    expected."""
    assert np.all(toolset_.tools == TOOLS)
    toolset_.tools = [AddTasksTool]
    assert toolset_.tools == [AddTasksTool]


def test_toolset_mode_getter_setter(toolset_):
    """Test that the _Toolset.mode property getter and setter work as
    expected, as well as the tool_names property."""
    assert toolset_.mode == "default"
    toolset_.mode = "shopping"
    assert toolset_.mode == "shopping"
    assert np.all(toolset_.tool_names == SHOPPING_TOOL_NAMES)


def test_toolset_get_tool_methods(toolset_):
    """Test that the _Toolset.get_tool and other get_* methods correctly
    retrieve the corresponding tools and their attributes."""
    for tool in TOOLS:
        tool_name = tool.__qualname__
        assert toolset_.get_tool(tool_name) == tool
        assert toolset_.get_input_schema(tool_name) == tool.input_schema
        assert toolset_.get_output_schema(tool_name) == tool.output_schema
        assert toolset_.get_config(tool_name) == tool.config_cls


def test_toolset_error_if_invalid_tool_name(toolset_):
    """Test that a ValueError is raised if an invalid tool name is provided."""
    with pytest.raises(ValueError):
        toolset_.get_tool("InvalidTool")
    with pytest.raises(ValueError):
        toolset_.get_input_schema("InvalidTool")
    with pytest.raises(ValueError):
        toolset_.get_output_schema("InvalidTool")
    with pytest.raises(ValueError):
        toolset_.get_config("InvalidTool")
