from read_write_manager import ReadWriteManager

manager = ReadWriteManager()
manager.write_file("test.txt", "This is a test.")
print(manager.read_file("test.txt"))
