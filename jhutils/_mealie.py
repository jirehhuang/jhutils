"""Mealie class."""

import os
from typing import Any, Dict, List

import requests

N_FOODS = 500
N_ITEMS = 50


class Mealie:
    """Client for interacting with the Mealie API."""

    def __init__(
        self, api_url: str, api_key: str, shopping_list_id: str | None = None
    ) -> None:
        self._shopping_list_id = shopping_list_id

        self._foods: List[Dict[str, Any]] = []
        self._shopping_items: List[Dict[str, Any]] | None = None

        self._api_url: str = api_url.rstrip("/")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    @classmethod
    def from_environ(cls) -> "Mealie":
        """Create Mealie instance from environment variables."""
        return cls(
            api_url=os.getenv("MEALIE_API_URL", ""),
            api_key=os.getenv("MEALIE_API_KEY", ""),
            shopping_list_id=os.getenv("MEALIE_SHOPPING_LIST_ID", None),
        )

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

    def load_foods(
        self, initial_per_page: int = N_FOODS, force: bool = False
    ) -> List[Dict[str, Any]]:
        """Retrieve foods data."""
        if not self._foods or force:
            params = {
                "page": 1,
                "perPage": initial_per_page,
                "orderBy": "name",
                "orderDirection": "asc",
            }
            response = self._request("GET", "api/foods", params=params)

            total = response["total"]
            if total > initial_per_page:
                response = self._request(
                    "GET",
                    "api/foods",
                    params=params | {"perPage": total},
                )
            self._foods = response["items"]

        return self._foods

    @property
    def foods(self) -> List[Dict[str, Any]]:
        """Getter for foods data."""
        return self.load_foods()

    @property
    def shopping_list_id(self) -> str | None:
        """Getter and setter for the shopping list ID."""
        return self._shopping_list_id

    @shopping_list_id.setter
    def shopping_list_id(self, shopping_list_id: str) -> None:
        # If the shopping list ID changes, reset the cached shopping items
        if shopping_list_id != self._shopping_list_id:
            self._shopping_items = None
        self._shopping_list_id = shopping_list_id

    def load_shopping_items(
        self, per_page: int = N_ITEMS, force: bool = False
    ) -> List[Dict[str, Any]]:
        """Retrieve unchecked items from Mealie shopping lists."""
        if self._shopping_items is None or force:
            page = 1
            params = {
                "page": page,
                "perPage": per_page,
                "orderBy": "checked",
                "orderDirection": "asc",
            }
            items = []
            while True:
                response = self._request(
                    "GET", "api/households/shopping/items", params=params
                )
                new_items = [
                    item for item in response["items"] if not item["checked"]
                ]
                items.extend(new_items)

                page += 1
                params["page"] = page

                if len(new_items) < per_page or not response["next"]:
                    break

            if self._shopping_list_id:
                items = [
                    item
                    for item in items
                    if item["shoppingListId"] == self._shopping_list_id
                ]
            self._shopping_items = items

        return self._shopping_items

    @property
    def shopping_items(self) -> List[Dict[str, Any]]:
        """Get shopping items."""
        return self.load_shopping_items()

    def add_shopping_items(self, items: List[Dict[str, Any]]):
        """Add items to the shopping list."""
        for item in items:
            if self._shopping_list_id:
                item.update({"shoppingListId": self._shopping_list_id})
            if not item.get("shoppingListId"):
                raise ValueError("Item is missing required key shoppingListId")

        return self._request(
            "POST",
            endpoint="api/households/shopping/items/create-bulk",
            data=items,
        )

    def delete_shopping_items(self, ids: List[str]):
        """Delete items from the shopping list by ID."""
        return self._request(
            "DELETE",
            endpoint="api/households/shopping/items",
            params={"ids": ids},
        )

    def parse_items(self, items: List[str]) -> List[Dict[str, Any]]:
        """Parse item names into food item dictionaries."""
        response = self._request(
            "POST",
            endpoint="api/parser/ingredients",
            data={"parser": "nlp", "ingredients": items},
        )
        return [item["ingredient"] for item in response["content"]]
