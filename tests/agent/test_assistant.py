"""Test the agents module."""

import json

import numpy as np
import pytest
from pydantic import ValidationError

from jhutils.agent import AssistantAgent
from jhutils.agent.tools import (
    AddTasksTool,
    AvailableToolsProvider,
    MakeChainToolOutputSchema,
    RespondTool,
    SelectedToolsProvider,
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


@pytest.fixture(name="assistant", scope="function")
def fixture_assistant(openrouter_client):
    """Return an instance of AssistantAgent."""
    return AssistantAgent(openrouter_client, bool_test=True)


@pytest.fixture(name="chain_tool_output_schema", scope="module")
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


def test_chain_schema_error_if_no_remainder_and_next_tool(
    add_tasks_input, chain_tool_output_schema
):
    """Test that a ValueError is raised if there is no remainder and next_tool
    is not None."""
    with pytest.raises(ValueError):
        chain_tool_output_schema(
            called_tool_input=add_tasks_input,
            remainder="",
            next_tool="RespondTool",
        )


def test_chain_schema_error_if_respond_not_last_tool(chain_tool_output_schema):
    """Test that a ValueError is raised if called_tool_input is
    RespondInputSchema and next_tool is not None."""
    respond_input = RespondTool().input_schema(response="This is a response.")
    with pytest.raises(ValueError):
        chain_tool_output_schema(
            called_tool_input=respond_input,
            remainder=REMAINDER,
            next_tool="AddTasksTool",
        )


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
    assert json.loads(history[1]["content"])["called_tool_input"] == {
        "items": ["onions"]
    }
    assert json.loads(history[3]["content"])["called_tool_input"] == {
        "tasks": ["Text Georgie back"]
    }
    assert response == "Done."
