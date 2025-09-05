"""Test Mealie module."""

import pytest


def test_get_foods(mealie):
    """Test that method .get_foods() executes successfully."""
    foods = mealie.get_foods(initial_perPage=1)
    assert isinstance(foods, list)


def test_set_shopping_list(mealie, mealie_shopping_list_id):
    """Test that method .set_shopping_list executes successfully."""
    mealie.shopping_list_id = mealie_shopping_list_id
    assert mealie.shopping_list_id == mealie_shopping_list_id
    mealie.shopping_list_id = None
    assert not mealie.shopping_list_id


def test_get_shopping_items(mealie):
    """Test that method .get_shopping_items() executes successfully."""
    items = mealie.get_shopping_items(perPage=1)
    assert isinstance(items, list)


def test_get_shopping_items_invalid_list(mealie):
    """Test that method .get_shopping_items() executes successfully."""
    mealie.shopping_list_id = "invalid_id"
    items = mealie.get_shopping_items()
    assert not items


def test_add_shopping_items_no_list(mealie):
    """Test that a ValueError is raised when attempting to add items without a
    shopping list.
    """
    mealie.shopping_list_id = None
    msg = "Item is missing required key shoppingListId"
    with pytest.raises(ValueError, match=msg):
        mealie.add_shopping_items([{"note": "potatoes"}])


def test_add_delete_shopping_items(mealie, mealie_shopping_list_id):
    """Test that items can be successfully added to and deleted from a shopping
    list.
    """
    items_before = mealie.get_shopping_items()
    mealie.shopping_list_id = mealie_shopping_list_id
    items = [
        {"isFood": False, "note": "non-food example"},
        {
            "isFood": True,
            "note": "food example",
            "foodId": "6062b2b6-1476-4b37-933b-b1866c9a4857",
        },
    ]
    response = mealie.add_shopping_items(items)
    mealie.delete_shopping_items(
        [
            item["id"]
            for item in response["createdItems"] + response["updatedItems"]
        ]
    )
    items_after = mealie.get_shopping_items()
    assert items_before == items_after
