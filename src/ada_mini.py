import sys
import tkinter as tk
import customtkinter as ctk
import threading
import subprocess
import json
from pathlib import Path
from pygame import mixer  # Added pygame for sound playback
from settings_menu import SettingsMenu
from settings_manager import load_settings
from system_monitor import SystemMonitor
from ada_animation_manager import AnimationGifHandler
from chatbot_handler import ChatbotHandler
from theme_manager import ThemeManager

class AdaMiniApp:
    def __init__(self):
        self.after_ids = {}  # Store callback IDs for later cancellation
        self.settings_window = None

        # Initialize theme manager and load theme
        self.theme_manager = ThemeManager()
        self.load_initial_theme()

        # Initialize main window
        self.root = ctk.CTk()

        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1000
        window_height = 800
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # Create main UI elements
        self.create_main_frame()
        self.create_chat_window()
        self.create_face_frame()
        self.create_input_area()

        # Initialize handlers
        self.init_handlers()

        # Set AI_NAME dynamically from ChatbotHandler
        self.AI_NAME = self.chatbot_handler.ai_name
        self.root.title(f"{self.AI_NAME} Assistant")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.configure(fg_color=self.THEME["BACKGROUND_COLOR"])

        # Play startup sound
        self.play_startup_sound()

    def load_initial_theme(self):
        themes = self.theme_manager.get_available_themes()
        settings = load_settings()
        current_theme = settings.get("current_theme", themes[0])
        self.THEME = self.theme_manager.load_theme(current_theme)
        self.BUTTON_STYLE = self.THEME["BUTTON_STYLE"]
        self.TEXTBOX_STYLE = self.THEME["TEXTBOX_STYLE"]
        self.INPUT_TEXTBOX_STYLE = self.THEME["INPUT_TEXTBOX_STYLE"]

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=12, fg_color=self.THEME["BACKGROUND_COLOR"])
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=0)

    def create_chat_window(self):
        self.chat_window = ctk.CTkTextbox(
            master=self.main_frame,
            **self.TEXTBOX_STYLE,
            state="disabled"
        )
        self.chat_window.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chat_window.tag_config("user", foreground=self.THEME["ACCENT_COLOR"])
        self.chat_window.tag_config("ai_name", foreground=self.THEME["AI_COLOR"])
        self.chat_window.tag_config("error", foreground="red")

    def create_face_frame(self):
        self.face_label_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12,
            fg_color=self.THEME["BACKGROUND_COLOR"]
        )
        self.face_label_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.graph_frame = ctk.CTkFrame(
            self.face_label_frame,
            corner_radius=12,
            fg_color=self.THEME["BACKGROUND_COLOR"],
            width=300,
            height=150
        )
        self.graph_frame.pack(pady=(100, 5))

    def create_input_area(self):
        self.bottom_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12,
            fg_color=self.THEME["BACKGROUND_COLOR"]
        )
        self.bottom_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=0)
        self.bottom_frame.columnconfigure(2, weight=0)
        self.bottom_frame.columnconfigure(3, weight=0)

        self.input_field = ctk.CTkTextbox(
            master=self.bottom_frame,
            **self.INPUT_TEXTBOX_STYLE,
            height=50
        )
        self.input_field.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_field.bind("<KeyRelease>", self.update_input_height)
        self.input_field.bind("<Return>", self.on_enter_key)

        self.send_button = ctk.CTkButton(
            master=self.bottom_frame,
            text="Send",
            **self.BUTTON_STYLE,
            command=self.on_submit
        )
        self.send_button.grid(row=0, column=1, sticky="ew")

        self.settings_button = ctk.CTkButton(
            master=self.bottom_frame,
            text="Settings",
            **self.BUTTON_STYLE,
            command=self.open_settings_menu
        )
        self.settings_button.grid(row=0, column=3, padx=(10, 0), sticky="ew")

    def init_handlers(self):
        # Ensure face_label_frame is created before using it in handlers
        if not hasattr(self, 'face_label_frame'):
            self.create_face_frame()

        self.animation_manager = AnimationGifHandler(
            root=self.root,
            canvas_frame=self.face_label_frame,
            text_color=self.THEME["TEXT_COLOR"],
            background_color=self.THEME["BACKGROUND_COLOR"]
        )
        self.animation_manager.animate_ascii()

        self.system_monitor = SystemMonitor(
            root=self.root,
            canvas_frame=self.graph_frame,
            background_color=self.THEME["BACKGROUND_COLOR"],
            text_color=self.THEME["TEXT_COLOR"],
            cpu_trend_color=self.THEME["CPU_TREND_COLOR"],
            memory_trend_color=self.THEME["MEMORY_TREND_COLOR"]
        )
        self.system_monitor.update()

        self.chatbot_handler = ChatbotHandler(self.animation_manager)

    def play_startup_sound(self):
        """Play the startup sound using the global volume from settings."""
        try:
            settings = load_settings()
            volume = settings.get("global_volume", 75) / 100  # Normalize volume to 0-1 range
            sound_path = Path(__file__).parent / "Sounds/Start.mp3"
            if sound_path.exists():
                mixer.init()
                mixer.music.set_volume(volume)
                mixer.music.load(str(sound_path))
                mixer.music.play()
            else:
                print(f"Startup sound not found at {sound_path}")
        except Exception as e:
            print(f"Error playing startup sound: {e}")

    def update_input_height(self, event=None):
        line_count_str = self.input_field.index("end-1c")
        line_count = int(line_count_str.split(".")[0])
        line_count = max(1, min(line_count, 3))
        new_height = 50 + (line_count - 1) * 30
        self.input_field.configure(height=new_height)

    def on_enter_key(self, event):
        self.on_submit()
        return "break"

    def open_settings_menu(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
        else:
            self.settings_window = SettingsMenu(
                self.root,
                button_widget=self.settings_button,
                theme_manager=self.theme_manager,
                on_theme_change=self.apply_theme,
                current_theme=self.THEME
            )

    def apply_theme(self, theme_name):
        self.THEME = self.theme_manager.load_theme(theme_name)
        self.BUTTON_STYLE = self.THEME["BUTTON_STYLE"]
        self.TEXTBOX_STYLE = self.THEME["TEXTBOX_STYLE"]
        self.INPUT_TEXTBOX_STYLE = self.THEME["INPUT_TEXTBOX_STYLE"]

        # Update all UI elements with new theme
        self.root.configure(fg_color=self.THEME["BACKGROUND_COLOR"])
        self.main_frame.configure(fg_color=self.THEME["BACKGROUND_COLOR"])
        self.chat_window.configure(**self.TEXTBOX_STYLE)
        self.chat_window.tag_config("user", foreground=self.THEME["ACCENT_COLOR"])
        self.chat_window.tag_config("ai_name", foreground=self.THEME["AI_COLOR"])

        self.face_label_frame.configure(fg_color=self.THEME["BACKGROUND_COLOR"])
        self.graph_frame.configure(fg_color=self.THEME["BACKGROUND_COLOR"])
        self.bottom_frame.configure(fg_color=self.THEME["BACKGROUND_COLOR"])

        self.input_field.configure(**self.INPUT_TEXTBOX_STYLE)
        self.send_button.configure(**self.BUTTON_STYLE)
        self.settings_button.configure(**self.BUTTON_STYLE)

        if hasattr(self, 'animation_manager'):
            self.animation_manager.update_colors(
                text_color=self.THEME["TEXT_COLOR"],
                background_color=self.THEME["BACKGROUND_COLOR"]
            )

        if hasattr(self, 'system_monitor'):
            self.system_monitor.update_colors(
                background_color=self.THEME["BACKGROUND_COLOR"],
                text_color=self.THEME["TEXT_COLOR"],
                cpu_trend_color=self.THEME["CPU_TREND_COLOR"],
                memory_trend_color=self.THEME["MEMORY_TREND_COLOR"]
            )

    def on_submit(self):
        user_input = self.input_field.get("1.0", "end-1c").strip()
        if not user_input:
            return
        self.input_field.delete("1.0", "end")
        self.input_field.configure(height=50)

        threading.Thread(
            target=self.chatbot_handler.handle_user_input,
            args=(user_input, self.chat_window),
            daemon=True
        ).start()

    def on_close(self):
        print("Stopping model: gemma2:2b ...")
        try:
            subprocess.run(["ollama", "stop", "gemma2:2b"], check=True)
        except Exception as e:
            print(f"Error stopping model: {e}")

        print("Cleaning up threads and callbacks...")
        for key, after_id in list(self.after_ids.items()):
            try:
                self.root.after_cancel(after_id)
            except tk.TclError:
                pass

        self.after_ids.clear()
        self.animation_manager.stop_all_animations()
        self.root.update()
        self.root.after(3000, self.safe_exit)

    def safe_exit(self):
        print("Cleaning up threads...")
        for thread in threading.enumerate():
            if thread is not threading.main_thread():
                print(f"Joining thread: {thread.name}")
                thread.join(timeout=1)
        try:
            self.root.destroy()
        except tk.TclError as e:
            print(f"Error during root.destroy(): {e}")
        import os
        os._exit(0)

    def run(self):
        self.animation_manager.set_face_state("WELCOME")
        self.root.after(5000, lambda: self.animation_manager.set_face_state("IDLE"))
        self.root.mainloop()

if __name__ == "__main__":
    app = AdaMiniApp()
    app.run()
