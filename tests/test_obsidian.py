"""Test Obsidian module."""


def test_list_files(obsidian):
    """Test that method .list_files() executes successfully."""
    obsidian.list_files("Inbox")
    expected_file_names = {"Eventually", "README.md"}
    file_names = {file["name"] for file in obsidian.files["Inbox"]}
    assert file_names.intersection(expected_file_names) == expected_file_names


def test_read_file(obsidian):
    """Test that method .read_file() executes successfully."""
    expected_start_text = "All new notes start in this folder."
    obsidian.read_file("Inbox/README.md")
    assert obsidian.files["Inbox/README.md"]["body"].startswith(
        expected_start_text
    )
