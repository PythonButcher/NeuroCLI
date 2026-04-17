# Gemini Handoff

## Scope

Gemini owns React presentation work only.

## Primary Areas

- Layout and styling in `web_client`
- Presentational React components
- UI polish, spacing, typography, empty states, and visual consistency

## Guardrails

- Do not move backend logic into the frontend.
- Do not redefine API payloads without coordination through Codex.
- Do not take ownership of Python-only app changes.
- If a React change requires new data or new backend behavior, record the request in `handoff/shared_decisions.md`.

## Current Notes

- Treat `api` and `neurocli_core` as authoritative for behavior.
- Prefer UI changes that preserve existing props and state boundaries unless Codex has documented a new contract.
