from textual.app import App
from textual.widgets import Header, Footer, Static, Input
from textual.message import Message
from neurocli_core.engine import get_ai_response

class NeuroApp(App):
    """The main application for NeuroCLI."""

    def compose(self):
        """Create child widgets for the app."""
        yield Header()
        yield Input(placeholder="Enter your prompt...", id="prompt_input")
        yield Static("AI response will appear here...", id="response_display")
        yield Footer()

    async def on_input_submit(self, event: Input.Submit):
        """Handle the submit event from the Input widget."""
        prompt_input = self.query_one("#prompt_input", Input)
        response_display = self.query_one("#response_display", Static)
        
        prompt = event.value
        response = get_ai_response(prompt)
        
        response_display.update(response)
        prompt_input.value = ""

def main():
    """The entry point for the command-line tool."""
    app = NeuroApp()
    app.run()

if __name__ == "__main__":
    main()
