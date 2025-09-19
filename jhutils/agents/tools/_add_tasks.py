"""Tool to add tasks to a task list."""

from typing import List, Optional

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from pydantic import Field


class AddTasksInputSchema(BaseIOSchema):
    """Input schema for tasks to add to the task list."""

    tasks: List[str] = Field(
        ...,
        description=(
            "Individual tasks to add. Each task should be written in the "
            "imperative mood from the perspective of the user. The first word "
            "should be capitalized."
        ),
    )


class AddTasksOutputSchema(BaseIOSchema):
    """Output schema of the AddTasks tool."""

    result: str = Field(
        ..., description="Confirmation message after adding the tasks."
    )


class AddTasksConfig(BaseToolConfig):
    """Configuration for the AddTasks tool."""


class AddTasksTool(BaseTool[AddTasksInputSchema, AddTasksOutputSchema]):
    """Add multiple tasks to the task list.

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
