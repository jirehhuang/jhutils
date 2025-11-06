"""Test the agent tools Toolset module."""

import numpy as np
import pytest

from jhutils._mealie import Mealie
from jhutils._obsidian import Obsidian
from jhutils.agent.tools import (
    AddTasksTool,
    Toolset,
)
from jhutils.agent.tools._tools import (
    AVAILABLE_MODES,
    TOOL_NAMES,
    TOOLS,
)
from jhutils.agent.tools._toolset import (
    AvailableToolsProvider,
    SelectedToolsProvider,
)


def test_dummy_toolset_has_no_tool_kwargs(toolset):
    """Test that the dummy Toolset instance has no tool constructor arguments
    in kwargs."""
    assert toolset.mode == "general"
    assert toolset.kwargs.get("mealie") is None
    assert toolset.kwargs.get("obsidian") is None


def test_toolset_construct_from_environ():
    """Test that Toolset.from_environ constructs a Toolset instance
    correctly from environment variables with tool kwargs."""
    toolset = Toolset.from_environ()
    assert isinstance(toolset, Toolset)
    assert toolset.mode == "general"
    assert isinstance(toolset.kwargs.get("mealie"), Mealie)
    assert isinstance(toolset.kwargs.get("obsidian"), Obsidian)


@pytest.mark.parametrize(
    "mode, tool_names",
    [
        ("general", AVAILABLE_MODES["general"]),
        ("shopping", AVAILABLE_MODES["shopping"]),
    ],
)
def test_toolset_constructs_with_mode(mode, tool_names):
    """Test that Toolset constructs correctly with different modes, as well
    as tool_names property."""
    toolset = Toolset(mode=mode)
    assert toolset.mode == mode
    assert np.all(toolset.available_tool_names == tool_names)


def test_toolset_mode_getter_setter(toolset):
    """Test that the Toolset.mode property getter and setter work as
    expected, as well as the tool_names property."""
    assert toolset.mode == "general"
    toolset.mode = "shopping"
    assert toolset.mode == "shopping"
    assert np.all(toolset.available_tool_names == AVAILABLE_MODES["shopping"])
    toolset.mode = "general"
    assert toolset.mode == "general"
    assert np.all(toolset.available_tool_names == AVAILABLE_MODES["general"])


def test_toolset_error_if_invalid_mode(toolset):
    """Test that a ValueError is raised if an invalid mode is provided to
    the mode setter."""
    with pytest.raises(ValueError):
        toolset.mode = "invalid_mode"


def test_toolset_all_tools(toolset):
    """Test that Toolset.all_tools property getter correctly returns the
    expected list of tools."""
    assert np.all(toolset.all_tools == TOOLS)
    assert np.all(toolset.all_tool_names == TOOL_NAMES)


def test_toolset_available_tools_getter(toolset):
    """Test that the Toolset.available_tools property getter works as
    expected."""
    assert np.all(toolset.available_tools == TOOLS)
    assert np.all(toolset.available_tool_names == TOOL_NAMES)


def test_toolset_selected_tools_getter_setter(toolset):
    """Test that the Toolset.selected_tools property getter and setter work as
    expected."""
    assert np.all(toolset.selected_tools == TOOLS)
    toolset.selected_tools = [AddTasksTool]
    assert toolset.selected_tools == [AddTasksTool]
    assert toolset.selected_tool_names == ["AddTasksTool"]


def test_toolset_error_if_invalid_selected_tools(toolset):
    """Test that a ValueError is raised if an invalid tool is provided to
    the selected_tools setter."""
    with pytest.raises(ValueError):
        toolset.selected_tools = [AddTasksTool, "InvalidTool"]  # type: ignore
    with pytest.raises(ValueError):
        toolset.selected_tools = ["InvalidTool"]  # type: ignore


def test_toolset_get_tool_methods(toolset):
    """Test that the Toolset.get_tool and other get_* methods correctly
    retrieve the corresponding tools and their attributes."""
    for tool in TOOLS:
        tool_name = tool.__qualname__
        assert toolset.get_tool(tool_name) == tool
        assert toolset.get_tool(tool_schema=tool.input_schema) == tool
        assert toolset.get_input_schema(tool_name) == tool.input_schema
        assert toolset.get_output_schema(tool_name) == tool.output_schema
        assert toolset.get_config(tool_name) == tool.config_cls


def test_toolset_error_if_get_missing_tool_name_and_schema(toolset):
    """Test that a ValueError is raised if neither tool_name nor tool_schema is
    provided."""
    msg = 'Either "tool_name" or "tool_schema" must be provided.'
    with pytest.raises(ValueError, match=msg):
        toolset.get_tool(tool_name=None, tool_schema=None)


def test_toolset_error_if_get_invalid_tool_name(toolset):
    """Test that a ValueError is raised if an invalid tool name is provided."""
    invalid_tool = "InvalidTool"
    msg = f'Tool with name "{invalid_tool}" not found in the toolset.'
    with pytest.raises(ValueError, match=msg):
        toolset.get_tool(tool_name=invalid_tool)
    with pytest.raises(ValueError, match=msg):
        toolset.get_input_schema(tool_name=invalid_tool)
    with pytest.raises(ValueError, match=msg):
        toolset.get_output_schema(tool_name=invalid_tool)
    with pytest.raises(ValueError, match=msg):
        toolset.get_config(tool_name=invalid_tool)


def test_toolset_error_if_get_invalid_tool_schema(toolset):
    """Test that a ValueError is raised if an invalid tool schema class or
    instance is provided."""

    class InvalidSchema:
        # pylint: disable=too-few-public-methods
        pass

    msg = 'Tool with name "InvalidSchema" not found in the toolset.'

    with pytest.raises(ValueError, match=msg):
        toolset.get_tool(tool_schema=InvalidSchema)  # type: ignore
    with pytest.raises(ValueError, match=msg):
        toolset.get_tool(tool_schema=InvalidSchema())  # type: ignore


def test_general_toolset_initialize_tools(toolset):
    """Test that the dummy Toolset without kwargs initializes tools
    without constructor arguments."""
    add_tasks_tool = toolset.initialize_tool("AddTasksTool")
    assert add_tasks_tool.obsidian is None
    add_shopping_items_tool = toolset.initialize_tool("AddShoppingItemsTool")
    assert add_shopping_items_tool.mealie is None


def test_toolset_kwargs_initialize_tools(obsidian, mealie):
    """Test that Toolset with kwargs correctly passes them to tool
    constructors."""
    toolset = Toolset(obsidian=obsidian, mealie=mealie)
    assert toolset.kwargs == {"obsidian": obsidian, "mealie": mealie}
    add_tasks_tool = toolset.initialize_tool("AddTasksTool")
    assert add_tasks_tool.obsidian == obsidian
    add_shopping_items_tool = toolset.initialize_tool("AddShoppingItemsTool")
    assert add_shopping_items_tool.mealie == mealie


def test_tools_providers(toolset):
    """Test that the AvailableToolsProvider and SelectedToolsProvider return
    the correct tools."""
    available_tools_info = AvailableToolsProvider(toolset=toolset).get_info()
    assert np.all(
        [
            tool_name in available_tools_info
            for tool_name in toolset.all_tool_names
        ]
    )
    selected_tools_info = SelectedToolsProvider(toolset=toolset).get_info()
    assert np.all(
        [
            tool_name in selected_tools_info
            for tool_name in toolset.selected_tool_names
        ]
    )
