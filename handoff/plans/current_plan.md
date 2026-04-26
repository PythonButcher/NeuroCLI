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
- The current architecture is one shared Python backend workflow with two frontends, not two separate backend implementations.

## Next Work

1. Run a manual Textual app smoke test against the real model runtime now that the shared stream contract is wired in.
2. Install or restore missing FastAPI runtime dependencies in the local environment, then rerun the API and browser verification.
3. Start Phase 5 as the frontend and feature-parity phase after the remaining smoke checks are handled or explicitly accepted as deferred.
4. Use `handoff/plans/phase_5_direction.md` as the starting point for UI polish and terminal-first product ideas.

## Main Files For The Next Step

- `neurocli_app/main.py`
- `neurocli_app/model_modal.py`
- `neurocli_app/workflow_adapter.py`
- `neurocli_core/workflow_service.py`
- `tests/test_textual_workflow_adapter.py`
- `api/main.py`
- `handoff/coordination/shared_decisions.md`
- `handoff/plans/phase_5_direction.md`

## Reference
See `handoff/plans/repair_plan.md` for the full roadmap.
