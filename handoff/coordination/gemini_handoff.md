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

## Web-Only Implementation Plan

Gemini should add the Phase 5 Textual interaction model to the React web UI only. Do not edit `neurocli_app`, `neurocli_core`, or `api` for this task. Use the Textual files only as references for behavior, ordering, and theme direction, then implement the web presentation in `web_client`.

Reference the Textual implementation in `neurocli_app/main.py`, especially the bottom action order and the `Review` action placement. Reference `neurocli_app/review_modal.py` for the Review Editor concept: editable proposed content, target/proposal metadata, disabled future editor feature controls, keep draft, and apply edited. Reference `neurocli_app/command_modal.py` for the command reference idea. Reference `neurocli_app/main.css` for the dark terminal window styling, bordered modal language, compact action rail, and Review Editor sizing.

In the React web UI, cross-reference only the web files that already own the browser presentation: `web_client/src/App.jsx`, `web_client/src/components/GitModal.jsx`, `web_client/src/components/RadarModal.jsx`, `web_client/src/components/ModelModal.jsx`, `web_client/src/components/ContextModal.jsx`, `web_client/src/components/TargetFileModal.jsx`, `web_client/src/index.css`, and any new presentational component under `web_client/src/components`. The current web theme already uses the same terminal palette: `#010409`, `#0d1117`, `#161b22`, `#30363d`, `#58a6ff`, `#8b949e`, `#c9d1d9`, `#3fb950`, and `#f85149`.

The bottom web action rail should be reordered into this workflow sequence: Settings, Clear, Model, Context, Radar, Run, Format, Review, Commit. Keep it responsive and content-driven so buttons do not drift apart on wide screens or collide on narrow screens. Use `flex-wrap`, consistent `gap`, and no expanding spacer between Radar and the run/review/commit controls. This mirrors the Textual rail fix.

Add a web `ReviewModal.jsx` as a presentational component matching the Git modal style. It should use a dark bordered window, a header with a relevant review icon, a metadata row for target/proposal readiness, a large editable textarea for proposed content, disabled placeholder controls for future editor features such as Find, Diff, Tests, and Explain, and footer actions for Cancel, Reset Draft, Keep Draft, and Apply Edited. The first implementation can consume the existing `proposedContent`, `targetFile`, and `handleApply` state/actions from `App.jsx`; do not invent new backend payloads.

Keep the current backend limits visible in the UI. React can edit and apply existing proposed content, but it still does not have Textual-equivalent formatted generated-file diff review for AI `file_update` responses. Do not fake that as a backend feature. If the UI needs a true proposal/diff contract, hand that back to Codex before proceeding.

Validation for Gemini should be browser-only: run the React build, check the bottom rail at narrow and wide widths, open Radar and Git to compare the modal language, open Review with no proposal to verify the empty/disabled state, create a format proposal through the existing web Format flow, edit it in Review, keep the draft, and apply edited content through the existing apply path.

## Phase 5 Completion Notes

- **Action Rail Alignment:** Reordered the bottom action rail to follow the workflow order: Settings, Clear, Model, Context, Radar, Run, Format, Review, Commit.
- **Review Editor:** Implemented `ReviewModal.jsx` mirroring the Textual Review Editor. It supports editing `proposedContent`, resetting drafts, keeping edited drafts, and applying edited content directly.
- **Command Reference:** Implemented `CommandModal.jsx` mirroring the Textual Command Reference. Added a "⌨ Commands" button to the header for discoverability.
- **Logic Wiring:** Updated `App.jsx` `handleApply` to support content overrides from the Review Modal. Wired the trash icon to clear transient console state.
- **Verification:** Successfully ran the React build (`npm run build`). The UI now mirrors the "command center" mental model of the Textual flagship.
- **Command Modal Fix:** Converted `CommandModal.jsx` from a keyboard shortcut reference into a clickable action reference. Removed unused Ctrl shortcuts that conflicted with browser defaults. Updated table headers to "Action" and "What it does."
- **Action Rail Fix:** Reworked the bottom action rail in `App.jsx` from a `justify-between` layout to a content-driven, responsive `flex-wrap` row. Removed the expanding spacer to prevent controls from drifting on wide screens.
- **Parity Note:** React still lacks the Textual-equivalent generated-file diff contract for AI `file_update` responses. This remains a backend/API gap for Codex to address.

