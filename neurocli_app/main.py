from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Header, Footer, Input, Button, Markdown, LoadingIndicator
from textual.worker import Worker, WorkerState
from textual_fspicker import FileOpen

from neurocli_core.engine import get_ai_response

class NeuroApp(App):
    """The main application for NeuroCLI."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with VerticalScroll(id="main-content"):
            with Horizontal(id="file-container"):
                yield Input(placeholder="Enter file path for context (optional)...", id="file_path_input")
                yield Button("Browse...", id="browse_button")
            yield Input(placeholder="Enter your prompt...", id="prompt_input")
            yield Markdown("AI response will appear here...", id="response_display")
            yield LoadingIndicator(id="loading_indicator")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.query_one("#loading_indicator").styles.display = "none"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the press of the 'Browse...' button."""
        if event.button.id == "browse_button":
            self.push_screen(FileOpen(), self.on_file_open_selected)

    def on_file_open_selected(self, path: str) -> None:
        """Callback for when a file is selected from the dialog."""
        if path:
            self.query_one("#file_path_input", Input).value = str(path)

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle the submission of the prompt input."""
        if message.input.id == "prompt_input":
            prompt = message.value
            file_path_input = self.query_one("#file_path_input", Input)
            file_path = file_path_input.value

            self.query_one("#loading_indicator").styles.display = "block"
            self.run_worker(lambda: get_ai_response(prompt, file_path), thread=True)
            message.input.value = ""

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        loading_indicator = self.query_one("#loading_indicator")
        markdown_display = self.query_one("#response_display", Markdown)

        if event.state == WorkerState.SUCCESS:
            response = event.worker.result
            markdown_display.update(response)
        elif event.state == WorkerState.ERROR:
            # Display the error in the Markdown widget
            error_message = f"### Worker Error\n\n```\n{event.worker.error}\n```"
            markdown_display.update(error_message)
        
        loading_indicator.styles.display = "none"

def main():
    app = NeuroApp()
    app.run()

if __name__ == "__main__":
    main()
