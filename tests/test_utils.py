"""Test utilities."""

from datetime import datetime

import pytest
import pytz
from docstring_parser import parse

from jhutils._utils import _convert_docstring, _match_phrase, _time_id
from jhutils.agent.tools._tools import AVAILABLE_MODES


def func_numpy(a: int = 1, b: int = 2) -> int:
    """Add two numbers.

    Parameters
    ----------
    a : int
        First
        number.
    b : int
        Second
        number.

    Returns
    -------
    int
        Sum of the
        numbers.
    """
    return a + b


def func_google(name: str = "") -> None:
    """Say hello.

    Args:
        name (str): Person's
            name.

    Returns
    -------
        None: Nothing is
            returned.
    """
    print(f"Hello, {name}!")


def func_mixed(x: float = 1.0) -> float:
    """Square a number.

    Square a number and return the result.

    This is a new paragraph in the long description.

    Parameters
    ----------
    x : float
        Value to
        square.
        - Bullet point in a list
        - Another bullet point

    Returns
    -------
    float
        Squared
        value.

    Notes
    -----
    This is an extra section that should be ignored.
    """
    return x * x


def no_docstring():  # noqa: D103
    pass


@pytest.mark.parametrize(
    "func", [func_numpy, func_google, func_mixed, no_docstring]
)
def test_convert_docstring_equivalence(func):
    """Test that converting preserves parsed docstring semantics."""
    func()  # For code coverage
    input_doc = func.__doc__
    output_doc = _convert_docstring(input_doc)

    parsed_in = parse(input_doc)
    parsed_out = parse(output_doc)

    # Compare description fields
    assert parsed_in.short_description == parsed_out.short_description
    assert (parsed_in.long_description or "").strip() == (
        parsed_out.long_description or ""
    ).strip()

    # Compare parameters
    assert len(parsed_in.params) == len(parsed_out.params)
    for p_in, p_out in zip(parsed_in.params, parsed_out.params, strict=False):
        assert p_in.arg_name == p_out.arg_name
        assert (p_in.type_name or "").strip() == (
            p_out.type_name or ""
        ).strip()
        assert (p_in.description or "").strip() == (
            p_out.description or ""
        ).strip()

    # Compare returns (optional)
    if parsed_in.returns or parsed_out.returns:
        assert parsed_in.returns is not None
        assert parsed_out.returns is not None
        assert (parsed_in.returns.type_name or "").strip() == (
            parsed_out.returns.type_name or ""
        ).strip()
        assert (parsed_in.returns.description or "").strip() == (
            parsed_out.returns.description or ""
        ).strip()


def test_time_id():
    """Test that the _time_id function returns a string of the expected
    format."""
    tid = _time_id(timezone="utc")
    assert isinstance(tid, str)
    time_from_id = pytz.utc.localize(
        datetime.strptime(tid, "%Y-%m-%d_%H-%M-%S-%f")
    )
    delta = 10
    assert (
        abs((datetime.now(pytz.utc) - time_from_id).total_seconds()) <= delta
    )


def test_match_none_if_no_phrases():
    """Test that _match_phrase returns None if no phrases are provided."""
    assert _match_phrase("test query", phrases=[]) is None


def test_exact_match_phrase():
    """Test that exact matches are correctly identified."""
    phrases = ["apple", "banana", "cherry"]
    for phrase in phrases:
        assert _match_phrase(phrase, phrases=phrases) == phrase


def test_empty_query_match_is_none():
    """Test that result is None if no query is provided."""
    assert _match_phrase("", phrases=["apple", "banana", "cherry"]) is None


@pytest.mark.parametrize(
    "query,expected",
    [
        ("activate testing mode", "testing"),
        ("go back to general mode", "general"),
        ("I'm going shopping", "shopping"),
        ("start cooking soon", "cooking"),
        ("theology mode", "theology"),
    ],
)
def test_fuzzy_match_modes(query: str, expected: str):
    """Test that queries can correctly match available modes."""
    assert (
        _match_phrase(
            query,
            phrases=list(AVAILABLE_MODES.keys()),
            as_index=False,
            score_cutoff=85,
        )
        == expected
    )


@pytest.mark.parametrize(
    "query,expected",
    [
        ("just some random text", None),
        ("completely unrelated sentence", None),
        ("Bible study mode", None),
        ("non-existent mode", None),
    ],
)
def test_fail_to_match_modes(query: str, expected: str):
    """Test that no mode is matched if the minimum score is not met.
    Can be used to calibrate the default score_cutoff threshold."""
    assert (
        _match_phrase(
            query,
            phrases=list(AVAILABLE_MODES.keys()),
            as_index=False,
            score_cutoff=85,
        )
        == expected
    )
