# Active Gate: Terminal-First Experience

## Goal

Make the Textual application a clear, reliable developer cockpit for the complete safe workflow.

## User Outcome

A Textual user can choose a target and context, configure the model, run the workflow, inspect the timeline and diff, edit the proposal, validate it, apply it with a backup, inspect workspace radar, and prepare a commit without leaving the application.

## Scope

Improve focus order, keyboard flow, diff readability, review-editor ergonomics, validation readiness, timeline clarity, reset behavior, and explicit safe-workflow controls.

Primary files:

- `neurocli_app/main.py`
- `neurocli_app/main.css`
- `neurocli_app/review_modal.py`
- `neurocli_app/command_modal.py`
- `neurocli_app/workflow_adapter.py`
- focused tests under `tests/`

Use `neurocli_core` only when a change requires shared behavior. Do not place workflow business rules in Textual widgets.

## Required Contracts

- `handoff/coordination/shared_decisions.md`
- `handoff/coordination/frontend_parity.md`
- `handoff/plans/roadmap.md`

## Acceptance

The Textual workflow must expose target, context, model, run, review, validation, apply-with-backup, radar, and commit-readiness controls with discoverable keyboard navigation.

No change may apply, commit, or push without explicit user action. Validation must use approved labels and reject unsafe targets without starting a process. Timeline metadata must remain concise and redacted.

## Verification

Run:

`python -m unittest discover tests`

`python -m ruff check neurocli_core api neurocli_app tests`

Perform a manual Textual smoke test covering target selection, context, model settings, streaming, proposal review, validation, reset, apply readiness, radar, and Git readiness.

Run the React checks if a shared contract or React integration changes:

`npm --prefix web_client run lint`

`npm --prefix web_client run build`

## Owner

Codex owns this gate. React presentation work begins only when this gate defines a bounded Gemini handoff. Control returns to the user for application-level acceptance after automated and manual verification.
