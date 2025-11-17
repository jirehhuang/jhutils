"""Test Mealie module."""

import numpy as np
import pytest

from jhutils import Mealie

TEST_RECIPE_NAME = "Al Pastor"


def _add_temporary_shopping_items(mealie, items):
    """Temporarily add items to the shopping list.

    Helper function to add items to the shopping list temporarily and then
    promptly delete them.
    """
    items_before = mealie.load_shopping_items(force=True)
    response = mealie.add_shopping_items(items)
    mealie.delete_shopping_items(
        [
            item["id"]
            for item in response["createdItems"] + response["updatedItems"]
        ]
    )
    items_after = mealie.load_shopping_items(force=True)
    assert items_before == items_after
    return response


def test_error_if_no_api_url():
    """Test that a ValueError is raised if the api_url argument is not
    provided."""
    msg = '"api_url" required to initialize Mealie instance.'
    with pytest.raises(ValueError, match=msg):
        Mealie(api_url="", api_key="api_key")


def test_error_if_no_api_key():
    """Test that a ValueError is raised if the api_key argument is not
    provided."""
    msg = '"api_key" required to initialize Mealie instance.'
    with pytest.raises(ValueError, match=msg):
        Mealie(api_url="api_url", api_key="")


def test_load_foods(mealie):
    """Test that method .load_foods() executes successfully."""
    foods = mealie.load_foods(initial_per_page=1, force=True)
    assert isinstance(foods, list)


def test_load_shopping_lists(mealie):
    """Test that method .load_shopping_lists() executes successfully."""
    shopping_lists = mealie.load_shopping_lists(initial_per_page=1, force=True)
    assert isinstance(shopping_lists, list)


def test_get_shopping_list_id(mealie):
    """Test that getting property shopping_list_id loads the first shopping
    list if not set."""
    mealie.shopping_list_id = None
    assert isinstance(mealie.shopping_list_id, str)


def test_set_shopping_list(mealie, mealie_shopping_list_id):
    """Test that method .set_shopping_list executes successfully."""
    mealie.shopping_list_id = mealie_shopping_list_id
    assert mealie.shopping_list_id == mealie_shopping_list_id
    mealie.shopping_list_id = None
    assert mealie._shopping_list_id is None  # pylint: disable=protected-access
    mealie.shopping_list_id = "id"
    assert mealie.shopping_list_id == "id"


def test_load_shopping_items(mealie):
    """Test that shopping_items property can be successfully retrieved."""
    items = mealie.load_shopping_items(per_page=1, force=True)
    assert np.array_equal(items, mealie.shopping_items)


def test_load_shopping_items_invalid_list(mealie):
    """Test that an empty shopping list is returned when an invalid list ID is
    provided."""
    mealie.shopping_list_id = "invalid_id"
    items = mealie.shopping_items
    assert not items


def test_load_recipes(mealie):
    """Test that recipes property can be successfully retrieved."""
    recipes = mealie.load_recipes()
    assert np.array_equal(recipes, mealie.recipes)
    assert isinstance(mealie.recipe_names, list)
    assert len(mealie.recipe_names) == len(mealie.recipes)


def test_get_recipe(mealie):
    """Test that method .get_recipe() executes successfully."""
    recipe_name = TEST_RECIPE_NAME
    assert isinstance(mealie.get_recipe(recipe_name), dict)


def test_get_scaled_recipe(mealie):
    """Test that method .get_recipe() correctly scales the recipe."""
    recipe_name = TEST_RECIPE_NAME
    recipe = mealie.get_recipe(recipe_name, scale_factor=1)
    scaled_recipe = mealie.get_recipe(recipe_name, scale_factor=7)
    assert (
        scaled_recipe["recipeIngredient"][0]["quantity"]
        == 7 * recipe["recipeIngredient"][0]["quantity"]
    )
    assert scaled_recipe["recipeIngredient"][0]["display"].startswith("7 x ")

    scaled_recipe = mealie.get_recipe(recipe_name, target_servings=123)
    assert " x " in scaled_recipe["recipeIngredient"][0]["display"]


def test_read_recipe(mealie):
    """Test that method .read_recipe() executes successfully."""
    recipe_name = TEST_RECIPE_NAME
    markdown_recipe = mealie.read_recipe(recipe_name)
    assert f"# {recipe_name}" in markdown_recipe
    assert "- Servings:" in markdown_recipe
    assert "- Total Time:" in markdown_recipe
    assert "- Prep Time:" in markdown_recipe
    assert "- Cook Time:" not in markdown_recipe  # Not working in Mealie API
    assert "- Yield:" in markdown_recipe


def test_read_scaled_recipe(mealie):
    """Test that method .read_recipe() correctly scales the recipe."""
    recipe_name = TEST_RECIPE_NAME
    assert "7 x " in mealie.read_recipe(recipe_name, scale_factor=7)
    assert " x " in mealie.read_recipe(recipe_name, target_servings=123)


def test_add_delete_shopping_items(mealie):
    """Test that items can be successfully added to and deleted from a shopping
    list."""
    items = [
        {"note": "test non-food example"},
        {
            "note": "example",
            "foodId": next(
                food["id"]
                for food in mealie.foods
                if food["name"] == "test food"
            ),
        },
    ]
    _add_temporary_shopping_items(mealie, items)


def test_parse_and_add_items(mealie):
    """Test that method .parse_items() correctly parses a list of
    strings into a list of dictionaries and can be added to the shopping
    list."""
    items = [
        "4 tbsp kosher salt, from Walmart",
        "little sheep spicy broth",
        "test food (1kg)",
    ]
    parsed_items = mealie.parse_items(items, as_payload=True)
    assert [item["name"] for item in parsed_items] == [
        "kosher salt",
        "Little Sheep spicy broth",
        "test food",
    ]
    _add_temporary_shopping_items(mealie, parsed_items)
