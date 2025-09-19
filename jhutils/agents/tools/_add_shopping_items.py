"""Tool to add shopping items to a shopping list."""

from typing import List, Optional

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from pydantic import Field


class AddShoppingItemsInputSchema(BaseIOSchema):
    """Input schema for items to add to the shopping list."""

    items: List[str] = Field(
        ...,
        description=(
            "Individual shopping items to add. Do not capitalize items."
        ),
    )


class AddShoppingItemsOutputSchema(BaseIOSchema):
    """Output schema of the AddShoppingItems tool."""

    result: str = Field(
        ..., description="Confirmation message after adding the items."
    )


class AddShoppingItemsConfig(BaseToolConfig):
    """Configuration for the AddShoppingItems tool."""


class AddShoppingItemsTool(
    BaseTool[AddShoppingItemsInputSchema, AddShoppingItemsOutputSchema]
):
    """Add multiple items to the shopping list.

    Parameters
    ----------
    config : AddShoppingItemsConfig
        Configuration for the tool.

    Attributes
    ----------
        input_schema (AddShoppingItemsInputSchema): The schema for the input
            data.
        output_schema (AddShoppingItemsOutputSchema): The schema for the output
            data.
    """

    input_schema = AddShoppingItemsInputSchema
    output_schema = AddShoppingItemsOutputSchema
    config_cls = AddShoppingItemsConfig

    def __init__(self, config: Optional[AddShoppingItemsConfig] = None):
        if config is None:
            config = AddShoppingItemsConfig()
        super().__init__(config)

    def run(
        self, params: AddShoppingItemsInputSchema
    ) -> AddShoppingItemsOutputSchema:
        """Execute the AddShoppingItemsTool with the given parameters.

        Parameters
        ----------
        params : AddShoppingItemsInputSchema
            The input parameters for the tool.

        Returns
        -------
            AddShoppingItemsOutputSchema: The result of the action.
        """
        # Placeholder
        joined_items = ", ".join(params.items)
        return AddShoppingItemsOutputSchema(
            result=f"Successfully added item(s): {joined_items}"
        )
