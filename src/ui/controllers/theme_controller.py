from PySide6.QtCore import QObject, Signal, Property, Slot
from pathlib import Path
import json
from backend import load_settings, save_settings

class ThemeController(QObject):
    themeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.themes_dir = Path(__file__).parent.parent.parent / "themes"
        self._available_themes = self._load_available_themes()
        
        # Load theme from settings
        settings = load_settings()
        self._current_theme_name = settings.get("current_theme", "Modern Dark")
        theme_file = self._current_theme_name.lower().replace(" ", "_")
        self._current_theme = self._load_theme(theme_file)
        
        if not self._current_theme:  # Fallback if theme load fails
            self._current_theme = self._load_theme("modern_dark")
            self._current_theme_name = "Modern Dark"

    def _load_available_themes(self):
        """Load list of available theme files"""
        themes = {}
        for theme_file in self.themes_dir.glob("*.json"):
            theme_name = theme_file.stem.replace("_", " ").title()
            themes[theme_name] = theme_file
        return themes

    def _load_theme(self, theme_name):
        """Load a specific theme file"""
        theme_file = self.themes_dir / f"{theme_name}.json"
        try:
            with open(theme_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading theme: {e}")
            return None

    @Property(str, notify=themeChanged)
    def currentTheme(self):
        return self._current_theme_name

    @Property(str, notify=themeChanged)
    def backgroundColor(self):
        return self._current_theme.get("BACKGROUND_COLOR", "#121212")

    @Property(str, notify=themeChanged)
    def textColor(self):
        return self._current_theme.get("TEXT_COLOR", "#E0E0E0")

    @Property(str, notify=themeChanged)
    def accentColor(self):
        return self._current_theme.get("ACCENT_COLOR", "#BB86FC")

    @Property(str, notify=themeChanged)
    def aiColor(self):
        return self._current_theme.get("AI_COLOR", "#03DAC6")

    @Property(str, notify=themeChanged)
    def buttonColor(self):
        return self._current_theme.get("BUTTON_COLOR", "#1F1F1F")

    @Property(str, notify=themeChanged)
    def buttonActiveColor(self):
        return self._current_theme.get("BUTTON_ACTIVE_COLOR", "#333333")

    @Property(str, notify=themeChanged)
    def inputBgColor(self):
        return self._current_theme.get("INPUT_BG_COLOR", "#1E1E1E")

    @Property(str, notify=themeChanged)
    def cpuTrendColor(self):
        return self._current_theme.get("CPU_TREND_COLOR", "#FF5722")

    @Property(str, notify=themeChanged)
    def memoryTrendColor(self):
        return self._current_theme.get("MEMORY_TREND_COLOR", "#4CAF50")

    @Property(int, notify=themeChanged)
    def cornerRadius(self):
        return self._current_theme.get("BUTTON_STYLE", {}).get("corner_radius", 12)

    @Property(str, notify=themeChanged)
    def fontFamily(self):
        return self._current_theme.get("BUTTON_STYLE", {}).get("font", ["Roboto", 14])[0]

    @Property(int, notify=themeChanged)
    def fontSize(self):
        return self._current_theme.get("BUTTON_STYLE", {}).get("font", ["Roboto", 14])[1]

    @Slot(str)
    def setTheme(self, theme_name):
        """Change the current theme and save to settings"""
        theme_file = theme_name.lower().replace(" ", "_")
        new_theme = self._load_theme(theme_file)
        if new_theme:
            self._current_theme = new_theme
            self._current_theme_name = theme_name
            # Save to settings
            settings = load_settings()
            settings["current_theme"] = theme_name
            save_settings(settings)
            self.themeChanged.emit()

    @Slot(result=list)
    def getAvailableThemes(self):
        """Get list of available themes"""
        return list(self._available_themes.keys())