"""Tool to add shopping items to a shopping list."""

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from pydantic import Field, conlist

from ..._mealie import Mealie

ItemsList = conlist(str, min_length=1)


class AddShoppingItemsInputSchema(BaseIOSchema):
    """Input schema for AddShoppingItemsTool.

    Use this tool for adding any and all items that need to be purchased.
    For example, all groceries and regular purchases.
    """

    items: ItemsList = Field(  # type: ignore[valid-type]
        ...,
        description=(
            "Individual shopping items to add. Do not capitalize items."
        ),
    )


class AddShoppingItemsOutputSchema(BaseIOSchema):
    """Output schema for AddShoppingItemsTool."""

    result: str = Field(
        ..., description="Confirmation message after adding the items."
    )


class AddShoppingItemsConfig(BaseToolConfig):
    """Configuration for AddShoppingItemsTool."""


class AddShoppingItemsTool(
    BaseTool[AddShoppingItemsInputSchema, AddShoppingItemsOutputSchema]
):
    """Add one or more individual shopping items to the shopping list."""

    input_schema = AddShoppingItemsInputSchema  # type: ignore
    output_schema = AddShoppingItemsOutputSchema  # type: ignore
    config_cls = AddShoppingItemsConfig

    def __init__(
        self,
        config: AddShoppingItemsConfig | None = None,
        mealie: Mealie | None = None,
    ):
        if config is None:
            config = AddShoppingItemsConfig()
        super().__init__(config)
        self._mealie = mealie

    @property
    def mealie(self) -> Mealie | None:
        """Get the Mealie instance."""
        return self._mealie

    def run(
        self, params: AddShoppingItemsInputSchema
    ) -> AddShoppingItemsOutputSchema:
        """Execute the AddShoppingItemsTool with the given parameters.

        Parameters
        ----------
        params
            The input parameters for the tool.

        Returns
        -------
            AddShoppingItemsOutputSchema: The result of the action.
        """
        items = params.items
        if isinstance(self.mealie, Mealie):
            parsed_items = self.mealie.parse_items(
                params.items, as_payload=True
            )
            self.mealie.add_shopping_items(parsed_items)
            items = [item["name"] for item in parsed_items]

        joined_items = ", ".join(items)
        item_plural = "item" if len(items) == 1 else "items"
        return AddShoppingItemsOutputSchema(
            result=f"Added {len(items)} {item_plural}: {joined_items}"
        )
