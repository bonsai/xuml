# ADR-0001: Local-first hybrid architecture and shared semantic IR

- Status: Accepted
- Date: 2026-10-22

## Context

AI-generated and existing code can become difficult to inspect. xuml must connect design intent, source code, static analysis, runtime observations, and diagrams without conflating facts with inference. Basic analysis must remain useful offline.

## Decisions

1. Start with a modular local CLI. Server APIs, workers, and containers are later extractions, not prerequisites.
2. Use a shared semantic IR as the canonical semantic representation. Typed ASTs, dependency graphs, and diagram layouts are derived projections.
3. Keep stable IDs and provenance across design elements, source symbols, diagnostics, events, and artifacts.
4. Start with Python class structure, then module dependency topology, then statically resolvable calls. Mark inferred and unknown targets explicitly.
5. Emit structured JSON diagnostics and stable CLI exit codes. Validation failure must not replace last-known-good outputs.
6. Render SVG, Mermaid, and PlantUML through independent renderers.
7. Use JSON for request/response contracts, YAML for configuration/templates, and JSONL for append-only event history.
8. Run differential checks on push/PR; run full validation on main merges, schedules, manual runs, and whenever impact is uncertain.
9. Block merges for serious errors. Waivers require reason, approver, expiry, linked Issue, and rule ID.
10. Use a small trusted metamodel bootstrap core. User-defined/self-described metamodels are allowed above it; theorem proving is not an initial requirement.
11. Keep reviewable artifacts in Git, JSONL history separate, local indexing in SQLite, and large binaries in external storage. PostgreSQL/object storage are later server options.
12. Choose implementation languages per component using runtime performance, reliability/type safety, topology fit, integration, and operability. Development speed is excluded from ADR scoring as negligible noise.

## Consequences

Benefits: offline-first use, shared semantics across diagrams, reusable diagnostics, traceable design drift, and a migration path to server-backed workflows.

Trade-offs: IR and diagnostic contracts need versioning; adapters/renderers need conformance tests; uncertain impact must trigger full analysis; explicit waiver handling adds process overhead.

## Initial acceptance criteria

- A Python fixture produces deterministic semantic IR.
- The same IR produces SVG, Mermaid, and PlantUML.
- Structural violations produce JSON diagnostics and nonzero exit codes.
- Failed validation preserves previous valid outputs.
- GitHub Actions performs differential push/PR checks and full main/scheduled/manual checks.
- Independent fixtures remain the test foundation; self-analysis is additional.
