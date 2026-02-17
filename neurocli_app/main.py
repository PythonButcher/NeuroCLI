from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal, Container
from textual.widgets import Header, Footer, Input, Button, Markdown, LoadingIndicator, Static
from textual.worker import Worker, WorkerState
from textual_fspicker import FileOpen
from neurocli_app.theme import arctic_theme, modern_theme

from neurocli_core.engine import get_ai_response
from neurocli_core.diff_generator import generate_diff
from neurocli_core.code_formatter import format_python_code

import os
from neurocli_core.file_handler import create_backup


SIDEBAR_LOGO = """╔════════════════════╗
║    >_  NeuroCLI    ║
╚════════════════════╝"""


class NeuroApp(App):
    """The main application for NeuroCLI."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]
    CSS_PATH = "main.css"

    _proposed_content: str = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Button("Reset", id="reset_screen")

        with Horizontal(id="app_layout"):
            with Container(id="sidebar"):
                yield Static(SIDEBAR_LOGO, id="background_image")
                with VerticalScroll(id="sidebar_nav"):
                    yield Button("Engine", id="nav_engine", classes="nav_button")
                    yield Button("Dashboard", id="nav_dashboard", classes="nav_button")
                    yield Button("Code Diffing", id="nav_code_diffing", classes="nav_button")
                    yield Button("Settings", id="nav_settings", classes="nav_button")

            with VerticalScroll(id="workspace"):
                with Container(id="workspace_panel"):
                    with Horizontal(id="file-container"):
                        yield Input(
                            placeholder="Enter file path for context (optional)...",
                            id="file_path_input",
                        )
                        yield Button("Browse...", id="browse_button")

                    yield Input(placeholder="Enter your prompt...", id="prompt_input")

                    with Container(id="run_row"):
                        yield Button("Run", id="run_button")

                    yield Markdown("AI response will appear here...", id="response_display")
                    yield LoadingIndicator(id="loading_indicator")
                    yield Button("Apply Changes", id="apply_button")

                    with Container(id="button_container"):
                        yield Static("Apply these changes?", id="dialog_text")
                        yield Button("Yes", id="yes", variant="success")
                        yield Button("No", id="no", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.register_theme(arctic_theme)
        self.register_theme(modern_theme)

        self.theme = "arctic"
        self.theme = "modern_dark_neon"
        self.query_one("#loading_indicator").styles.display = "none"
        self.query_one("#apply_button").styles.display = "none"
        self.query_one("#button_container").styles.display = "none"

    def _run_prompt(self) -> None:
        """Run the AI request using values from existing inputs."""
        prompt_input = self.query_one("#prompt_input", Input)
        prompt = prompt_input.value
        if not prompt.strip():
            return

        file_path = self.query_one("#file_path_input", Input).value
        self.query_one("#background_image").styles.display = "none"
        self.query_one("#loading_indicator").styles.display = "block"
        self.run_worker(lambda: get_ai_response(prompt, file_path), thread=True)
        prompt_input.value = ""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button actions while keeping existing wiring intact."""
        if event.button.id == "browse_button":
            self.push_screen(FileOpen(), self.on_file_open_selected)
        elif event.button.id == "run_button":
            self._run_prompt()
        elif event.button.id == "apply_button":
            self.query_one("#button_container").styles.display = "block"

        elif event.button.id == "yes":
            file_path = self.query_one("#file_path_input", Input).value
            if file_path and self._proposed_content:
                try:
                    backup_dir = os.path.join(os.path.dirname(file_path), "backups")
                    create_backup(file_path, backup_dir)

                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(self._proposed_content)

                    self.query_one("#response_display").update(
                        f"Changes applied to {file_path} successfully."
                    )
                    self._proposed_content = ""
                    self.query_one("#apply_button").styles.display = "none"
                    self.query_one("#button_container").styles.display = "none"
                except Exception as error:
                    self.query_one("#response_display").update(
                        f"Error applying changes: {error}"
                    )

        elif event.button.id == "no":
            self.query_one("#button_container").styles.display = "none"

    def on_file_open_selected(self, path: str) -> None:
        """Callback for when a file is selected from the dialog."""
        if path:
            self.query_one("#file_path_input", Input).value = str(path)

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle prompt input submit on Enter."""
        if message.input.id == "prompt_input":
            self._run_prompt()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        loading_indicator = self.query_one("#loading_indicator")
        markdown_display = self.query_one("#response_display", Markdown)

        if event.state == WorkerState.SUCCESS:
            original_content, new_content = event.worker.result
            if original_content:
                formatted_content = format_python_code(new_content)
                diff = generate_diff(original_content, formatted_content)
                markdown_display.update(diff)
                self._proposed_content = formatted_content
                self.query_one("#apply_button").styles.display = "block"
            else:
                markdown_display.update(new_content)
                self.query_one("#apply_button").styles.display = "none"

        elif event.state == WorkerState.ERROR:
            error_message = f"### Worker Error\n\n```\n{event.worker.error}\n```"
            markdown_display.update(error_message)

        self.query_one("#background_image").styles.display = "block"
        loading_indicator.styles.display = "none"


def main():
    app = NeuroApp()
    app.run()


if __name__ == "__main__":
    main()
