# xuml

xuml makes existing and AI-generated code easier to inspect. It extracts source structure into a common semantic intermediate representation (IR), checks implementation against design, and generates reviewable diagrams.

**Status:** planning/bootstrap. Initial delivery is a local-first CLI; server infrastructure is not required.

## First vertical slice

1. Parse Python classes, attributes, inheritance, and type annotations.
2. Convert facts into a shared semantic IR.
3. Validate structure and emit JSON diagnostics.
4. Render SVG, Mermaid (`.mmd`), and PlantUML (`.puml`).
5. Test fixed fixtures, malformed inputs, deterministic output, and failure paths.
6. Run GitHub Actions on push and pull requests.

Next, add module dependency topology, then call relationships. Mark inferred or unknown targets explicitly.

## Architecture

Source adapters → parser/analyzer → semantic IR → validators → render plugins.

The semantic model is canonical. AST, graph, and layout are derived projections; layout changes must not change model meaning.

- [Architecture diagram](docs/architecture.svg)
- [ADR-0001](docs/adr/0001-architecture.md)
- [Grill Me decisions](grilled.yaml)
- [Implementation Issue #1](https://github.com/bonsai/xuml/issues/1)

## Repository policy

- GitHub Issues are the canonical entry point for feature work.
- Keep source, DSL, YAML, ADRs, and reviewable diagrams in Git.
- JSON is used for request/response contracts; YAML for configuration/templates; JSONL for append-only event history.
- Use SQLite locally; PostgreSQL and object storage are later server options.
- Serious CI errors block merge. Exceptions require reason, approver, expiry, linked Issue, and rule ID.
- On validation failure, preserve last-known-good generated outputs.
- Local Git hooks are optional; GitHub Actions is the final quality gate.

## Implementation phases

- P0: versioned IR, IDs, diagnostics, exit codes, provenance, fixtures.
- P1: Python structural analysis, validation, SVG/Mermaid/PlantUML.
- P2: regression tests and push/PR CI.
- P3: module topology and cycle detection.
- P4: call analysis and self-verification.
- P5: DSL and metamodel validation.
- P6: JSONL/SQLite; optional API, SSE dashboard, PostgreSQL, and object storage.
