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
- NeuroCLI now has one shared backend workflow with two frontend surfaces.
- The FastAPI layer in `api` is a bridge from React to `neurocli_core`, not a separate business backend.
- The React frontend Phase 3 logic has been rewired to the real API contract.
- The Textual app Phase 4 contract alignment is now wired in code.

## Active Contract Notes

- The main shared workflow lives in `neurocli_core/workflow_service.py`.
- The main API routes are `POST /api/ai/prompt` and `POST /api/ai/stream`.
- Local backend startup should use `http://127.0.0.1:8010`.
- `web_client/src/lib/api.js` is the shared frontend integration entry point.
- `App.jsx` now parses structured stream events and falls back to the sync prompt endpoint when streaming is unavailable.
- `FileTree.jsx` controls `target_file` selection and prompt context toggles.
- `ModelModal.jsx` now maps to the optional `model` and `model_options` fields instead of showing a placeholder-only message.
- `GitModal.jsx` no longer advertises AI commit-message generation because that is not part of the current backend contract.
- `neurocli_app/workflow_adapter.py` now builds the same request fields for the Textual app and validates raw JSON `model_options`.
- `neurocli_app/main.py` now streams through `stream_ai_workflow` and applies the final normalized workflow response through one shared handler.
- `neurocli_app/model_modal.py` is the Textual entry point for `model` and `model_options`.
- Phase 5 should improve both frontends while preserving shared behavior: prompt runs, file-targeted updates, context attachments, model settings, streaming, formatting, apply, radar, and git workflows.

## Coordination Rule
If frontend work needs a backend contract change, record it in `handoff/coordination/shared_decisions.md`.

## Verification Notes

- `python -m unittest tests.test_ai_services tests.test_textual_workflow_adapter` passes locally
- `python -m py_compile neurocli_app\\main.py neurocli_app\\model_modal.py neurocli_app\\workflow_adapter.py neurocli_core\\workflow_service.py` passes locally
- `python -m unittest tests.test_api_main` could not run here because `fastapi` is not installed in the current environment
