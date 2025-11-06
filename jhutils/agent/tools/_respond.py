"""Tool to respond to the user."""

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from pydantic import Field


class RespondInputSchema(BaseIOSchema):
    """Input schema for RespondTool.

    Use RespondTool to send a response to the user if none of the other
    Available Tool(s) are applicable to address the user query. For example,
    use this to answer questions, or to explain to the user that you do not
    know how to address their query. If called, this should always be the last
    tool because it responds to the user.
    """

    response: str | None = Field(
        ...,
        description=(
            "The concise response to be sent addressing the entirety of the "
            "user query. "
            "This input value will be directly reflected to the user. "
            "Should be in paragraph format, without formatting, as if "
            "responding verbally to the user. "
            "Do not make up answers for the sake of responding. "
            "If you do not know the answer, say so honestly."
        ),
    )


class RespondOutputSchema(BaseIOSchema):
    """Output schema for RespondTool."""

    response: str | None = Field(..., description="The response to the user.")


class RespondConfig(BaseToolConfig):
    """Configuration for RespondTool."""


class RespondTool(BaseTool[RespondInputSchema, RespondOutputSchema]):
    """Respond to the user, such as by answering a question or explaining."""

    input_schema = RespondInputSchema  # type: ignore
    output_schema = RespondOutputSchema  # type: ignore
    config_cls = RespondConfig

    def __init__(self, config: RespondConfig | None = None):
        if config is None:
            config = RespondConfig()
        super().__init__(config)

    def run(self, params: RespondInputSchema) -> RespondOutputSchema:
        """Return the input response as the output to the user.

        Parameters
        ----------
        params
            The input parameters for the tool.

        Returns
        -------
            RespondOutputSchema: The reflected response.
        """
        return RespondOutputSchema(response=params.response)
