# Gemini Handoff

## Scope
Gemini owns React presentation work only.

## Primary Areas

- layout and styling in `web_client`
- presentational React components
- UI polish, spacing, empty states, and visual consistency

## Guardrails

- do not move backend logic into the frontend
- do not redefine API payloads without coordination through Codex
- do not take ownership of Python-only app changes
- if a React change needs new backend behavior, record it in `handoff/coordination/shared_decisions.md`

## Current Notes

- treat `api` and `neurocli_core` as the source of truth for behavior
- prefer UI work that keeps existing props and state boundaries unless Codex documents a new contract
