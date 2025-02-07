from PySide6.QtCore import QObject, Signal, Property, Slot
from backend import load_settings, save_settings
from pygame import mixer
from pathlib import Path

class SettingsController(QObject):
    settingsChanged = Signal()
    volumeChanged = Signal()
    personalityChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = load_settings()
        self._volume = self._settings.get("global_volume", 75)
        self._personality = self._settings.get("personality", "conversational")
        
        # Initialize pygame mixer
        try:
            mixer.init()
            self.apply_volume(self._volume)
        except Exception as e:
            print(f"Error initializing mixer: {e}")

    @Property(int, notify=volumeChanged)
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        if self._volume != value:
            self._volume = value
            self._settings["global_volume"] = value
            save_settings(self._settings)
            self.apply_volume(value)
            self.volumeChanged.emit()

    def apply_volume(self, volume):
        """Apply volume to pygame mixer"""
        try:
            mixer_volume = volume / 100.0
            mixer.music.set_volume(mixer_volume)
        except Exception as e:
            print(f"Error setting volume: {e}")

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
        self.apply_volume(self._volume)
        self.settingsChanged.emit()
        self.volumeChanged.emit()
        self.personalityChanged.emit()

    @Slot()
    def playStartupSound(self):
        """Play startup sound with current volume"""
        try:
            sounds_dir = Path(__file__).parent.parent.parent / "sounds"
            sound_path = sounds_dir / "Start.mp3"
            if sound_path.exists():
                mixer.music.load(str(sound_path))
                mixer.music.play()
        except Exception as e:
            print(f"Error playing startup sound: {e}")