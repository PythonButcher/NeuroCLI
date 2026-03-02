# Implementation Plan: Workspace Radar (Health & Heatmap)

## Goal Description
Implement a "Workspace Radar" reporting modal that provides developers with a quick overview of their current working directory. It will visually display the codebase's language breakdown (Lines of Code and file types) and extract technical debt by cleanly listing all `# TODO` or `// FIXME` comments found in active files.

## Proposed Changes

### 1. Core Logic (The Engine)
- **[NEW] [radar_engine.py](file:///c:/Users/18022/Desktop/NeuroCLI/neurocli_core/radar_engine.py)**
  - Create `scan_workspace_health() -> dict`
    - Traverses the `CWD`, intentionally ignoring standard exclusion folders (`.git`, `.venv`, `__pycache__`, `node_modules`, `tests`, etc.).
    - Tracks occurrences of file extensions mapping to languages (e.g., Python, CSS, Markdown, Text).
    - Counts the total Lines of Code (LOC) for tracked files.
    - Returns a dictionary detailing the LOC per language and the calculated percentage.
  - Create `scan_technical_debt() -> list[dict]`
    - Reads through valid files line-by-line using a regex or simple string matching to find `# TODO`, `// TODO`, `# FIXME`, `<!-- TODO`, etc.
    - Returns a list of dictionaries, where each dict contains `file_name`, `line_number`, and `message`.

### 2. UI Components
- **[NEW] [radar_modal.py](file:///c:/Users/18022/Desktop/NeuroCLI/neurocli_app/radar_modal.py)**
  - Create `RadarModal(ModalScreen)`.
  - Use a `Grid` layout (or nested `Horizontal`/`Vertical` containers) to split the view into:
    - **Code Composition (Left)**: A stylised list or progress bar displaying the top languages and total LOC using the data from `scan_workspace_health()`.
    - **Technical Debt (Right)**: A `DataTable` that consumes the list from `scan_technical_debt()` to cleanly display the file path, line, and message for every TODO/FIXME found.
    - **Recent AI Heatmap**: A stylized placeholder container stating "Tracking active...".
- **[MODIFY] [main.py](file:///c:/Users/18022/Desktop/NeuroCLI/neurocli_app/main.py)**
  - Add a `btn_radar` button to the `toolbox` row (e.g., `📊 Radar`).
  - Update `on_button_pressed` to capture `#btn_radar` and push the `RadarModal` screen.

### 3. Styling
- **[MODIFY] [main.css](file:///c:/Users/18022/Desktop/NeuroCLI/neurocli_app/main.css)**
  - Add CSS classes for the `RadarModal`, ensuring a sleek, dark dashboard aesthetic with clear borders and distinct sections for composition and technical debt. Include styling for the `DataTable`.

## Verification Plan
1. Launch the application.
2. Click the new `📊 Radar` button in the toolbox.
3. Verify the modal opens and correctly calculates the lines of code and language composition for the `NeuroCLI` workspace.
4. Verify the `DataTable` accurately identifies and lists the 3 `TODO/FIXME` comments we recently added to `GEMINI.md`.
