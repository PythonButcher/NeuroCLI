# NeuroCLI Repair Plan

## Goal
Keep both product surfaces alive:

- The Python-only Textual application in `neurocli_app`
- The React frontend in `web_client`

Both experiences should use a functional backend for the main AI workflow instead of mocks or UI-only placeholders.

## Desired End State

### Shared backend strategy
- `neurocli_core` remains the single source of truth for AI behavior, prompt assembly, file context handling, formatting, backup creation, and git helpers.
- The Python Textual app calls `neurocli_core` directly.
- The React app calls a FastAPI backend in `api/`, and that API delegates to `neurocli_core` instead of duplicating business logic.

### Functional expectations
- A user can submit a prompt from either UI and receive a real AI response.
- File-targeted edits work from both UIs.
- Additional context files can be attached and passed into the main AI workflow.
- The web app can browse files, view diffs, apply edits, and use git utilities without placeholder behavior.
- The repo can be installed and run with documented commands for both app modes.

## Current Gaps

### Web workflow gaps
- The React command flow uses `/stream`, but the backend currently streams fake data instead of calling `neurocli_core`.
- The React client expects JSON-parsed SSE chunks, while the backend currently emits plain text chunks.
- Context management in the React app is mostly presentational and is not wired into the AI request path.
- Settings and model selection are placeholder-only UI.
- At least one React modal has an import/runtime bug (`Sparkles` in `GitModal.jsx`).

### Backend/runtime gaps
- `api/main.py` exists, but the FastAPI stack is not represented in `pyproject.toml`.
- The repo does not currently provide a clean documented startup path for the API server.
- The web app hardcodes `http://localhost:8000` and does not use environment-based configuration or a Vite proxy.

### Cross-surface product gaps
- The Python and web experiences do not yet share one clearly defined application service contract for prompt execution.
- There are limited validation steps proving that both UIs produce the same backend-driven behavior.

## Implementation Plan

### Phase 1: Stabilize the shared backend contract
1. Define a small service layer in `neurocli_core` for the main AI workflow.
2. Make that service accept:
   - `prompt`
   - optional `target_file`
   - optional `context_paths`
   - optional model/config selection hooks
3. Standardize the return shape so both the Textual app and FastAPI can consume it cleanly.
4. Separate synchronous response generation from streaming generation if needed, but keep both backed by the same core logic.

### Phase 2: Make the API a real backend
1. Replace the fake `/stream` implementation in `api/main.py` with real calls into `neurocli_core`.
2. Decide on one web protocol for AI responses:
   - SSE with structured JSON payloads, or
   - standard JSON for non-streaming requests
3. Add endpoints for:
   - prompt execution
   - streaming prompt execution
   - file/context-aware requests
   - model/config retrieval if that feature remains in scope
4. Keep existing useful endpoints for files, format, apply, radar, and git, but clean up their error handling and response shapes.
5. Add path-safety rules so file operations stay inside the workspace root.

### Phase 3: Wire the React app to the real backend
1. Update `web_client/src/App.jsx` to call the real API contract.
2. Fix the SSE parsing mismatch between frontend and backend.
3. Pass `targetFile` and `contextPaths` through the request payload instead of dropping them.
4. Make the file tree and context manager actually add and remove context files in a usable way.
5. Fix the `GitModal.jsx` import/runtime issue and remove placeholder-only commit message behavior unless backed by a real endpoint.
6. Move API base URL configuration into environment variables or a Vite proxy.

### Phase 4: Preserve and align the Python Textual app
1. Keep the current direct `neurocli_core` integration in `neurocli_app`.
2. Refactor only where needed so the Textual app and API both depend on the same backend service functions.
3. Confirm the Python UI still supports:
   - prompt execution
   - target-file editing
   - context paths
   - formatting and apply flow
   - radar and git tools

### Phase 5: Dependency and startup cleanup
1. Update `pyproject.toml` with required backend packages:
   - `fastapi`
   - `uvicorn`
   - `pydantic`
   - `sse-starlette`
2. Decide whether frontend formatting dependencies like Prettier should be repo-local dev dependencies or documented external requirements.
3. Add clear run commands for:
   - Textual app
   - FastAPI backend
   - React frontend
4. Add a root-level developer workflow section to `README.md`.

### Phase 6: Testing and verification
1. Add backend tests for the API prompt routes.
2. Add tests for file, apply, and formatting endpoints.
3. Add at least one React integration test for the prompt submission flow.
4. Add smoke tests confirming:
   - Python UI can still invoke the real AI backend logic
   - Web UI can invoke the same logic through FastAPI
5. Validate that both frontends handle missing API keys and backend failures gracefully.

## Proposed File Areas

### Core/backend
- `neurocli_core/engine.py`
- `neurocli_core/ai_services.py`
- `neurocli_core/file_handler.py`
- `neurocli_core/git_engine.py`
- `api/main.py`
- `pyproject.toml`

### React frontend
- `web_client/src/App.jsx`
- `web_client/src/components/FileTree.jsx`
- `web_client/src/components/ContextModal.jsx`
- `web_client/src/components/GitModal.jsx`
- `web_client/vite.config.js`
- `web_client/README.md`

### Docs/tests
- `README.md`
- `tests/`
- optional new API/web test files

## Acceptance Criteria

### Python Textual app
- Launches from the documented command.
- Uses real `neurocli_core` AI execution.
- Can submit prompts with optional target file and context.
- Can show proposed changes and apply them successfully.

### React app
- Launches with the documented frontend and backend commands.
- Can submit prompts and receive real backend responses.
- Can send target file and context paths to the backend.
- Can browse files, format files, and apply changes.
- Can open git and radar views without runtime errors.

### Shared platform
- No fake AI stream remains in the main workflow.
- One documented backend contract powers both app modes.
- Repo dependencies are sufficient to run the API locally.

## Recommended Execution Order
1. Fix the shared backend contract in `neurocli_core`.
2. Replace the fake FastAPI AI flow with a real one.
3. Wire the React app to the real API contract.
4. Fix frontend placeholders and runtime issues.
5. Clean up dependencies and documentation.
6. Add tests and perform end-to-end validation for both app modes.

## Nice-to-Have Follow-ups
- Add model selection backed by real configuration rather than placeholder UI.
- Add structured status events for streaming so the web client can show progress cleanly.
- Add a unified settings store shared by both interfaces.
- Add CI checks for Python tests, frontend lint/build, and API smoke tests.
