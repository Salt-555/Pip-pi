import tkinter as tk
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from settings_menu import SettingsMenu

class GUIManager:
    def __init__(self, app_instance, theme_data):
        self.app = app_instance
        self.THEME = theme_data
        self.BUTTON_STYLE = self.THEME["BUTTON_STYLE"]
        self.TEXTBOX_STYLE = self.THEME["TEXTBOX_STYLE"]
        self.INPUT_TEXTBOX_STYLE = self.THEME["INPUT_TEXTBOX_STYLE"]
        self.settings_window = None
        self.setup_main_window()
        self.root.bind('<<ReopenSettings>>', self._reopen_settings)
        self.input_field.bind("<Return>", self._handle_return)
        self.input_field.bind("<Shift-Return>", self._handle_shift_return)

    def _handle_return(self, event):
        if not event.state & 0x1:  # No Shift key
            self.app.on_submit()
            return 'break'  # Prevents default newline
        
    def _handle_shift_return(self, event):
        return  # Allows default newline behavior

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

        # Create the graph frame with system monitor components
        self.graph_frame = ctk.CTkFrame(
            self.face_label_frame,
            corner_radius=12,
            fg_color=self.THEME["BACKGROUND_COLOR"],
            width=300,
            height=150
        )
        self.graph_frame.pack(pady=(100, 5))
        
        # Initialize the matplotlib figure and canvas
        self.system_monitor_fig = Figure(figsize=(3.75, 1.5), dpi=100)
        self.system_monitor_ax = self.system_monitor_fig.add_subplot(111)
        
        # Style the plot
        self.system_monitor_ax.set_facecolor(self.THEME["BACKGROUND_COLOR"])
        self.system_monitor_fig.patch.set_facecolor(self.THEME["BACKGROUND_COLOR"])
        
        # Create the canvas and pack it
        self.system_monitor_canvas = FigureCanvasTkAgg(
            self.system_monitor_fig, 
            master=self.graph_frame
        )
        self.system_monitor_canvas_widget = self.system_monitor_canvas.get_tk_widget()
        self.system_monitor_canvas_widget.pack(expand=True, fill="both")
        
        # Initial styling of the plot
        self._style_system_monitor_plot()

    def _style_system_monitor_plot(self):
        """Apply consistent styling to the system monitor plot."""
        self.system_monitor_ax.spines['top'].set_color(self.THEME["TEXT_COLOR"])
        self.system_monitor_ax.spines['bottom'].set_color(self.THEME["TEXT_COLOR"])
        self.system_monitor_ax.spines['left'].set_color(self.THEME["TEXT_COLOR"])
        self.system_monitor_ax.spines['right'].set_color(self.THEME["TEXT_COLOR"])
        self.system_monitor_ax.tick_params(colors=self.THEME["TEXT_COLOR"], labelsize=8)

        self.system_monitor_ax.set_ylim(0, 100)  # Y-axis range: 0 to 100%
        self.system_monitor_ax.set_ylabel(
            "Usage (%)", 
            color=self.THEME["TEXT_COLOR"], 
            fontsize=8
        )
        self.system_monitor_ax.set_xlabel(
            "Time",
            color=self.THEME["TEXT_COLOR"],
            fontsize=8
        )
        self.system_monitor_ax.set_title(
            "System Monitor",
            fontsize=10,
            fontweight="bold",
            color=self.THEME["TEXT_COLOR"]
        )
        self.system_monitor_fig.subplots_adjust(left=0.2, bottom=0.3)
        
        # Ensure legend is properly styled
        # Legend will be added by SystemMonitor when data is available

    def get_system_monitor_components(self):
        """Return the system monitor components for use by the SystemMonitor class."""
        return {
            "canvas": self.system_monitor_canvas,
            "figure": self.system_monitor_fig,
            "ax": self.system_monitor_ax,
            "colors": {
                "background": self.THEME["BACKGROUND_COLOR"],
                "text": self.THEME["TEXT_COLOR"],
                "cpu": self.THEME["CPU_TREND_COLOR"],
                "memory": self.THEME["MEMORY_TREND_COLOR"]
            }
        }

    def update_system_monitor_colors(self, theme_data):
        """Update the system monitor plot colors when theme changes."""
        self.system_monitor_ax.set_facecolor(theme_data["BACKGROUND_COLOR"])
        self.system_monitor_fig.patch.set_facecolor(theme_data["BACKGROUND_COLOR"])
        self._style_system_monitor_plot()
        self.system_monitor_canvas.draw()

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
        
        # Update system monitor colors
        self.update_system_monitor_colors(theme_data)

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

    def _reopen_settings(self, event=None):
        if hasattr(self, 'settings_button'):
            self.settings_window = SettingsMenu(
                self.root,
                button_widget=self.settings_button,
                theme_manager=self.app.theme_manager,
                on_theme_change=self.app.apply_theme,
                current_theme=self.THEME,
                app=self.app
            )

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
                current_theme=self.THEME,
                app=self.app
            )