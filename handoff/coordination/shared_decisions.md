# Shared Decisions And Contracts

## Architecture

`neurocli_core` is the single source of workflow and business behavior. `neurocli_app` calls it directly. `api` exposes it to `web_client`. Frontends may present behavior differently but must not duplicate or weaken shared rules.

Textual is the flagship surface. React is a supported companion. `frontend_parity.md` is the authoritative record of intentional surface differences.

## Shared AI Workflow

The workflow entry point lives in `neurocli_core/workflow_service.py`.

Request fields are `prompt`, optional `target_file`, optional `context_paths`, optional `model`, and optional `model_options`.

Normalized response fields are `ok`, `status`, `response_kind`, `prompt`, `output_text`, `target_file`, `context_paths`, `original_content`, `model`, `error`, optional `proposal`, optional `validation_result`, and `timeline`.

Stream events use `start`, `delta`, `complete`, or `error`. Incremental text is carried in `delta`; final normalized responses are carried in `response`; state transitions may include `timeline_event`.

## Generated-File Proposal

AI `file_update` responses include `response.proposal`; chat responses keep it `null`. The artifact is built in `neurocli_core/generated_file_proposal.py` and carries `target_path`, `original_content`, `original_content_reference`, `proposed_content`, `normalized_content`, `diff_text`, `status`, and `errors`.

Statuses are:

- `ready`: normalized content differs and can be reviewed.
- `no_change`: normalized content matches the original.
- `error`: proposal creation, formatting, or diff generation failed.

React must consume this backend artifact rather than treating raw model text as directly applicable content. Textual may retain its local review path while it preserves editable review, diff inspection, backup creation, and explicit apply.

## Validation

`neurocli_core/validation_result.py` defines the validation artifact, allowlist policy, and shell-free runner. Result fields are `status`, `command_label`, `duration_seconds`, `exit_code`, `skipped`, `output_excerpt`, and `error_details`.

Statuses are `passed`, `failed`, `timeout`, `skipped`, or `rejected`. Commands are selected by stable label and run with `shell=False`; model or frontend text must never supply raw command text or argv.

Built-in labels are `python_unittest` and `react_build`. A workspace may add labels through `neurocli_validation.json`, where each command defines an argv string array and optional positive timeout.

Textual and React can run workspace validation with `python_unittest`. When a Python target is selected, each surface builds a narrow `python_unittest_target` policy entry for that file. Non-Python or out-of-workspace targets are rejected without starting a process.

The API route is `POST /api/validate`. Prompt, stream, and apply do not run validation automatically.

## Workflow Timeline

`neurocli_core/workflow_timeline.py` defines `WorkflowTimelineEvent`. Fields are `event_type`, `status`, `label`, `summary`, `metadata`, and `occurred_at`.

Event types are `context_collected`, `target_read`, `model_request_started`, `stream_complete`, `proposal_created`, `diff_generated`, `validation_run`, `apply_ready`, `backup_created`, and `commit_prepared`.

Statuses are `completed`, `running`, `skipped`, or `error`.

Timeline events are concise metadata, not an audit copy of reviewed artifacts. They must not store full prompts, source files, generated output, diffs, credentials, secrets, authorization data, or long command output. Redaction is applied by the shared timeline helpers.

Workflow responses include `timeline`; stream transitions may include `timeline_event`; validation, apply, and commit API responses may attach `timeline` without changing their primary response fields.

Textual displays the current safe-loop lane. React displays a compact recent-event label from the same event shape.

## Workspace And API Safety

Primary AI routes are `POST /api/ai/prompt` and `POST /api/ai/stream`. The local API defaults to `http://127.0.0.1:8010`.

The API resolves file paths inside the configured workspace before reading, formatting, applying, validating, or committing. File operations outside the workspace are rejected. Apply creates a backup before writing. Neither frontend may apply or commit automatically.

React API integration belongs in `web_client/src/lib/api.js`. The base URL comes from `VITE_API_BASE_URL` and defaults to the local API address. Streaming uses POST with `fetch`, not the retired GET/EventSource flow.

## Git Difference

Textual can generate an AI commit-message draft through `neurocli_core.git_engine`. React exposes manual status, diff, and commit operations through the API. Do not add AI commit-message behavior to React until Codex defines a shared API contract.

## Documentation And Harness

`handoff/plans/current_plan.md` owns current status. The roadmap owns phase order. Completed or superseded detail belongs in `handoff/archive/`.

Project-local `.agents`, `.codex`, and `.gemini` directories remain empty placeholders. Do not add skills, hooks, custom agents, or provider-specific automation until a recurring project need justifies the maintenance cost.
