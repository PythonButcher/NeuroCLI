# Current Plan

## Active Objective

Repair NeuroCLI so both supported product modes remain functional:

- Python-only Textual application
- React frontend backed by FastAPI

Both modes must use a real backend for the main AI workflow.

## Current Status

Phase 1 is now implemented in `neurocli_core`.
Phase 2 is the active next step: replace the fake FastAPI prompt flow with the shared backend service contract.

## Execution Order

1. Stabilize `neurocli_core` as the shared backend contract. Completed.
2. Replace the fake AI flow in `api/main.py` with real backend integration. Active next step.
3. Wire `web_client` to the real API contract.
4. Fix React placeholder areas and runtime issues.
5. Preserve and verify `neurocli_app`.
6. Clean up dependencies, docs, and tests.

## Responsibility Split

### Codex

- Backend architecture
- `neurocli_core`
- `api`
- `neurocli_app`
- React logic and integration
- Testing and dependency cleanup

### Gemini

- React UI-only work in `web_client`
- Styling
- Presentational component cleanup
- UX polish that does not redefine backend behavior

## Reference

See `application_repair_plan.md` for the full repair plan.
