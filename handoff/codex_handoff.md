# Codex Handoff

## Scope

Codex owns backend and logic-heavy work across this repo.

## Primary Areas

- `neurocli_core`
- `api`
- `neurocli_app`
- React state, API calls, request/response handling, and integration code in `web_client`

## Current Notes

- The web app currently has a partial backend, but the main AI command flow is still mocked.
- The React app should not own business logic that properly belongs in `neurocli_core`.
- When UI tasks require backend support, Codex should define the contract first and document it in `handoff/shared_decisions.md`.

## Phase 1 Backend Contract

Codex implemented the shared AI workflow contract in `neurocli_core/workflow_service.py`.

The primary entry points are:

- `build_ai_workflow_request(...)`
- `execute_ai_workflow(request)`
- `stream_ai_workflow(request)`

The Textual app now consumes `execute_ai_workflow(...)` directly instead of relying on the older tuple-only contract.
`neurocli_core/ai_services.py` remains as a compatibility wrapper for legacy callers.

## Phase 2 Guidance

FastAPI should consume `AIWorkflowResponse.to_dict()` for synchronous responses and `AIWorkflowStreamEvent.to_dict()` for SSE payloads.
The API should not rebuild prompts or duplicate file/context assembly logic. It should only validate request input, enforce workspace path safety, and delegate to `neurocli_core`.

## Before Handoff To Gemini

- Document any changed request or response shapes that affect the UI.
- Call out any loading, error, or empty states the UI should represent.
- Note any components that are safe for UI-only refactor versus components that are still under integration.
