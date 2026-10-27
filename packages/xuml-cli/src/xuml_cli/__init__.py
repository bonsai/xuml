"""xuml CLI entry point."""

from __future__ import annotations

from xuml.cli import main as _main

def main() -> int:
    import sys
    # Skill-integrated jar engine support: python reads jar directly
    # via xuml-plantuml (PlantUMLRenderer) or skill scripts
    return _main(sys.argv[1:])

if __name__ == "__main__":
    raise SystemExit(main())