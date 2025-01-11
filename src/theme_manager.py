import json
from pathlib import Path

class ThemeManager:
    def __init__(self):
        self.themes_dir = Path(__file__).parent / "themes"
        self.current_theme = None
        self._available_themes = self._load_available_themes()
        
    def _load_available_themes(self):
        """Load list of available theme files"""
        themes = {}
        for theme_file in self.themes_dir.glob("*.json"):
            theme_name = theme_file.stem.replace("_", " ").title()
            themes[theme_name] = theme_file
        return themes
    
    def get_available_themes(self):
        """Return list of available theme names"""
        return list(self._available_themes.keys())
    
    def convert_font_settings(self, style_dict):
        """Convert font lists from JSON to tuples for CustomTkinter"""
        if "font" in style_dict:
            style_dict["font"] = tuple(style_dict["font"])
        return style_dict
    
    def load_theme(self, theme_name):
        """Load specific theme by name"""
        if theme_name not in self._available_themes:
            raise ValueError(f"Theme '{theme_name}' not found")
            
        theme_path = self._available_themes[theme_name]
        try:
            with open(theme_path) as f:
                theme_data = json.load(f)
                
            # Convert font settings in all style dictionaries
            theme_data["BUTTON_STYLE"] = self.convert_font_settings(theme_data["BUTTON_STYLE"])
            theme_data["TEXTBOX_STYLE"] = self.convert_font_settings(theme_data["TEXTBOX_STYLE"])
            theme_data["INPUT_TEXTBOX_STYLE"] = self.convert_font_settings(theme_data["INPUT_TEXTBOX_STYLE"])
            
            self.current_theme = theme_name
            return theme_data
            
        except Exception as e:
            raise Exception(f"Error loading theme '{theme_name}': {e}")