# neurocli_app/main.py

from textual.app import App
from textual.widgets import Header, Footer, Static, Input
from textual.message import Submit

from neurocli_core.engine import get_ai_response

class NeuroApp(App):
    """The main application for NeuroCLI."""

    # Add this BINDINGS variable
    BINDINGS = [("ctrl+q", "quit", "Quit")]

    def compose(self):
        """Create child widgets for the app."""
        yield Header()
        yield Input(placeholder="Enter your prompt...", id="prompt_input")
        yield Static("AI response will appear here...", id="response_display")
        yield Footer()

    async def on_input_submit(self, message: Submit) -> None:
        """Handle the submission of the input."""
        prompt_input = self.query_one("#prompt_input", Input)
        response_display = self.query_one("#response_display", Static)

        prompt = prompt_input.value
        response = get_ai_response(prompt)

        response_display.update(response)
        prompt_input.value = ""

def main():
    app = NeuroApp()
    app.run()

if __name__ == "__main__":
    main()