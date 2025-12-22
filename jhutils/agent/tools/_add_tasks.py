"""Tool to add tasks to a task list."""

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig
from pydantic import Field, conlist

from ..._obsidian import Obsidian

TasksList = conlist(str, min_length=1)


class AddTasksInputSchema(BaseIOSchema):
    """Input schema for AddTasksTool.

    Use this tool for adding one or more tasks, action items, or to-dos.
    All shopping items that need to be purchased should be added using the
    AddShoppingItemsTool instead--NEVER with AddTasksTool.
    """

    tasks: TasksList = Field(  # type: ignore[valid-type]
        ...,
        description=(
            "Individual tasks to add, with all applicable context. "
            "The first word of each task should be capitalized. "
            "Each task should be written in the imperative mood, as if "
            "written by the user for the user to perform. "
            "Do not end each task with punctuation. "
            "If requested by the user to add or remind of a task, extract the "
            "task and do not use 'add' or 'remind' as the task."
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
    """Add one or more independent tasks to the task list."""

    input_schema = AddTasksInputSchema  # type: ignore
    output_schema = AddTasksOutputSchema  # type: ignore
    config_cls = AddTasksConfig

    def __init__(
        self,
        obsidian: Obsidian,
        config: AddTasksConfig | None = None,
    ):
        if config is None:
            config = AddTasksConfig()
        super().__init__(config)
        self._obsidian = obsidian

    @property
    def obsidian(self) -> Obsidian:
        """Get the Obsidian instance."""
        return self._obsidian

    def run(self, params: AddTasksInputSchema) -> AddTasksOutputSchema:
        """Execute the AddTasksTool with the given parameters.

        Parameters
        ----------
        params
            The input parameters for the tool.

        Returns
        -------
            AddTasksOutputSchema: The result of the action.
        """
        self.obsidian.add_tasks(params.tasks)

        joined_tasks = ", ".join(params.tasks)
        task_plural = "task" if len(params.tasks) == 1 else "tasks"
        return AddTasksOutputSchema(
            result=f"Added {len(params.tasks)} {task_plural}: {joined_tasks}"
        )
