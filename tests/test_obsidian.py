"""Test Obsidian module."""

import os

import pytest


def test_list_files(obsidian):
    """Test that method .list_files() executes successfully and contains
    selected expected files."""
    obsidian.list_files("Inbox")
    expected_file_names = {"Eventually", "README.md"}
    file_names = {file["name"] for file in obsidian.files["Inbox"]}
    assert file_names.intersection(expected_file_names) == expected_file_names


def test_read_file(obsidian):
    """Test that method .read_file() executes successfully."""
    expected_start_text = "All new notes start in this folder."
    obsidian.read_file("Inbox/README.md")
    assert obsidian.files["Inbox/README.md"]["content"].startswith(
        expected_start_text
    )


def test_read_nonexistent_file(obsidian):
    """Test that an error is raised if method .read_file() is used on a
    non-existent file."""
    with pytest.raises(Exception) as e:
        obsidian.read_file("nonexistent-file.md")
    assert "404 Client Error" in str(e.value)


def test_add_existing_file(obsidian):
    """Test that an error is raised if method .add_file() is used on an
    existing file."""
    with pytest.raises(Exception) as e:
        obsidian.add_file("Inbox/README.md", "This is a test content.")
    assert "422 Client Error" in str(e.value)


def test_add_update_delete_file(obsidian):
    """Test that method .add_file() and .delete_file() behave as expected."""
    file_path = "Inbox/temp-note.md"
    content = "This is a temporary note."

    # Add file and verify that it exists and has the correct content
    obsidian.add_file(file_path, content)
    assert file_path in [
        file["path"]
        for file in obsidian.list_files(os.path.dirname(file_path))
    ]
    assert obsidian.read_file(file_path)["content"] == content

    # Update file and verify that it has the correct updated content
    new_content = "This is an updated temporary note."
    obsidian.update_file(file_path, content=new_content)
    assert file_path in [
        file["path"]
        for file in obsidian.list_files(os.path.dirname(file_path))
    ]
    assert obsidian.read_file(file_path)["content"] == new_content

    # Delete file and verify that it no longer exists
    obsidian.delete_file(file_path)
    assert file_path not in [
        file["path"]
        for file in obsidian.list_files(os.path.dirname(file_path))
    ]


def test_add_tasks(obsidian):
    """Test that method .add_tasks() behaves as expected."""
    tasks = [
        "Visit parents",
        "Call Andrew",
        "Finish drafting announcements",
    ]
    response = obsidian.add_tasks(tasks)
    assert "content" in response
