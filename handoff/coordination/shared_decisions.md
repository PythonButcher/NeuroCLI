# Shared Decisions

## Architecture

- NeuroCLI has one shared backend contract and two supported frontends.
- `neurocli_core` is the backend source of truth for workflow and business behavior.
- `neurocli_app` is the full Python Textual frontend and should call `neurocli_core` directly.
- `api` is a FastAPI bridge that exposes the shared backend contract to the React frontend.
- `web_client` is the React frontend.
- Feature work should preserve parity between the Textual and React frontends whenever the shared backend supports the same behavior.
- The active roadmap is `handoff/plans/roadmap.md`.
- The current completed implementation slice is Phase 3 workflow timeline.
- Older phase plans live in `handoff/archive/` and are historical reference only.

## Compound Checkpoints

A compound checkpoint is required for every phase and implementation slice. It answers, in one practical statement, what a user can do after the work that they could not do before.

Each checkpoint must name the available surface: Textual app, React app, API, or backend only. Because Textual is the flagship app, backend-only or React-only work must document the missing Textual checkpoint and should not be described as product-complete.

Completed Phase 2 checkpoint: approved validation is usable in both app surfaces through the shared `ValidationResult` artifact. Users can run the safe `python_unittest` label and see pass, fail, timeout, skipped, or policy rejection details.

Completed Phase 3 checkpoint: Textual users can see the current safe-loop workflow timeline, including context collection, target read, model request start, stream completion, proposal creation, diff generation, validation, apply readiness, backup creation, and commit preparation when those steps occur. React consumes the same backend timeline event shape and shows compact status only.

## Ownership

- Codex owns backend, Python, API, shared logic, and React integration logic
- Gemini owns React UI and presentation work only

## Read Order

- `handoff/README.md`
- `handoff/plans/current_plan.md`
- `handoff/plans/roadmap.md`
- `handoff/coordination/shared_decisions.md`
- `handoff/coordination/frontend_parity.md`

## Frontend Differences

Textual and React may intentionally differ. The canonical record of those differences is `handoff/coordination/frontend_parity.md`.

If one surface gains a feature the other does not have, update `frontend_parity.md` in the same slice. The difference should be marked as temporary, intentional, or a blocked parity gap.

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
- optional `proposal`
- optional `validation_result`
- `timeline`

## Generated File Proposal Contract

AI `file_update` responses now include a shared generated-file proposal artifact at `response.proposal`. Non-file chat responses keep `proposal` as `null`.

The proposal artifact is created in `neurocli_core/generated_file_proposal.py` and exposed unchanged through `api` via the normal workflow response serialization. React generated-file review must consume this backend artifact instead of treating raw `output_text` as directly applicable file content.

Proposal fields:

- `target_path`
- `original_content`
- `original_content_reference`
- `proposed_content`
- `normalized_content`
- `diff_text`
- `status`
- `errors`

Proposal status values:

- `ready`: formatted or normalized content differs from the original and can be reviewed before apply.
- `no_change`: normalized content matches the original; no apply action should be offered.
- `error`: proposal creation failed, such as empty model output, formatter failure, or diff failure; no apply action should be offered.

The artifact currently stores `original_content` directly because the existing workflow response already returns the original target content. A later persistence layer may replace this with a durable content reference, but frontends should not invent that reference.

Textual keeps its existing review/apply path for generated-file proposals. It may consume the shared proposal later only if that preserves the current format, diff, editable review, backup, and explicit apply behavior.

## Validation Result Contract

Workflow responses now include a shared validation artifact at `response.validation_result`. The workflow currently reports validation as skipped by default; validation is not run automatically during prompt, stream, or apply.

The validation artifact is created in `neurocli_core/validation_result.py` and can also be returned by `POST /api/validate`. Validation execution is selected only by a stable `command_label`; neither model output nor frontend text can provide a raw shell command.

Validation fields:

- `status`
- `command_label`
- `duration_seconds`
- `exit_code`
- `skipped`
- `output_excerpt`
- `error_details`

Validation status values:

- `passed`: the approved command exited with code 0.
- `failed`: the approved command ran and exited non-zero, or the executable failed to start.
- `timeout`: the approved command exceeded its configured timeout.
- `skipped`: validation was not requested for the current workflow response.
- `rejected`: a requested label was not present in the active command policy and no process was started.

Command policy rules:

- Validation uses `ValidationCommandPolicy`, an explicit allowlist keyed by `command_label`.
- Built-in labels currently include `python_unittest` and `react_build`.
- A workspace may add labels through `neurocli_validation.json` with `commands.<label>.argv` as a string array and optional `timeout_seconds`.
- Commands run with `shell=False`; raw command strings are not accepted by the shared validation runner.
- Model output must never be treated as a validation command label or argv source.

React consumes `response.validation_result` in the status strip and can run the approved `python_unittest` label through `/api/validate`.

Textual can run the approved `python_unittest` label through the Validate action or Ctrl+T and displays the shared artifact. Neither app accepts raw validation command text.

## Workflow Timeline Contract

Timeline events are defined in `neurocli_core.workflow_timeline.WorkflowTimelineEvent`. The artifact is intentionally concise and redacted by default. Timeline events must not store full source files, secrets, raw model prompts, raw model outputs, diffs, or long command output. Those details stay in their existing reviewed artifacts, such as the workflow response, proposal, validation excerpt, or local file system.

Timeline event fields:

- `event_type`
- `status`
- `label`
- `summary`
- `metadata`
- `occurred_at`

Current event types:

- `context_collected`
- `target_read`
- `model_request_started`
- `stream_complete`
- `proposal_created`
- `diff_generated`
- `validation_run`
- `apply_ready`
- `backup_created`
- `commit_prepared`

Current event status values:

- `completed`
- `running`
- `skipped`
- `error`

Workflow responses include a `timeline` list. Stream events may include a single `timeline_event` for state transitions that occur before the final response, such as model request start or stream completion. API validation, apply, and commit responses may include `timeline` while preserving their existing top-level success, status, message, error, and validation fields.

Textual is the reference surface for displaying the timeline as a safe-loop lane. React consumes the same event shape through the API and currently displays a compact companion status label rather than a full lane.

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
- validation is exposed through `POST /api/validate` with a policy-approved `command_label`
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

The first council-backed implementation topic was the generated-file review parity gap: define a shared generated-file proposal and diff contract so React can review AI file updates before apply while preserving the Textual review flow. That is now historical context; the active checkpoint is Textual validation.

Completed real council runs:

- `handoff/agent_council/runs/2026-05-03-project-direction/`
- `handoff/agent_council/runs/2026-05-03-practical-state-of-art-features/`

These runs support the current direction: terminal-first AI development environment, React as a supported companion surface, and structured orchestration later after durable artifacts exist.

## Open Work

- Confirm the local Textual smoke-test path against the real model runtime.
- Confirm the local FastAPI and React browser smoke-test path against the real model runtime.
- Run live smoke verification for shared proposal, validation, and timeline display against Textual, the local FastAPI backend, and React once model credentials/runtime are available.
- Keep timeline content redacted by default and avoid storing full source files, secrets, raw model prompts, diffs, or long outputs.
- Keep frontend cleanup from changing backend rules without updating this file.

## Historical Phase 5 Parity Audit

The shared prompt contract is aligned for both frontends: `prompt`, optional `target_file`, optional `context_paths`, optional `model`, and optional `model_options` flow through `neurocli_core`. Streaming is also aligned through structured `start`, `delta`, `complete`, and `error` events.

The main parity gap was generated file review. Textual formats a generated `file_update`, builds a diff with `neurocli_core.diff_generator`, and applies only after backup creation. React now consumes the shared backend proposal/diff artifact for generated file updates instead of treating `output_text` as directly applicable proposed content.

Formatting existing files is aligned in behavior but not contract shape: Textual calls `format_code` and `generate_diff` directly; React uses `/api/format`, which mirrors that behavior through the API bridge. Apply-with-backup is also aligned in behavior: Textual calls `create_backup` and writes locally; React uses `/api/apply`.

Radar is aligned by service ownership. Textual calls `scan_workspace_health`, `scan_technical_debt`, and `scan_recent_edits`; React gets the same data through `/api/radar`.

Git is intentionally inconsistent today. React uses `/api/git/status`, `/api/git/diff`, and `/api/git/commit` with a manually entered commit message. Textual still generates an AI commit message through `neurocli_core.git_engine.generate_commit_message` and commits/pushes from the modal. Do not add AI commit-message UX to React unless Codex first exposes it as a shared backend/API contract.

## Historical Phase 5 Textual UI Decision

The Textual app is the flagship terminal experience. It now exposes a compact status strip with workflow state, active target file, context count, model state, and apply readiness. It also has a top command icon that opens a command reference modal, so keyboard controls are discoverable without occupying a permanent strip. The Textual action rail follows the workflow order Settings, Clear, Model, Context, Radar, Run, Format, Review, Commit. The Textual `Review` action opens an editable proposal window before commit, letting users revise generated or formatted content and then either keep the edited draft or apply it through the existing backup path. Keyboard bindings are part of the product contract for the terminal surface: Ctrl+R run, Ctrl+F format, Ctrl+A apply, Ctrl+M model, Ctrl+O context, Ctrl+D radar, Ctrl+E review, Ctrl+G git, Ctrl+K commands, Ctrl+L reset, and Ctrl+Q quit.

## Roadmap Decision

The active roadmap phases are:

0. Baseline and documentation.
1. Shared proposal and diff artifact.
2. Validation result artifact and safe validation.
3. Workflow timeline.
4. Terminal-first experience.
5. Shared intelligence and React parity.
6. State-of-the-art layer.

Do not start MCP-style connectors, background task lanes, autonomous commits, productized council UI, or React-only orchestration controls during the Phase 4 terminal-first slice unless the active roadmap explicitly changes.
