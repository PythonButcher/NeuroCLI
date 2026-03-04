import os
import re
from typing import Dict, List, Any
from datetime import datetime

# Exclude standard problematic folders
EXCLUDED_DIRS = {'.git', '.venv', '__pycache__', 'node_modules', 'tests', '.idea', '.vscode', 'build', 'dist', 'neurocli.egg-info'}

# Mapping of file extensions to languages
LANGUAGE_MAP = {
    '.py': 'Python',
    '.css': 'CSS',
    '.md': 'Markdown',
    '.txt': 'Text',
    '.js': 'JavaScript',
    '.html': 'HTML',
    '.json': 'JSON',
    '.sh': 'Shell',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML'
}

# Regex to find common TODO/FIXME patterns
# Matches # TODO, // FIXME, <!-- TODO, /* FIXME */, etc.
DEBT_REGEX = re.compile(r'(?i)(?:#|//|<!--|/\*\*?|\*)\s*(TODO|FIXME)\b\s*:?\s*(.*)')

def _is_valid_file(file_name: str) -> bool:
    """Check if the file has a mapped extension."""
    _, ext = os.path.splitext(file_name)
    return ext.lower() in LANGUAGE_MAP

def scan_workspace_health(cwd: str = '.') -> Dict[str, Any]:
    """
    Scans the workspace to calculate Lines of Code (LOC) per language.
    """
    loc_by_lang = {}
    total_loc = 0
    
    for root, dirs, files in os.walk(cwd):
        # Modify dirs in-place to exclude unwanted directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            if _is_valid_file(file):
                ext = os.path.splitext(file)[1].lower()
                lang = LANGUAGE_MAP[ext]
                
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Count non-empty lines for LOC
                        count = sum(1 for line in f if line.strip())
                        
                        if lang not in loc_by_lang:
                            loc_by_lang[lang] = 0
                        loc_by_lang[lang] += count
                        total_loc += count
                except (UnicodeDecodeError, IOError):
                    # Skip files that can't be read as text
                    continue
                    
    # Calculate percentages and sort by volume
    composition = {}
    for lang, count in sorted(loc_by_lang.items(), key=lambda item: item[1], reverse=True):
        percentage = round((count / total_loc) * 100, 1) if total_loc > 0 else 0
        composition[lang] = {
            'loc': count,
            'percentage': percentage
        }
        
    return {
        'total_loc': total_loc,
        'composition': composition
    }

def scan_technical_debt(cwd: str = '.') -> List[Dict[str, Any]]:
    """
    Scans valid files line-by-line to find TODO/FIXME comments.
    """
    debt_list = []
    
    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            if _is_valid_file(file):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, cwd)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            match = DEBT_REGEX.search(line)
                            if match:
                                msg_type = match.group(1).upper()
                                raw_msg = match.group(2).strip()
                                
                                # Clean up closing comment tags and hashes
                                clean_msg = re.sub(r'(-->|\*/|#)+$', '', raw_msg).strip()
                                
                                if not clean_msg:
                                    message = msg_type
                                else:
                                    message = f"{msg_type} {clean_msg}"
                                    
                                debt_list.append({
                                    'file_name': rel_path,
                                    'line_number': line_num,
                                    'message': message
                                })
                except (UnicodeDecodeError, IOError):
                    continue
                    
    return debt_list

def scan_recent_edits(cwd: str = '.') -> List[Dict[str, Any]]:
    """
    Scans the workspace to find recent AI modifications by looking for 
    `backups/` directories and parsing the timestamped files within them.
    Returns the 10 most recent edits.
    """
    edits = []
    
    # Matches filenames like: my_file_20260303_224551.py
    # Group 1: original name (my_file), Group 2: timestamp, Group 3: extension (.py)
    backup_regex = re.compile(r'^(.*)_(\d{8}_\d{6})(\.[a-zA-Z0-9]+)?$')
    
    for root, dirs, files in os.walk(cwd):
        # We still exclude the main problematic folders
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        # Only process files if we are inside a 'backups' directory
        if os.path.basename(root) == 'backups':
            for file in files:
                match = backup_regex.search(file)
                if match:
                    base_name, timestamp_str, ext = match.groups()
                    original_name = f"{base_name}{ext}" if ext else base_name
                    
                    try:
                        # Parse the timestamp: YYYYMMDD_HHMMSS
                        backup_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        
                        # Build the relative path representing the original file location
                        # The original file is one level up from the /backups folder
                        parent_dir = os.path.dirname(root)
                        original_path = os.path.join(parent_dir, original_name)
                        rel_path = os.path.relpath(original_path, cwd)
                        
                        edits.append({
                            'original_file': rel_path,
                            'backup_time': backup_time,
                            'timestamp_str': backup_time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                    except ValueError:
                        pass # Ignore if timestamp matching fails
                        
    # Sort by the most recent edits first
    edits.sort(key=lambda x: x['backup_time'], reverse=True)
    
    # Return top 10 recent edits
    return edits[:10]
