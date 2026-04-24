# Current Plan

## Goal
Keep both supported versions of NeuroCLI working:

- the Python Textual app in `neurocli_app`
- the React web app in `web_client`

Both should use the same real AI workflow in `neurocli_core`.

## Status

- Phase 1 is done.
- Phase 2 is done.
- Phase 3 is next.
- Phase 4 comes after Phase 3.

## Next Work

1. Rewire the React app to the real API contract.
2. Remove the last placeholder frontend behavior.
3. Verify the Python app still matches the shared backend contract.

## Main Files For The Next Step

- `web_client/src/App.jsx`
- `web_client/src/components/FileTree.jsx`
- `web_client/src/components/ContextModal.jsx`
- `web_client/src/components/GitModal.jsx`
- `api/main.py`
- `handoff/coordination/shared_decisions.md`

## Reference
See `handoff/plans/repair_plan.md` for the full roadmap.
