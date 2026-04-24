# Current Plan

## Goal
Keep both supported versions of NeuroCLI working:

- the Python Textual app in `neurocli_app`
- the React web app in `web_client`

Both should use the same real AI workflow in `neurocli_core`.

## Status

- Phase 1 is done.
- Phase 2 is done.
- Phase 3 code wiring is done, but the final live browser smoke test is still pending.
- Phase 4 contract alignment work is now in place for `neurocli_app`.

## Next Work

1. Run a manual Textual app smoke test against the real model runtime now that the shared stream contract is wired in.
2. Install or restore missing FastAPI runtime dependencies in the local environment, then rerun the API and browser verification.
3. Expand end-to-end verification for both app surfaces in the later test phase.

## Main Files For The Next Step

- `neurocli_app/main.py`
- `neurocli_app/model_modal.py`
- `neurocli_app/workflow_adapter.py`
- `neurocli_core/workflow_service.py`
- `tests/test_textual_workflow_adapter.py`
- `api/main.py`
- `handoff/coordination/shared_decisions.md`

## Reference
See `handoff/plans/repair_plan.md` for the full roadmap.
