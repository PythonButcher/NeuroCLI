# NeuroCLI React Frontend

This is the React companion surface for NeuroCLI.

The shared backend source of truth is `neurocli_core`. The React app reaches it through the FastAPI bridge in `api`, using `web_client/src/lib/api.js`. React should not duplicate backend workflow logic or invent API payloads that Codex has not defined.

## Current Role

React is a supported companion frontend, not a separate product backend. It should mirror shared safety-critical capabilities where the backend supports them, while using browser-native presentation.

React now consumes backend generated-file proposal artifacts for AI file updates. It should not replace that contract with frontend-only diff logic.

Validation is backend/API-defined and React has a safe Validate action over the approved `python_unittest` label. Do not replace it with raw command input or frontend-defined validation behavior.

## Compound Checkpoint Rule

Before changing React presentation, identify the current compound checkpoint in `../handoff/plans/current_plan.md`. Do not make React imply that a backend-only feature is fully available in the product when the Textual flagship checkpoint is still missing.

## Local Run

Install dependencies from this folder, then run the Vite dev server:

```bash
npm install
npm run dev
```

The frontend API base URL comes from `VITE_API_BASE_URL` and defaults to `http://127.0.0.1:8010`.

## Build

```bash
npm run build
```

## Planning References

Start with `../handoff/plans/current_plan.md`, `../handoff/plans/roadmap.md`, `../handoff/coordination/frontend_parity.md`, and `../handoff/coordination/gemini_handoff.md` before changing React presentation.
