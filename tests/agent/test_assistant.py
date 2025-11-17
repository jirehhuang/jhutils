"""Test the agents module."""

import json

import instructor
import numpy as np
import pytest

from jhutils import Mealie, Obsidian
from jhutils.agent import AssistantAgent, AssistantFactory
from jhutils.agent.tools import Toolset


@pytest.fixture(name="assistant", scope="function")
def fixture_assistant(openai_client, toolset):
    """Return an instance of AssistantAgent with a dummy toolset instance so
    that tool calling can be tested without making actual API calls."""
    return AssistantAgent(client=openai_client, toolset=toolset)


def test_assistant_from_environ():
    """Test that AssistantAgent.from_environ constructs an AssistantAgent
    instance correctly from environment variables without optional
    arguments."""
    assistant = AssistantAgent.from_environ()
    assert isinstance(assistant, AssistantAgent)
    assert isinstance(assistant.toolset.kwargs.get("mealie"), Mealie)
    assert isinstance(assistant.toolset.kwargs.get("obsidian"), Obsidian)


# pylint: disable=protected-access
def test_assistant_factory():
    """Test that AssistantFactory creates an AssistantAgent instance
    correctly from environment variables."""
    factory = AssistantFactory()
    assert factory._client is None
    assert factory._toolset is None
    assert factory._assistant is None
    assert isinstance(factory.assistant, AssistantAgent)
    assert isinstance(factory._client, instructor.Instructor)
    assert isinstance(factory._toolset, Toolset)


@pytest.mark.flaky(reruns=1)
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
    assert response.startswith("Added 4 tasks:")
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


@pytest.mark.flaky(reruns=1)
def test_assistant_select_and_execute_add_shopping_items(assistant):
    """Test that the assistant can correctly select and execute the
    AddShoppingItemsTool."""
    query = (
        "I need cheese, bread, paper towels, and potatoes. "
        "I'm also running low on tapioca starch. "
        "I should pick up green onions for garnish."
    )
    response = assistant.run(query)
    assert response.startswith("Added 6 items:")
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


def test_assistant_select_and_execute_read_recipe(assistant):
    """Test that the assistant can correctly select and execute the
    ReadRecipeTool."""
    query = "How do I make Al Pastor tacos?"
    expected_start = "Mealie instance not available to read recipe"

    assistant.toolset.match_mode("cooking")
    response = assistant.run(query)

    assert response.startswith(expected_start)
    assert "Al Pastor" in response


@pytest.mark.flaky(reruns=1)
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


@pytest.mark.flaky(reruns=1)
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


@pytest.mark.flaky(reruns=1)
def test_assistant_chain_tools_task_shopping(assistant):
    """Test that the assistant can correctly chain multiple tools:
    AddTasksTool and AddShoppingItemsTool."""
    query = (
        "Add onions to my shopping list. Then, remind me to text Georgie back."
    )
    response = assistant.run(query)
    assert response.startswith("Added 1 item:")
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


@pytest.mark.flaky(reruns=1)
def test_assistant_chain_tools_shopping_respond(assistant):
    """Test that the assistant can correctly chain multiple tools:
    AddTasksTool and RespondTool."""
    query = (
        "Remind me to Venmo Joshua for the magnet. "
        "Also, give me a concise one-sentence explanation on the difference "
        "between propitiation and expiation from a Reformed perspective."
    )
    response = assistant.run(query)
    assert np.all(
        [
            phrase in response.lower()
            for phrase in ["propitiation", "expiation"]
        ]
    )
    history = assistant.agent.history.get_history()
    assert json.loads(history[1]["content"])["called_tool_input"] == {
        "tasks": ["Venmo Joshua for the magnet"]
    }
