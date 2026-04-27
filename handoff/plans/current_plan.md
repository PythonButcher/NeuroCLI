# Current Plan

## Goal
Keep NeuroCLI moving as one shared backend product with two supported frontends:

- the Python Textual app in `neurocli_app`
- the React web app in `web_client`

`neurocli_core` is the backend source of truth. The Textual app calls it directly, and the React app reaches it through the FastAPI bridge in `api`.

## Status

- Phase 1 is done.
- Phase 2 is done.
- Phase 3 code wiring is done, but the final live browser smoke test is still pending.
- Phase 4 contract alignment work is in place for `neurocli_app`; the remaining work is runtime smoke testing.
- Phase 5 has started with a frontend and feature-parity audit plus a focused Textual-first polish slice.
- The current architecture is one shared Python backend workflow with two frontends, not two separate backend implementations.

## Phase 5 Audit Snapshot

Prompt runs, streaming output, file targeting, context attachments, model override, and model options are wired through the shared workflow contract for both frontends. The Textual app calls `neurocli_core` through `neurocli_app/workflow_adapter.py`; the React app calls the same contract through `api/main.py`.

Formatting, diff review, and apply-with-backup are strongest in the Textual app. Textual formats generated file updates, shows a diff, and only then exposes apply. The API has separate `/api/format` and `/api/apply` endpoints for React, but React AI file-update responses currently set `proposedContent` directly from `output_text` and do not receive a generated formatted diff from the backend contract. That parity gap should be fixed by defining a shared proposal/diff contract in `neurocli_core` or the API bridge before Gemini polishes the React presentation.

Radar is aligned at the service level: Textual calls `neurocli_core.radar_engine` directly and React consumes `/api/radar`. Git is partially aligned: React uses status, diff, and manual commit endpoints; Textual still uses `neurocli_core.git_engine` to generate an AI commit message and commit/push from the modal. The current backend contract does not expose AI commit-message generation to React, so this remains a documented parity difference rather than a frontend-only feature for Gemini to invent.

## Phase 5 Textual Slice

The Textual app now has a visible command-center status strip showing workflow state, target file, context count, model state, and apply readiness. It also has keyboard bindings for run, format, apply, model, context, radar, git, reset, and quit. The reset and clear controls now clear transient prompt/diff/stream state and refocus the prompt input. Worker state handling no longer hides the loading indicator on non-terminal worker transitions.

## Next Work

1. Run a manual Textual app smoke test against the real model runtime with `PYTHONPATH=.codex_tmp_py/site-packages` or an equivalent installed environment.
2. Define a shared generated-file proposal contract so React can review formatted diffs before apply, matching the Textual flow.
3. Decide whether AI commit-message generation should become a shared backend/API contract or stay Textual-only for now.
4. Run the pending live browser smoke test against the local FastAPI backend and real model runtime.
5. Continue Textual flagship polish: focus order, command palette candidate, diff readability, radar access, and git action clarity.

## Main Files For The Next Step

- `neurocli_app/main.py`
- `neurocli_app/model_modal.py`
- `neurocli_app/workflow_adapter.py`
- `neurocli_core/workflow_service.py`
- `tests/test_textual_workflow_adapter.py`
- `api/main.py`
- `web_client/src/App.jsx`
- `web_client/src/lib/api.js`
- `handoff/coordination/shared_decisions.md`
- `handoff/plans/phase_5_direction.md`

## Reference
See `handoff/plans/repair_plan.md` for the full roadmap.
