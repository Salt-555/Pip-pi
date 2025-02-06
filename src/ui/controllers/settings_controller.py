from PySide6.QtCore import QObject, Signal, Property, Slot
from backend import load_settings, save_settings

class SettingsController(QObject):
    settingsChanged = Signal()
    volumeChanged = Signal()
    personalityChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = load_settings()
        self._volume = self._settings.get("global_volume", 75)
        self._personality = self._settings.get("personality", "conversational")

    @Property(int, notify=volumeChanged)
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        if self._volume != value:
            self._volume = value
            self._settings["global_volume"] = value
            save_settings(self._settings)
            self.volumeChanged.emit()

    @Property(str, notify=personalityChanged)
    def personality(self):
        return self._personality

    @personality.setter
    def personality(self, value):
        if self._personality != value:
            self._personality = value.lower()
            self._settings["personality"] = self._personality
            save_settings(self._settings)
            self.personalityChanged.emit()

    @Slot()
    def loadSettings(self):
        """Reload settings from file"""
        self._settings = load_settings()
        self._volume = self._settings.get("global_volume", 75)
        self._personality = self._settings.get("personality", "conversational")
        self.settingsChanged.emit()
        self.volumeChanged.emit()
        self.personalityChanged.emit()