from __future__ import annotations

import difflib
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal, Container
from textual.widgets import Header, Footer, Input, Button, Markdown, LoadingIndicator, Static
from textual.worker import Worker, WorkerState
from textual_fspicker import FileOpen

from neurocli_app.theme import arctic_theme, modern_theme
from neurocli_app.art import BACKGROUND_ART
from neurocli_core.engine import get_ai_response
from neurocli_core.diff_generator import generate_diff
from neurocli_core.code_formatter import format_python_code
from neurocli_core import git_tools
from neurocli_core.git_tools import GitError, GitRepositoryNotFound


class NeuroApp(App):
    """The main application for NeuroCLI."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]
    CSS_PATH = "main.css"

    _proposed_content: str = ""
    _git_patch: str = ""
    _last_diff_markdown: str = ""
    _selected_file_path: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static(BACKGROUND_ART, id="background_image")
        yield Button("Reset", id="reset_screen")
        with VerticalScroll(id="main-content"):
            with Horizontal(id="file-container"):
                yield Input(placeholder="Enter file path for context (optional)...", id="file_path_input")
                yield Button("Browse...", id="browse_button")
            yield Input(placeholder="Enter your prompt...", id="prompt_input")
            yield Markdown("AI response will appear here...", id="response_display")
            yield Button("Apply Changes", id="apply_button")
            with Container(id="git_container"):
                yield Markdown("Git status will appear here once a file is selected.", id="git_status_display")
                with Horizontal(id="git_buttons"):
                    yield Button("Stage Diff", id="stage_diff")
                    yield Button("Open in $EDITOR", id="open_editor")
            yield LoadingIndicator(id="loading_indicator")
            with Container(id="button_container"):
                yield Static("How should NeuroCLI apply this patch?", id="dialog_text")
                yield Button("Apply & Stage", id="apply_stage", variant="success")
                yield Button("Apply (Working Tree)", id="apply_worktree", variant="primary")
                yield Button("Cancel", id="cancel_apply", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.register_theme(arctic_theme)
        self.register_theme(modern_theme)

        # Set the app's theme
        self.theme = "arctic"
        self.theme = "modern_dark_neon"
        self.query_one("#loading_indicator").styles.display = "none"
        self.query_one("#apply_button").styles.display = "none"
        self.query_one("#button_container").styles.display = "none"
        self._set_git_buttons_enabled(stage=False, open_editor=False)

    def _set_git_buttons_enabled(self, *, stage: bool, open_editor: bool) -> None:
        self.query_one("#stage_diff", Button).disabled = not stage
        self.query_one("#open_editor", Button).disabled = not open_editor

    def refresh_git_status(self) -> None:
        """Trigger a background update of the Git status widget."""
        git_status_display = self.query_one("#git_status_display", Markdown)
        file_path = self._selected_file_path
        if not file_path:
            git_status_display.update("Select a file to view Git status.")
            self._set_git_buttons_enabled(stage=False, open_editor=False)
            return

        try:
            git_tools.detect_git_root(file_path)
        except GitRepositoryNotFound as exc:
            git_status_display.update(f"### Git Status\n{exc}")
            self._set_git_buttons_enabled(stage=False, open_editor=True)
            return

        git_status_display.update("Fetching Git status...")

        def status_worker() -> str:
            try:
                return git_tools.get_status_for_path(file_path)
            except GitRepositoryNotFound as exc:
                return f"### Git Status\n{exc}"
            except GitError as exc:
                return f"### Git Status\nError: {exc}"

        self._set_git_buttons_enabled(stage=True, open_editor=True)
        self.run_worker(status_worker, thread=True, name="git-status")

    def _build_patch(self, original_content: str, new_content: str) -> str:
        if not self._selected_file_path:
            return ""

        path_obj = Path(self._selected_file_path).resolve()
        relative_path = path_obj
        try:
            repo_root = git_tools.detect_git_root(path_obj)
            relative_path = path_obj.relative_to(repo_root)
        except GitRepositoryNotFound:
            pass

        diff = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{relative_path.as_posix()}",
            tofile=f"b/{relative_path.as_posix()}",
        )
        return "".join(diff)

    def _apply_patch_worker(self, stage: bool) -> str:
        if not self._selected_file_path:
            raise GitError("No file selected for applying the patch.")
        if not self._git_patch.strip():
            raise GitError("There is no patch to apply.")

        path_obj = Path(self._selected_file_path).resolve()

        try:
            message = git_tools.apply_patch(self._git_patch, start_path=path_obj)
        except GitRepositoryNotFound:
            if stage:
                raise GitError("Staging requires a Git repository.")
            if not self._proposed_content:
                raise GitError("No generated content is available to write.")
            path_obj.write_text(self._proposed_content, encoding="utf-8")
            return f"Wrote changes directly to {path_obj} (no Git repository detected)."
        if stage:
            staged = git_tools.stage_paths([path_obj])
            message = f"{message}\n{staged}"
        return message

    def _stage_worker(self) -> str:
        if not self._selected_file_path:
            raise GitError("No file selected to stage.")
        path_obj = Path(self._selected_file_path).resolve()
        try:
            return git_tools.stage_paths([path_obj])
        except GitRepositoryNotFound as exc:
            raise GitError(str(exc))

    def _open_editor_worker(self) -> str:
        if not self._selected_file_path:
            raise GitError("No file selected to open.")
        return git_tools.open_in_editor(self._selected_file_path)

    def _update_response_with_message(self, message: str) -> None:
        markdown_display = self.query_one("#response_display", Markdown)
        if self._last_diff_markdown:
            markdown_display.update(f"{self._last_diff_markdown}\n\n> {message}")
        else:
            markdown_display.update(message)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the UI."""
        if event.button.id == "browse_button":
            self.push_screen(FileOpen(), self.on_file_open_selected)
        elif event.button.id == "apply_button":
            self.query_one("#button_container").styles.display = "block"
        elif event.button.id == "apply_worktree":
            self.query_one("#button_container").styles.display = "none"
            self.run_worker(lambda: self._apply_patch_worker(stage=False), thread=True, name="git-apply")
        elif event.button.id == "apply_stage":
            self.query_one("#button_container").styles.display = "none"
            self.run_worker(lambda: self._apply_patch_worker(stage=True), thread=True, name="git-apply-stage")
        elif event.button.id == "cancel_apply":
            self.query_one("#button_container").styles.display = "none"
        elif event.button.id == "stage_diff":
            self.run_worker(self._stage_worker, thread=True, name="git-stage")
        elif event.button.id == "open_editor":
            self.run_worker(self._open_editor_worker, thread=True, name="open-editor")

    def on_file_open_selected(self, path: str) -> None:
        """Callback for when a file is selected from the dialog."""
        if path:
            self.query_one("#file_path_input", Input).value = str(path)
            self._selected_file_path = str(path)
            self.refresh_git_status()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle the submission of the prompt input."""
        if message.input.id == "prompt_input":
            prompt = message.value
            file_path_input = self.query_one("#file_path_input", Input)
            file_path = file_path_input.value or None
            self._selected_file_path = file_path

            self.query_one("#background_image").styles.display = "none"
            self.query_one("#loading_indicator").styles.display = "block"
            self.run_worker(lambda: get_ai_response(prompt, file_path), thread=True, name="ai-request")
            message.input.value = ""
            if file_path:
                self.refresh_git_status()
            else:
                self.query_one("#git_status_display", Markdown).update("Select a file to view Git status.")
                self._set_git_buttons_enabled(stage=False, open_editor=False)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        markdown_display = self.query_one("#response_display", Markdown)

        if event.worker.name == "ai-request":
            loading_indicator = self.query_one("#loading_indicator")
            if event.state == WorkerState.SUCCESS:
                original_content, new_content = event.worker.result
                if original_content:
                    formatted_content = format_python_code(new_content)
                    diff = generate_diff(original_content, formatted_content)
                    self._last_diff_markdown = diff
                    self._proposed_content = formatted_content
                    self._git_patch = self._build_patch(original_content, formatted_content)
                    markdown_display.update(diff)
                    self.query_one("#apply_button").styles.display = "block" if self._git_patch else "none"
                else:
                    markdown_display.update(new_content)
                    self._last_diff_markdown = new_content
                    self._proposed_content = ""
                    self._git_patch = ""
                    self.query_one("#apply_button").styles.display = "none"
            elif event.state == WorkerState.ERROR:
                error_message = f"### Worker Error\n\n```\n{event.worker.error}\n```"
                markdown_display.update(error_message)
                self._last_diff_markdown = error_message
                self._proposed_content = ""
                self._git_patch = ""
                self.query_one("#apply_button").styles.display = "none"

            self.query_one("#background_image").styles.display = "block"
            loading_indicator.styles.display = "none"
            return

        if event.worker.name == "git-status":
            if event.state == WorkerState.SUCCESS:
                self.query_one("#git_status_display", Markdown).update(event.worker.result)
            elif event.state == WorkerState.ERROR:
                self.query_one("#git_status_display", Markdown).update(
                    f"### Git Status\nError: {event.worker.error}"
                )
            return

        if event.state == WorkerState.SUCCESS:
            message = event.worker.result
            self._update_response_with_message(message)
            if event.worker.name in {"git-apply", "git-apply-stage"}:
                self._proposed_content = ""
                self._git_patch = ""
                self.query_one("#apply_button").styles.display = "none"
                if self._selected_file_path:
                    self.refresh_git_status()
            elif event.worker.name == "git-stage" and self._selected_file_path:
                self.refresh_git_status()
        elif event.state == WorkerState.ERROR:
            self._update_response_with_message(f"Error: {event.worker.error}")

    def on_unmount(self) -> None:
        """Ensure background workers stop on exit."""
        self.workers.cancel_all()


def main():
    app = NeuroApp()
    app.run()


if __name__ == "__main__":
    main()
