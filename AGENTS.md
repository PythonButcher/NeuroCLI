# AGENTS.md

## NeuroCLI Agent Routing

This repository supports parallel work between Codex and Gemini. Read this file first before making changes.

## Source of Truth

- `neurocli_core` is the shared backend and main AI workflow source of truth.
- NeuroCLI now has one shared backend contract with two supported frontends.
- `neurocli_app` is the full Python Textual frontend. It calls `neurocli_core` directly.
- `api` is the FastAPI bridge that exposes `neurocli_core` to the React frontend.
- `web_client` is the React frontend.

## Codex Ownership

Codex is the primary owner for:

- All backend work
- All `neurocli_core` changes
- All `api` changes
- All `neurocli_app` changes
- Python-only app fixes and features
- React application logic, state, data flow, API wiring, and integration work
- Shared architecture, testing, and documentation for backend behavior

## Gemini Ownership

Gemini is the primary owner for:

- React frontend UI and presentation work only
- Visual layout, styling, component presentation, UX polish, and static frontend content in `web_client`

Gemini should not be the primary owner for:

- Backend logic
- API contracts
- Python application changes
- Core AI workflow behavior
- React business logic or backend integration decisions unless coordinated through Codex

## Collaboration Rules

- Codex defines or approves backend contracts before Gemini builds UI against them.
- Gemini should prefer presentational React changes that preserve existing logic boundaries.
- If a React task mixes UI and logic, Codex owns the logic layer and Gemini owns the presentational layer.
- Shared decisions, blockers, plans, and handoffs should be written in the `handoff/` folder.

## Files To Review First

- `AGENTS.md`
- `GEMINI.md`
- `handoff/README.md`
- `handoff/plans/current_plan.md`
- `handoff/plans/repair_plan.md`

## Working Agreement

- Do not duplicate backend logic in the React app.
- Do not duplicate backend workflow logic in the Textual app.
- Keep business logic in Python where practical, inside `neurocli_core`.
- Keep the Python Textual app and React frontend as feature-aligned as practical.
- If a feature cannot be identical across both frontends, document the reason and preserve the same backend contract.
- Prefer additive collaboration notes in `handoff/` over rewriting another agent's instructions.
