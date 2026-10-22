# xuml

xuml makes systems and AI-generated code easier to inspect. It routes typed intent through a reusable YAML catalog, validates the request, and emits a machine-readable route plus a reviewable SVG.

**Status:** Python + YAML first vertical slice. The same core is designed to be exposed through CLI, MCP, and Agent Skill interfaces later.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
xuml check
xuml route examples/intent.yaml --json-out out/route.json --svg-out out/route.svg
pytest
```

To run without installing the console script:

```bash
PYTHONPATH=src python -m xuml.cli check
PYTHONPATH=src python -m xuml.cli route examples/intent.yaml --svg-out out/route.svg
```

## First vertical slice

- **Python core:** catalog loading, validation, deterministic routing, SVG rendering, CLI.
- **YAML catalog:** reusable diagram entries declare stable IDs, supported intent dimensions, output format, template key, and assumptions.
- **Multi-dimensional intent:** domain, use case, granularity, layer, network, workflow, perspective, diagram type, output format, and constraints can coexist. Unrecognized dimensions are preserved and surfaced in warnings.
- **Traceable result:** JSON output includes selected catalog entry, matched dimensions, assumptions, unknown dimensions, and warnings.
- **Safe baseline:** routing is deterministic and local-first; model-assisted inference and remote services are intentionally deferred.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/xuml/catalog.py` | Load and check YAML catalog and dimension definitions |
| `src/xuml/router.py` | Deterministic multi-dimensional routing |
| `src/xuml/validate.py` | Intent diagnostics |
| `src/xuml/render.py` | Minimal dependency-free SVG renderer |
| `src/xuml/cli.py` | `check` and `route` commands |
| `schemas/catalog.yaml` | Starter design catalog |
| `schemas/dimensions.yaml` | Dimension vocabulary and guidance |
| `examples/intent.yaml` | Runnable sample request |
| `tests/` | Contract and routing tests |

## Issues are canonical

Detailed requirements, design decisions, acceptance criteria, implementation plans, open questions, and verification results live in GitHub Issues. Do not duplicate specifications in standalone documents.

- [Issue #3 — Intent-to-SVG MCP/API/server](https://github.com/bonsai/xuml/issues/3)
- [Issue #5 — Accepted local-first hybrid architecture](https://github.com/bonsai/xuml/issues/5)
- [Issue #6 — Shared SVG diagram quality rules](https://github.com/bonsai/xuml/issues/6)
- [Issue #8 — Ontology and gradual granularity](https://github.com/bonsai/xuml/issues/8)
- [Issue #9 — Agentic router](https://github.com/bonsai/xuml/issues/9)
- [Issue #10 — Skill, MCP server, CLI, and rich catalog](https://github.com/bonsai/xuml/issues/10)
- [Issue #11 — Python + YAML core](https://github.com/bonsai/xuml/issues/11)

## Existing architecture assets

- [Documentation portal](docs/index.html)
- [Architecture diagram (SVG)](docs/diagram/architecture.svg)
- [Architecture source (Mermaid)](docs/diagram/architecture.mmd)
- [Architecture source (PlantUML)](docs/diagram/architecture.puml)

## Next

Expand schema validation and catalog compatibility checks; add catalog-backed design templates; implement source adapters and shared semantic IR; then expose the same core through MCP and an Agent Skill. Keep generated artifacts reproducible and preserve last-known-good outputs when validation fails.
