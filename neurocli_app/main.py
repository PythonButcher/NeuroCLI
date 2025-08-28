from textual.app import App
from textual.widgets import Header, Footer, Static, Input

# This import is no longer needed
# from textual.message import Submit 

from neurocli_core.engine import get_ai_response

class NeuroApp(App):
    """The main application for NeuroCLI."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]

    def compose(self):
        """Create child widgets for the app."""
        yield Header()
        yield Input(placeholder="Enter file path for context (optional)...", id="file_path_input")
        yield Input(placeholder="Enter your prompt...", id="prompt_input")
        yield Static("AI response will appear here...", id="response_display")
        yield Footer()

    # The decorator and the type hint must be changed to Input.Submitted
    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle the submission of the input."""
        if message.input.id == "prompt_input":
            response_display = self.query_one("#response_display", Static)
            file_path_input = self.query_one("#file_path_input", Input)
            
            prompt = message.value
            file_path = file_path_input.value
            
            response = get_ai_response(prompt, file_path=file_path if file_path else None)
            
            response_display.update(response)
            
            message.input.value = ""

def main():
    app = NeuroApp()
    app.run()

if __name__ == "__main__":
    main()