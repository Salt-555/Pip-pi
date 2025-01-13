import sys
from pathlib import Path

# Add the src folder to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from read_write_manager import ReadWriteManager

# Testing the ReadWriteManager
manager = ReadWriteManager()
manager.write_file("test.txt", "This is a test.")
print(manager.read_file("test.txt"))
