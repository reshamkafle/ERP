"""HTML escaping for user-controlled strings rendered in templates."""

from html import escape


def escape_html(value: object | None) -> str:
    """Escape a value for safe inclusion in HTML text nodes and attributes."""
    if value is None:
        return ""
    return escape(str(value), quote=True)
