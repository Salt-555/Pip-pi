import sys
from pathlib import Path
from PySide6.QtCore import QUrl, QObject
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

# Ensure backend is in path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

class ApplicationController(QObject):
    def __init__(self):
        super().__init__()
        # Will add more initialization here as we build
        self.engine = None
        
    def initialize_qml(self):
        app = QApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        
        # Set context properties here later
        
        # Load the main QML file
        qml_file = Path(__file__).parent / "ui" / "qml" / "main.qml"
        self.engine.load(QUrl.fromLocalFile(str(qml_file)))
        
        if not self.engine.rootObjects():
            sys.exit(-1)
            
        return app.exec()

def main():
    controller = ApplicationController()
    sys.exit(controller.initialize_qml())

if __name__ == "__main__":
    main()