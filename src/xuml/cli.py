"""Command-line entry point for xuml."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from xuml.catalog import CatalogError, load_catalog, load_dimensions, load_yaml
from xuml.render import render_svg
from xuml.router import route
from xuml.validate import validate_intent


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="xuml", description="Route typed diagram intent through a YAML catalog.")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="Validate catalog and dimension definitions")
    check.add_argument("--catalog", default="schemas/catalog.yaml")
    check.add_argument("--dimensions", default="schemas/dimensions.yaml")
    run = sub.add_parser("route", help="Route a YAML intent and emit JSON plus optional SVG")
    run.add_argument("intent", help="Path to intent YAML")
    run.add_argument("--catalog", default="schemas/catalog.yaml")
    run.add_argument("--dimensions", default="schemas/dimensions.yaml")
    run.add_argument("--json-out", default="-", help="JSON output path or '-' for stdout")
    run.add_argument("--svg-out", help="Optional SVG output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
        dimension_spec = load_dimensions(args.dimensions)
        if args.command == "check":
            print(json.dumps({"status": "ok", "catalog_entries": len(catalog["entries"]), "dimensions": len(dimension_spec["dimensions"])}, indent=2))
            return 0
        intent = load_yaml(args.intent)
        diagnostics = validate_intent(intent, dimension_spec)
        result = route(intent, catalog)
        result["diagnostics"] = diagnostics
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.json_out == "-":
            print(payload, end="")
        else:
            Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.json_out).write_text(payload, encoding="utf-8")
        if args.svg_out:
            Path(args.svg_out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.svg_out).write_text(render_svg(result), encoding="utf-8")
        return 0 if result["status"] == "matched" else 2
    except (CatalogError, ValueError) as exc:
        print(f"xuml: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
