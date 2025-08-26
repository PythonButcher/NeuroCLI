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
        yield Input(placeholder="Enter your prompt...", id="prompt_input")
        yield Static("AI response will appear here...", id="response_display")
        yield Footer()

    # The decorator and the type hint must be changed to Input.Submitted
    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle the submission of the input."""
        response_display = self.query_one("#response_display", Static)
        
        # The prompt text is now available directly on the message event
        prompt = message.value 
        response = get_ai_response(prompt)
        
        response_display.update(response)
        
        # Clear the input by targeting the widget that sent the message
        message.input.value = ""

def main():
    app = NeuroApp()
    app.run()

if __name__ == "__main__":
    main()