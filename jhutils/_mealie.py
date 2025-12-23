"""Mealie class."""

import os
from typing import Any

import numpy as np
import requests

from ._utils import _match_phrase

N_PER_PAGE = 500
N_ITEMS = 50


# pylint: disable=too-many-locals
def _recipe_as_markdown(recipe: dict[str, Any]) -> str:
    """Convert a recipe dictionary to a markdown string.

    # Title

    Description (optional)

    - Servings: X (optional)
    - Total Time: Z (optional)
    - Prep Time: X (optional)
    - Cook Time: Y (optional, not working in Mealie API)
    - Yield: X yield text (optional)

    ## Ingredients

    - ingredient 1
    - ingredient 2
    ...

    ## Instructions

    ### Step title (optional)

    1. Step summary:
    Instruction text

    Step 2:
    Instruction text for step with no summary

    ## Notes (optional)

    1. Note title:
    Note text
    """
    lines = [f"# {recipe["name"]}"]

    description = recipe["description"].strip()
    if description:
        lines.append(f"\n{description}")

    metadata = {
        "recipeServings": "Servings",
        "totalTime": "Total Time",
        "prepTime": "Prep Time",
        "cookTime": "Cook Time",
        "recipeYieldQuantity": "Yield",
    }
    for key, label in metadata.items():
        value = recipe[key]

        if value:
            line = f"- {label}: {value}"

            if key == "recipeServings":
                line = "\n" + line
            elif key == "recipeYieldQuantity":
                line += f' {recipe.get("recipeYield", "").strip()}\n'

            lines.append(line)

    lines.append("\n## Ingredients\n")
    for ingredient in recipe["recipeIngredient"]:
        lines.append(f"- {ingredient['display']}".strip())

    lines.append("\n## Instructions\n")
    instructions = recipe["recipeInstructions"]
    for idx, instruction in enumerate(instructions, start=1):
        title = instruction["title"].strip()
        if title:
            lines.append(f"### {title}\n")

        summary = instruction["summary"].strip()
        lines.append(f"{idx}. {summary}:" if summary else f"Step {idx}:")

        lines.append(f"{instruction['text'].strip()}\n")

    notes = recipe["notes"]
    if notes:
        lines.append("## Notes\n")
        for idx, note in enumerate(notes, start=1):
            title = note["title"].strip()
            lines.append(f"{idx}. {title}:" if title else f"Note {idx}:")
            lines.append(f"{note['text'].strip()}\n")

    return "\n".join(lines)


class Mealie:
    """Client for interacting with the Mealie API."""

    def __init__(
        self, api_url: str, api_key: str, shopping_list_id: str | None = None
    ) -> None:
        self._shopping_list_id = shopping_list_id

        self._foods: list[dict[str, Any]] | None = None
        self._shopping_lists: list[dict[str, Any]] | None = None
        self._shopping_items: list[dict[str, Any]] | None = None
        self._recipes: list[dict[str, Any]] | None = None

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
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Make API request to endpoint with error handling."""
        url = f"{self._api_url}/{endpoint.lstrip('/')}"

        response = self.session.request(method, url, params=params, json=data)
        response.raise_for_status()

        response_json = response.json()
        if isinstance(response_json, list):
            response_json = {"content": response_json}

        return response_json

    def _get_total_items(
        self, endpoint: str, params: dict[str, Any]
    ) -> list[dict[str, Any]]:
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
    ) -> list[dict[str, Any]]:
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
    def foods(self) -> list[dict[str, Any]]:
        """Getter for foods data."""
        return self.load_foods()

    def load_shopping_lists(
        self, initial_per_page: int = N_PER_PAGE, force: bool = False
    ) -> list[dict[str, Any]]:
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
    def shopping_lists(self) -> list[dict[str, Any]]:
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
    ) -> list[dict[str, Any]]:
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
    def shopping_items(self) -> list[dict[str, Any]]:
        """Get shopping items."""
        return self.load_shopping_items()

    def load_recipes(self, force: bool = False) -> list[dict[str, Any]]:
        """Retrieve recipes data."""
        if self._recipes is None or force:
            params = {
                "page": 1,
                "perPage": N_PER_PAGE,
                "orderBy": "name",
                "orderDirection": "asc",
            }
            self._recipes = self._get_total_items("api/recipes", params)

        return self._recipes

    @property
    def recipes(self) -> list[dict[str, Any]]:
        """Getter for recipes data."""
        return self.load_recipes()

    @property
    def recipe_names(self) -> list[str]:
        """Get a list of recipe names."""
        return [recipe.get("name", "Unknown") for recipe in self.recipes]

    def get_recipe(
        self,
        recipe_name: str,
        scale_factor: float = 1,
        target_servings: int | None = None,
    ) -> dict[str, Any] | None:
        """Get a recipe by name, with optional scaling.

        Parameters
        ----------
        recipe_name
            The name of the recipe to retrieve.
        scale_factor
            Factor by which to scale ingredient quantities.
        target_servings
            If provided and ``scale_factor`` is 1, scale the recipe to this
            number of servings.
        """
        recipe_index = _match_phrase(
            recipe_name,
            phrases=self.recipe_names,
            as_index=True,
            score_cutoff=85,
        )
        recipe = (
            self.recipes[recipe_index]
            if isinstance(recipe_index, int)
            else None
        )

        if recipe is None:
            return None

        recipe = self._request("GET", f"api/recipes/{recipe['slug']}")

        recipe_servings = recipe["recipeServings"]
        if (
            recipe_servings
            and np.isclose(scale_factor, 1)
            and target_servings is not None
        ):
            scale_factor = target_servings / recipe_servings

        if not np.isclose(scale_factor, 1):
            for ingredient in recipe["recipeIngredient"]:
                if ingredient["quantity"]:
                    ingredient["quantity"] *= scale_factor

                    ingredient["display"] = (
                        f"{scale_factor:.2g} x {ingredient['display']}"
                    )

            if recipe_servings:
                recipe["recipeServings"] = int(
                    round(recipe_servings * scale_factor)
                )

        return recipe

    def read_recipe(
        self,
        recipe_name: str,
        scale_factor: float = 1,
        target_servings: int | None = None,
    ) -> str:
        """Read a recipe as Markdown, with optional scaling.

        Parameters
        ----------
        recipe_name
            The name of the recipe to retrieve.
        scale_factor
            Factor by which to scale ingredient quantities.
        target_servings
            If provided and ``scale_factor`` is 1, scale the recipe to this
            number of servings.
        """
        recipe = self.get_recipe(
            recipe_name,
            scale_factor=scale_factor,
            target_servings=target_servings,
        )

        if recipe is None:
            return f"Recipe '{recipe_name}' not found."

        return _recipe_as_markdown(recipe)

    def add_shopping_items(self, items: list[dict[str, Any]]):
        """Add items to the shopping list."""
        for item in items:
            if self.shopping_list_id:
                item.update({"shoppingListId": self.shopping_list_id})

        return self._request(
            "POST",
            endpoint="api/households/shopping/items/create-bulk",
            data=items,
        )

    def delete_shopping_items(self, ids: list[str]):
        """Delete items from the shopping list by ID."""
        return self._request(
            "DELETE",
            endpoint="api/households/shopping/items",
            params={"ids": ids},
        )

    @staticmethod
    def _parsed2payload(ingredient: dict[str, Any]) -> dict[str, Any]:
        """Convert parsed ingredient data into a payload dictionary."""
        unit = ingredient.get("unit", {}) or {}

        # Non-food items must be entered as a note
        food = ingredient.get("food", {})
        name = food.get("name", "")
        note = ingredient.get("note", "")
        if food.get("id") is None:
            food = None
            note = f"{name}, {note}" if note else name

        return {
            "name": name,
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
            "food": food,
            "note": note,
            "shoppingListId": ingredient.get("shoppingListId", None),
            "foodId": (food or {}).get("id", None),
            "unitId": unit.get("id", None),
            "checked": False,
            "position": 0,
            "extras": {},
            "id": "",
            "recipeReferences": [],
        }

    def parse_items(
        self, items: list[str], as_payload: bool = True
    ) -> list[dict[str, Any]]:
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
