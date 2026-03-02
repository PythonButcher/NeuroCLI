from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Label, ListView, ListItem, Static
from pathlib import Path


class ContextModal(ModalScreen[set[str]]):
    """A modal screen that manages selection of multiple files/directories as context."""

    CSS_PATH = "main.css"

    def __init__(self, current_context: set[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_paths: set[str] = set(current_context)
        self.estimated_tokens: int = 0

    def compose(self) -> ComposeResult:
        with Container(id="context_dialog"):
            yield Label("📎 Context Manager", id="context_header")
            
            with Horizontal(id="context_main_area"):
                # Left side: Directory Tree for picking
                with Vertical(id="context_tree_container"):
                    yield Label("Workspace:")
                    yield DirectoryTree("./", id="context_tree")
                
                # Right side: Selected Items and Actions
                with Vertical(id="context_selection_container"):
                    yield Label("Selected Context (Click to remove):")
                    yield ListView(id="context_list")
                    
                    with Horizontal(id="context_info_row"):
                        yield Label("Tokens (Est): 0", id="token_estimator")
                        yield Button("Clear All", id="btn_clear_context", variant="error")

            with Horizontal(id="context_action_row"):
                yield Button("Cancel", id="btn_cancel_context")
                yield Button("Save Context", id="btn_save_context", variant="success")

    def on_mount(self) -> None:
        self._refresh_list()
        self._update_tokens()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Add file to context when selected."""
        path_str = str(event.path)
        if path_str not in self.selected_paths:
            self.selected_paths.add(path_str)
            self._refresh_list()
            self._update_tokens()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Optionally add directory to context when selected. For now, we allow it."""
        path_str = str(event.path)
        if path_str not in self.selected_paths:
            self.selected_paths.add(path_str)
            self._refresh_list()
            self._update_tokens()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Remove item from context when clicked in the list."""
        path_str = str(event.item.name) # Use name property we set on ListItem
        if path_str in self.selected_paths:
            self.selected_paths.remove(path_str)
            self._refresh_list()
            self._update_tokens()

    def _refresh_list(self) -> None:
        """Refresh the visible list view based on selected_paths set."""
        list_view = self.query_one("#context_list", ListView)
        list_view.clear()
        
        for path in sorted(self.selected_paths):
            p = Path(path)
            # Display basename but keep full path as identifier via `name`
            item = ListItem(Label(f"📄 {p.name}" if p.is_file() else f"📁 {p.name}"))
            item.name = path
            list_view.append(item)

    def _update_tokens(self) -> None:
        """Calculate a rough token estimation for selected files."""
        total_chars = 0
        for path_str in self.selected_paths:
            p = Path(path_str)
            if p.is_file():
                try:
                    # Quick character count. A real token estimator would use tiktoken.
                    # We assume ~4 chars per token.
                    with open(p, "r", encoding="utf-8") as f:
                        total_chars += len(f.read())
                except Exception:
                    pass
            elif p.is_dir():
                # Rough estimate for directories by summing up file contents
                for child in p.rglob("*"):
                    if child.is_file():
                        try:
                            with open(child, "r", encoding="utf-8") as f:
                                total_chars += len(f.read())
                        except Exception:
                            pass
                            
        self.estimated_tokens = total_chars // 4
        self.query_one("#token_estimator", Label).update(f"Tokens (Est): ~{self.estimated_tokens:,}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_cancel_context":
            self.dismiss() # Dismiss without returning value
        elif event.button.id == "btn_save_context":
            self.dismiss(self.selected_paths)
        elif event.button.id == "btn_clear_context":
            self.selected_paths.clear()
            self._refresh_list()
            self._update_tokens()
