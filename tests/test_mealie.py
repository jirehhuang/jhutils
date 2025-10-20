"""Test Mealie module."""

import numpy as np
import pytest


def test_load_foods(mealie):
    """Test that method .load_foods() executes successfully."""
    foods = mealie.load_foods(initial_per_page=1, force=True)
    assert isinstance(foods, list)


def test_set_shopping_list(mealie, mealie_shopping_list_id):
    """Test that method .set_shopping_list executes successfully."""
    mealie.shopping_list_id = mealie_shopping_list_id
    assert mealie.shopping_list_id == mealie_shopping_list_id
    mealie.shopping_list_id = None
    assert not mealie.shopping_list_id


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


def test_add_shopping_items_no_list(mealie):
    """Test that a ValueError is raised when attempting to add items without a
    shopping list."""
    msg = "Item is missing required key shoppingListId"
    mealie.shopping_list_id = None
    with pytest.raises(ValueError, match=msg):
        mealie.add_shopping_items([{"note": "potatoes"}])


def test_add_delete_shopping_items(mealie, mealie_shopping_list_id):
    """Test that items can be successfully added to and deleted from a shopping
    list."""
    items_before = mealie.load_shopping_items(force=True)
    mealie.shopping_list_id = mealie_shopping_list_id
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
    response = mealie.add_shopping_items(items)
    mealie.delete_shopping_items(
        [
            item["id"]
            for item in response["createdItems"] + response["updatedItems"]
        ]
    )
    items_after = mealie.load_shopping_items(force=True)
    assert items_before == items_after


def test_parse_items(mealie):
    """Test that method .parse_items() correctly parses a list of
    strings into a list of dictionaries."""
    items = ["milk", "2 eggs", "flour (1kg)"]
    parsed_items = mealie.parse_items(items)
    assert [item["display"] for item in parsed_items] == [
        "milk",
        "2 eggs",
        "1 kilogram flour",
    ]
