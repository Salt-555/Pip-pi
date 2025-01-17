import tkinter as tk
import customtkinter as ctk
from settings_menu import SettingsMenu
from pygame import mixer

class GUIManager:
    def __init__(self, app_instance, theme_data):
        self.app = app_instance
        self.THEME = theme_data
        self.BUTTON_STYLE = self.THEME["BUTTON_STYLE"]
        self.TEXTBOX_STYLE = self.THEME["TEXTBOX_STYLE"]
        self.INPUT_TEXTBOX_STYLE = self.THEME["INPUT_TEXTBOX_STYLE"]
        self.settings_window = None
        self.setup_main_window()
        
    def setup_main_window(self):
        self.root = ctk.CTk()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1000
        window_height = 800
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        self.create_main_frame()
        self.create_chat_window()
        self.create_face_frame()
        self.create_input_area()
        
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.configure(fg_color=self.THEME["BACKGROUND_COLOR"])
        
    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(
            self.root, corner_radius=12, fg_color=self.THEME["BACKGROUND_COLOR"]
        )
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

        self.send_button = ctk.CTkButton(
            master=self.bottom_frame,
            text="Send",
            **self.BUTTON_STYLE,
            command=self.app.on_submit
        )
        self.send_button.grid(row=0, column=1, sticky="ew")

        self.settings_button = ctk.CTkButton(
            master=self.bottom_frame,
            text="Settings",
            **self.BUTTON_STYLE,
            command=self.open_settings_menu
        )
        self.settings_button.grid(row=0, column=3, padx=(10, 0), sticky="ew")

    def update_input_height(self, event=None):
        line_count_str = self.input_field.index("end-1c")
        line_count = int(line_count_str.split(".")[0])
        line_count = max(1, min(line_count, 3))
        new_height = 50 + (line_count - 1) * 30
        self.input_field.configure(height=new_height)

    def open_settings_menu(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
        else:
            self.settings_window = SettingsMenu(
                self.root,
                button_widget=self.settings_button,
                theme_manager=self.app.theme_manager,
                on_theme_change=self.app.apply_theme,
                current_theme=self.THEME
            )

    def apply_theme_to_gui(self, theme_data):
        self.THEME = theme_data
        self.BUTTON_STYLE = self.THEME["BUTTON_STYLE"]
        self.TEXTBOX_STYLE = self.THEME["TEXTBOX_STYLE"]
        self.INPUT_TEXTBOX_STYLE = self.THEME["INPUT_TEXTBOX_STYLE"]

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

    def get_user_input(self):
        return self.input_field.get("1.0", "end-1c").strip()

    def clear_input_field(self):
        self.input_field.delete("1.0", "end")
        self.input_field.configure(height=50)

    def update_chat_window(self, message, tag=None):
        self.chat_window.configure(state="normal")
        self.chat_window.insert("end", message, tag if tag else "")
        self.chat_window.configure(state="disabled")
        self.chat_window.see("end")