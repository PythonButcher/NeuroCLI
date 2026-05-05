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
- React polish should aim for feature parity with the Textual app where the shared backend supports the same flow
- the Phase 5 audit found that React already mirrors prompt runs, streaming, target file, context, model override, model options, radar, manual git status/diff/commit, existing-file formatting, and apply-with-backup through the API bridge
- React generated-file review now consumes the backend `response.proposal` artifact for AI `file_update` responses; do not replace this with frontend-only diff logic
- AI commit-message generation exists in the Textual git modal through `neurocli_core.git_engine`, but it is not exposed by the current React API contract
- Textual has a Review Editor for editing the current generated/formatted proposal before apply. React now mirrors this mental model by staging backend `proposal.normalized_content` and showing backend proposal errors/status in the review flow.
- The active roadmap now lives in `handoff/plans/roadmap.md`.
- The current shared proposal/diff capability is backend-defined. Gemini presentation work should preserve the `response.proposal` contract and keep apply disabled for non-ready proposals.

## Current UI Direction For Gemini

React presentation polish should mirror the same developer command-center mental model now reinforced in Textual: active target file, context stack, model state, streaming state, apply readiness, review lane, radar access, and clear git actions. UI work should stay presentational unless Codex updates `web_client` state/API wiring or the FastAPI contract.

Future React polish should follow Codex handoff order: validation results, workflow timeline, workspace intelligence, git review lane, model profiles, and later orchestration surfaces if those contracts exist.

## Historical Phase 5 Web-Only Implementation Plan

This plan has been implemented and is kept as context for the current React presentation shape. It is not the active next-work list.

The Phase 5 Textual interaction model was added to the React web UI only. The implementation used the Textual files as references for behavior, ordering, and theme direction, then implemented the web presentation in `web_client`.

Reference the Textual implementation in `neurocli_app/main.py`, especially the bottom action order and the `Review` action placement. Reference `neurocli_app/review_modal.py` for the Review Editor concept: editable proposed content, target/proposal metadata, disabled future editor feature controls, keep draft, and apply edited. Reference `neurocli_app/command_modal.py` for the command reference idea. Reference `neurocli_app/main.css` for the dark terminal window styling, bordered modal language, compact action rail, and Review Editor sizing.

In the React web UI, cross-reference only the web files that already own the browser presentation: `web_client/src/App.jsx`, `web_client/src/components/GitModal.jsx`, `web_client/src/components/RadarModal.jsx`, `web_client/src/components/ModelModal.jsx`, `web_client/src/components/ContextModal.jsx`, `web_client/src/components/TargetFileModal.jsx`, `web_client/src/index.css`, and any new presentational component under `web_client/src/components`. The current web theme already uses the same terminal palette: `#010409`, `#0d1117`, `#161b22`, `#30363d`, `#58a6ff`, `#8b949e`, `#c9d1d9`, `#3fb950`, and `#f85149`.

The bottom web action rail was reordered into this workflow sequence: Settings, Clear, Model, Context, Radar, Run, Format, Review, Commit. It should stay responsive and content-driven so buttons do not drift apart on wide screens or collide on narrow screens.

The web `ReviewModal.jsx` consumes `proposedContent`, `targetFile`, `handleApply`, and the backend-generated `proposal` metadata from `App.jsx`. It can show proposal status and errors, but should remain a presentation component.

Keep backend limits visible in the UI. React can edit and apply ready backend proposals, but validation results, workflow timeline state, and model profiles are not part of the current proposal contract.

Historical validation for this slice was browser-only: React build, bottom rail at narrow and wide widths, Radar and Git modal comparison, Review empty/disabled state, format proposal through the existing web Format flow, edit in Review, keep draft, and apply edited content through the existing apply path.

## Phase 5 Completion Notes

- **Action Rail Alignment:** Reordered the bottom action rail to follow the workflow order: Settings, Clear, Model, Context, Radar, Run, Format, Review, Commit.
- **Review Editor:** Implemented `ReviewModal.jsx` mirroring the Textual Review Editor. It supports editing `proposedContent`, resetting drafts, keeping edited drafts, and applying edited content directly.
- **Command Reference:** Implemented `CommandModal.jsx` mirroring the Textual Command Reference. Added a "⌨ Commands" button to the header for discoverability.
- **Logic Wiring:** Updated `App.jsx` `handleApply` to support content overrides from the Review Modal. Wired the trash icon to clear transient console state.
- **Verification:** Successfully ran the React build (`npm run build`). The UI now mirrors the "command center" mental model of the Textual flagship.
- **Command Modal Fix:** Converted `CommandModal.jsx` from a keyboard shortcut reference into a clickable action reference. Removed unused Ctrl shortcuts that conflicted with browser defaults. Updated table headers to "Action" and "What it does."
- **Action Rail Fix:** Reworked the bottom action rail in `App.jsx` from a `justify-between` layout to a content-driven, responsive `flex-wrap` row. Removed the expanding spacer to prevent controls from drifting on wide screens.
- **Parity Note:** React still lacks the Textual-equivalent generated-file diff contract for AI `file_update` responses. This remains a backend/API gap for Codex to address.

