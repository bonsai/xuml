# xuml-core

Core semantic IR, analysis, and rendering library for xuml.

## Modules

- `xuml.analyze` — Python AST → semantic IR
- `xuml.render` — IR → SVG rendering
- `xuml.source` — Source loading (local files, GitHub URLs)
- `xuml.cli` — CLI entry point (also available via `xuml-cli` package)

## Installation

```bash
pip install -e packages/xuml-core
```

## Development

```bash
cd packages/xuml-core
pip install -e ".[dev]"
pytest
```