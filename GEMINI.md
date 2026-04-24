# GEMINI.md

## NeuroCLI Gemini Instructions

Read this file first for Gemini work in this repository.

## Project Overview

- **Name:** NeuroCLI
- **Goal:** Maintain two supported product surfaces:
  - the Python-only Textual app
  - the React web frontend
- **Shared architecture:** `neurocli_core` remains the reusable backend source of truth.

## Gemini Role

Gemini is responsible for React frontend UI work only.

### Gemini should focus on

- Visual design in `web_client`
- Styling and layout
- Presentational React components
- UX polish, empty states, loading states, and consistency

### Gemini should not be the primary owner for

- `neurocli_core`
- `api`
- `neurocli_app`
- Python backend work
- Main AI workflow behavior
- React business logic and integration contracts unless Codex has already defined them

## Core Architectural Principle

Keep business logic separate from presentation:

- **`neurocli_core`:** backend engine and shared logic
- **`neurocli_app`:** Python Textual interface
- **`api`:** FastAPI backend for the React app
- **`web_client`:** React frontend

The React frontend should not become the place where backend logic lives.

## Collaboration With Codex

- Codex owns backend, Python, API, shared logic, and React integration logic.
- Gemini owns UI-only work in `web_client`.
- If a UI task depends on new backend data or changed payloads, record that in `handoff/coordination/shared_decisions.md`.
- Before starting, review:
  - `handoff/README.md`
  - `handoff/plans/current_plan.md`
  - `handoff/coordination/gemini_handoff.md`
  - `handoff/coordination/shared_decisions.md`

## UI Conventions

- Preserve established component boundaries where possible.
- Prefer presentational improvements over logic rewrites.
- Do not move stateful backend behavior into JSX components.
- Keep components ready to consume backend data from Codex-defined contracts.

## Safety

- Never delete or modify unrelated files without clear intent.
- Avoid changing backend-facing behavior without documenting it in the handoff docs.
