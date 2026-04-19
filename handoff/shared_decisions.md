# Shared Decisions

## Architectural Decisions

- `neurocli_core` is the shared backend source of truth.
- `neurocli_app` stays as a supported Python-only interface.
- `web_client` stays as a supported React interface.
- The React app should call `api`, and `api` should delegate to `neurocli_core`.

## Ownership Decisions

- Codex owns backend, Python, API, shared logic, and React integration logic.
- Gemini owns React UI and visual presentation only.

## Documentation Decisions

- Codex reads `AGENTS.md` first.
- Gemini reads `GEMINI.md` first.
- Both agents should read `handoff/README.md` and `handoff/current_plan.md`.

## Open Coordination Topics

- Final API contract for the web AI workflow
- Which React components are safe for UI-only refactors before backend rewiring is complete

## Shared AI Workflow Contract

The shared prompt execution contract now lives in `neurocli_core/workflow_service.py`.

Request shape:

- `prompt` is required
- `target_file` is optional
- `context_paths` is optional and normalized to an ordered list
- `model` is optional
- `model_options` is the hook for provider-specific config overrides

Synchronous response shape:

- `ok`
- `status`
- `response_kind`
- `prompt`
- `output_text`
- `target_file`
- `context_paths`
- `original_content`
- `model`
- `error`

Streaming event shape:

- `event`
- `delta`
- optional `response` on `complete` or `error`

Contract rules:

- `response_kind` is `file_update` when the target resolves to a file, even if that file is empty
- `original_content` is preserved in the response so callers can generate diffs without rebuilding context
- sync and streaming execution share the same prompt/context preparation path
- FastAPI and future React integration should consume this contract, not recreate backend behavior
