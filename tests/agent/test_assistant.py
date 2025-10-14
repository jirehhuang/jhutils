"""Test the agents module."""

import json

import numpy as np
import pytest

from jhutils.agent import AssistantAgent


@pytest.fixture(name="assistant", scope="function")
def fixture_assistant(openrouter_client):
    """Return an instance of AssistantAgent."""
    return AssistantAgent(openrouter_client, bool_test=True)


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
    expected_phrases = ["glorify God", "enjoy Him forever"]
    response = assistant.run(query)
    assert all(
        expected_phrase in response for expected_phrase in expected_phrases
    )


def test_assistant_respond_sorry_if_cannot_answer(assistant):
    """Test that the assistant correctly acknowledges inability to handle a
    query where no tool is applicable and the assistant does not know."""
    query = "What did Grace make for dinner last Tuesday?"
    expected_phrases = ["sorry", "don't know", "do not know"]
    response = assistant.run(query)
    assert any(
        expected_phrase in response for expected_phrase in expected_phrases
    )
    history = assistant.agent.history.get_history()
    assert "response" in json.loads(history[1]["content"])["called_tool_input"]


def test_assistant_chain_tools_task_shopping_respond(assistant):
    """Test that the assistant can correctly chain multiple tools:
    AddTasksTool, AddShoppingItemsTool, RespondTool."""
    query = "Add onions to my shopping list. Remind me to text Georgie back."
    response = assistant.run(query)
    history = assistant.agent.history.get_history()
    called_tool_inputs = [
        json.loads(history[i]["content"])["called_tool_input"] for i in [1, 3]
    ]
    assert np.any(
        [
            called_tool_input == {"items": ["onions"]}
            for called_tool_input in called_tool_inputs
        ]
    )
    assert np.any(
        [
            called_tool_input == {"tasks": ["Text Georgie back"]}
            for called_tool_input in called_tool_inputs
        ]
    )
    assert response == "Done."
