import shutil
import os
from datetime import datetime

def create_backup(source_file, backup_dir):
    """
    Creates a backup of the specified file in the backup directory.
    The backup file will have a timestamp appended to its name.

    Args:
        source_file (str): Path to the file to be backed up.
        backup_dir (str): Directory where the backup will be stored.

    Returns:
        str: Path to the backup file if successful, None otherwise.
    """
    try:
        # Ensure the source file exists
        if not os.path.isfile(source_file):
            raise FileNotFoundError(f"Source file '{source_file}' does not exist.")

        # Ensure the backup directory exists, create it if not
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Generate a timestamped backup file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.basename(source_file)
        backup_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
        backup_file_path = os.path.join(backup_dir, backup_file_name)

        # Copy the file to the backup directory
        shutil.copy2(source_file, backup_file_path)

        return backup_file_path

    except Exception as e:
        print(f"Error during backup: {e}")
        return None
