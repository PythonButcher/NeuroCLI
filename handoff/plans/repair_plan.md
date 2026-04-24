# NeuroCLI Repair Plan

## Goal
Keep both versions of NeuroCLI working:

- the Python Textual app in `neurocli_app`
- the React web app in `web_client`

Both versions should use the same real AI workflow from `neurocli_core`.

## Current State

### Phase 1
Done.

We added a shared AI workflow service in `neurocli_core`.
That service now accepts:

- `prompt`
- optional `target_file`
- optional `context_paths`
- optional `model`
- optional `model_options`

It also returns one stable response shape for normal requests and one stable event shape for streaming.

### Phase 2
Done.

We replaced the fake AI flow in `api/main.py`.
The API now calls the shared workflow service in `neurocli_core` instead of making up fake stream output.

The API now has:

- a real prompt endpoint
- a real streaming endpoint
- workspace path checks for file reads and writes
- updated backend dependencies and tests

## Next Work

### Phase 3: Wire the React App to the Real Backend
This is the current active phase.

What we need to do:

1. Run a final live browser smoke test against the local backend with the real model runtime available.
2. Confirm no contract drift remains between the React app and `api/main.py`.

What is already done in Phase 3:

1. `web_client/src/App.jsx` now sends the real request body to `POST /api/ai/stream` and falls back to `POST /api/ai/prompt` when streaming is unavailable.
2. The web app now parses the structured stream events from the backend instead of assuming plain-text SSE chunks.
3. `target_file`, `context_paths`, `model`, and `model_options` are now wired into the React request payload.
4. The file tree now controls `target_file` selection and lets users toggle prompt context files directly.
5. The context modal now reflects the real `context_paths` payload instead of placeholder-only behavior.
6. `GitModal.jsx` no longer crashes at runtime and now uses only the backend git endpoints that actually exist.
7. The frontend API base URL now comes from `VITE_API_BASE_URL`, defaulting to `http://127.0.0.1:8010`, through a shared client module.

What Phase 3 should look like when closed:

- a web user can send a prompt and get a real backend response
- a web user can target a file
- a web user can attach context files
- the web app can handle backend errors without breaking
- the web app is no longer using the old fake AI flow
- local browser verification is complete against the running backend

### Phase 4: Preserve and Align the Python App
This phase is now active in code.

What we need to do:

1. Keep `neurocli_app` working with the shared workflow service.
2. Check that Python and web requests follow the same backend contract.
3. Confirm the Python app still supports prompt runs, file-targeted updates, context paths, formatting, apply flow, radar, and git tools.
4. Refactor only if needed to keep both app versions lined up with the same backend behavior.

What Phase 4 should look like when done:

- the Python app still works end to end
- the Python app and web backend use the same workflow rules
- there is no drift between the Python path and the web path for the main AI flow

What is already done in Phase 4:

1. `neurocli_app/main.py` now builds the same normalized workflow request fields used by the web path: `prompt`, optional `target_file`, optional `context_paths`, optional `model`, and optional `model_options`.
2. The Textual app now uses `stream_ai_workflow` through `neurocli_app/workflow_adapter.py` and applies the same final normalized response shape used by sync and streaming callers.
3. The Textual app now has a model settings modal so users can set `model` and raw JSON `model_options` without introducing app-specific request fields.
4. File updates still go through the existing local review flow: the normalized workflow response is formatted, diffed, and then applied with backup creation.
5. Radar and git flows remain on the existing `neurocli_core` services instead of duplicating backend logic in the app.
6. Added adapter-level tests to pin the Phase 4 request mapping and streaming contract.

Remaining Phase 4 gaps:

- manual end-to-end Textual verification with a real model runtime still needs to be run
- API/browser verification is blocked in this environment until `fastapi` is installed again
- larger end-to-end test expansion is still deferred to the later test phase

## Later Work

### Phase 5
Clean up startup docs, dependency setup, and local run instructions.

### Phase 6
Expand tests and do full end-to-end verification for both app versions.
