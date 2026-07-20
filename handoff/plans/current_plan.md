# Current Plan

## Current Direction

NeuroCLI should move forward as a terminal-first AI development environment with one shared Python capability engine and two supported frontend surfaces.

`neurocli_core` remains the backend source of truth. The Textual app in `neurocli_app` is the flagship surface and should be the first place where core workflow capabilities become practically usable. The React frontend in `web_client` is a supported companion surface and reaches the same backend behavior through the FastAPI bridge in `api`.

The Agent Council runs on May 3, 2026 clarified the product loop to strengthen: understand repo state, select target and context, generate a structured proposal, review a diff, validate the result, apply with backup, and prepare a commit with human approval.

## Compound Checkpoint Standard

Every implementation slice must answer this question before it is considered complete: what can a user do after this work that they could not do before?

That answer must name the surface: Textual app, React app, API, or backend only. Backend-only work is allowed as groundwork, but it is not a complete product checkpoint unless the docs explicitly name the missing app checkpoint. Because Textual is the flagship app, a phase that adds capability only to React or only to the API must identify the next Textual step.

## Current Status

Phase 1 is complete. React consumes backend generated-file proposal/diff artifacts for AI `file_update` responses. Textual keeps its existing local review/apply path because it already protects editable review, diff, backup, and explicit apply.

Phase 2 is complete at the compound-checkpoint level. The backend defines `ValidationResult`, `ValidationCommandPolicy`, and a shell-free runner selected only by approved command label. The API exposes `POST /api/validate`. Textual has a Validate action and Ctrl+T path that runs the approved `python_unittest` label and displays status, command label, duration, exit code, skipped state, details, and output excerpt. React has a matching Validate action over `/api/validate` and displays the same artifact.

Phase 3 is now complete at the compound-checkpoint level. The backend defines a redacted `WorkflowTimelineEvent` artifact, workflow responses include `timeline`, stream events may include `timeline_event`, and validation/apply/commit API responses attach timeline state without changing their existing primary fields. Textual, as the flagship app, shows a visible safe-loop timeline lane for the current run. React consumes the same backend timeline state and displays a compact companion status label.

The current practical answer is: a Textual user can now see where the workflow is in the safe loop, including context collection, target read, model request start, stream completion, proposal creation, diff generation, validation, apply readiness, backup creation, and commit preparation when those steps occur.

## Active Roadmap

The active phased roadmap lives in `handoff/plans/roadmap.md`. The next implementation slice is Phase 4: Terminal-First Experience.

## Current Compound Checkpoint

After Phase 3, a Textual user can see where the workflow is in the safe loop: context collected, target read, model request started, stream complete, proposal created, diff generated, validation run, apply ready, backup created, and commit prepared. Timeline events are redacted by default and do not store full source files, secrets, raw model prompts, diffs, or long command output.

React receives the same timeline event semantics through the API and displays a compact companion status label. Textual remains the reference surface for the full terminal-first workflow lane.

## Immediate Next Work

1. Start Phase 4 terminal-first experience work without changing backend contracts casually.
2. Improve Textual focus order, diff readability, review lane ergonomics, validation readiness, and safe workflow controls around the shared artifacts.
3. Preserve the existing timeline, proposal, validation, apply-with-backup, radar, and git behavior while improving terminal usability.
4. Keep React changes limited to consuming documented backend contracts unless the Phase 4 work explicitly defines a shared contract.

## Main Files For The Next Slice

- `neurocli_core/workflow_service.py`
- `neurocli_core/workflow_timeline.py`
- `api/main.py`
- `neurocli_app/main.py`
- `neurocli_app/workflow_adapter.py`
- `web_client/src/App.jsx`
- `tests/test_ai_services.py`
- `tests/test_workflow_timeline.py`
- `tests/test_api_main.py`
- `tests/test_textual_workflow_adapter.py`
- `handoff/plans/roadmap.md`
- `handoff/coordination/shared_decisions.md`
- `handoff/coordination/frontend_parity.md`
- `handoff/coordination/codex_handoff.md`

## Verification Notes

Use the local dependency cache when FastAPI, Textual, or SSE dependencies are unavailable in the default Python environment:

`$env:PYTHONPATH='.codex_tmp_py\\site-packages'; python -m unittest tests.test_workflow_timeline tests.test_validation_result tests.test_textual_workflow_adapter tests.test_api_main tests.test_ai_services tests.test_generated_file_proposal tests.test_radar_engine`

`npm --prefix web_client run build`

Full `python -m unittest discover tests` is currently blocked because `tests/testcli.py` contains plain error text and is not valid Python.

## Current Council Inputs

The active roadmap is based on these council runs:

- `handoff/agent_council/runs/2026-05-03-project-direction/`
- `handoff/agent_council/runs/2026-05-03-practical-state-of-art-features/`

Each real council run must include both `output.json` and a companion `README.md`.

## Archived Context

Older phase plans and idea documents are in `handoff/archive/`. They are useful history, not the active roadmap. In particular, `handoff/archive/repair_plan.md` and `handoff/archive/phase_5_direction.md` have been superseded by this current plan and `handoff/plans/roadmap.md`.
