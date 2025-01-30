import customtkinter as ctk
from .settings_manager import load_settings, save_settings
from .theme_manager import ThemeManager

class SettingsMenu(ctk.CTkToplevel):
    def __init__(self, master, button_widget=None, theme_manager=None, on_theme_change=None, current_theme=None, app=None):
        super().__init__(master)
        self.title("Settings")
        self.theme_manager = theme_manager or ThemeManager()
        self.on_theme_change = on_theme_change
        self.current_theme = current_theme
        self.app = app
        self.button_widget = button_widget
        self.settings = load_settings()

        if not self.current_theme:
            raise ValueError("Current theme data must be provided")

        self._create_ui()
        self._setup_bindings()
        self._position_window()
        self.lift()
        self.focus_force()

    def _position_window(self):
        window_width = 400
        window_height = 500
        
        if self.button_widget:
            button_x = self.button_widget.winfo_rootx()
            button_y = self.button_widget.winfo_rooty()
            screen_height = self.winfo_screenheight()
            
            # Position above or below button based on space
            if button_y - window_height - 5 < 0:
                y_position = button_y + self.button_widget.winfo_height() + 5
            else:
                y_position = button_y - window_height - 5
                
            # Ensure window stays within screen bounds
            screen_width = self.winfo_screenwidth()
            x_position = min(max(button_x, 0), screen_width - window_width)
        else:
            # Center on screen if no button reference
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x_position = (screen_width - window_width) // 2
            y_position = (screen_height - window_height) // 2
            
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.resizable(False, False)

    def _create_ui(self):
        self.configure(fg_color=self.current_theme["BACKGROUND_COLOR"])
        
        self.border_frame = ctk.CTkFrame(
            self, 
            fg_color=self.current_theme["ACCENT_COLOR"],
            corner_radius=12
        )
        self.border_frame.pack(expand=True, fill="both", padx=2, pady=2)

        self.content_frame = ctk.CTkFrame(
            self.border_frame,
            fg_color=self.current_theme["BACKGROUND_COLOR"],
            corner_radius=12
        )
        self.content_frame.pack(expand=True, fill="both", padx=2, pady=2)

        self._create_audio_section()
        self._create_monitor_section()
        self._create_theme_section()
        self._create_about_section()

    def _create_section_header(self, parent, text):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=(self.current_theme["BUTTON_STYLE"]["font"][0], 16, "bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )

    def _create_audio_section(self):
        audio_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        audio_frame.pack(fill="x", padx=20, pady=10)

        header = self._create_section_header(audio_frame, "Audio Settings")
        header.pack(anchor="w", pady=(0, 5))

        self.volume_slider = ctk.CTkSlider(
            audio_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._on_volume_change,
            fg_color=self.current_theme["ACCENT_COLOR"],
            progress_color=self.current_theme["ACCENT_COLOR"],
            button_color=self.current_theme["BUTTON_COLOR"],
            button_hover_color=self.current_theme["BUTTON_ACTIVE_COLOR"]
        )
        self.volume_slider.set(self.settings.get("global_volume", 75))
        self.volume_slider.pack(fill="x", pady=5)

        self.volume_label = ctk.CTkLabel(
            audio_frame,
            text=f"Volume: {int(self.volume_slider.get())}%",
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.volume_label.pack()

    def _create_monitor_section(self):
        monitor_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        monitor_frame.pack(fill="x", padx=20, pady=10)

        header = self._create_section_header(monitor_frame, "System Monitor")
        header.pack(anchor="w", pady=(0, 5))

        self.monitor_switch = ctk.CTkSwitch(
            monitor_frame,
            text="Show System Monitor",
            command=self._toggle_monitor,
            fg_color=self.current_theme["ACCENT_COLOR"],
            progress_color=self.current_theme["ACCENT_COLOR"],
            button_color=self.current_theme["BUTTON_COLOR"],
            button_hover_color=self.current_theme["BUTTON_ACTIVE_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"]
        )
        show_monitor = self.settings.get("show_monitor", False)
        if show_monitor:
            self.monitor_switch.select()
        else:
            self.monitor_switch.deselect()
        self.monitor_switch.pack(pady=5)

        rate_frame = ctk.CTkFrame(monitor_frame, fg_color="transparent")
        rate_frame.pack(fill="x", pady=5)
        
        rate_label = ctk.CTkLabel(
            rate_frame,
            text="Update Rate:",
            text_color=self.current_theme["TEXT_COLOR"]
        )
        rate_label.pack(side="left", padx=(0, 10))

        self.update_rate_slider = ctk.CTkSlider(
            rate_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            command=self._on_update_rate_change,
            fg_color=self.current_theme["ACCENT_COLOR"],
            progress_color=self.current_theme["ACCENT_COLOR"],
            button_color=self.current_theme["BUTTON_COLOR"],
            button_hover_color=self.current_theme["BUTTON_ACTIVE_COLOR"],
            width=200
        )
        self.update_rate_slider.set(self.settings.get("monitor_update_rate", 2))
        self.update_rate_slider.pack(side="left", expand=True, fill="x", padx=5)

        self.update_rate_label = ctk.CTkLabel(
            rate_frame,
            text=f"{int(self.update_rate_slider.get())}s",
            text_color=self.current_theme["TEXT_COLOR"],
            width=30
        )
        self.update_rate_label.pack(side="left")

    def _create_theme_section(self):
        theme_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        theme_frame.pack(fill="x", padx=20, pady=10)

        header = self._create_section_header(theme_frame, "Theme Settings")
        header.pack(anchor="w", pady=(0, 5))

        themes = self.theme_manager.get_available_themes()
        current_theme_name = self.settings.get("current_theme", themes[0])
        
        self.theme_var = ctk.StringVar(value=current_theme_name)
        self.theme_dropdown = ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=themes,
            command=self._on_theme_select,
            fg_color=self.current_theme["BUTTON_COLOR"],
            button_color=self.current_theme["BUTTON_COLOR"],
            button_hover_color=self.current_theme["BUTTON_ACTIVE_COLOR"],
            dropdown_fg_color=self.current_theme["BACKGROUND_COLOR"],
            dropdown_hover_color=self.current_theme["BUTTON_ACTIVE_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            dropdown_text_color=self.current_theme["TEXT_COLOR"],
            font=self.current_theme["BUTTON_STYLE"]["font"]
        )
        self.theme_dropdown.pack(pady=5)

    def _create_about_section(self):
        about_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        about_frame.pack(fill="x", padx=20, pady=10)

        header = self._create_section_header(about_frame, "About")
        header.pack(anchor="w", pady=(0, 5))

        version_label = ctk.CTkLabel(
            about_frame,
            text="Version 1.0.0",
            text_color=self.current_theme["TEXT_COLOR"]
        )
        version_label.pack()

    def _setup_bindings(self):
        self.bind("<FocusOut>", self._close_on_focus_out)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _close_on_focus_out(self, event):
        if event.widget not in (self, self.theme_dropdown, self.theme_dropdown._dropdown_menu):
            self.destroy()

    def _on_volume_change(self, value):
        volume = int(value)
        self.settings['global_volume'] = volume
        self.volume_label.configure(text=f"Volume: {volume}%")
        save_settings(self.settings)

    def _toggle_monitor(self):
        show_monitor = bool(self.monitor_switch.get())
        self.settings['show_monitor'] = show_monitor
        save_settings(self.settings)
        
        if self.app:
            if show_monitor:
                self.app.gui.graph_frame.pack(pady=(100, 5))
                self.app.system_monitor.start()
            else:
                self.app.gui.graph_frame.pack_forget()
                self.app.system_monitor.stop()

    def _on_update_rate_change(self, value):
        rate = int(value)
        self.settings['monitor_update_rate'] = rate
        self.update_rate_label.configure(text=f"{rate}s")
        save_settings(self.settings)
        if self.app and hasattr(self.app, 'system_monitor'):
            self.app.system_monitor.set_update_rate(rate * 1000)

    def _on_theme_select(self, theme_name):
        if self.on_theme_change:
            self.settings['current_theme'] = theme_name
            save_settings(self.settings)
            self.destroy()
            self.on_theme_change(theme_name)
            self.after(100, lambda: self.master.event_generate('<<ReopenSettings>>'))