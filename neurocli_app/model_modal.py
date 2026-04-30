from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea


class ModelModal(ModalScreen[dict[str, str] | None]):
    """Modal that edits the shared workflow ``model`` and ``model_options`` fields."""

    CSS_PATH = "main.css"

    def __init__(
        self,
        current_model: str,
        current_model_options_text: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.current_model = current_model
        self.current_model_options_text = current_model_options_text

    def compose(self) -> ComposeResult:
        with Container(id="context_dialog"):
            yield Label("🤖 Model Settings", id="context_header")

            with Vertical(id="context_selection_container"):
                yield Label("Model Override")
                yield Input(
                    placeholder="Leave blank to use the backend default model",
                    id="model_input",
                )

                yield Label("Model Options JSON")
                yield TextArea(
                    id="model_options_input",
                    language="json",
                    show_line_numbers=False,
                )

            with Horizontal(id="context_action_row"):
                yield Button("Cancel", id="btn_cancel_model")
                yield Button("Clear", id="btn_clear_model", variant="warning")
                yield Button("Save", id="btn_save_model", variant="success")

    def on_mount(self) -> None:
        self.query_one("#model_input", Input).value = self.current_model
        self.query_one("#model_options_input", TextArea).load_text(
            self.current_model_options_text
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_cancel_model":
            self.dismiss()
        elif event.button.id == "btn_clear_model":
            self.query_one("#model_input", Input).value = ""
            self.query_one("#model_options_input", TextArea).load_text("")
        elif event.button.id == "btn_save_model":
            self.dismiss(
                {
                    "model": self.query_one("#model_input", Input).value,
                    "model_options_text": self.query_one(
                        "#model_options_input", TextArea
                    ).text,
                }
            )
