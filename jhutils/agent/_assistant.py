"""Tool chaining assistant agent."""

from typing import Optional, TypeVar

import instructor
from atomic_agents import AgentConfig, AtomicAgent, BaseIOSchema
from atomic_agents.context import (
    SystemPromptGenerator,
)
from pydantic import Field

from .tools import (
    AvailableToolsProvider,
    MakeChainToolOutputSchema,
    SelectedToolsProvider,
    Toolset,
)

InputSchema = TypeVar("InputSchema", bound=BaseIOSchema)
OutputSchema = TypeVar("OutputSchema", bound=BaseIOSchema)


DEFAULT_MODEL = "gpt-4o-mini"
MODEL_API_PARAMETERS = {"temperature": 0.0}

ASSISTANT_BACKGROUND = [
    (
        "You are an assistant who helps address user input queries by "
        "sequentially calling tools to perform actions."
    ),
]
# Tool summaries are included in their docstrings and injected dynamically.
# Output details are included in ChainToolOutputSchema.
# Tool input details are included in their respective input schemas, which are
# injected via ChainToolOutputSchema.
OUTPUT_INSTRUCTIONS = [
    "Analyze the user input query to fill out ChainToolOutputSchema.",
    "Make sure to follow the instructions in the schema EXACTLY.",
]


class QueryInputSchema(BaseIOSchema):
    """Input schema providing the user query."""

    query: str = Field(
        ...,
        description=("The user input query to be analyzed and addressed."),
    )


# pylint: disable=too-few-public-methods
class AssistantAgent:
    """Tool chaining assistant agent class."""

    _input_schema = QueryInputSchema
    _toolset = Toolset()

    def __init__(self, client: instructor.Instructor):
        self._config = AgentConfig(
            client=client,
            model=DEFAULT_MODEL,
            model_api_parameters=MODEL_API_PARAMETERS,
            system_prompt_generator=SystemPromptGenerator(
                background=ASSISTANT_BACKGROUND,
                output_instructions=OUTPUT_INSTRUCTIONS,
            ),
        )
        self._output_schema: Optional[BaseIOSchema] = None
        self.agent: Optional[AtomicAgent[BaseIOSchema, BaseIOSchema]] = None

    def run(self, query: str) -> str:
        """Run the assistant agent."""
        history = self.agent.history if self.agent else None

        while True:
            # (Re)create agent with selected toolset and history
            self._output_schema = MakeChainToolOutputSchema(
                toolset=self._toolset
            )
            self.agent = AtomicAgent[self._input_schema, self._output_schema](
                config=self._config
            )
            if history:
                self.agent.history = history
            for provider in [AvailableToolsProvider, SelectedToolsProvider]:
                self.agent.register_context_provider(
                    provider.__qualname__, provider(toolset=self._toolset)
                )

            response = self.agent.run(self._input_schema(query=query))

            tool_response = None
            if response.called_tool_input is not None:
                called_tool = self._toolset.get_tool_by_schema(
                    response.called_tool_input
                )()
                tool_response = called_tool.run(response.called_tool_input)

            if response.next_tool is None:
                if tool_response and hasattr(tool_response, "response"):
                    return tool_response.response
                return "Done."

            query = response.remainder
            self._toolset.selected_tools = [
                self._toolset.get_tool(response.next_tool)
            ]
            history = self.agent.history
