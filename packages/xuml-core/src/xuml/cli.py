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


def _run_py2puml(source_value: str, output_value: str | None) -> int:
    source_path = Path(source_value).expanduser()
    if not source_path.exists() or not source_path.is_dir():
        print(f"xuml: error: -pyu requires an existing Python package directory: {source_path}", file=sys.stderr)
        return 1

    executable = shutil.which("py2puml")
    if executable is None:
        print(
            "xuml: error: py2puml is not installed or not on PATH. Install it with: "
            "python -m pip install py2puml",
            file=sys.stderr,
        )
        return 1

    module_name = source_path.name
    try:
        result = subprocess.run(
            [executable, str(source_path), module_name],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"xuml: error: could not start py2puml: {exc}", file=sys.stderr)
        return 1

    if result.returncode != 0:
        message = result.stderr.strip() or f"py2puml exited with status {result.returncode}"
        print(f"xuml: py2puml: {message}", file=sys.stderr)
        return result.returncode or 1

    output = Path(output_value).expanduser() if output_value else Path(f"{module_name}.puml")
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.stdout, encoding="utf-8")
    except OSError as exc:
        print(f"xuml: error: could not write {output}: {exc}", file=sys.stderr)
        return 1

    print(f"PlantUML written: {output}")
    print("Engine: py2puml")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xuml",
        description="Choose a source-to-diagram engine.",
        epilog=(
            "Examples:\\n"
            "  xuml -svg ./module.py\\n"
            "  xuml -svg ./module.py -o module.svg\\n"
            "  xuml -pyu ./mypackage\\n"
            "  xuml -pyu ./mypackage -o class-diagram.puml\\n"
            "Install the optional py2puml engine with: python -m pip install py2puml"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"xuml {__version__}")
    parser.add_argument("--list-engines", action="store_true", help="list available diagram engines")
    parser.add_argument("source", nargs="?", help="local Python file (defaults to the -svg engine)")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("-svg", dest="svg_source", metavar="SOURCE", help="xuml built-in engine: Python file or GitHub blob URL")
    modes.add_argument("-pyu", dest="pyu_source", metavar="PACKAGE_DIR", help="run external py2puml on a local Python package directory")
    parser.add_argument("-o", "--output", metavar="FILE", help="output file path (SVG or PlantUML depending on engine)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_engines:
        print("svg     xuml built-in Python AST -> SVG")
        print(f"pyu     py2puml external engine ({'available' if shutil.which('py2puml') else 'not installed'})")
        return 0

    if args.pyu_source:
        if args.source:
            parser.error("do not combine a positional source with -pyu")
        return _run_py2puml(args.pyu_source, args.output)

    source_value = args.svg_source or args.source
    if not source_value:
        parser.error("provide a source file or use -svg <source> or -pyu <package-directory>")

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
