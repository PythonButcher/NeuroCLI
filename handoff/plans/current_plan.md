# Current Plan

## Goal
Keep both supported versions of NeuroCLI working:

- the Python Textual app in `neurocli_app`
- the React web app in `web_client`

Both should use the same real AI workflow in `neurocli_core`.

## Status

- Phase 1 is done.
- Phase 2 is done.
- Phase 3 is active and the React integration wiring is now in place.
- Phase 4 comes after Phase 3.

## Next Work

1. Finish Phase 3 verification with a live browser run against the local backend and model runtime.
2. Verify the Python app still matches the shared backend contract.
3. Start Phase 4 only after the shared contract is confirmed across both app surfaces.

## Main Files For The Next Step

- `web_client/src/App.jsx`
- `web_client/src/components/FileTree.jsx`
- `web_client/src/components/ContextModal.jsx`
- `web_client/src/components/GitModal.jsx`
- `web_client/src/components/ModelModal.jsx`
- `web_client/src/lib/api.js`
- `api/main.py`
- `handoff/coordination/shared_decisions.md`

## Reference
See `handoff/plans/repair_plan.md` for the full roadmap.
