from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label


class CommandModal(ModalScreen[None]):
    """A terminal command reference window for the Textual app."""

    CSS_PATH = "main.css"

    COMMANDS: tuple[tuple[str, str, str], ...] = (
        ("Ctrl+R", "Run prompt", "Send the current prompt through the shared workflow."),
        ("Ctrl+F", "Format file", "Format the active target file and show a review diff."),
        ("Ctrl+A", "Apply changes", "Apply the reviewed proposal after creating a backup."),
        ("Ctrl+M", "Model settings", "Set model override and raw model options JSON."),
        ("Ctrl+O", "Context manager", "Attach or remove files from the prompt context stack."),
        ("Ctrl+D", "Workspace radar", "Open repository health, debt, and recent edit signals."),
        ("Ctrl+E", "Review editor", "Edit the current proposal before keeping or applying it."),
        ("Ctrl+G", "Git review", "Open the git status, diff, and commit workflow."),
        ("Ctrl+L", "Reset view", "Clear transient prompt, stream, diff, and apply state."),
        ("Ctrl+K", "Commands", "Open this command reference window."),
        ("Ctrl+Q", "Quit", "Exit NeuroCLI."),
    )

    def compose(self) -> ComposeResult:
        with Container(id="command_dialog"):
            yield Label("⌨ Command Reference", id="command_header")

            with Vertical(id="command_main_area"):
                yield DataTable(id="command_table")

            with Horizontal(id="command_action_row"):
                yield Button("Close", id="btn_close_commands", variant="error")

    def on_mount(self) -> None:
        table = self.query_one("#command_table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("Key", "Action", "Result")

        for shortcut, action, result in self.COMMANDS:
            table.add_row(shortcut, action, result)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_close_commands":
            self.dismiss()
