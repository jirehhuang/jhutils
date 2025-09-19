"""Tool to respond to the user."""

from typing import Optional

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from pydantic import Field


class RespondInputSchema(BaseIOSchema):
    """Input schema for responding to the user."""

    response: str = Field(
        ...,
        description=(
            "The concise response to be sent addressing the user's request."
        ),
    )


class RespondOutputSchema(BaseIOSchema):
    """Output schema of responding to the user."""

    response: str = Field(..., description="The response to the user.")


class RespondConfig(BaseToolConfig):
    """Configuration for the Respond tool."""


class RespondTool(BaseTool[RespondInputSchema, RespondOutputSchema]):
    """Add multiple tasks to the task list.

    Parameters
    ----------
    config : RespondConfig
        Configuration for the tool.

    Attributes
    ----------
        input_schema (RespondInputSchema): The schema for the input data.
        output_schema (RespondOutputSchema): The schema for the output data.
    """

    input_schema = RespondInputSchema
    output_schema = RespondOutputSchema
    config_cls = RespondConfig

    def __init__(self, config: Optional[RespondConfig] = None):
        if config is None:
            config = RespondConfig()
        super().__init__(config)

    def run(self, params: RespondInputSchema) -> RespondOutputSchema:
        """Return the input response as the output to the user.

        Parameters
        ----------
        params : RespondInputSchema
            The input parameters for the tool.

        Returns
        -------
            RespondOutputSchema: The reflected response.
        """
        return RespondOutputSchema(response=params.response)
