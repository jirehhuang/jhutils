"""Tests for the Manager class."""

import pytest
from smolagents import CodeAgent

from jhutils._agents import (
    MANAGER_INSTRUCTIONS,
    SCRIBE_DESCRIPTION,
    SCRIBE_INSTRUCTIONS,
    SHOPPING_DESCRIPTION,
    SHOPPING_INSTRUCTIONS,
    ToolSchedulingAgent,
)


def get_shopping_list() -> list:
    """Get the current contents of the shopping list.

    This should be used when the user wants to know what is currently on the
    shopping list.

    Example trigger phrases include:
    - "What is on my shopping list?"
    - "I'm at Costco. What do I need to get?"
    - "What do I need to get from {store}?"

    Returns
    -------
    list
        The current list of shopping items.
    """
    return ["milk", "cheese"]


def add_shopping_item(item: str) -> None:
    """Add a shopping item to shopping list.

    Example trigger phrases include:
    - "I need to get chicken thighs"
    - "remember to get onions"
    - "I'm almost out of toilet paper"
    - "baby wipes, sparkling water, kimchi"

    Parameters
    ----------
    item: str
        The shopping item to add, in all lowercase. Should be a single item
        that has definitely NOT already been added to the shopping list.
    """
    # Internally skips adding duplicate items, so the shopping list does not
    # need to be checked beforehand
    print(item)


def add_task(task: str) -> None:
    """Add an independent task to the tasks list.

    Add a single, independently executable task or action item. If it depends
    on other tasks, or is part of a larger body of thought, or if it needs to
    be longer than a single sentence, use :func:`add_note` instead.

    Example trigger phrases include:
    [
        {
            "user": "I need to make sure coffee gets picked up on Sunday",
            "task": "Make sure coffee gets picked up on Sunday"
        },
        {
            "user": "add delegate T-shirt distribution logistics",
            "task": "Delegate T-shirt distribution logistics"
        },
        {
            "user": "remind me to respond to Chris' email about lunch",
            "task": "Respond to Chris' email about lunch"
        },
        {
            "user": "I should send out the assigned groups",
            "task": "Send assigned groups"
        }
    ]

    Parameters
    ----------
    task: str
        The independent task or action item to add. Written in the imperative
        mood from the perspective of the user. "Remember to" and "Remind [self]
        to" are not meaningful actions for the user.
    """
    print(task)


def add_note(title: str, body: str) -> None:
    """Add provided note to notes.

    Add a note, as if by a detail-oriented and devoted assistant who is
    organizing and curating the thoughts and mental notes of a busy
    executive. Additionally:
    - Write from the perspective of the user
    - Include all details
    - Use checkboxes for tasks and action items that need to be completed

    Example trigger phrases include:
    - "I'm thinking out loud"
    - "brainstorming"
    - "here's what I'm thinking"
    - "these are my thoughts"
    - "write me a note"

    Parameters
    ----------
    title: str
        A short title for the note.
    body: str
        The body of the note, written from the perspective of the user, as if a
        note to self for future reference. Additionally:
        - Attempt to be concise, but complete. Do not omit any details!
        - If more than a single paragraph, write in Markdown format
        - If section headings are applicable, use heading levels 3 or higher
        - Use checkboxes for tasks and action items that need to be completed
    """
    print(title, body)


@pytest.fixture(name="shopping_agent", scope="module")
def fixture_shopping_agent(llm):
    """Return fixture for the shopping agent instance."""
    return ToolSchedulingAgent(
        name="shopping_assistant",
        description=SHOPPING_DESCRIPTION,
        instructions=SHOPPING_INSTRUCTIONS,
        tools=[get_shopping_list, add_shopping_item],
        model=llm,
        max_steps=10,
    )


@pytest.fixture(name="scribe_agent", scope="module")
def fixture_scribe_agent(llm):
    """Return fixture for the scribe agent instance."""
    return ToolSchedulingAgent(
        name="scribe_assistant",
        description=SCRIBE_DESCRIPTION,
        instructions=SCRIBE_INSTRUCTIONS,
        tools=[add_task, add_note],
        model=llm,
        max_steps=10,
    )


@pytest.fixture(name="manager_agent", scope="module")
def fixture_manager_agent(llm, shopping_agent, scribe_agent):
    """Return fixture for the manager agent instance."""
    return CodeAgent(
        name="executive_manager",
        instructions=MANAGER_INSTRUCTIONS,
        tools=[],
        model=llm,
        managed_agents=[shopping_agent, scribe_agent],
        additional_authorized_imports=["datetime"],
        max_steps=10,
    )


def test_add_shopping_items(shopping_agent):
    """Test the manager agent with a sample query."""
    items = ["paper towels", "cheese"]
    query = ", ".join(items)
    shopping_agent.run(query)
    assert len(shopping_agent.actions) == len(items)
