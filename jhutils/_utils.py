"""General utility functions."""

import textwrap
from datetime import datetime

import pytz
from docstring_parser import Docstring, DocstringParam, DocstringReturns, parse
from rapidfuzz import fuzz, process


def _time_id(timezone="US/Pacific") -> str:
    """Generate a unique time-based identifier."""
    now = datetime.now(pytz.timezone(timezone))
    return now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]


def _format_param(p: DocstringParam) -> str:
    """Format a parameter into Google style, preserving line breaks."""
    type_str = f" ({p.type_name})" if p.type_name else ""
    desc = (p.description or "").strip()

    lines = desc.splitlines()
    formatted = [f"    {p.arg_name}{type_str}: {lines[0]}"]
    for line in lines[1:]:
        formatted.append(f"        {line.strip()}")
    return "\n".join(formatted)


def _format_returns(ret: DocstringReturns) -> str:
    """Format a return section into Google style, preserving line breaks."""
    type_str = f" {ret.type_name}" if ret.type_name else ""
    desc = (ret.description or "").strip()

    lines = desc.splitlines()
    formatted = [f"    {type_str}: {lines[0]}".rstrip()]
    for line in lines[1:]:
        formatted.append(f"        {line.strip()}")
    return "\n".join(formatted)


def _convert_docstring(docstring: str | None) -> str:
    """Convert a docstring to normalized Google style.

    Parameters
    ----------
    docstring
        Input docstring (NumPy or Google style).

    Returns
    -------
    str
        Google-style docstring containing:
        - One-line summary
        - Extended description
        - Parameters
        - Returns
    """
    if not docstring:
        return ""

    parsed: Docstring = parse(docstring)

    lines: list[str] = []

    # Summary
    if parsed.short_description:
        lines.append(parsed.short_description.strip())
        lines.append("")

    # Extended description
    if parsed.long_description:
        lines.append(textwrap.dedent(parsed.long_description).strip())
        lines.append("")

    # Parameters
    if parsed.params:
        lines.append("Args:")
        for p in parsed.params:
            lines.append(_format_param(p))
        lines.append("")

    # Returns
    if parsed.returns:
        lines.append("Returns:")
        lines.append(_format_returns(parsed.returns))
        lines.append("")

    return "\n".join(lines).strip()


def _match_phrase(
    query: str,
    phrases: list[str],
    as_index: bool = False,
    score_cutoff: float = 85,
):
    """Return best match from phrases.

    Based on an exact (case-insensitive) match first, then fuzzy match using
    WRatio score.

    Parameters
    ----------
    query
        The input text query.
    phrases
        Candidate phrases to search.
    as_index
        If True, return index of matched phrase; otherwise return the matched
        string.
    score_cutoff
        Minimum WRatio score for a fuzzy match to be considered valid.

    Returns
    -------
    str or int or None
        The matched phrase or index, or ``None`` if no candidates exist.
    """
    if not phrases:
        return None

    # Case-insensitive exact match
    lower_map = {p.lower(): i for i, p in enumerate(phrases)}
    q_lower = query.lower()

    if q_lower in lower_map:
        idx = lower_map[q_lower]
        return idx if as_index else phrases[idx]

    # Fuzzy match fallback (WRatio)
    result = process.extractOne(
        query, phrases, scorer=fuzz.WRatio, score_cutoff=score_cutoff
    )

    if result is None:
        return None

    match, _, idx = result

    return idx if as_index else match
