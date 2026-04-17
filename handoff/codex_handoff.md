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

## Before Handoff To Gemini

- Document any changed request or response shapes that affect the UI.
- Call out any loading, error, or empty states the UI should represent.
- Note any components that are safe for UI-only refactor versus components that are still under integration.
