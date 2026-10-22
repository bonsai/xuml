# xuml

xuml makes existing and AI-generated code easier to inspect. It extracts source structure into a common semantic intermediate representation (IR), checks implementation against design, and generates reviewable diagrams.

**Status:** design/bootstrap. Local-first core; the same diagram-generation engine is intended to be exposed through CLI, MCP, and a versioned HTTP API/server so compatible clients can generate SVG from intent.

## Start here

- [Documentation portal](docs/index.html)
- [Architecture diagram (SVG)](docs/diagram/architecture.svg)
- [Architecture source (Mermaid)](docs/diagram/architecture.mmd)
- [Architecture source (PlantUML)](docs/diagram/architecture.puml)
- [ADR-0001: local-first hybrid architecture](docs/adr/0001-architecture.md)

## Development is Issue-first

Detailed requirements, design decisions, acceptance criteria, implementation plans, open questions, and verification results belong in GitHub Issues—not duplicated long-form documents under `docs/`.

- [Issue #1 — Local-first analysis CLI](https://github.com/bonsai/xuml/issues/1)
- [Issue #2 — Minimal docs and documentation portal](https://github.com/bonsai/xuml/issues/2)
- [Issue #3 — Intent-to-SVG MCP/API/server](https://github.com/bonsai/xuml/issues/3)
- [Issue #4 — Architecture decisions and open questions](https://github.com/bonsai/xuml/issues/4)

## Architecture in brief

Source adapters → parser/analyzer → semantic IR → validators → render plugins.

The semantic model is canonical. AST, graph, and layout are derived projections; layout changes must not change model meaning. Keep confirmed static facts, inferred relations, runtime observations, and unknowns distinct.

## Repository conventions

- Keep `docs/` limited to the portal, concise overview, stable ADRs, and diagrams.
- Store diagram source and rendered output together in `docs/diagram/` (`.puml`, `.mmd`, `.svg`).
- Pages workflow source: `wf/dep-pages.yml`; GitHub Actions entry point: `.github/workflows/dep-pages.yml`.
- JSON for versioned contracts and IR; YAML for configuration/templates; JSONL for append-only event history.
- Local SQLite first; PostgreSQL and object storage are optional later server components.
- Serious CI errors block merge; waivers require a reason, approver, expiry, linked Issue, and rule ID.
- Failed validation must preserve last-known-good generated outputs.

## First vertical slice

Python class structure → common IR → structural validation → JSON diagnostics → SVG, Mermaid, and PlantUML. Then add module dependency topology and call relationships.

Implementation phases and acceptance criteria are maintained in the linked Issues.
