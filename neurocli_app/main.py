from textual.app import App
from textual.widgets import Header, Footer, Static
from neurocli_core.engine import get_greeting

class NeuroApp(App):
    """The main application for NeuroCLI."""

    def compose(self) -> None:
        """Create child widgets for the app."""
        yield Header()
        yield Static(get_greeting())
        yield Footer()

if __name__ == "__main__":
    app = NeuroApp()
    app.run()