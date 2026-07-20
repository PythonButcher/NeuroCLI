# Current Plan

## Current Direction

NeuroCLI is a terminal-first AI development environment with one shared Python capability engine. `neurocli_app` is the flagship Textual surface; `web_client` is the React companion through `api`; `neurocli_core` owns shared workflow behavior.

## Current Status

Phase 3 is complete at the compound-checkpoint level. The backend emits concise, redacted workflow timeline events. Textual renders the current safe-loop lane, and React consumes the same event semantics as a compact status summary.

The Phase 3 closeout also cleaned the repository harness and environment policy: required React API-client source is no longer hidden by `.gitignore`, runtime backups and build artifacts are excluded from Git, malformed test artifacts were removed or converted to fixtures, and root agent instructions now route to one current status source.

Phases 1–3 are complete:

1. Shared generated-file proposal and diff artifact.
2. Policy-approved validation artifact available in Textual and React.
3. Redacted workflow timeline available in both surfaces, with the fuller lane in Textual.

## Current Compound Checkpoint

A Textual user can see context collection, target reading, model execution, stream completion, proposal and diff creation, validation, apply readiness, backup creation, and commit preparation when those steps occur. React receives the same backend events and shows a compact recent-event summary.

Timeline metadata excludes full prompts, source contents, generated output, diffs, secrets, and long command output. The detailed reviewed artifacts remain separate.

The repository closeout adds a second practical outcome: contributors can clone the project without committing secrets, environments, dependency trees, builds, runtime backups, or caches, while required Python and React source remains visible to Git.

## Next Work

The next implementation slice is Phase 4: Terminal-First Experience.

Improve Textual focus order, diff readability, review ergonomics, validation readiness, and safe workflow controls without changing shared backend contracts casually. Preserve proposal review, timeline, validation, apply-with-backup, radar, and explicit commit approval.

React work during Phase 4 should be limited to documented shared contracts; there is no active Gemini UI handoff yet.

Live Textual and browser smoke tests against a real model runtime remain manual because they require local credentials.

## Verification

Run from the repository root:

`python -m unittest discover tests`

`python -m ruff check neurocli_core api neurocli_app tests`

`npm --prefix web_client run lint`

`npm --prefix web_client run build`

`python handoff/agent_council/validate_council_output.py handoff/agent_council/runs/2026-05-03-project-direction/output.json`

`python handoff/agent_council/validate_council_output.py handoff/agent_council/runs/2026-05-03-practical-state-of-art-features/output.json`
