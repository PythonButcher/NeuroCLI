# NeuroCLI React Frontend

This is the React companion surface for NeuroCLI.

The shared backend source of truth is `neurocli_core`. The React app reaches it through the FastAPI bridge in `api`, using `web_client/src/lib/api.js`. React should not duplicate backend workflow logic or invent API payloads that Codex has not defined.

## Current Role

React is a supported companion frontend, not a separate product backend. It should mirror shared safety-critical capabilities where the backend supports them, while using browser-native presentation.

The current known parity gap is generated-file review. Textual can format, diff, review, and apply generated file updates with backup. React should not claim equivalent generated-file diff review until Codex exposes a shared proposal/diff artifact through `api`.

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

Start with `../handoff/plans/current_plan.md`, `../handoff/plans/roadmap.md`, and `../handoff/coordination/gemini_handoff.md` before changing React presentation.
