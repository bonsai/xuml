"""Dependency-free SVG renderer for xuml semantic IR."""

from __future__ import annotations

import html
from pathlib import Path
import os
import tempfile
from typing import Any


def render_svg(ir: dict[str, Any]) -> str:
    nodes = ir.get("nodes", [])
    edges = ir.get("edges", [])
    title = str(ir.get("source", {}).get("name", "xuml diagram"))
    width = 760
    row_height = 54
    top = 76
    height = max(160, top + max(1, len(nodes)) * row_height + 30)

    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{html.escape(title)}</title>',
        '<desc id="desc">Static structure extracted by xuml from Python source.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="24" y="34" font-family="sans-serif" font-size="20" font-weight="600" fill="#172033">{html.escape(title)}</text>',
        f'<text x="24" y="55" font-family="sans-serif" font-size="11" fill="#64748b">xuml semantic IR v{html.escape(str(ir.get("ir_version", "unknown")))}</text>',
    ]

    for index, node in enumerate(nodes):
        y = top + index * row_height
        kind = str(node.get("kind", "symbol"))
        name = str(node.get("name", "unnamed"))
        parent = node.get("parent")
        line = node.get("line", "?")
        label = f"{kind}: {name}"
        if parent:
            label = f"  {label}"
        chunks.extend([
            f'<rect x="24" y="{y}" width="712" height="40" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>',
            f'<text x="38" y="{y + 17}" font-family="monospace" font-size="12" fill="#0f172a">{html.escape(label)}</text>',
            f'<text x="720" y="{y + 17}" text-anchor="end" font-family="sans-serif" font-size="10" fill="#64748b">L{html.escape(str(line))}</text>',
        ])

    if edges:
        y = top + len(nodes) * row_height + 8
        chunks.append(f'<text x="24" y="{y}" font-family="sans-serif" font-size="11" fill="#475569">Relations: {len(edges)} (imports / inheritance)</text>')
    chunks.append("</svg>")
    return "\n".join(chunks) + "\n"


def write_svg_atomic(output: str | Path, svg: str) -> Path:
    """Write a complete SVG atomically, leaving an existing file untouched on failure."""
    destination = Path(output).expanduser()
    parent = destination.parent
    if not parent.exists() or not parent.is_dir():
        raise OSError(f"Output directory does not exist: {parent}")
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            prefix=f".{destination.name}.", suffix=".tmp",
            dir=str(parent), delete=False,
        ) as stream:
            temp_name = stream.name
            stream.write(svg)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, destination)
        temp_name = None
        return destination
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
