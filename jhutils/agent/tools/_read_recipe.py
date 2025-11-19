"""Tool to read recipe."""

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from pydantic import Field

from ..._mealie import Mealie


class ReadRecipeInputSchema(BaseIOSchema):
    """Input schema for ReadRecipeTool.

    Use this tool to read a Markdown-formatted recipe.
    """

    recipe_name: str = Field(
        ...,
        description=("Name of the recipe to retrieve."),
    )
    scale_factor: float = Field(
        default=1,
        description=(
            "The factor by which to scale the recipe ingredients (default: 1)."
        ),
    )
    target_servings: int | None = Field(
        default=None,
        description=(
            "The desired number of servings to scale the recipe to (optional)."
        ),
    )


class ReadRecipeOutputSchema(BaseIOSchema):
    """Output schema for ReadRecipeTool."""

    result: str = Field(
        ..., description="Recipe in Markdown format, or a fallback message."
    )


class ReadRecipeConfig(BaseToolConfig):
    """Configuration for ReadRecipeTool."""


class ReadRecipeTool(BaseTool[ReadRecipeInputSchema, ReadRecipeOutputSchema]):
    """Read a recipe."""

    input_schema = ReadRecipeInputSchema  # type: ignore
    output_schema = ReadRecipeOutputSchema  # type: ignore
    config_cls = ReadRecipeConfig

    def __init__(
        self,
        config: ReadRecipeConfig | None = None,
        mealie: Mealie | None = None,
    ):
        if config is None:
            config = ReadRecipeConfig()
        super().__init__(config)
        self._mealie = mealie

    @property
    def mealie(self) -> Mealie | None:
        """Get the Mealie instance."""
        return self._mealie

    def run(self, params: ReadRecipeInputSchema) -> ReadRecipeOutputSchema:
        """Execute the ReadRecipeTool with the given parameters.

        Parameters
        ----------
        params
            The input parameters for the tool.

        Returns
        -------
            ReadRecipeOutputSchema: The result of the action.
        """
        if isinstance(self.mealie, Mealie):
            recipe_str = self.mealie.read_recipe(
                recipe_name=params.recipe_name,
                scale_factor=params.scale_factor,
                target_servings=params.target_servings,
            )
        else:
            recipe_str = (
                "Mealie instance not available to "
                f"read recipe '{params.recipe_name}'."
            )

        return ReadRecipeOutputSchema(result=recipe_str)
