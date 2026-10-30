"""Static Python analysis into a small, versioned semantic IR."""

from __future__ import annotations

import ast
from typing import Any


def analyze_python(source: str, source_name: str, origin: str) -> dict[str, Any]:
    """Parse source text (never execute it) and return canonical structural IR."""
    try:
        tree = ast.parse(source, filename=source_name)
    except SyntaxError as exc:
        location = f"line {exc.lineno}" if exc.lineno else "unknown line"
        raise ValueError(f"Python parse failed at {location}: {exc.msg}") from exc

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    def add_node(kind: str, name: str, lineno: int, parent: str | None = None) -> str:
        node_id = f"{parent}.{name}" if parent else name
        nodes.append({
            "id": node_id,
            "kind": kind,
            "name": name,
            "parent": parent,
            "line": lineno,
        })
        return node_id

    module_name = source_name.removesuffix(".py") or source_name
    module_id = add_node("module", module_name, 1)

    def visit_body(body: list[ast.stmt], parent_id: str) -> None:
        for item in body:
            if isinstance(item, ast.ClassDef):
                class_id = add_node("class", item.name, item.lineno, parent_id)
                for base in item.bases:
                    base_name = ast.unparse(base)
                    edges.append({"from": class_id, "to": base_name, "kind": "inherits"})
                visit_body(item.body, class_id)
            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "async_function" if isinstance(item, ast.AsyncFunctionDef) else "function"
                function_id = add_node(kind, item.name, item.lineno, parent_id)
                # Methods are functions nested under classes in the IR.
                visit_body(item.body, function_id)
            elif isinstance(item, (ast.Import, ast.ImportFrom)):
                if isinstance(item, ast.Import):
                    imported = [alias.name for alias in item.names]
                else:
                    prefix = "." * item.level + (item.module or "")
                    imported = [prefix]
                for imported_name in imported:
                    edges.append({"from": module_id, "to": imported_name, "kind": "imports"})

    visit_body(tree.body, module_id)
    return {
        "ir_version": "1.0",
        "source": {"name": source_name, "origin": origin, "language": "python"},
        "nodes": nodes,
        "edges": edges,
    }
