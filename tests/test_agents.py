"""Test the agents module."""

import json

import numpy as np
import pytest

from jhutils.agents import AssistantAgent
from jhutils.agents.assistant import (
    AvailableToolsProvider,
    SelectedToolsProvider,
)


@pytest.fixture(name="assistant", scope="function")
def fixture_assistant(openrouter_client):
    """Return an instance of AssistantAgent."""
    return AssistantAgent(openrouter_client)


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


def test_assistant_select_and_execute_add_tasks(assistant):
    """Test that the assistant can correctly select and execute the
    AddTasksTool."""
    query = (
        "I need to make sure to pick up coffee on Sunday. "
        "Add delegate T-shirt distribution logistics. "
        "Remind me to respond to Chris' email about lunch. "
        "I should send out the assigned groups. "
    )
    response = assistant.run(query)
    assert response == "Done."
    history = assistant.agent.history.get_history()
    assert json.loads(history[1]["content"]) == {
        "called_tool_input": {
            "tasks": [
                "Pick up coffee on Sunday",
                "Delegate T-shirt distribution logistics",
                "Respond to Chris' email about lunch",
                "Send out the assigned groups",
            ]
        },
        "remainder": "",
        "next_tool": None,
    }


def test_assistant_select_and_execute_add_shopping_items(assistant):
    """Test that the assistant can correctly select and execute the
    AddShoppingItemsTool."""
    query = (
        "I need cheese, bread, paper towels, and potatoes. "
        "I'm also running low on tapioca starch. "
        "I should pick up green onions for garnish."
    )
    response = assistant.run(query)
    assert response == "Done."
    history = assistant.agent.history.get_history()
    assert json.loads(history[1]["content"]) == {
        "called_tool_input": {
            "items": [
                "cheese",
                "bread",
                "paper towels",
                "potatoes",
                "tapioca starch",
                "green onions",
            ]
        },
        "remainder": "",
        "next_tool": None,
    }


def test_assistant_select_and_execute_respond(assistant):
    """Test that the assistant can correctly select and execute the
    RespondTool."""
    query = (
        "According to the Westminster Shorter Catechism, what is the chief "
        "end of man?"
    )
    expected_response = (
        "According to the Westminster Shorter Catechism, the chief end of man "
        "is to glorify God and to enjoy Him forever."
    )
    response = assistant.run(query)
    assert response == expected_response
    history = assistant.agent.history.get_history()
    assert json.loads(history[1]["content"]) == {
        "called_tool_input": {"response": expected_response},
        "remainder": "",
        "next_tool": None,
    }
