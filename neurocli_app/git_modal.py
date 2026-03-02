from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, TextArea, LoadingIndicator
from textual.worker import Worker, WorkerState

from neurocli_core.git_engine import (
    get_staged_diff,
    generate_commit_message,
    execute_commit_and_push
)


class GitModal(ModalScreen[None]):
    """A modal screen that displays an AI-generated commit message for review."""

    CSS_PATH = "main.css"
    
    _add_all: bool = False

    def compose(self) -> ComposeResult:
        with Container(id="git_dialog"):
            yield Label("🐙 The Git Whisperer - Review Commit", id="git_header")
            
            with Vertical(id="git_main_area"):
                yield LoadingIndicator(id="git_loading_indicator")
                yield TextArea(id="commit_text_area", language="markdown", show_line_numbers=False)
                
            with Horizontal(id="git_action_row"):
                yield Button("Cancel", id="btn_cancel_git", variant="error")
                yield Button("Commit & Push", id="btn_commit_push", variant="success")

    def on_mount(self) -> None:
        """Fetch the diff and get the AI generated commit message when the modal opens."""
        # Hide the text area and action row while loading
        self.query_one("#commit_text_area").styles.display = "none"
        self.query_one("#git_action_row").styles.display = "none"
        
        # Start a worker thread to perform the diff and AI call without blocking the UI
        self.run_worker(self._generate_message_worker, thread=True, id="fetch_commit_message")

    def _generate_message_worker(self) -> str:
        """Worker thread function to run the process."""
        diff_text, is_fallback = get_staged_diff()
        self._add_all = is_fallback
        
        if not diff_text:
            return "No changes detected to commit."
            
        return generate_commit_message(diff_text)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when any worker state changes."""
        
        # Handle the fetch worker finishing
        if event.worker.id == "fetch_commit_message":
            if event.state == WorkerState.SUCCESS:
                self.query_one("#git_loading_indicator").styles.display = "none"
                text_area = self.query_one("#commit_text_area", TextArea)
                text_area.load_text(event.worker.result)
                text_area.styles.display = "block"
                self.query_one("#git_action_row").styles.display = "block"
                
            elif event.state == WorkerState.ERROR:
                self.query_one("#git_loading_indicator").styles.display = "none"
                text_area = self.query_one("#commit_text_area", TextArea)
                text_area.load_text(f"Error generating commit message: {event.worker.error}")
                text_area.styles.display = "block"
                self.query_one("#btn_cancel_git").styles.display = "block"
                # Don't show commit button if there's an error
                
        # Handle the push worker finishing
        elif event.worker.id == "execute_commit":
            if event.state == WorkerState.SUCCESS:
                self.app.notify("Successfully committed and pushed changes!", title="Git", severity="information")
                self.dismiss()
            elif event.state == WorkerState.ERROR:
                self.query_one("#git_loading_indicator").styles.display = "none"
                self.app.notify(f"Git execution failed: {event.worker.error}", title="Git Error", severity="error", timeout=10)
                self.query_one("#git_action_row").styles.display = "block"


    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_cancel_git":
            self.dismiss()
            
        elif event.button.id == "btn_commit_push":
            # Hide action row while pushing
            self.query_one("#git_action_row").styles.display = "none"
            self.query_one("#git_loading_indicator").styles.display = "block"
            
            commit_message = self.query_one("#commit_text_area", TextArea).text
            
            # Start worker for the git operation
            self.run_worker(
                lambda: execute_commit_and_push(commit_message, self._add_all),
                thread=True,
                id="execute_commit"
            )
