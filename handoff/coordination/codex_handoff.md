# Codex Ownership And Integration Guide

Codex owns `neurocli_core`, `api`, `neurocli_app`, Python tests, shared architecture, documentation, and React state/API integration.

## Integration Map

- `neurocli_core/workflow_service.py`: shared prompt and streaming workflow.
- `neurocli_core/generated_file_proposal.py`: reviewable file proposal and diff artifact.
- `neurocli_core/validation_result.py`: shell-free validation policy and results.
- `neurocli_core/workflow_timeline.py`: redacted timeline events.
- `api/main.py`: workspace-safe bridge for React.
- `neurocli_app/workflow_adapter.py`: thin Textual adapter over shared contracts.
- `web_client/src/lib/api.js`: React API and stream client.

## Safety Boundaries

Validation accepts stable command labels, never arbitrary shell text. A selected Python target uses a generated `python_unittest_target` policy entry; a non-Python or out-of-workspace target is rejected without starting a process.

Apply operations require explicit user action and create backups. Commit operations require explicit approval. Timeline events stay concise and do not embed prompts, source, output, diffs, secrets, or long logs.

Textual and React may differ in presentation depth. Consult `frontend_parity.md` before changing either surface.

For current work, read `handoff/active_gate/README.md`.
