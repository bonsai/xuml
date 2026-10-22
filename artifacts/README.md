# Artifacts

Generated outputs from GitHub Actions belong under this directory.

- `issue-graph/` is created by `.github/workflows/make-issue-graph.yml` during a workflow run.
- The workflow uploads `artifacts/issue-graph/` as the `issue-graph` Actions artifact (14-day retention).
- Generated graph files are not committed back to the repository; only this directory convention is tracked.
