# Current Plan

## Current Direction

NeuroCLI should move forward as a terminal-first AI development environment with one shared Python capability engine and two supported frontend surfaces.

`neurocli_core` remains the backend source of truth. The Textual app in `neurocli_app` is the flagship terminal surface and calls `neurocli_core` directly. The React frontend in `web_client` is a supported companion surface and reaches the same backend behavior through the FastAPI bridge in `api`.

The Agent Council runs on May 3, 2026 clarified the next direction: do not chase autonomous orchestration first, and do not turn React into a separate product center. Build a reliable repo-aware loop first: understand context, target files, generate proposals, review diffs, validate results, and prepare commits with human approval.

## Active Roadmap

The active phased roadmap lives in `handoff/plans/roadmap.md`.

The next implementation slice should be Phase 1 from that roadmap: define a shared generated-file proposal and diff artifact in `neurocli_core`, expose it through `api`, and make React consume that artifact instead of treating raw `output_text` as directly applyable proposed content.

## Current Status

Phases 1 and 2 of the earlier repair work are complete: the shared AI workflow service exists in `neurocli_core`, and the FastAPI bridge calls the real workflow instead of a fake stream.

The Phase 3 React wiring is implemented but still needs final live browser smoke verification against the local backend and real model runtime.

The Phase 4 Textual alignment is implemented but still needs manual runtime smoke verification against the real model runtime.

Phase 5 produced useful Textual and React polish, including command/reference modals, review editors, action-rail alignment, model settings, context selection, and backend-bound prompt fields. The remaining critical gap is shared generated-file review: Textual can format, diff, review, and apply with backup; React still lacks a shared backend proposal/diff artifact for AI `file_update` responses.

## Immediate Next Work

1. Confirm the local verification baseline: document exactly how to run the Textual smoke test, the FastAPI backend, and the React browser smoke test with the available dependency setup.
2. Define the shared generated-file proposal/diff artifact in `neurocli_core`.
3. Add focused tests for proposal creation, malformed model output, format/diff failure, non-file chat responses, and workspace path safety.
4. Expose the proposal/diff artifact through `api`.
5. Update React integration so generated-file review consumes backend proposal data instead of raw `output_text` alone.
6. Update Textual only where it can safely consume the shared artifact without weakening its current review/apply path.
7. Record the new contract in `handoff/coordination/shared_decisions.md` and update Codex/Gemini handoff notes before Gemini does any presentation-only React polish.

## Main Files For The Next Slice

- `neurocli_core/workflow_service.py`
- `neurocli_core/diff_generator.py`
- `neurocli_core/formatter.py`
- `api/main.py`
- `neurocli_app/main.py`
- `neurocli_app/workflow_adapter.py`
- `web_client/src/App.jsx`
- `web_client/src/lib/api.js`
- `tests/test_ai_services.py`
- `tests/test_api_main.py`
- `tests/test_textual_workflow_adapter.py`
- `handoff/plans/roadmap.md`
- `handoff/coordination/shared_decisions.md`
- `handoff/coordination/codex_handoff.md`
- `handoff/coordination/gemini_handoff.md`

## Current Council Inputs

The active roadmap is based on these council runs:

- `handoff/agent_council/runs/2026-05-03-project-direction/`
- `handoff/agent_council/runs/2026-05-03-practical-state-of-art-features/`

Each real council run must include both `output.json` and a companion `README.md`.

## Archived Context

Older phase plans and idea documents are in `handoff/archive/`. They are useful history, not the active roadmap. In particular, `handoff/archive/repair_plan.md` and `handoff/archive/phase_5_direction.md` have been superseded by this current plan and `handoff/plans/roadmap.md`.
