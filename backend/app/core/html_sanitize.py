"""Sanitize HTML for safe browser rendering (labels, print views)."""

from html import escape
from html.parser import HTMLParser


class _Sanitizer(HTMLParser):
    _ALLOWED_TAGS = frozenset(
        {
            "html",
            "head",
            "body",
            "title",
            "style",
            "h1",
            "h2",
            "h3",
            "div",
            "span",
            "p",
            "b",
            "strong",
            "br",
        },
    )
    _DROP_TAGS = frozenset({"script", "iframe", "object", "embed", "link", "meta", "base"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lower = tag.lower()
        if lower in self._DROP_TAGS:
            return
        if lower not in self._ALLOWED_TAGS:
            return
        safe_attrs = []
        for name, value in attrs:
            lname = name.lower()
            if lname.startswith("on") or lname in {"src", "href", "xlink:href", "formaction"}:
                continue
            if value is None:
                safe_attrs.append(f" {lname}")
            else:
                safe_attrs.append(f' {lname}="{value}"')
        self._parts.append(f"<{lower}{''.join(safe_attrs)}>")

    def handle_endtag(self, tag: str) -> None:
        lower = tag.lower()
        if lower in self._DROP_TAGS or lower not in self._ALLOWED_TAGS:
            return
        self._parts.append(f"</{lower}>")

    def handle_data(self, data: str) -> None:
        self._parts.append(escape(data))

    def handle_entityref(self, name: str) -> None:
        self._parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._parts.append(f"&#{name};")

    def get_html(self) -> str:
        return "".join(self._parts)


def sanitize_html(html: str) -> str:
    parser = _Sanitizer()
    parser.feed(html)
    parser.close()
    return parser.get_html()
