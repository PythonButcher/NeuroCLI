import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

# from neurocli_core import ... # UI-agnostic core logic import

app = FastAPI(title="NeuroCLI API")

# Allow CORS for the React frontend (running on Vite's default port 5173 or 5174)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NeuroCLI API is running. Ready to bridge to neurocli_core."}

@app.post("/execute")
async def execute_command(command: str):
    # Standard synchronous execution
    return {"status": "success", "command": command}

import os
from pathlib import Path
from neurocli_core.radar_engine import scan_workspace_health, scan_technical_debt, scan_recent_edits

@app.get("/api/radar")
async def get_radar_stats():
    """Returns aggregated stats from the radar engine for the current workspace."""
    project_root = str(Path(__file__).parent.parent.resolve())
    
    health = scan_workspace_health(project_root)
    debt = scan_technical_debt(project_root)
    edits = scan_recent_edits(project_root, max_items=20, max_days=7)
    
    return {
        "health": health,
        "debt": debt,
        "edits": edits
    }

def get_directory_tree(path: Path) -> dict:
    """Recursively builds a directory tree structure."""
    result = {"name": path.name, "path": str(path), "type": "directory", "children": []}
    
    try:
        # Exclude common hidden/build directories
        excludes = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}
        
        # Sort so directories come first, then files, both alphabetically
        entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        
        for entry in entries:
            if entry.name in excludes:
                continue
                
            if entry.is_dir():
                result["children"].append(get_directory_tree(entry))
            else:
                result["children"].append({"name": entry.name, "path": str(entry), "type": "file"})
    except PermissionError:
        pass # Skip directories we can't read
        
    return result

@app.get("/api/files")
async def get_files():
    """Returns the directory structure of the current workspace root."""
    # Assuming the API runs from /api, the project root is its parent directory
    project_root = Path(__file__).parent.parent.resolve()
    return get_directory_tree(project_root)

from pydantic import BaseModel
from neurocli_core.file_handler import create_backup
from neurocli_core.diff_generator import generate_diff
from neurocli_core.code_formatter import format_code
from neurocli_core.git_engine import execute_commit_and_push, get_staged_diff
import subprocess

class FormatRequest(BaseModel):
    file_path: str

class ApplyRequest(BaseModel):
    file_path: str
    content: str
    
class CommitRequest(BaseModel):
    message: str

def _get_git_status():
    try:
        # Get status
        status_result = subprocess.run(
            ["git", "status", "-s"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        lines = status_result.stdout.strip().split("\n")
        unsaved = [line[3:] for line in lines if len(line) > 3]
        
        branch_result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, encoding="utf-8", check=True)
        branch = branch_result.stdout.strip()
        
        return f"On branch {branch}", unsaved
    except subprocess.CalledProcessError:
        return "Not a git repository or git error.", []

@app.get("/api/git/status")
async def get_status_endpoint():
    status_msg, unsaved_files = _get_git_status()
    # Attempt to extract branch if possible, otherwise send raw message
    return {"status_message": status_msg, "unsaved_files": unsaved_files}

@app.get("/api/git/diff")
async def get_diff_endpoint(path: str = None):
    try:
        diff_text, is_fallback = get_staged_diff()
        return {"diffs": diff_text}
    except Exception as e:
        return {"diffs": str(e)}

@app.post("/api/git/commit")
async def execute_commit_endpoint(req: CommitRequest):
    try:
        # We'll just use add_all=True if there are unstaged changes
        status_msg, unsaved_files = _get_git_status()
        add_all = len(unsaved_files) > 0
        
        execute_commit_and_push(req.message, add_all=add_all)
        return {"success": True, "message": "Successfully committed and pushed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/file")
async def get_file_content(path: str):
    """Reads a file's content and returns it."""
    try:
        if not os.path.exists(path) or not os.path.isfile(path):
            return {"error": "File not found"}
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/format")
async def format_file_endpoint(req: FormatRequest):
    """Formats a file and returns the diff and proposed content, just like the TUI."""
    if not os.path.exists(req.file_path):
        return {"error": "File not found."}

    try:
        with open(req.file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        formatted_content = format_code(original_content, req.file_path)
        
        if formatted_content == original_content:
            return {"status": "no_change", "message": "No formatting needed.", "diff": ""}
        else:
            diff = generate_diff(original_content, formatted_content)
            return {
                "status": "changes_proposed", 
                "diff": diff, 
                "proposed_content": formatted_content
            }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/apply")
async def apply_changes_endpoint(req: ApplyRequest):
    """Writes proposed changes back to the file system, backing it up first."""
    try:
        backup_dir = os.path.join(os.path.dirname(req.file_path), "backups")
        create_backup(req.file_path, backup_dir)

        with open(req.file_path, "w", encoding="utf-8") as file:
            file.write(req.content)

        return {"status": "success", "message": f"Changes applied to {os.path.basename(req.file_path)} successfully."}
    except Exception as error:
        return {"error": str(error)}

async def fake_data_streamer(command: str):
    """
    Simulates the core logic yielding tokens character-by-character.
    Will be replaced by direct neurocli_core calls later.
    """
    response_text = f"Running conceptual analysis on command: '{command}'...\nAnalyzing syntax... [OK]\nGenerating optimized output...\n\nHello, this is a simulated generative response streaming character by character."
    
    # Simulate thinking time
    await asyncio.sleep(0.5)
    
    words = response_text.split(" ")
    for i, word in enumerate(words):
        # Add space back except for the first word
        yield {"data": (word + " ") if i < len(words) - 1 else word}
        await asyncio.sleep(0.05) # Delay between words

@app.get("/stream")
async def stream_command(command: str):
    return EventSourceResponse(fake_data_streamer(command))
