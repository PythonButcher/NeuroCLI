# NeuroCLI

NeuroCLI is a terminal-first AI development environment with one Python capability engine and two product surfaces:

- `neurocli_app`: flagship Python Textual application
- `web_client`: React companion application through the FastAPI bridge in `api`

Shared workflow and business behavior lives in `neurocli_core`.

## Local Setup

Requirements are Python 3.10+, Node.js for the web app, and an OpenAI API key.

Copy `.env.example` to `.env`, then set your real key locally. `.env` is ignored by Git.

Install the Python application:

```powershell
python -m pip install -e .
```

Run Textual:

```powershell
neurocli
```

Run the API in a second terminal:

```powershell
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8010
```

Run React in a third terminal:

```powershell
npm --prefix web_client install
npm --prefix web_client run dev
```

React defaults to `http://127.0.0.1:8010`. Override it locally with `web_client/.env` using the example in `web_client/.env.example`.

## Verification

```powershell
python -m unittest discover tests
python -m ruff check neurocli_core api neurocli_app tests
npm --prefix web_client run lint
npm --prefix web_client run build
```

Live model smoke testing requires valid credentials and remains separate from deterministic automated tests.

## Project Navigation

Start with [AGENTS.md](AGENTS.md), then read [the current plan](handoff/plans/current_plan.md). The active roadmap, contracts, parity record, owner handoffs, and archives are routed through [handoff/README.md](handoff/README.md).
