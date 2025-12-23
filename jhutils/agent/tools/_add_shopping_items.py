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

    # Because the tool schemas are aggregated in MakeChainToolOutputSchema
    # via the tool_input_type type, the preceding docstring is used to
    # determine when to use this tool.

    # The following description is used to provide details informing how to
    # specify the input if using this tool.
    items: ItemsList = Field(  # type: ignore[valid-type]
        ...,
        description=(
            "Individual shopping items to add.\n"
            "- Do NOT capitalize items.\n"
            "- Do NOT attempt to infer quantity and unit. "
            "If they are not EXPLICITLY provided by the user, ONLY specify "
            "the name (and note, if applicable). "
            "For example, 'milk, from Safeway', or 'toilet paper'."
            "- Use format: '<quantity> <unit> <name>, <note>', as applicable. "
            "For example, '10 lb russet potatoes, from Costco', "
            "'2 yellow onions', or 'hydrogen peroxide, from Walmart'.\n"
        ),
    )


class AddShoppingItemsOutputSchema(BaseIOSchema):
    """Output schema for AddShoppingItemsTool."""

    # The preceding docstring is not used for calling the tool.

    # The following description is not used for calling the tool.
    result: str = Field(
        ..., description="Confirmation message after adding the items."
    )


class AddShoppingItemsConfig(BaseToolConfig):
    """Configuration for AddShoppingItemsTool."""


class AddShoppingItemsTool(
    BaseTool[AddShoppingItemsInputSchema, AddShoppingItemsOutputSchema]
):
    """Add one or more individual shopping items to the shopping list."""

    # The one-line summary in the docstring is used by AvailableToolsProvider
    # to help determine whether or not to select this tool next (next_tool).
    input_schema = AddShoppingItemsInputSchema  # type: ignore
    output_schema = AddShoppingItemsOutputSchema  # type: ignore
    config_cls = AddShoppingItemsConfig

    def __init__(
        self,
        mealie: Mealie,
        config: AddShoppingItemsConfig | None = None,
    ):
        if config is None:
            config = AddShoppingItemsConfig()
        super().__init__(config)
        self._mealie = mealie

    @property
    def mealie(self) -> Mealie:
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
        parsed_items = self.mealie.parse_items(params.items, as_payload=True)
        self.mealie.add_shopping_items(parsed_items)
        items = [item["name"] for item in parsed_items]

        joined_items = ", ".join(items)
        item_plural = "item" if len(items) == 1 else "items"
        return AddShoppingItemsOutputSchema(
            result=f"Added {len(items)} {item_plural}: {joined_items}"
        )
