import customtkinter as ctk
from settings_manager import load_settings, save_settings
from theme_manager import ThemeManager

class SettingsMenu(ctk.CTkToplevel):
    def __init__(self, master, button_widget=None, theme_manager=None, on_theme_change=None, current_theme=None):
        super().__init__(master)
        self.title("Settings")
        self.geometry("400x400")
        self.resizable(False, False)

        self.theme_manager = theme_manager or ThemeManager()
        self.on_theme_change = on_theme_change
        self.current_theme = current_theme  # Store the current theme data

        if not self.current_theme:
            raise ValueError("Current theme data must be provided")

        # Create an outer frame to act as the colored border
        border_frame = ctk.CTkFrame(
            self, 
            fg_color=self.current_theme["ACCENT_COLOR"],
            corner_radius=0
        )
        border_frame.pack(expand=True, fill="both", padx=2, pady=2)

        # Inner frame for the actual content
        content_frame = ctk.CTkFrame(
            border_frame, 
            fg_color=self.current_theme["BACKGROUND_COLOR"],
            corner_radius=0
        )
        content_frame.pack(expand=True, fill="both")

        # Position the window relative to the button
        if button_widget:
            self.position_above_button(button_widget)

        # Load settings
        self.settings = load_settings()

        # Volume setting
        volume_label = ctk.CTkLabel(
            content_frame,
            text="Volume",
            font=self.current_theme["BUTTON_STYLE"]["font"],
            text_color=self.current_theme["TEXT_COLOR"],
            bg_color=self.current_theme["BACKGROUND_COLOR"]
        )
        volume_label.pack(pady=(20, 10))

        self.volume_slider = ctk.CTkSlider(
            content_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.on_volume_change,
            fg_color=self.current_theme["ACCENT_COLOR"],
            progress_color=self.current_theme["ACCENT_COLOR"],
            button_color=self.current_theme["BUTTON_COLOR"],
            button_hover_color=self.current_theme["BUTTON_ACTIVE_COLOR"]
        )
        self.volume_slider.set(self.settings.get("global_volume", 75))
        self.volume_slider.pack(pady=10)

        # Theme selection
        theme_label = ctk.CTkLabel(
            content_frame,
            text="Theme",
            font=self.current_theme["BUTTON_STYLE"]["font"],
            text_color=self.current_theme["TEXT_COLOR"],
            bg_color=self.current_theme["BACKGROUND_COLOR"]
        )
        theme_label.pack(pady=(20, 10))

        # Get available themes
        themes = self.theme_manager.get_available_themes()
        current_theme_name = self.settings.get("current_theme", themes[0])

        # Theme dropdown with matching style
        self.theme_var = ctk.StringVar(value=current_theme_name)
        self.theme_dropdown = ctk.CTkOptionMenu(
            content_frame,
            variable=self.theme_var,
            values=themes,
            command=self.on_theme_select,
            fg_color=self.current_theme["BUTTON_COLOR"],
            button_color=self.current_theme["BUTTON_COLOR"],
            button_hover_color=self.current_theme["BUTTON_ACTIVE_COLOR"],
            dropdown_fg_color=self.current_theme["BACKGROUND_COLOR"],
            dropdown_hover_color=self.current_theme["BUTTON_ACTIVE_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            dropdown_text_color=self.current_theme["TEXT_COLOR"],
            font=self.current_theme["BUTTON_STYLE"]["font"]
        )
        self.theme_dropdown.pack(pady=10)

        # Bind global click event to close settings menu when clicking outside
        self.bind("<FocusOut>", self.close_on_focus_out)

    def position_above_button(self, button_widget):
        """Position the settings menu just above the button."""
        button_x = button_widget.winfo_rootx()
        button_y = button_widget.winfo_rooty()
        self.geometry(f"400x400+{button_x}+{button_y - 400 - 5}")

    def close_on_focus_out(self, event):
        """Close the settings menu when focus is lost, unless it's the dropdown."""
        if event.widget not in (self, self.theme_dropdown, self.theme_dropdown._dropdown_menu):
            self.destroy()


    def on_volume_change(self, value):
        """Update the volume setting and save it to the settings file."""
        self.settings['global_volume'] = int(value)
        save_settings(self.settings)

    def on_theme_select(self, theme_name):
        """Handle theme selection and save to settings."""
        if self.on_theme_change:
            self.on_theme_change(theme_name)
        self.settings['current_theme'] = theme_name
        save_settings(self.settings)