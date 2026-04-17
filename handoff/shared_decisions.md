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
