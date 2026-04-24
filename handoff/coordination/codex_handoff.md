# Codex Handoff

## Scope
Codex owns backend and integration work across this repo.

## Primary Areas

- `neurocli_core`
- `api`
- `neurocli_app`
- React logic and API wiring in `web_client`

## Current Notes

- `neurocli_core` is the shared backend source of truth.
- The web backend in `api` now uses the real AI workflow service.
- The React frontend Phase 3 logic has been rewired to the real API contract.

## Active Contract Notes

- The main shared workflow lives in `neurocli_core/workflow_service.py`.
- The main API routes are `POST /api/ai/prompt` and `POST /api/ai/stream`.
- Local backend startup should use `http://127.0.0.1:8010`.
- `web_client/src/lib/api.js` is the shared frontend integration entry point.
- `App.jsx` now parses structured stream events and falls back to the sync prompt endpoint when streaming is unavailable.
- `FileTree.jsx` controls `target_file` selection and prompt context toggles.
- `ModelModal.jsx` now maps to the optional `model` and `model_options` fields instead of showing a placeholder-only message.
- `GitModal.jsx` no longer advertises AI commit-message generation because that is not part of the current backend contract.

## Coordination Rule
If frontend work needs a backend contract change, record it in `handoff/coordination/shared_decisions.md`.
