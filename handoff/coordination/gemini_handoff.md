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
- the Phase 5 audit found that React already mirrors prompt runs, streaming, target file, context, model override, model options, radar, manual git status/diff/commit, existing-file formatting, and apply-with-backup through the API bridge
- React does not yet have Textual-equivalent generated-file diff review for AI `file_update` responses; do not solve this with frontend-only diff logic unless Codex first defines the shared backend/API contract
- AI commit-message generation exists in the Textual git modal through `neurocli_core.git_engine`, but it is not exposed by the current React API contract
- Textual now has a Review Editor for editing the current generated/formatted proposal before apply. React should eventually mirror this mental model, but only after Codex defines the shared generated-file proposal/diff contract.

## Phase 5 UI Direction For Gemini

React presentation polish should mirror the same developer command-center mental model now reinforced in Textual: active target file, context stack, model state, streaming state, apply readiness, review lane, radar access, and clear git actions. UI work should stay presentational unless Codex updates `web_client` state/API wiring or the FastAPI contract.
