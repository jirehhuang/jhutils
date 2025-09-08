"""Obsidian class to interact with an Obsidian vault backed up on GitHub."""

import base64
from typing import Any, Dict, List, Optional

import requests


class Obsidian:
    """Client for interacting with an Obsidian vault GitHub repository."""

    def __init__(
        self, owner: str, repository: str, branch: str, github_token: str
    ) -> None:
        self._api_url: str = (
            f"https://api.github.com/repos/{owner}/{repository}/contents"
        )
        self._branch: str = branch
        self._files: Dict[str, Any] = {}

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"token {github_token}"})

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any] | List[Dict[str, Any]]:
        """Make API request to endpoint with error handling."""
        url = f"{self._api_url}/{endpoint.lstrip('/')}"

        response = self.session.request(method, url, params=params, json=data)
        response.raise_for_status()

        return response.json()

    def list_files(self, path: str = "") -> list:
        """List files from a folder in the repository."""
        response = self._request("GET", f"{path}?ref={self._branch}")
        self._files.update({path: response})
        return self._files[path]

    def read_file(self, file_path: str) -> None:
        """Read a file from the repository."""
        response = self._request("GET", f"{file_path}?ref={self._branch}")
        if isinstance(response, dict):
            response.update(
                {"body": base64.b64decode(response["content"]).decode("utf-8")}
            )
        self._files.update({file_path: response})
        return self._files[file_path]
