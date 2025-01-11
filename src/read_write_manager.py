import os
from pathlib import Path

class ReadWriteManager:
    def __init__(self, base_folder="ai_files"):
        self.base_folder = Path(base_folder)
        if not self.base_folder.exists():
            self.base_folder.mkdir(parents=True)

    def list_files(self):
        """List all files in the ai_files directory."""
        return [file.name for file in self.base_folder.glob("*") if file.is_file()]

    def read_file(self, filename):
        """Read the contents of a specific file."""
        file_path = self.base_folder / filename
        if not file_path.exists() or not file_path.is_file():
            return f"[Error: File '{filename}' not found.]"
        with file_path.open("r", encoding="utf-8") as file:
            return file.read()
