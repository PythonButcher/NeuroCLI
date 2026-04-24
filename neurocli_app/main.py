import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, DirectoryTree, Input, LoadingIndicator, Markdown, Static
from textual.worker import Worker, WorkerState
from textual_fspicker import FileOpen

from neurocli_app.context_modal import ContextModal
from neurocli_app.git_modal import GitModal
from neurocli_app.model_modal import ModelModal
from neurocli_app.radar_modal import RadarModal
from neurocli_app.theme import arctic_theme, fleet_dark, modern_theme, solid_modern
from neurocli_app.workflow_adapter import (
    build_textual_workflow_request,
    run_textual_stream_workflow,
)
from neurocli_core.code_formatter import format_code
from neurocli_core.diff_generator import generate_diff
from neurocli_core.file_handler import create_backup
from neurocli_core.workflow_service import AIWorkflowRequest, AIWorkflowResponse, AIWorkflowStreamEvent


class NeuroApp(App):
    """The main application for NeuroCLI."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]
    CSS_PATH = "main.css"

    _proposed_content: str = ""
    _streamed_output: str = ""
    context_paths: set[str] = set()
    selected_model: str = ""
    model_options_text: str = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Horizontal(id="app_layout"):
            with Container(id="sidebar"):
                yield Static("NeuroCLI", id="sidebar_title")
                with VerticalScroll(id="sidebar_nav"):
                    yield DirectoryTree(path="./", id="file_tree")
                yield Button("Reset", id="reset_screen")

            with Container(id="workspace"):
                yield Static("NeuroCLI v1.0 | Engine Dashboard", id="workspace_header")
                with Container(id="workspace_panel"):
                    # Output/History Section
                    yield Markdown("AI response will appear here...", id="response_display")
                    yield LoadingIndicator(id="loading_indicator")
                    yield Button("Apply Changes", id="apply_button")

                    # Input/Prompt Section (Warp-style Block)
                    with Container(id="prompt_block"):
                        with Horizontal(id="file-container"):
                            yield Input(
                                placeholder="Target file path (optional)...",
                                id="file_path_input",
                            )
                            yield Button("Browse...", id="browse_button")

                        yield Input(placeholder="❯ Enter your prompt...", id="prompt_input")

                        with Horizontal(id="action_row"):
                            with Horizontal(id="toolbox"):
                                yield Button("⚙️", id="btn_settings", classes="tool_btn")
                                yield Button("🗑️", id="btn_clear", classes="tool_btn")
                                yield Button("🤖 Model", id="btn_model", classes="tool_btn")
                                yield Button("📎 Context", id="btn_context", classes="tool_btn")
                                yield Button("📊 Radar", id="btn_radar", classes="tool_btn")

                            with Horizontal(id="run_row"):
                                yield Button("Commit 🐙", id="btn_commit", classes="run_btn")
                                yield Button("Format", id="format_button")
                                yield Button("Run", id="run_button")

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.register_theme(arctic_theme)
        self.register_theme(modern_theme)
        self.register_theme(solid_modern)
        self.register_theme(fleet_dark)

        self.theme = "fleet_dark"
        self.query_one("#loading_indicator").styles.display = "none"
        self.query_one("#apply_button").styles.display = "none"
        self._refresh_model_button()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when a file is selected in the DirectoryTree."""
        self._display_file_content(str(event.path))

    def _display_file_content(self, path_str: str) -> None:
        """Helper to read and display file content in the Markdown widget."""
        path = Path(path_str)
        
        if not path.exists() or not path.is_file():
            return

        self.query_one("#file_path_input", Input).value = str(path)

        # Clear proposed content and hide apply button as we are viewing a new file
        self._proposed_content = ""
        self.query_one("#apply_button").styles.display = "none"

        try:
            # Determine extension for syntax highlighting
            ext = path.suffix.lower().lstrip(".")
            if not ext:
                ext = "text"

            # Read file content safely
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Update the response display with the file content
            markdown_view = f"### Viewing: {path.name}\n\n```{ext}\n{content}\n```"
            self.query_one("#response_display", Markdown).update(markdown_view)
        except Exception as e:
            self.query_one("#response_display", Markdown).update(
                f"### Error\n\nFailed to read file: {e}"
            )

    def _run_prompt(self) -> None:
        """Run the AI request using the shared streaming workflow contract."""

        prompt_input = self.query_one("#prompt_input", Input)
        prompt = prompt_input.value
        if not prompt.strip():
            return

        try:
            request = build_textual_workflow_request(
                prompt,
                target_file=self.query_one("#file_path_input", Input).value,
                context_paths=self.context_paths,
                model=self.selected_model,
                model_options_text=self.model_options_text,
            )
        except ValueError as error:
            self.query_one("#response_display", Markdown).update(f"### Request Error\n\n{error}")
            return
        
        self._streamed_output = ""
        self._proposed_content = ""
        self.query_one("#apply_button").styles.display = "none"
        self.query_one("#loading_indicator").styles.display = "block"
        self.query_one("#response_display", Markdown).update(
            self._render_stream_output(request)
        )
        self.run_worker(
            lambda: run_textual_stream_workflow(
                request,
                lambda event: self.call_from_thread(
                    self._handle_stream_event,
                    request,
                    event,
                ),
            ),
            thread=True,
            name="run_ai_workflow",
        )
        prompt_input.value = ""

    def _format_file(self) -> None:
        """Format the currently selected file."""
        file_path = self.query_one("#file_path_input", Input).value
        if not file_path or not os.path.exists(file_path):
            self.query_one("#response_display", Markdown).update("Please select a valid file to format.")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            formatted_content = format_code(original_content, file_path)
            
            if formatted_content == original_content:
                self.query_one("#response_display", Markdown).update("No formatting needed.")
                self.query_one("#apply_button").styles.display = "none"
                self._proposed_content = ""
            else:
                diff = generate_diff(original_content, formatted_content)
                self.query_one("#response_display", Markdown).update(diff)
                self._proposed_content = formatted_content
                self.query_one("#apply_button").styles.display = "block"
        except RuntimeError as e:
            self.query_one("#response_display", Markdown).update(f"### Formatter Error\n\n{e}")
        except Exception as e:
            self.query_one("#response_display", Markdown).update(f"Error formatting file: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button actions while keeping existing wiring intact."""
        if event.button.id == "browse_button":
            self.push_screen(FileOpen(), self.on_file_open_selected)
        elif event.button.id == "run_button":
            self._run_prompt()
        elif event.button.id == "format_button":
            self._format_file()
        elif event.button.id == "btn_model":
            self.push_screen(
                ModelModal(self.selected_model, self.model_options_text),
                self._on_model_modal_dismissed,
            )
        elif event.button.id == "btn_context":
            self.push_screen(ContextModal(self.context_paths), self._on_context_modal_dismissed)
        elif event.button.id == "btn_radar":
            self.push_screen(RadarModal())
        elif event.button.id == "btn_commit":
            self.push_screen(GitModal())
        elif event.button.id == "apply_button":
            file_path = self.query_one("#file_path_input", Input).value
            if file_path and self._proposed_content:
                try:
                    backup_dir = os.path.join(os.path.dirname(file_path), "backups")
                    create_backup(file_path, backup_dir)

                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(self._proposed_content)

                    self.query_one("#response_display").update(
                        f"Changes applied to {file_path} successfully."
                    )
                    self._proposed_content = ""
                    self.query_one("#apply_button").styles.display = "none"
                except Exception as error:
                    self.query_one("#response_display").update(
                        f"Error applying changes: {error}"
                    )

    def _on_context_modal_dismissed(self, selected_paths: set[str] | None) -> None:
        """Callback for when ContextModal finishes."""
        if selected_paths is not None:
            self.context_paths = selected_paths
            btn = self.query_one("#btn_context", Button)
            
            if self.context_paths:
                btn.label = f"📎 Context ({len(self.context_paths)})"
                btn.variant = "primary"
            else:
                btn.label = "📎 Context"
                btn.variant = "default"

    def _on_model_modal_dismissed(self, payload: dict[str, str] | None) -> None:
        """Persist model overrides only when the modal explicitly saves them."""

        if payload is None:
            return

        self.selected_model = payload.get("model", "").strip()
        self.model_options_text = payload.get("model_options_text", "")
        self._refresh_model_button()

    def _refresh_model_button(self) -> None:
        """Reflect whether this run will use backend defaults or overrides."""

        button = self.query_one("#btn_model", Button)
        has_overrides = bool(self.selected_model or self.model_options_text.strip())
        button.label = "🤖 Model*" if has_overrides else "🤖 Model"
        button.variant = "primary" if has_overrides else "default"

    def on_file_open_selected(self, path: str) -> None:
        """Callback for when a file is selected from the dialog."""
        if path:
            self._display_file_content(str(path))

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle input submit on Enter for both prompt and file path."""
        if message.input.id == "prompt_input":
            self._run_prompt()
        elif message.input.id == "file_path_input":
            self._display_file_content(message.input.value)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        if event.worker.name != "run_ai_workflow":
            return

        loading_indicator = self.query_one("#loading_indicator")
        markdown_display = self.query_one("#response_display", Markdown)

        if event.state == WorkerState.ERROR:
            error_message = f"### Worker Error\n\n```\n{event.worker.error}\n```"
            markdown_display.update(error_message)

        loading_indicator.styles.display = "none"

    def _handle_stream_event(
        self,
        request: AIWorkflowRequest,
        event: AIWorkflowStreamEvent,
    ) -> None:
        """Render incremental stream output and then apply the final response shape."""

        markdown_display = self.query_one("#response_display", Markdown)

        if event.event == "start":
            self._streamed_output = ""
            markdown_display.update(self._render_stream_output(request))
            return

        if event.event == "delta":
            self._streamed_output += event.delta
            markdown_display.update(self._render_stream_output(request))
            return

        if event.response is not None:
            self._handle_workflow_response(event.response)
        self.query_one("#loading_indicator").styles.display = "none"

    def _render_stream_output(self, request: AIWorkflowRequest) -> str:
        """Render a readable live preview while the shared workflow is streaming."""

        if self._request_targets_file(request):
            file_name = Path(request.target_file or "").name or "selected file"
            language = Path(request.target_file or "").suffix.lower().lstrip(".") or "text"
            generated_text = self._streamed_output or "# Generating file update..."
            return f"### Generating update for {file_name}\n\n```{language}\n{generated_text}\n```"

        return self._streamed_output or "Generating response..."

    def _request_targets_file(self, request: AIWorkflowRequest) -> bool:
        """Treat existing files as full-file update requests for stream preview purposes."""

        if not request.target_file:
            return False

        try:
            return Path(request.target_file).is_file()
        except OSError:
            return False

    def _handle_workflow_response(self, response: AIWorkflowResponse) -> None:
        """Apply the normalized response shape shared by sync and streaming callers."""

        markdown_display = self.query_one("#response_display", Markdown)
        file_path_input = self.query_one("#file_path_input", Input)

        if response.target_file:
            file_path_input.value = response.target_file

        if not response.ok:
            self._proposed_content = ""
            markdown_display.update(response.error or "Unknown AI workflow error.")
            self.query_one("#apply_button").styles.display = "none"
            return

        if response.response_kind == "file_update":
            file_path = response.target_file or file_path_input.value
            try:
                # The formatter runs after generation so both UIs can share one
                # backend contract while the Textual app still presents a reviewable diff.
                formatted_content = format_code(response.output_text, file_path)
                diff = generate_diff(response.original_content, formatted_content)
                markdown_display.update(diff)
                self._proposed_content = formatted_content
                self.query_one("#apply_button").styles.display = "block"
            except RuntimeError as error:
                self._proposed_content = ""
                markdown_display.update(f"### Formatter Error\n\n{error}")
                self.query_one("#apply_button").styles.display = "none"
            return

        self._proposed_content = ""
        markdown_display.update(response.output_text)
        self.query_one("#apply_button").styles.display = "none"


def main():
    app = NeuroApp()
    app.run()


if __name__ == "__main__":
    main()
