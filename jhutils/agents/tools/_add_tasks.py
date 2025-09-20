"""Tool to add tasks to a task list."""

from typing import List, Optional

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from pydantic import Field


class AddTasksInputSchema(BaseIOSchema):
    """Input schema for AddTasksTool."""

    tasks: List[str] = Field(
        ...,
        description=(
            "Individual tasks to add. Each task should be written in the "
            "imperative mood from the perspective of the user. The first word "
            "should be capitalized."
        ),
    )


class AddTasksOutputSchema(BaseIOSchema):
    """Output schema for AddTasksTool."""

    result: str = Field(
        ..., description="Confirmation message after adding the tasks."
    )


class AddTasksConfig(BaseToolConfig):
    """Configuration for AddTasksTool."""


class AddTasksTool(BaseTool[AddTasksInputSchema, AddTasksOutputSchema]):
    """Add one or more independent tasks to the task list.

    Use this tool for adding one or more tasks, action items, or to-dos. Use
    AddShoppingItemsTool instead for shopping items that need to be purchased.
    However, prefer using AddTasksTool over AddShoppingItemsTool if uncertain
    about which to use.

    Parameters
    ----------
    config : AddTasksConfig
        Configuration for the tool.

    Attributes
    ----------
        input_schema (AddTasksInputSchema): The schema for the input data.
        output_schema (AddTasksOutputSchema): The schema for the output data.
    """

    input_schema = AddTasksInputSchema
    output_schema = AddTasksOutputSchema
    config_cls = AddTasksConfig

    def __init__(self, config: Optional[AddTasksConfig] = None):
        if config is None:
            config = AddTasksConfig()
        super().__init__(config)

    def run(self, params: AddTasksInputSchema) -> AddTasksOutputSchema:
        """Execute the AddTasksTool with the given parameters.

        Parameters
        ----------
        params : AddTasksInputSchema
            The input parameters for the tool.

        Returns
        -------
            AddTasksOutputSchema: The result of the action.
        """
        # Placeholder
        joined_tasks = ", ".join(params.tasks)
        return AddTasksOutputSchema(
            result=f"Successfully added task(s): {joined_tasks}"
        )
