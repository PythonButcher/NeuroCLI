# Shared Decisions

## Architecture

- NeuroCLI has one shared backend contract and two supported frontends.
- `neurocli_core` is the backend source of truth for workflow and business behavior.
- `neurocli_app` is the full Python Textual frontend and should call `neurocli_core` directly.
- `api` is a FastAPI bridge that exposes the shared backend contract to the React frontend.
- `web_client` is the React frontend.
- Feature work should preserve parity between the Textual and React frontends whenever the shared backend supports the same behavior.
- The active roadmap is `handoff/plans/roadmap.md`.
- The next implementation slice is the shared generated-file proposal/diff artifact.
- Older phase plans live in `handoff/archive/` and are historical reference only.

## Ownership

- Codex owns backend, Python, API, shared logic, and React integration logic
- Gemini owns React UI and presentation work only

## Read Order

- `handoff/README.md`
- `handoff/plans/current_plan.md`
- `handoff/plans/roadmap.md`
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

## Historical React Phase 3 Contract Notes

- `web_client` now uses a shared API client in `web_client/src/lib/api.js`
- the frontend API base URL comes from `VITE_API_BASE_URL` and defaults to `http://127.0.0.1:8010`
- the React app must use `POST` streaming with `fetch`; it must not use the old `GET /stream?command=...` EventSource flow
- file selection in the tree controls `target_file`
- paperclip toggles in the tree control `context_paths`
- the model modal controls the optional `model` and `model_options` request fields
- the Git modal should use only `/api/git/status`, `/api/git/diff`, and `/api/git/commit`

## Historical Textual Phase 4 Contract Notes

- `neurocli_app/workflow_adapter.py` is the Textual-side adapter for the shared workflow contract
- the Textual app now sends the same request fields as the web path: `prompt`, optional `target_file`, optional `context_paths`, optional `model`, and optional `model_options`
- the Textual model modal maps directly to `model` and raw JSON `model_options`; it does not invent extra backend fields
- the Textual run flow now consumes structured events from `stream_ai_workflow`
- the Textual app uses the same normalized final response shape for both streamed completions and direct workflow responses
- local formatting, diff review, apply with backup, radar, and git actions remain app-side integrations over `neurocli_core` services
- context selections are sorted before request construction so the set-backed Textual UI produces deterministic `context_paths`

## Planning Workflow

The reusable Agent Council workflow lives in `handoff/agent_council/`. It is a planning and handoff system only. It can be used before major product, architecture, AI workflow, testing, or cross-frontend implementation decisions to capture structured debate and a strict JSON output for downstream analysis.

Council outputs do not change runtime behavior and do not define frontend or backend contracts by themselves. If a council recommends a contract change, Codex still owns defining or approving that contract before Gemini builds UI against it.

Each council subject must have its own folder under `handoff/agent_council/runs/`. A subject is a complete four-round council run, not one round inside a larger run. The final JSON for that subject must be saved as `output.json` inside the subject folder.

Every real council subject folder must also include a companion `README.md` created at the same time as `output.json`. That README must discuss the JSON output in human-readable terms, including what the council decided, how future agents should use the JSON, what the output does not authorize, and how to validate the run.

The recommended first council topic is the current generated-file review parity gap: define a shared generated-file proposal and diff contract so React can review AI file updates before apply while preserving the Textual review flow.

Completed real council runs:

- `handoff/agent_council/runs/2026-05-03-project-direction/`
- `handoff/agent_council/runs/2026-05-03-practical-state-of-art-features/`

These runs support the current direction: terminal-first AI development environment, React as a supported companion surface, and structured orchestration later after durable artifacts exist.

## Open Work

- Confirm the local Textual smoke-test path against the real model runtime.
- Confirm the local FastAPI and React browser smoke-test path against the real model runtime.
- Define the shared generated-file proposal/diff artifact in `neurocli_core`.
- Expose the proposal/diff artifact through `api` for React.
- Update React integration so AI file updates review backend proposal/diff data rather than raw `output_text` alone.
- Keep frontend cleanup from changing backend rules without updating this file.

## Historical Phase 5 Parity Audit

The shared prompt contract is aligned for both frontends: `prompt`, optional `target_file`, optional `context_paths`, optional `model`, and optional `model_options` flow through `neurocli_core`. Streaming is also aligned through structured `start`, `delta`, `complete`, and `error` events.

The main parity gap is generated file review. Textual formats a generated `file_update`, builds a diff with `neurocli_core.diff_generator`, and applies only after backup creation. React receives the same final workflow response but currently treats `output_text` as directly applyable proposed content, so it lacks the same formatted generated diff before apply. Fix this with a shared proposal/diff contract before treating the React UI as feature-complete.

Formatting existing files is aligned in behavior but not contract shape: Textual calls `format_code` and `generate_diff` directly; React uses `/api/format`, which mirrors that behavior through the API bridge. Apply-with-backup is also aligned in behavior: Textual calls `create_backup` and writes locally; React uses `/api/apply`.

Radar is aligned by service ownership. Textual calls `scan_workspace_health`, `scan_technical_debt`, and `scan_recent_edits`; React gets the same data through `/api/radar`.

Git is intentionally inconsistent today. React uses `/api/git/status`, `/api/git/diff`, and `/api/git/commit` with a manually entered commit message. Textual still generates an AI commit message through `neurocli_core.git_engine.generate_commit_message` and commits/pushes from the modal. Do not add AI commit-message UX to React unless Codex first exposes it as a shared backend/API contract.

## Historical Phase 5 Textual UI Decision

The Textual app is the flagship terminal experience. It now exposes a compact status strip with workflow state, active target file, context count, model state, and apply readiness. It also has a top command icon that opens a command reference modal, so keyboard controls are discoverable without occupying a permanent strip. The Textual action rail follows the workflow order Settings, Clear, Model, Context, Radar, Run, Format, Review, Commit. The Textual `Review` action opens an editable proposal window before commit, letting users revise generated or formatted content and then either keep the edited draft or apply it through the existing backup path. Keyboard bindings are part of the product contract for the terminal surface: Ctrl+R run, Ctrl+F format, Ctrl+A apply, Ctrl+M model, Ctrl+O context, Ctrl+D radar, Ctrl+E review, Ctrl+G git, Ctrl+K commands, Ctrl+L reset, and Ctrl+Q quit.

## Roadmap Decision

The active roadmap phases are:

1. Baseline and documentation.
2. Shared proposal and diff artifact.
3. Validation result artifact.
4. Workflow timeline.
5. Terminal-first experience.
6. Shared intelligence and React parity.
7. State-of-the-art layer.

Do not start MCP-style connectors, background task lanes, autonomous commits, productized council UI, or React-only diff logic before the shared proposal/diff artifact and verification baseline are in place.
