"""Tool to respond to the user."""

from typing import Optional

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from pydantic import Field


class RespondInputSchema(BaseIOSchema):
    """Input schema for RespondTool."""

    response: str | None = Field(
        ...,
        description=(
            "The concise response to be sent addressing the user query. "
            "If None or no text is provided, the action will be skipped."
        ),
    )


class RespondOutputSchema(BaseIOSchema):
    """Output schema for RespondTool."""

    response: str | None = Field(..., description="The response to the user.")


class RespondConfig(BaseToolConfig):
    """Configuration for RespondTool."""


class RespondTool(BaseTool[RespondInputSchema, RespondOutputSchema]):
    """Respond to the user query.

    Use RespondTool to send a final response to the user if the user asked a
    question or if none of the Available Tool(s) are applicable to address the
    remaining user query. If called, this should always be the last tool.

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
