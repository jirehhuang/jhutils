"""Tool chaining assistant agent."""

import os
from typing import TypeVar

import instructor
import openai
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
DEFAULT_TEMPERATURE = 0.0
MODEL_API_PARAMETERS = {"temperature": DEFAULT_TEMPERATURE}

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


def make_openai_client_from_environ() -> instructor.Instructor:
    """Create Instructor client from environment variables."""
    return instructor.from_openai(
        openai.OpenAI(
            base_url=os.getenv(
                "OPENAI_BASE_URL", "https://openrouter.ai/api/v1"
            ),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    )


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

    def __init__(
        self,
        client: instructor.Instructor,
        toolset: Toolset,
        model: str = DEFAULT_MODEL,
        model_api_parameters: dict | None = None,
    ):
        if model_api_parameters is None:
            model_api_parameters = MODEL_API_PARAMETERS
        self._config = AgentConfig(
            client=client,
            model=model,
            model_api_parameters=model_api_parameters,
            system_prompt_generator=SystemPromptGenerator(
                background=ASSISTANT_BACKGROUND,
                output_instructions=OUTPUT_INSTRUCTIONS,
            ),
        )
        self._toolset = toolset
        self._output_schema: BaseIOSchema | None = None
        self.agent: AtomicAgent[BaseIOSchema, BaseIOSchema] | None = None

    @classmethod
    def from_environ(
        cls,
        client: instructor.Instructor | None = None,
        toolset: Toolset | None = None,
    ) -> "AssistantAgent":
        """Create AssistantAgent instance from environment variables."""
        if client is None:
            client = make_openai_client_from_environ()
        if toolset is None:
            toolset = Toolset.from_environ()
        return cls(
            client=client,
            toolset=toolset,
            model=os.getenv("ASSISTANT_MODEL", DEFAULT_MODEL),
            model_api_parameters={
                "temperature": float(
                    os.getenv(
                        "ASSISTANT_TEMPERATURE", str(DEFAULT_TEMPERATURE)
                    )
                )
            },
        )

    @property
    def toolset(self) -> Toolset:
        """Get the toolset."""
        return self._toolset

    def run(
        self,
        query: str,
        reset_selected_tools: bool = True,
        max_chain: int = 5,
    ) -> str:
        """Run the assistant agent.

        Parameters
        ----------
        query
            The user input query to be analyzed and addressed.
        reset_selected_tools
            Whether to reset the selected tools before running the agent.
        max_chain
            The maximum number of tool calls to make in addressing the query.

        Raises
        ------
        RuntimeError
            If the maximum chain length is exceeded.
        """
        result_text = []

        history = self.agent.history if self.agent else None

        # Reset the selected tools to avoid being influenced by prior runs
        if reset_selected_tools:
            self.toolset.reset_selected_tools()

        for _ in range(max_chain):
            # (Re)create agent with selected toolset and history
            self._output_schema = MakeChainToolOutputSchema(
                toolset=self.toolset
            )
            self.agent = AtomicAgent[self._input_schema, self._output_schema](
                config=self._config
            )
            if history:
                self.agent.history = history
            for provider in [AvailableToolsProvider, SelectedToolsProvider]:
                self.agent.register_context_provider(
                    provider.__qualname__, provider(toolset=self.toolset)
                )

            response = self.agent.run(self._input_schema(query=query))

            tool_response = None
            if response.called_tool_input is not None:
                called_tool = self.toolset.initialize_tool(
                    tool_schema=response.called_tool_input
                )
                tool_response = called_tool.run(response.called_tool_input)

            if tool_response and hasattr(tool_response, "result"):
                result_text.append(tool_response.result)

            if response.next_tool is None:
                if tool_response and hasattr(tool_response, "response"):
                    return tool_response.response
                return "\n".join(result_text) or "Done."

            query = response.remainder
            self.toolset.selected_tools = [
                self.toolset.get_tool(response.next_tool)
            ]
            history = self.agent.history

        raise RuntimeError(
            f"Maximum chain length of {max_chain} exceeded "
            f'in mode: "{self.toolset.mode}". '
            f'Failed to address remaining query: "{query}"'
        )


class AssistantFactory:
    """Factory class for initializing and accessing the assistant agent."""

    def __init__(self):
        """Initialize the manager with production mode flag."""
        self._client: instructor.Instructor | None = None
        self._toolset: Toolset | None = None
        self._assistant: AssistantAgent | None = None

    @property
    def client(self) -> instructor.Instructor:
        """Get the OpenAI client used by the assistant agent."""
        if self._client is None:
            self._client = make_openai_client_from_environ()
        return self._client

    @property
    def toolset(self) -> Toolset:
        """Get the toolset used by the assistant agent."""
        if self._toolset is None:
            self._toolset = Toolset.from_environ()
        return self._toolset

    @property
    def assistant(self) -> AssistantAgent:
        """Get the assistant agent."""
        if self._assistant is None:
            self._assistant = AssistantAgent(
                client=self.client, toolset=self.toolset
            )
        return self._assistant
