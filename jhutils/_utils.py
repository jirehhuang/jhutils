"""General utility functions."""

import textwrap
from datetime import datetime

import pytz
from docstring_parser import Docstring, DocstringParam, DocstringReturns, parse


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
    docstring : str or None
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
