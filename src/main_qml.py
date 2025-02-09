import sys
from pathlib import Path
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from ui.controllers.theme_controller import ThemeController
from ui.controllers.settings_controller import SettingsController
from ui.controllers.face_controller import FaceController

# Ensure backend is in path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

class ApplicationController:
    def __init__(self):
        self.engine = None
        self.theme_controller = ThemeController()
        self.settings_controller = SettingsController()
        self.face_controller = FaceController()
        
    def initialize_qml(self):
        app = QApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        
        # Register controllers
        context = self.engine.rootContext()
        context.setContextProperty("themeController", self.theme_controller)
        context.setContextProperty("settingsController", self.settings_controller)
        context.setContextProperty("faceController", self.face_controller)
        
        # Load the main QML file
        qml_file = Path(__file__).parent / "ui" / "qml" / "main.qml"
        self.engine.load(QUrl.fromLocalFile(str(qml_file)))
        
        if not self.engine.rootObjects():
            sys.exit(-1)
        
        # Play startup sound after a short delay to ensure mixer is ready
        QTimer.singleShot(100, self.settings_controller.playStartupSound)
            
        return app.exec()

def main():
    controller = ApplicationController()
    sys.exit(controller.initialize_qml())

if __name__ == "__main__":
    main()