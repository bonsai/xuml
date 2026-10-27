# xuml

xuml makes existing and AI-generated code easier to inspect. It extracts source structure into a common semantic intermediate representation (IR), checks implementation against design, and generates reviewable diagrams.

**Status:** design/bootstrap. Local-first core; the same diagram-generation engine is intended to be exposed through CLI, MCP, and a versioned HTTP API/server so compatible clients can generate SVG from intent.

## Monorepo Structure

```
xuml/
├── packages/
│   ├── xuml-core/        # Core semantic IR, analysis, rendering
│   ├── xuml-cli/         # CLI entry point (xuml command)
│   └── xuml-plantuml/    # PlantUML rendering integration
├── .agents/skills/
│   └── plantuml-jar/     # Skill: offline PlantUML rendering
├── docs/                 # Documentation portal
│   ├── index.html
│   ├── diagram/          # Architecture diagrams
│   └── design/           # Design proposals
├── artifacts/            # Generated artifacts (gitignored)
├── tools/                # Development scripts
├── pyproject.toml        # Workspace config
├── README.md
└── SKILLS.md             # Skills index
```

## Quick Start

### Install all packages (development)

```bash
# Using uv (recommended)
uv sync

# Or with pip
pip install -e packages/xuml-core
pip install -e packages/xuml-cli
pip install -e packages/xuml-plantuml
```

### Generate SVG from Python source (built-in engine)

```bash
xuml -svg ./module.py -o module.svg
```

### Generate PlantUML from Python package (py2puml engine)

```bash
pip install py2puml
xuml -pyu ./mypackage -o class-diagram.puml
```

### Render PlantUML to SVG (offline, using skill)

```bash
# Using skill script
bash .agents/skills/plantuml-jar/scripts/render.sh class-diagram.puml -tsvg

# Or from Python
python -c "from xuml_plantuml import render_puml; render_puml('class-diagram.puml', 'svg')"
```

### List available engines

```bash
xuml --list-engines
```

## Documentation

- [Documentation portal](docs/index.html)
- [Architecture diagram (SVG)](docs/diagram/architecture.svg)
- [Architecture source (Mermaid)](docs/diagram/architecture.mmd)
- [Architecture source (PlantUML)](docs/diagram/architecture.puml)
- [Skills index](SKILLS.md)

## Issues are Canonical

All detailed requirements, design decisions, ADRs, acceptance criteria, implementation plans, open questions, and verification results live in GitHub Issues.

- [Issue #1 — Local-first analysis CLI](https://github.com/bonsai/xuml/issues/1)
- [Issue #2 — Minimal docs policy](https://github.com/bonsai/xuml/issues/2)
- [Issue #3 — Intent-to-SVG MCP/API/server](https://github.com/bonsai/xuml/issues/3)
- [Issue #4 — Architecture decisions and open questions](https://github.com/bonsai/xuml/issues/4)
- [ADR-0001 — Accepted local-first hybrid architecture](https://github.com/bonsai/xuml/issues/5)

## Architecture in Brief

Source adapters → parser/analyzer → semantic IR → validators → render plugins.

The semantic model is canonical. AST, graph, and layout are derived projections; layout changes must not change model meaning. Keep confirmed static facts, inferred relations, runtime observations, and unknowns distinct.

## Repository Policy

- Keep docs limited to index.html and diagrams under docs/diagram/.
- Keep diagram sources and rendered output together (.puml, .mmd, .svg).
- Put all specifications, ADRs, design discussions, acceptance criteria, and progress in tagged GitHub Issues.
- Pages deployment entry point: .github/workflows/dep-pages.yml.
- JSON for versioned contracts and IR; YAML for configuration/templates; JSONL for append-only event history.
- Local SQLite first; PostgreSQL and object storage are optional later server components.
- Serious CI errors block merge; waivers require a reason, approver, expiry, linked Issue, and rule ID.
- Failed validation must preserve last-known-good generated outputs.

## Development

```bash
# Run tests
cd packages/xuml-core && pytest

# Install skill dependencies
bash .agents/skills/plantuml-jar/scripts/ensure-jar.sh
```