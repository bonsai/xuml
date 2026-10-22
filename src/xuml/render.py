"""Small dependency-free SVG renderer for the first vertical slice."""
from __future__ import annotations

from html import escape
from typing import Any


def render_svg(route_result: dict[str, Any], title: str | None = None) -> str:
    selected = route_result.get("selected") or {}
    heading = title or selected.get("title") or "xuml — no matching design"
    status = route_result.get("status", "unknown")
    dimensions = route_result.get("requested", {})
    rows = [f"{key}: {value}" for key, value in sorted(dimensions.items())]
    rows += [f"Matched: {', '.join(route_result.get('matched_dimensions', [])) or 'none'}"]
    rows += [f"Warnings: {'; '.join(route_result.get('warnings', [])) or 'none'}"]
    height = max(190, 110 + len(rows) * 26)
    text_rows = "".join(
        f'<text x="28" y="{104 + i * 26}" font-family="system-ui, sans-serif" font-size="14" fill="#263238">{escape(row)}</text>'
        for i, row in enumerate(rows)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" viewBox="0 0 900 {height}" width="900" height="{height}">
  <title id="title">{escape(heading)}</title>
  <desc id="desc">xuml route result, status {escape(status)}</desc>
  <rect width="900" height="{height}" rx="16" fill="#f7f8fa"/>
  <rect width="900" height="66" rx="16" fill="#e8edf2"/>
  <text x="28" y="41" font-family="system-ui, sans-serif" font-size="23" font-weight="700" fill="#18212b">{escape(heading)}</text>
  <text x="870" y="40" text-anchor="end" font-family="monospace" font-size="13" fill="#455a64">{escape(status)}</text>
  {text_rows}
</svg>
'''
