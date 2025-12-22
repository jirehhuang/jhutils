"""Obsidian class to interact with an Obsidian vault backed up on GitHub."""

import base64
import os
from typing import Any, Dict, List

import requests

from ._utils import _time_id

INBOX_PATH = "Inbox"


# pylint: disable=too-many-arguments,too-many-positional-arguments
class Obsidian:
    """Client for interacting with an Obsidian vault GitHub repository.

    Parameters
    ----------
    github_token
        GitHub token with access to the repository.
    owner
        Owner of the repository.
    repository
        Name of the repository.
    branch
        Branch of the repository.
    prompts_path
        Path to the folder in the repository containing system prompts for the
        various assistant modes.
    """

    def __init__(  # noqa: PLR0913
        self,
        github_token: str,
        owner: str,
        repository: str,
        branch: str,
        prompts_path: str | None = None,
    ) -> None:
        if not github_token:
            raise ValueError(
                '"github_token" required to initialize Obsidian instance.'
            )
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"token {github_token}"})

        if not owner or not repository:
            raise ValueError(
                '"owner" and "repository" are required to initialize Obsidian '
                "instance."
            )
        self._api_url: str = (
            f"https://api.github.com/repos/{owner}/{repository}/contents"
        )
        self._branch: str = branch or "main"
        self._files: Dict[str, Any] = {}
        self._prompts_path: str | None = prompts_path

    @classmethod
    def from_environ(cls) -> "Obsidian":
        """Create Obsidian instance from environment variables."""
        return cls(
            github_token=os.getenv("OBSIDIAN_VAULT_TOKEN", ""),
            owner=os.getenv("OBSIDIAN_VAULT_OWNER", ""),
            repository=os.getenv(
                "OBSIDIAN_VAULT_REPOSITORY", "obsidian-vault"
            ),
            branch=os.getenv("OBSIDIAN_VAULT_BRANCH", "main"),
            prompts_path=os.getenv("OBSIDIAN_VAULT_PROMPTS_PATH", None),
        )

    # pylint: disable=duplicate-code
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] | None = None,
        data: Dict[str, Any] | List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        """Make API request to endpoint with error handling."""
        url = f"{self._api_url}/{endpoint.lstrip('/')}"

        response = self.session.request(method, url, params=params, json=data)
        response.raise_for_status()

        response_json = response.json()
        if isinstance(response_json, list):
            response_json = {"content": response_json}

        return response_json

    @property
    def prompts_path(self) -> str | None:
        """Get the prompts path.

        The prompts path is the folder in the repository where the system
        prompts for the assistant are stored. This property is used by the
        Toolset class to retrieve the system prompt for a given mode.

        Note that this system prompt is not for the AssistantAgent class
        itself, but for a manager agent delegating to the AssistantAgent.
        """
        return self._prompts_path

    @property
    def files(self) -> Dict[str, Any]:
        """Getter for the files."""
        return self._files

    def list_files(self, path: str = "") -> List[Dict[str, Any]]:
        """List files from a folder in the repository."""
        response = self._request("GET", f"{path}?ref={self._branch}")
        self._files.update({path: response["content"]})
        return self._files[path]

    def read_file(
        self, file_path: str, none_if_404: bool = False
    ) -> Dict[str, Any] | None:
        """Read a file from the repository."""
        try:
            response = self._request("GET", f"{file_path}?ref={self._branch}")
            response.update(
                {
                    "content": base64.b64decode(response["content"]).decode(
                        "utf-8"
                    )
                }
            )
            self._files.update({file_path: response})
            return self._files[file_path]
        except requests.exceptions.HTTPError as e:
            if none_if_404:
                return None
            raise e

    def add_file(
        self, file_path: str, content: str, message: str | None = None
    ) -> Dict[str, Any]:
        """Add a new file to the repository."""
        data = {
            "message": message or f"add {file_path}",
            "content": base64.b64encode(content.encode("utf-8")).decode(
                "utf-8"
            ),
            "branch": self._branch,
        }
        return self._request("PUT", file_path, data=data)

    def delete_file(
        self, file_path: str, sha: str | None = None
    ) -> Dict[str, Any]:
        """Delete a file from the repository."""
        if sha is None:
            sha = self._files.get(file_path, {}).get("sha")
            # pragma: no cover
            if sha is None:
                file = self.read_file(file_path) or {}
                sha = file.get("sha")
        data = {
            "message": f"delete {file_path}",
            "sha": sha,
            "branch": self._branch,
        }
        return self._request("DELETE", file_path, data=data)

    def update_file(
        self, file_path: str, content: str, sha: str | None = None
    ) -> Dict[str, Any]:
        """Update an existing file in the repository."""
        if sha is None:
            sha = self._files.get(file_path, {}).get("sha")
            # pragma: no cover
            if sha is None:
                file = self.read_file(file_path) or {}
                sha = file.get("sha")
        data = {
            "message": f"update {file_path}",
            "content": base64.b64encode(content.encode("utf-8")).decode(
                "utf-8"
            ),
            "sha": sha,
            "branch": self._branch,
        }
        return self._request("PUT", file_path, data=data)

    def add_tasks(self, tasks: List[str]) -> dict:
        """Add tasks to the Inbox folder as a markdown file."""
        file_path = os.path.join(INBOX_PATH, f"task_{_time_id()}.md")
        content = "\n".join(f"- [ ] {task}" for task in tasks)
        return self.add_file(
            file_path, content=content, message=f"task: add {file_path}"
        )
