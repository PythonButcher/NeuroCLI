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
This is the next active phase.

What we need to do:

1. Update `web_client/src/App.jsx` to use the real API routes.
2. Stop using the old fake stream flow.
3. Parse the real streaming event format from the backend.
4. Send `target_file` and `context_paths` in the request body.
5. Make the context picker actually control what gets sent to the backend.
6. Fix the `GitModal.jsx` runtime issue and remove placeholder-only git behavior that has no real backend support.
7. Move the API base URL into a cleaner frontend config path such as environment variables or a Vite proxy.

What Phase 3 should look like when done:

- a web user can send a prompt and get a real backend response
- a web user can target a file
- a web user can attach context files
- the web app can handle backend errors without breaking
- the web app is no longer using the old fake AI flow

### Phase 4: Preserve and Align the Python App
This phase comes right after Phase 3.

What we need to do:

1. Keep `neurocli_app` working with the shared workflow service.
2. Check that Python and web requests follow the same backend contract.
3. Confirm the Python app still supports prompt runs, file-targeted updates, context paths, formatting, apply flow, radar, and git tools.
4. Refactor only if needed to keep both app versions lined up with the same backend behavior.

What Phase 4 should look like when done:

- the Python app still works end to end
- the Python app and web backend use the same workflow rules
- there is no drift between the Python path and the web path for the main AI flow

## Later Work

### Phase 5
Clean up startup docs, dependency setup, and local run instructions.

### Phase 6
Expand tests and do full end-to-end verification for both app versions.
