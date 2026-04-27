# Shared Decisions

## Architecture

- NeuroCLI has one shared backend contract and two supported frontends.
- `neurocli_core` is the backend source of truth for workflow and business behavior.
- `neurocli_app` is the full Python Textual frontend and should call `neurocli_core` directly.
- `api` is a FastAPI bridge that exposes the shared backend contract to the React frontend.
- `web_client` is the React frontend.
- Feature work should preserve parity between the Textual and React frontends whenever the shared backend supports the same behavior.

## Ownership

- Codex owns backend, Python, API, shared logic, and React integration logic
- Gemini owns React UI and presentation work only

## Read Order

- `handoff/README.md`
- `handoff/plans/current_plan.md`
- `handoff/coordination/shared_decisions.md`

## Shared AI Contract

The shared prompt workflow lives in `neurocli_core/workflow_service.py`.

Request fields:

- `prompt`
- optional `target_file`
- optional `context_paths`
- optional `model`
- optional `model_options`

Sync response fields:

- `ok`
- `status`
- `response_kind`
- `prompt`
- `output_text`
- `target_file`
- `context_paths`
- `original_content`
- `model`
- `error`

Stream event fields:

- `event`
- `delta`
- optional `response`

Stream event semantics:

- `start` begins a request and carries an empty `delta`
- `delta` carries incremental text in `delta`
- `complete` carries the final normalized workflow response in `response`
- `error` carries the normalized workflow error response in `response`

## API Rules

- the main API routes are `POST /api/ai/prompt` and `POST /api/ai/stream`
- the API resolves file paths inside the workspace before calling `neurocli_core`
- file endpoints reject reads and writes outside the workspace
- local backend startup should use `http://127.0.0.1:8010`

## React Phase 3 Contract Notes

- `web_client` now uses a shared API client in `web_client/src/lib/api.js`
- the frontend API base URL comes from `VITE_API_BASE_URL` and defaults to `http://127.0.0.1:8010`
- the React app must use `POST` streaming with `fetch`; it must not use the old `GET /stream?command=...` EventSource flow
- file selection in the tree controls `target_file`
- paperclip toggles in the tree control `context_paths`
- the model modal controls the optional `model` and `model_options` request fields
- the Git modal should use only `/api/git/status`, `/api/git/diff`, and `/api/git/commit`

## Textual Phase 4 Contract Notes

- `neurocli_app/workflow_adapter.py` is the Textual-side adapter for the shared workflow contract
- the Textual app now sends the same request fields as the web path: `prompt`, optional `target_file`, optional `context_paths`, optional `model`, and optional `model_options`
- the Textual model modal maps directly to `model` and raw JSON `model_options`; it does not invent extra backend fields
- the Textual run flow now consumes structured events from `stream_ai_workflow`
- the Textual app uses the same normalized final response shape for both streamed completions and direct workflow responses
- local formatting, diff review, apply with backup, radar, and git actions remain app-side integrations over `neurocli_core` services
- context selections are sorted before request construction so the set-backed Textual UI produces deterministic `context_paths`

## Open Work

- Phase 3 still needs a final live browser smoke test against the local backend and real model runtime
- Phase 4 still needs a manual Textual smoke test against a real model runtime
- local API verification can pass when `.codex_tmp_py/site-packages` is added to `PYTHONPATH`; the default Python path still does not see those local dependencies
- Phase 5 should focus on frontend quality, feature parity, and a terminal-first experience that still uses the shared backend contract
- frontend cleanup should not change backend rules without updating this file

## Phase 5 Parity Audit

The shared prompt contract is aligned for both frontends: `prompt`, optional `target_file`, optional `context_paths`, optional `model`, and optional `model_options` flow through `neurocli_core`. Streaming is also aligned through structured `start`, `delta`, `complete`, and `error` events.

The main parity gap is generated file review. Textual formats a generated `file_update`, builds a diff with `neurocli_core.diff_generator`, and applies only after backup creation. React receives the same final workflow response but currently treats `output_text` as directly applyable proposed content, so it lacks the same formatted generated diff before apply. Fix this with a shared proposal/diff contract before treating the React UI as feature-complete.

Formatting existing files is aligned in behavior but not contract shape: Textual calls `format_code` and `generate_diff` directly; React uses `/api/format`, which mirrors that behavior through the API bridge. Apply-with-backup is also aligned in behavior: Textual calls `create_backup` and writes locally; React uses `/api/apply`.

Radar is aligned by service ownership. Textual calls `scan_workspace_health`, `scan_technical_debt`, and `scan_recent_edits`; React gets the same data through `/api/radar`.

Git is intentionally inconsistent today. React uses `/api/git/status`, `/api/git/diff`, and `/api/git/commit` with a manually entered commit message. Textual still generates an AI commit message through `neurocli_core.git_engine.generate_commit_message` and commits/pushes from the modal. Do not add AI commit-message UX to React unless Codex first exposes it as a shared backend/API contract.

## Phase 5 Textual UI Decision

The Textual app is the flagship terminal experience. It now exposes a compact status strip with workflow state, active target file, context count, model state, and apply readiness. Keyboard bindings are part of the product contract for the terminal surface: Ctrl+R run, Ctrl+F format, Ctrl+A apply, Ctrl+M model, Ctrl+O context, Ctrl+D radar, Ctrl+G git, Ctrl+L reset, and Ctrl+Q quit.
