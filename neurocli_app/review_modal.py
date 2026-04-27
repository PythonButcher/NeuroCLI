from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static, TextArea


class ReviewModal(ModalScreen[dict[str, str] | None]):
    """Editable review lane for the current AI or formatter proposal."""

    CSS_PATH = "main.css"

    def __init__(
        self,
        *args,
        target_file: str,
        proposed_content: str,
        baseline_content: str,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.target_file = target_file
        self.proposed_content = proposed_content
        self.baseline_content = baseline_content

    def compose(self) -> ComposeResult:
        with Container(id="review_dialog"):
            yield Label("🧭 Review Editor", id="review_header")

            with Horizontal(id="review_meta_row"):
                yield Static(self._build_target_label(), id="review_target_label")
                yield Static(self._build_proposal_label(), id="review_ready_label")

            with Horizontal(id="review_future_row"):
                yield Button("🔎 Find", id="btn_review_find", classes="review_future_btn")
                yield Button("↔ Diff", id="btn_review_diff", classes="review_future_btn")
                yield Button("🧪 Tests", id="btn_review_tests", classes="review_future_btn")
                yield Button("✨ Explain", id="btn_review_explain", classes="review_future_btn")

            with Vertical(id="review_main_area"):
                yield TextArea(
                    id="review_text_area",
                    language=self._detect_language(),
                    show_line_numbers=True,
                )

            with Horizontal(id="review_action_row"):
                yield Button("Cancel", id="btn_cancel_review", variant="error")
                yield Button("Reset Draft", id="btn_reset_review", variant="warning")
                yield Button("Keep Draft", id="btn_keep_review")
                yield Button("Apply Edited", id="btn_apply_review", variant="success")

    def on_mount(self) -> None:
        text_area = self.query_one("#review_text_area", TextArea)
        text_area.load_text(self._initial_editor_text())

        has_proposal = bool(self.proposed_content)
        self.query_one("#btn_keep_review", Button).disabled = not has_proposal
        self.query_one("#btn_apply_review", Button).disabled = not has_proposal

        # These controls reserve space for editor upgrades without implying they run today.
        for button_id in (
            "#btn_review_find",
            "#btn_review_diff",
            "#btn_review_tests",
            "#btn_review_explain",
        ):
            self.query_one(button_id, Button).disabled = True

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_cancel_review":
            self.dismiss()
            return

        if event.button.id == "btn_reset_review":
            self.query_one("#review_text_area", TextArea).load_text(
                self.proposed_content or self._initial_editor_text()
            )
            return

        if event.button.id == "btn_keep_review":
            self.dismiss(
                {
                    "action": "keep",
                    "content": self.query_one("#review_text_area", TextArea).text,
                }
            )
            return

        if event.button.id == "btn_apply_review":
            self.dismiss(
                {
                    "action": "apply",
                    "content": self.query_one("#review_text_area", TextArea).text,
                }
            )

    def _build_target_label(self) -> str:
        if not self.target_file:
            return "Target: none"
        return f"Target: {Path(self.target_file).name}"

    def _build_proposal_label(self) -> str:
        if not self.proposed_content:
            return "Proposal: not ready"
        line_count = len(self.proposed_content.splitlines())
        return f"Proposal: editable draft, {line_count:,} lines"

    def _detect_language(self) -> str:
        suffix = Path(self.target_file).suffix.lower().lstrip(".")
        return suffix or "text"

    def _initial_editor_text(self) -> str:
        if self.proposed_content:
            return self.proposed_content

        return (
            "No editable proposal is ready yet.\n\n"
            "Run a file-targeted prompt or format a selected file first, then reopen Review."
        )
