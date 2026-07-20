# Gemini Handoff

## Current Status

There is no active Gemini UI implementation slice. Phase 4 is currently Codex-owned Textual work.

## Ownership Boundary

Gemini owns React presentation in `web_client`: layout, styling, accessible interaction, presentational components, empty/loading states, and UX polish.

Gemini must preserve state and API boundaries already defined by Codex. If a requested UI needs new workflow data or behavior, record the gap here and stop before inventing frontend-only logic.

## Required Context Before React Work

Read:

- `handoff/plans/current_plan.md`
- `handoff/coordination/shared_decisions.md`
- `handoff/coordination/frontend_parity.md`
- `web_client/README.md`

React already consumes the shared prompt, streaming, proposal, validation, apply, radar, Git, and timeline contracts. Presentation can differ from Textual, but shared safety guarantees must not.

## Handoff Format

When a React slice becomes active, replace this status with one bounded goal, a limited file set, the exact existing contract fields to consume, and short build/browser acceptance checks. Completed implementation diaries belong in `handoff/archive/`, not here.
