"""Mealie class."""

import os
from typing import Any, Dict, List

import requests

N_PER_PAGE = 500
N_ITEMS = 50


class Mealie:
    """Client for interacting with the Mealie API."""

    def __init__(
        self, api_url: str, api_key: str, shopping_list_id: str | None = None
    ) -> None:
        self._shopping_list_id = shopping_list_id

        self._foods: List[Dict[str, Any]] | None = None
        self._shopping_lists: List[Dict[str, Any]] | None = None
        self._shopping_items: List[Dict[str, Any]] | None = None

        if not api_url:
            raise ValueError(
                '"api_url" required to initialize Mealie instance.'
            )
        self._api_url: str = api_url.rstrip("/")

        if not api_key:
            raise ValueError(
                '"api_key" required to initialize Mealie instance.'
            )
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
            shopping_list_id=os.getenv("MEALIE_SHOPPING_LIST_ID"),
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

    def _get_total_items(
        self, endpoint: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Retrieve total count from an endpoint."""
        response = self._request("GET", endpoint, params=params)

        total = response["total"]
        if total > params.get("perPage", N_PER_PAGE):
            response = self._request(
                "GET",
                endpoint,
                params=params | {"perPage": total},
            )
        return response["items"]

    def load_foods(
        self, initial_per_page: int = N_PER_PAGE, force: bool = False
    ) -> List[Dict[str, Any]]:
        """Retrieve foods data."""
        if not self._foods or force:
            params = {
                "page": 1,
                "perPage": initial_per_page,
                "orderBy": "name",
                "orderDirection": "asc",
            }
            self._foods = self._get_total_items("api/foods", params)
        return self._foods

    @property
    def foods(self) -> List[Dict[str, Any]]:
        """Getter for foods data."""
        return self.load_foods()

    def load_shopping_lists(
        self, initial_per_page: int = N_PER_PAGE, force: bool = False
    ) -> List[Dict[str, Any]]:
        """Retrieve shopping lists data."""
        if not self._shopping_lists or force:
            params = {
                "page": 1,
                "perPage": initial_per_page,
                "orderBy": "updatedAt",
                "orderDirection": "desc",
            }
            self._shopping_lists = self._get_total_items(
                "api/households/shopping/lists", params
            )
        return self._shopping_lists

    @property
    def shopping_lists(self) -> List[Dict[str, Any]]:
        """Getter for shopping lists data."""
        return self.load_shopping_lists()

    @property
    def shopping_list_id(self) -> str | None:
        """Getter and setter for the shopping list ID."""
        if not self._shopping_list_id and self.shopping_lists is not None:
            self._shopping_list_id = self.shopping_lists[0]["id"]
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

            if self.shopping_list_id:
                items = [
                    item
                    for item in items
                    if item["shoppingListId"] == self.shopping_list_id
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
            if self.shopping_list_id:
                item.update({"shoppingListId": self.shopping_list_id})

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

    @staticmethod
    def _parsed2payload(ingredient: Dict[str, Any]) -> Dict[str, Any]:
        """Convert parsed ingredient data into a payload dictionary."""
        food = ingredient.get("food", {})
        unit = ingredient.get("unit", {}) or {}

        return {
            "name": food.get("name", ""),
            "quantity": ingredient.get("quantity", 1),
            "unit": {
                "id": unit.get("id", ""),
                "name": unit.get("name", ""),
                "pluralName": unit.get("pluralName", ""),
                "description": unit.get("description", ""),
                "extras": unit.get("extras", {}),
                "fraction": unit.get("fraction", False),
                "abbreviation": unit.get("abbreviation", ""),
                "pluralAbbreviation": unit.get("pluralAbbreviation", ""),
                "useAbbreviation": unit.get("useAbbreviation", False),
                "aliases": unit.get("aliases", []),
                "createdAt": unit.get("createdAt", ""),
                "updatedAt": unit.get("updatedAt", ""),
            },
            "food": {
                "id": food.get("id", ""),
                "name": food.get("name", ""),
                "pluralName": food.get("pluralName", ""),
                "description": food.get("description", ""),
                "extras": food.get("extras", {}),
                "labelId": food.get("labelId", ""),
                "aliases": food.get("aliases", []),
                "householdsWithIngredientFood": food.get(
                    "householdsWithIngredientFood", []
                ),
                "label": food.get("label", {}),
                "createdAt": food.get("createdAt", ""),
                "updatedAt": food.get("updatedAt", ""),
            },
            "note": ingredient.get("note", ""),
            "shoppingListId": ingredient.get("shoppingListId", None),
            "foodId": food.get("id", None),
            "unitId": unit.get("id", None),
            "checked": False,
            "position": 0,
            "extras": {},
            "id": "",
            "recipeReferences": [],
        }

    def parse_items(
        self, items: List[str], as_payload: bool = True
    ) -> List[Dict[str, Any]]:
        """Parse item names into food item dictionaries."""
        response = self._request(
            "POST",
            endpoint="api/parser/ingredients",
            data={"parser": "nlp", "ingredients": items},
        )
        ingredients = [item["ingredient"] for item in response["content"]]
        if as_payload:
            ingredients = [
                self._parsed2payload(ingredient) for ingredient in ingredients
            ]
        return ingredients
