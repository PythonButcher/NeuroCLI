from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal, Container
from textual.widgets import Header, Footer, Input, Button, Markdown, LoadingIndicator, Static
from textual.worker import Worker, WorkerState
from textual_fspicker import FileOpen
#from theme import arctic_theme #, modern_theme

from neurocli_core.engine import get_ai_response
from neurocli_core.diff_generator import generate_diff
from neurocli_core.code_formatter import format_python_code


class NeuroApp(App):
    """The main application for NeuroCLI."""
    BINDINGS = [("ctrl+q", "quit", "Quit")]
   # DEFAULT_THEME = modern_theme
    #CSS_PATH = "modern.css"
     # --- ADD THIS CSS TO STYLE THE LAYOUT ---
    CSS = """
    #file-container {
        height: auto;
    }

    #file_path_input {
        width: 1fr;
    }

    #browse_button {
        width: auto;
    }
    """


    _proposed_content: str = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with VerticalScroll(id="main-content"):
            with Horizontal(id="file-container"):
                yield Input(placeholder="Enter file path for context (optional)...", id="file_path_input")
                yield Button("Browse...", id="browse_button")
            yield Input(placeholder="Enter your prompt...", id="prompt_input")
            yield Markdown("AI response will appear here...", id="response_display")
            yield Button("Apply Changes", id="apply_button")
            yield LoadingIndicator(id="loading_indicator")
            
            # --- CORRECTED SECTION ---
            # The Container now properly wraps the dialog widgets.
            # Each widget inside is yielded within the 'with' block.
            with Container(id="button_container"):
                yield Static("Do you want to continue?", id="dialog_text")
                yield Button("Yes", id="yes", variant="success")
                yield Button("No", id="no", variant="error")
                
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        #self.register_theme(arctic_theme) 
        #self.register_theme(modern_theme)  

        # Set the app's theme
        #self.theme = "arctic" 
        #self.theme = "modern_dark_neon" 
        self.query_one("#loading_indicator").styles.display = "none"
        self.query_one("#apply_button").styles.display = "none"
        self.query_one("#button_container").styles.display = "none"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the press of the 'Browse...' button."""
        if event.button.id == "browse_button":
            self.push_screen(FileOpen(), self.on_file_open_selected)
        elif event.button.id == "apply_button":
            self.query_one("#button_container").styles.display = "block"

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
        
        loading_indicator.styles.display = "none"

def main():
    app = NeuroApp()
    app.run()

if __name__ == "__main__":
    main()
