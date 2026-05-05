# NeuroCLI

NeuroCLI has two supported app paths:

- a Python Textual app in `neurocli_app`
- a React web app in `web_client`

Both should use the same shared backend logic from `neurocli_core`.
The Textual app is the flagship product surface; React is the companion web surface.

## Getting Started

### Requirements

- Python 3.10+
- an OpenAI API key in the project `.env` file

Example:

```bash
OPENAI_API_KEY=sk-your-key
```

### Install

```bash
pip install -e .
```

### Run The Python App

```bash
neurocli
```

### Run The API Bridge

```bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8010
```

The React frontend defaults to `http://127.0.0.1:8010` for API calls.

### Run The React Frontend

```bash
cd web_client
npm install
npm run dev
```

### Local Verification Notes

The active plan still calls for manual Textual smoke testing and live browser smoke testing against the real model runtime. Some local test commands may require dependencies installed into `.codex_tmp_py/site-packages` and `PYTHONPATH` pointed at that folder.

## Project Docs

Project planning and handoff docs live in `handoff/`.

Project work uses compound checkpoints. Each phase should say plainly what someone can do in NeuroCLI after the work lands that they could not do before, and whether that capability is available in Textual, React, or only the backend/API.

Start with:

- `handoff/README.md`
- `handoff/plans/current_plan.md`
- `handoff/plans/roadmap.md`
- `handoff/coordination/shared_decisions.md`

Older phase plans live in `handoff/archive/` and are kept for historical context only.
