from textual.app import App
from textual.widgets import Header, Footer, Static
from neurocli_core.engine import get_greeting

class NeuroApp(App):
    """The main application for NeuroCLI."""

    def compose(self):
        """Create child widgets for the app."""
        yield Header()
        yield Static(get_greeting())
        yield Footer()

def main():
    """The entry point for the command-line tool."""
    app = NeuroApp()
    app.run()

if __name__ == "__main__":
    main()