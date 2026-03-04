from textual.app import App
from neurocli_app.radar_modal import RadarModal
from textual.widgets import DataTable

class TestApp(App):
    def on_mount(self):
        self.push_screen(RadarModal())

    async def on_ready(self):
        modal = self.screen
        edits_table = modal.query_one("#edits_table", DataTable)
        print(f"Edits Table row count: {edits_table.row_count}")
        self.exit()

if __name__ == "__main__":
    app = TestApp()
    app.run(headless=True)
