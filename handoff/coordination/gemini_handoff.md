# Gemini Ownership Guide

Gemini owns React presentation in `web_client`: layout, styling, accessible interaction, presentational components, empty/loading states, and UX polish.

Gemini must preserve state and API boundaries defined by Codex. If an assigned UI goal needs new workflow data or behavior, record the backend gap and stop before inventing frontend-only logic.

Before React work, read:

- `handoff/active_gate/README.md`
- `handoff/coordination/shared_decisions.md`
- `handoff/coordination/frontend_parity.md`
- `web_client/README.md`

React consumes the shared prompt, streaming, proposal, validation, apply, radar, Git, and timeline contracts. Presentation can differ from Textual, but shared safety guarantees must not.

Gemini acts only when `handoff/active_gate/README.md` assigns a bounded React goal with target files, contract fields, acceptance checks, and verification commands.
