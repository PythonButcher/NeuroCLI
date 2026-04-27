import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, DirectoryTree, Input, LoadingIndicator, Markdown, Static
from textual.worker import Worker
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

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+r", "run_prompt", "Run"),
        ("ctrl+f", "format_file", "Format"),
        ("ctrl+a", "apply_changes", "Apply"),
        ("ctrl+m", "open_model", "Model"),
        ("ctrl+o", "open_context", "Context"),
        ("ctrl+d", "open_radar", "Radar"),
        ("ctrl+g", "open_git", "Git"),
        ("ctrl+l", "reset_workspace", "Reset"),
    ]
    CSS_PATH = "main.css"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._proposed_content: str = ""
        self._streamed_output: str = ""
        self._workflow_state: str = "Idle"
        self.context_paths: set[str] = set()
        self.selected_model: str = ""
        self.model_options_text: str = ""

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
                yield Static("", id="workspace_status")
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
        self._refresh_workspace_status()
        self.query_one("#prompt_input", Input).focus()

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
        self._workflow_state = "Viewing file"
        self._refresh_workspace_status()

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
            self._workflow_state = "File read error"
            self._refresh_workspace_status()

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
            self._workflow_state = "Request error"
            self._refresh_workspace_status()
            return
        
        self._streamed_output = ""
        self._proposed_content = ""
        self._workflow_state = "Streaming"
        self.query_one("#apply_button").styles.display = "none"
        self.query_one("#loading_indicator").styles.display = "block"
        self._refresh_workspace_status()
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
            self._workflow_state = "Format needs target"
            self._refresh_workspace_status()
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            formatted_content = format_code(original_content, file_path)
            
            if formatted_content == original_content:
                self.query_one("#response_display", Markdown).update("No formatting needed.")
                self.query_one("#apply_button").styles.display = "none"
                self._proposed_content = ""
                self._workflow_state = "Format clean"
            else:
                diff = generate_diff(original_content, formatted_content)
                self.query_one("#response_display", Markdown).update(diff)
                self._proposed_content = formatted_content
                self.query_one("#apply_button").styles.display = "block"
                self._workflow_state = "Format review ready"
        except RuntimeError as e:
            self.query_one("#response_display", Markdown).update(f"### Formatter Error\n\n{e}")
            self._workflow_state = "Formatter error"
        except Exception as e:
            self.query_one("#response_display", Markdown).update(f"Error formatting file: {e}")
            self._workflow_state = "Format error"
        finally:
            self._refresh_workspace_status()

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
            self.action_open_radar()
        elif event.button.id == "btn_commit":
            self.action_open_git()
        elif event.button.id == "btn_clear":
            self.action_reset_workspace()
        elif event.button.id == "reset_screen":
            self.action_reset_workspace()
        elif event.button.id == "apply_button":
            self.action_apply_changes()

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
            self._workflow_state = "Context updated"
            self._refresh_workspace_status()

    def _on_model_modal_dismissed(self, payload: dict[str, str] | None) -> None:
        """Persist model overrides only when the modal explicitly saves them."""

        if payload is None:
            return

        self.selected_model = payload.get("model", "").strip()
        self.model_options_text = payload.get("model_options_text", "")
        self._refresh_model_button()
        self._workflow_state = "Model updated"
        self._refresh_workspace_status()

    def _refresh_model_button(self) -> None:
        """Reflect whether this run will use backend defaults or overrides."""

        button = self.query_one("#btn_model", Button)
        has_overrides = bool(self.selected_model or self.model_options_text.strip())
        button.label = "🤖 Model*" if has_overrides else "🤖 Model"
        button.variant = "primary" if has_overrides else "default"

    def _refresh_workspace_status(self) -> None:
        """Keep the terminal command-center strip aligned with active workflow state."""

        target_file = self.query_one("#file_path_input", Input).value.strip()
        target_label = Path(target_file).name if target_file else "none"
        model_label = self.selected_model or "backend default"
        if self.model_options_text.strip():
            model_label = f"{model_label} + options"

        apply_label = "ready" if self._proposed_content else "idle"
        status_text = (
            f"State: {self._workflow_state} | "
            f"Target: {target_label} | "
            f"Context: {len(self.context_paths)} | "
            f"Model: {model_label} | "
            f"Apply: {apply_label}"
        )
        self.query_one("#workspace_status", Static).update(status_text)

    def _apply_changes(self) -> None:
        """Apply the currently reviewed proposal after creating a local backup."""

        file_path = self.query_one("#file_path_input", Input).value
        if not file_path or not self._proposed_content:
            self._workflow_state = "Nothing to apply"
            self._refresh_workspace_status()
            return

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
            self._workflow_state = "Applied with backup"
        except Exception as error:
            self.query_one("#response_display").update(
                f"Error applying changes: {error}"
            )
            self._workflow_state = "Apply error"
        finally:
            self._refresh_workspace_status()

    def _reset_workspace_view(self) -> None:
        """Reset transient prompt, stream, diff, and apply state without changing files."""

        self._proposed_content = ""
        self._streamed_output = ""
        self._workflow_state = "Reset"
        self.query_one("#prompt_input", Input).value = ""
        self.query_one("#response_display", Markdown).update("AI response will appear here...")
        self.query_one("#loading_indicator").styles.display = "none"
        self.query_one("#apply_button").styles.display = "none"
        self._refresh_workspace_status()
        self.query_one("#prompt_input", Input).focus()

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

        state_name = getattr(event.state, "name", str(event.state))
        if state_name not in {"SUCCESS", "ERROR", "CANCELLED"}:
            return

        loading_indicator = self.query_one("#loading_indicator")
        markdown_display = self.query_one("#response_display", Markdown)

        if state_name == "ERROR":
            error_message = f"### Worker Error\n\n```\n{event.worker.error}\n```"
            markdown_display.update(error_message)
            self._workflow_state = "Worker error"
            self._refresh_workspace_status()

        if state_name == "CANCELLED":
            self._workflow_state = "Cancelled"
            self._refresh_workspace_status()

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
            self._workflow_state = "Streaming started"
            self._refresh_workspace_status()
            markdown_display.update(self._render_stream_output(request))
            return

        if event.event == "delta":
            self._streamed_output += event.delta
            self._workflow_state = "Streaming output"
            self._refresh_workspace_status()
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
            self._workflow_state = "Workflow error"
            self._refresh_workspace_status()
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
                self._workflow_state = "Diff review ready"
            except RuntimeError as error:
                self._proposed_content = ""
                markdown_display.update(f"### Formatter Error\n\n{error}")
                self.query_one("#apply_button").styles.display = "none"
                self._workflow_state = "Formatter error"
            finally:
                self._refresh_workspace_status()
            return

        self._proposed_content = ""
        markdown_display.update(response.output_text)
        self.query_one("#apply_button").styles.display = "none"
        self._workflow_state = "Completed"
        self._refresh_workspace_status()

    def action_run_prompt(self) -> None:
        """Keyboard action for the shared AI workflow."""

        self._run_prompt()

    def action_format_file(self) -> None:
        """Keyboard action for formatting the active target file."""

        self._format_file()

    def action_apply_changes(self) -> None:
        """Keyboard action for the reviewed apply-with-backup path."""

        self._apply_changes()

    def action_open_model(self) -> None:
        """Open model overrides without introducing app-specific fields."""

        self.push_screen(
            ModelModal(self.selected_model, self.model_options_text),
            self._on_model_modal_dismissed,
        )

    def action_open_context(self) -> None:
        """Open the context stack manager."""

        self.push_screen(ContextModal(self.context_paths), self._on_context_modal_dismissed)

    def action_open_radar(self) -> None:
        """Open workspace radar backed by neurocli_core services."""

        self.push_screen(RadarModal())

    def action_open_git(self) -> None:
        """Open the git action lane backed by neurocli_core git services."""

        self.push_screen(GitModal())

    def action_reset_workspace(self) -> None:
        """Keyboard action for clearing transient terminal state."""

        self._reset_workspace_view()


def main():
    app = NeuroApp()
    app.run()


if __name__ == "__main__":
    main()
