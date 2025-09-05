"""Mealie class."""

from typing import Any, Dict, List, Optional

import requests

N_FOODS = 500
N_ITEMS = 50


class Mealie:
    """Client for interacting with the Mealie API."""

    def __init__(self, api_url: str, api_key: str) -> None:
        self._shopping_list_id: str | None = None

        self._api_url = api_url.rstrip("/")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Make API request to endpoint with error handling."""
        url = f"{self._api_url}/{endpoint.lstrip('/')}"

        response = self.session.request(method, url, params=params, json=data)
        response.raise_for_status()

        return response.json()

    def get_foods(self, initial_perPage: int=N_FOODS) -> Dict[str, Any]:
        """Retrieve foods data."""
        params = {
            "page": 1,
            "perPage": initial_perPage,
            "orderBy": "name",
            "orderDirection": "asc",
        }
        response = self._request("GET", "api/foods", params=params)

        total = response["total"]
        if total > initial_perPage:
            response = self._request(
                "GET", "api/foods", params=params.update({"perPage": total})
            )

        return response["items"]

    @property
    def shopping_list_id(self) -> str | None:
        """Setter and getter for the shopping list ID."""
        return self._shopping_list_id

    @shopping_list_id.setter
    def shopping_list_id(self, shopping_list_id: str) -> None:
        self._shopping_list_id = shopping_list_id

    def get_shopping_items(self, perPage: int=N_ITEMS) -> List[Dict[str, Any]]:
        """Retrieve unchecked items from Mealie shopping lists."""
        params = {
            "page": 1,
            "perPage": perPage,
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
            if len(new_items) < perPage or not response["next"]:
                break

            params["page"] += 1

        if self._shopping_list_id:
            items = [
                item
                for item in items
                if item["shoppingListId"] == self._shopping_list_id
            ]
        return items

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

    def delete_shopping_items(self, ids: Dict[str, Any]):
        """Delete items from the shopping list by ID."""
        return self._request(
            "DELETE",
            endpoint="api/households/shopping/items",
            params={"ids": ids},
        )
