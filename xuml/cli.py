"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .analyze import analyze_python
from .render import render_svg, write_svg_atomic
from .source import SourceError, load_source


def _default_output(source_name: str) -> Path:
    return Path(f"{Path(source_name).stem or 'diagram'}.svg")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xuml",
        description="Analyze Python source without executing it and generate an SVG diagram.",
        epilog=(
            "Examples:\n"
            "  xuml -svg ./module.py\n"
            "  xuml -svg https://github.com/owner/repo/blob/main/src/module.py\n"
            "  xuml -svg https://github.com/owner/repo/blob/main/src/module.py -o out.svg"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"xuml {__version__}")
    parser.add_argument("source", nargs="?", help="local Python file (alternative to -svg)")
    parser.add_argument("-svg", dest="svg_source", metavar="SOURCE", help="source file path or GitHub blob URL")
    parser.add_argument("-o", "--output", metavar="SVG", help="output SVG path (default: <source-name>.svg)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source_value = args.svg_source or args.source
    if not source_value:
        parser.error("provide a source file or use -svg <source-url>")

    try:
        source = load_source(source_value)
        ir = analyze_python(source.text, source.name, source.origin)
        svg = render_svg(ir)
        output = Path(args.output).expanduser() if args.output else _default_output(source.name)
        written = write_svg_atomic(output, svg)
    except (SourceError, ValueError, OSError) as exc:
        print(f"xuml: error: {exc}", file=sys.stderr)
        return 1

    print(f"SVG written: {written}")
    print(f"IR: {len(ir['nodes'])} nodes, {len(ir['edges'])} relations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
