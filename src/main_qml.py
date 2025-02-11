import sys
from pathlib import Path
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from ui.controllers.theme_controller import ThemeController
from ui.controllers.settings_controller import SettingsController
from ui.controllers.face_controller import FaceController
from ui.controllers.chat_controller import ChatController

class ApplicationController:
    def __init__(self):
        self.engine = None
        self.theme_controller = ThemeController()
        self.settings_controller = SettingsController()
        self.face_controller = FaceController()
        self.chat_controller = ChatController()
        
    def initialize_qml(self):
        app = QApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        
        # Register controllers
        context = self.engine.rootContext()
        context.setContextProperty("themeController", self.theme_controller)
        context.setContextProperty("settingsController", self.settings_controller)
        context.setContextProperty("faceController", self.face_controller)
        context.setContextProperty("chatController", self.chat_controller)
        
        # Load the main QML file
        qml_file = Path(__file__).parent / "ui" / "qml" / "main.qml"
        self.engine.load(QUrl.fromLocalFile(str(qml_file)))
        
        if not self.engine.rootObjects():
            sys.exit(-1)
        
        # Play startup sound after a short delay
        QTimer.singleShot(100, self.settings_controller.playStartupSound)
        
        # Ensure proper cleanup
        app.aboutToQuit.connect(self.cleanup)
        
        return app.exec()
    
    def cleanup(self):
        """Clean up resources before application exit"""
        if hasattr(self, 'chat_controller'):
            self.chat_controller.cleanup()

def main():
    controller = ApplicationController()
    sys.exit(controller.initialize_qml())

if __name__ == "__main__":
    main()