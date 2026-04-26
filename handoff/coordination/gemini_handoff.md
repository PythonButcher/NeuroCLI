# Gemini Handoff

## Scope
Gemini owns React presentation work only.

## Primary Areas

- layout and styling in `web_client`
- presentational React components
- UI polish, spacing, empty states, and visual consistency

## Guardrails

- do not move backend logic into the frontend
- do not redefine API payloads without coordination through Codex
- do not take ownership of Python-only app changes
- if a React change needs new backend behavior, record it in `handoff/coordination/shared_decisions.md`
- preserve the one-backend/two-frontends architecture: React presentation should consume the FastAPI bridge, and the bridge should remain aligned with `neurocli_core`

## Current Notes

- treat `neurocli_core` as the source of truth for behavior
- treat `api` as the FastAPI bridge from React to the shared backend, not as a separate behavior layer
- prefer UI work that keeps existing props and state boundaries unless Codex documents a new contract
- the React logic layer now sends `target_file`, `context_paths`, `model`, and `model_options` to the backend
- the file tree paperclip control and context modal now reflect real backend-bound prompt context instead of placeholder UX
- avoid reintroducing the old fake stream assumptions or placeholder AI git behaviors
- Phase 5 React polish should aim for feature parity with the Textual app where the shared backend supports the same flow
