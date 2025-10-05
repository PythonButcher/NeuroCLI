from textual import events
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Container
from textual.widgets import Header, Footer, Input, Button, Markdown, LoadingIndicator, Static
from textual.worker import Worker, WorkerState
from textual_fspicker import FileOpen
from neurocli_app.theme import arctic_theme, modern_theme, nocturne_theme
from neurocli_app.art import BACKGROUND_ART

from neurocli_core.engine import get_ai_response
from neurocli_core.diff_generator import generate_diff
from neurocli_core.code_formatter import format_python_code


class NeuroApp(App):
    """The main application for NeuroCLI."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]
    CSS_PATH = "main.css"

    _proposed_content: str = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=False, id="app_header")

        with Container(id="app_shell"):
            with VerticalScroll(id="brand_column"):
                yield Static(BACKGROUND_ART, id="background_image")
                yield Static(
                    "Craft your development workflow with a focused AI copilot.",
                    id="brand_caption",
                )

            with VerticalScroll(id="interaction_column"):
                with Container(id="file_container"):
                    yield Input(
                        placeholder="Enter file path for context (optional)...",
                        id="file_path_input",
                    )
                    yield Button("Browse", id="browse_button")

                yield Input(placeholder="Describe what you need...", id="prompt_input")
                yield Markdown("AI response will appear here...", id="response_display")

                with Container(id="action_bar"):
                    yield Button("Reset", id="reset_screen")
                    yield Button("Apply Changes", id="apply_button", variant="primary")

                yield LoadingIndicator(id="loading_indicator")

                with Container(id="button_container"):
                    yield Static("Apply these changes?", id="dialog_text")
                    yield Button("Yes", id="yes", variant="success")
                    yield Button("No", id="no", variant="error")

        yield Footer(id="app_footer")


    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.register_theme(arctic_theme)
        self.register_theme(modern_theme)
        self.register_theme(nocturne_theme)

        self.theme = "nocturne"
        self.query_one("#loading_indicator").styles.display = "none"
        self.query_one("#apply_button").styles.display = "none"
        self.query_one("#button_container").styles.display = "none"
        self.call_after_refresh(lambda: self._apply_responsive_layout(self.size.width))

    def on_resize(self, event: events.Resize) -> None:
        """Adjust the layout whenever the terminal is resized."""
        self._apply_responsive_layout(event.size.width)

    def _apply_responsive_layout(self, width: int) -> None:
        """Toggle responsive styling classes based on terminal width."""
        app_shell = self.query_one("#app_shell")
        brand_column = self.query_one("#brand_column")
        interaction_column = self.query_one("#interaction_column")

        if width < 120:
            app_shell.add_class("narrow")
            brand_column.add_class("narrow")
            interaction_column.add_class("narrow")
        else:
            app_shell.remove_class("narrow")
            brand_column.remove_class("narrow")
            interaction_column.remove_class("narrow")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the press of the 'Browse...' button."""
        if event.button.id == "browse_button":
            self.push_screen(FileOpen(), self.on_file_open_selected)
        elif event.button.id == "apply_button":
            self.query_one("#button_container").styles.display = "grid"
        elif event.button.id == "reset_screen":
            self.query_one("#file_path_input", Input).value = ""
            self.query_one("#prompt_input", Input).value = ""
            self.query_one("#response_display", Markdown).update(
                "AI response will appear here..."
            )
            self._proposed_content = ""
            self.query_one("#apply_button").styles.display = "none"
            self.query_one("#button_container").styles.display = "none"
            self.query_one("#background_image").styles.display = "block"
            self.query_one("#loading_indicator").styles.display = "none"

        # ---- When confirmed Yes on dialog box ---- #
        elif event.button.id == "yes":
            file_path = self.query_one("#file_path_input", Input).value
            if file_path and self._proposed_content:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(self._proposed_content)
                    self.query_one("#response_display").update(f"Changes applied to {file_path} successfully.")
                    self._proposed_content = ""
                    self.query_one("#apply_button").styles.display = "none"
                    self.query_one("#button_container").styles.display = "none"
                except Exception as e:
                    self.query_one("#response_display").update(f"Error applying changes: {e}")
        
        # ---- When confirmed No on dialog box ---- #
        elif event.button.id == "no":
            # Just hide the dialog
            self.query_one("#button_container").styles.display = "none"


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

            # --- 4. HIDE THE BACKGROUND IMAGE ---
            self.query_one("#background_image").styles.display = "none"

            self.query_one("#loading_indicator").styles.display = "block"
            self.run_worker(lambda: get_ai_response(prompt, file_path), thread=True)
            message.input.value = ""

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
            # Display the error in the Markdown widget
            error_message = f"### Worker Error\n\n```\n{event.worker.error}\n```"
            markdown_display.update(error_message)
            
        # --- 4. SHOW THE BACKGROUND IMAGE AGAIN ---
        self.query_one("#background_image").styles.display = "block"
        loading_indicator.styles.display = "none"

def main():
    app = NeuroApp()
    app.run()

if __name__ == "__main__":
    main()
