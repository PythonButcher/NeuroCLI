from textual.app import App
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Header, Footer, Input, Button, Markdown, LoadingIndicator
from textual_fspicker import FileOpen

from neurocli_core.engine import get_ai_response

class NeuroApp(App):
    """The main application for NeuroCLI."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]

    def compose(self):
        """Create child widgets for the app."""
        yield Header()
        with VerticalScroll():
            with Horizontal():
                yield Input(placeholder="Enter file path for context (optional)...", id="file_path_input")
                yield Button("Browse...", id="browse_button")
            yield Input(placeholder="Enter your prompt...", id="prompt_input")
            yield Markdown("AI response will appear here...", id="response_display")
            yield LoadingIndicator(id="loading_indicator")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the Browse button press."""
        if event.button.id == "browse_button":
            # This is the new, simplified logic
            path = await self.push_screen_wait(FileOpen())
            if path:
                self.query_one("#file_path_input", Input).value = str(path)

    # This entire method is no longer needed and should be deleted
    # async def on_file_open_selected(self, event: FileOpen.Selected) -> None:
    #     ...

    def on_ai_response(self, response: str) -> None:
        """Callback to handle the AI response from the worker."""
        self.query_one("#response_display", Markdown).update(response)
        self.query_one("#loading_indicator").display = False

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle the submission of the main prompt input."""
        if message.input.id == "prompt_input":
            file_path_input = self.query_one("#file_path_input", Input)
            
            prompt = message.value
            file_path = file_path_input.value

            self.query_one("#loading_indicator").display = True
            
            # Run the API call in the background
            self.run_worker(
                get_ai_response, prompt, file_path, thread=True
            )
            
            message.input.value = ""

def main():
    app = NeuroApp()
    app.run()

if __name__ == "__main__":
    main()