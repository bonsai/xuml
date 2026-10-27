"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from . import __version__
from .analyze import analyze_python
from .render import render_svg, write_svg_atomic
from .source import SourceError, load_source


def _default_output(source_name: str) -> Path:
    return Path(f"{Path(source_name).stem or 'diagram'}.svg")


def _default_puml_output(source_value: str) -> Path:
    path = Path(source_value).expanduser()
    name = path.stem if path.is_file() else (path.name or "diagram")
    return Path(f"{name}.puml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xuml",
        description="Choose a Python diagram engine: xuml (SVG) or py2puml (PlantUML).",
        epilog=(
            "Examples:\n"
            "  xuml -svg ./module.py\n"
            "  xuml -svg https://github.com/owner/repo/blob/main/src/module.py\n"
            "  xuml -pyu ./my_package -o my-package.puml\n"
            "  xuml -pyu ./my_package/module.py -o module.puml"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"xuml {__version__}")
    parser.add_argument("source", nargs="?", help="local Python file (alternative to -svg or -pyu)")
    engines = parser.add_mutually_exclusive_group()
    engines.add_argument("-svg", dest="svg_source", metavar="SOURCE", help="use xuml's native SVG engine")
    engines.add_argument(
        "-pyu",
        dest="pyu_source",
        metavar="PATH",
        help="use py2puml to generate PlantUML from a local Python file or package directory",
    )
    parser.add_argument("-o", "--output", metavar="FILE", help="output file (SVG for -svg, PUML for -pyu)")
    return parser


def _run_py2puml(source_value: str, output: Path) -> int:
    if "://" in source_value:
        print(
            "xuml: error: -pyu requires a local Python file or package directory; "
            "remote URLs are not supported by py2puml.",
            file=sys.stderr,
        )
        return 1

    uvx = shutil.which("uvx")
    if not uvx:
        print("xuml: error: uvx was not found. Install uv: https://docs.astral.sh/uv/", file=sys.stderr)
        return 1

    command = [
        uvx, "--from", "py2puml", "py2puml",
        "--path", str(Path(source_value).expanduser()),
        "--output-file", str(output),
    ]
    try:
        result = subprocess.run(command, check=False)
    except OSError as exc:
        print(f"xuml: error: could not start py2puml via uvx: {exc}", file=sys.stderr)
        return 1

    if result.returncode != 0:
        print(f"xuml: py2puml failed with exit code {result.returncode}", file=sys.stderr)
        return result.returncode
    print(f"PlantUML written: {output}")
    print("Engine: py2puml")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source_value = args.svg_source or args.pyu_source or args.source
    if not source_value:
        parser.error("provide a source path or use -svg <source> / -pyu <path>")

    if args.pyu_source:
        output = Path(args.output).expanduser() if args.output else _default_puml_output(source_value)
        return _run_py2puml(source_value, output)

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
    print("Engine: xuml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
