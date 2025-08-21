from textual.app import App, Header, Footer
from neurocli_core.engine import get_greeting

class NeuroApp(App):
    """The main application for NeuroCLI."""

    def compose(self):
        """Create child widgets for the app."""
        yield Header()
        yield get_greeting()
        yield Footer()

if __name__ == "__main__":
    app = NeuroApp()
    app.run()
