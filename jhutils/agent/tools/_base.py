"""Base configuration for tools."""

from atomic_agents import BaseToolConfig


class BaseToolTestConfig(BaseToolConfig):
    """Configuration for BaseTool with test options."""

    bool_test: bool = False
