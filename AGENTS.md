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

## Compound Checkpoints

Every phase, implementation slice, and handoff must include a compound checkpoint. A compound checkpoint is the plain-language answer to: "What can a user do after this work that they could not do before?"

The checkpoint must name the surface where the capability is available. Because Textual is the flagship app, a backend-only or React-only capability is not considered a full product checkpoint unless the docs explicitly say why Textual is deferred and what the next Textual checkpoint is.

Each implementation handoff must state three things: the user-visible capability now available, the backend or API contract that supports it, and any surface that still cannot use it.

## Files To Review First

- `AGENTS.md`
- `GEMINI.md`
- `handoff/README.md`
- `handoff/plans/current_plan.md`
- `handoff/plans/roadmap.md`
- `handoff/coordination/shared_decisions.md`
- `handoff/coordination/frontend_parity.md`

## Working Agreement

- Do not duplicate backend logic in the React app.
- Do not duplicate backend workflow logic in the Textual app.
- Keep business logic in Python where practical, inside `neurocli_core`.
- Keep the Python Textual app and React frontend as feature-aligned as practical.
- If a feature cannot be identical across both frontends, document the reason and preserve the same backend contract.
- Prefer additive collaboration notes in `handoff/` over rewriting another agent's instructions.
- Older phase plans live in `handoff/archive/` and should be treated as historical reference, not active roadmap.
