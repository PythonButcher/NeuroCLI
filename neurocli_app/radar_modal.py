from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label, DataTable, Static
from pathlib import Path

from neurocli_core.radar_engine import scan_workspace_health, scan_technical_debt

class RadarModal(ModalScreen[None]):
    """A modal screen that displays Workspace Radar (Health & Heatmap)."""

    CSS_PATH = "main.css"

    def compose(self) -> ComposeResult:
        with Container(id="radar_dialog"):
            yield Label("📊 Workspace Radar", id="radar_header")
            
            with Grid(id="radar_grid"):
                # Left side: Code Composition
                with Vertical(id="radar_composition"):
                    yield Label("Code Composition", classes="radar_section_title")
                    yield Vertical(id="composition_content")
                    
                # Right side: Technical Debt
                with Vertical(id="radar_debt"):
                    yield Label("Technical Debt", classes="radar_section_title")
                    yield DataTable(id="debt_table")
                    
                # Bottom: AI Heatmap
                with Container(id="radar_heatmap"):
                    yield Label("Recent AI Heatmap", classes="radar_section_title")
                    yield Static("Tracking active...", id="heatmap_placeholder")
                    
            with Horizontal(id="radar_action_row"):
                yield Button("Close", id="btn_close_radar", variant="error")

    def on_mount(self) -> None:
        self._load_health()
        self._load_debt()

    def _load_health(self) -> None:
        # Load the stats dynamically, ensuring we scan the project root
        project_root = str(Path(__file__).parent.parent.resolve())
        health_data = scan_workspace_health(project_root)
        composition_view = self.query_one("#composition_content", Vertical)
        
        total_loc = health_data["total_loc"]
        composition_view.mount(Label(f"Total Lines of Code: {total_loc:,}", id="total_loc_label"))
        
        for lang, data in health_data["composition"].items():
            loc = data["loc"]
            pct = data["percentage"]
            
            # Simple textual progress bar mapping 100% to 20 chars
            bar_len = 20
            filled = int((pct / 100) * bar_len)
            bar = "█" * filled + "-" * (bar_len - filled)
            
            composition_view.mount(
                Label(f"{lang:10} | {bar} {pct:4.1f}% ({loc:,} LOC)", classes="lang_row")
            )

    def _load_debt(self) -> None:
        project_root = str(Path(__file__).parent.parent.resolve())
        debt_data = scan_technical_debt(project_root)
        table = self.query_one("#debt_table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        table.add_columns("File", "Line", "Message")
        
        for item in debt_data:
            table.add_row(item["file_name"], str(item["line_number"]), item["message"])

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_close_radar":
            self.dismiss()
