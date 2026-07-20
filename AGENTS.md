# NeuroCLI Agent Map

Use this file as a router. Current work belongs only in `handoff/active_gate/`; historical detail belongs in `handoff/archive/`.

## Start Here

| Need | Read |
| --- | --- |
| Start any project task | `handoff/active_gate/README.md` |
| Understand the phased direction | `handoff/plans/roadmap.md` |
| Change a backend or API contract | `handoff/coordination/shared_decisions.md` |
| Compare Textual and React behavior | `handoff/coordination/frontend_parity.md` |
| Review owner-specific work | `handoff/coordination/codex_handoff.md` or `handoff/coordination/gemini_handoff.md` |
| Run a major design discussion | `handoff/agent_council/README.md` |
| Consult old plans | `handoff/archive/README.md`, only when current docs point there |

## Architecture

NeuroCLI has one shared Python capability engine and two supported frontends.

- `neurocli_core` owns workflow and business behavior.
- `neurocli_app` is the flagship Python Textual frontend and calls the core directly.
- `api` exposes the same core behavior through FastAPI.
- `web_client` is the React companion frontend and calls `api`.

Do not duplicate backend behavior in either frontend. Preserve the same safety contract when presentation differs.

## Ownership

Codex owns Python, `neurocli_core`, `api`, `neurocli_app`, tests, shared architecture, documentation, and React state/API integration.

Gemini owns React presentation work in `web_client`: layout, styling, presentational components, accessibility, empty/loading states, and UX polish. Backend or contract gaps go into `handoff/coordination/gemini_handoff.md` for Codex review.

## Working Rules

- Read `handoff/active_gate/README.md` before making changes; do not scan archives by default.
- Keep business rules in `neurocli_core` where practical.
- Use `apply_patch` for source and documentation edits.
- Preserve user changes and avoid destructive Git commands.
- Make coding changes one bounded step at a time and verify each slice.
- Update active documentation when status, contracts, parity, or ownership changes.
- Keep `.agents/`, `.codex/`, and `.gemini/` free of project-local skills until a demonstrated need exists.
- Keep the active gate entirely forward-looking. Never put prior-phase references, completion recaps, implementation history, or review history in `handoff/active_gate/`.

## Compound Checkpoint

Every phase or implementation slice must state what a user can do now, which surface supports it, the backend/API contract behind it, and any surface that still lacks it. Textual is the flagship, so backend-only or React-only work is not a complete product checkpoint unless the Textual deferral is explicit.
