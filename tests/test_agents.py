"""Test the agents module."""

import pytest

from jhutils.agents import AssistantAgent, AssistantInputSchema
from jhutils.agents.tools import (
    AddShoppingItemsInputSchema,
    AddTasksInputSchema,
)


@pytest.mark.parametrize(
    "query, expected_schema, expected_tool_parameters, expected_result",
    [
        (
            "cheese, bread, paper towels, and potatoes",
            AddShoppingItemsInputSchema,
            {"items": ["cheese", "bread", "paper towels", "potatoes"]},
            (
                "Successfully added item(s): "
                "cheese, bread, paper towels, potatoes"
            ),
        ),
        (
            (
                "I need to make to pick up coffee on Sunday. "
                "Add delegate T-shirt distribution logistics. "
                "Remind me to respond to Chris' email about lunch. "
                "I should send out the assigned groups."
            ),
            AddTasksInputSchema,
            {
                "tasks": [
                    "Pick up coffee on Sunday",
                    "Delegate T-shirt distribution logistics",
                    "Respond to Chris' email about lunch",
                    "Send out the assigned groups",
                ]
            },
            None,
        ),
    ],
)
def test_agent_tool_selection_and_execution(
    openrouter_client,
    query,
    expected_schema,
    expected_tool_parameters,
    expected_result,
):
    """Test that the agent can respond to a query by selecting the appropriate
    tool, providing the correct inputs, and predictably return the expected
    result."""
    # Test that the correct tool is selected with the correct parameters
    assistant_agent = AssistantAgent(openrouter_client)
    input_schema = AssistantInputSchema(chat_message=query)
    assistant_output = assistant_agent.agent.run(input_schema)
    assert isinstance(assistant_output.tool_parameters, expected_schema)
    assert (
        assistant_output.tool_parameters.model_dump()
        == expected_tool_parameters
    )
    response = assistant_agent.execute_tool(assistant_output)
    if expected_result:
        assert response.model_dump() == {"result": expected_result}
        final_answer = assistant_agent.respond_and_reset(response)
        print(final_answer.final_answer)
