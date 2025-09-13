"""General utility functions."""

import textwrap
from typing import Optional

from docstring_parser import Docstring, DocstringParam, DocstringReturns, parse


def _format_param(p: DocstringParam) -> str:
    """Format a parameter into Google style."""
    type_str = f" ({p.type_name})" if p.type_name else ""
    desc = f": {p.description}" if p.description else ""
    return f"    {p.arg_name}{type_str}{desc}"


def _format_returns(ret: DocstringReturns) -> str:
    """Format a return section into Google style."""
    type_str = f" {ret.type_name}" if ret.type_name else ""
    desc = f": {ret.description}" if ret.description else ""
    return f"    {type_str}{desc}".rstrip()


def _convert_docstring(docstring: Optional[str]) -> str:
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
