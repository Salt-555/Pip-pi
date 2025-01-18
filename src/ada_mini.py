import sys
import threading
import subprocess
from pathlib import Path
from pygame import mixer
from settings_manager import load_settings
from system_monitor import SystemMonitor
from ada_animation_manager import AnimationGifHandler
from theme_manager import ThemeManager
from chatbot_handler import ChatbotHandler
from gui_manager import GUIManager

class EventManager:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, handler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event_type, data=None):
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(data)

class AdaMiniApp:
    def __init__(self):
        self.after_ids = {}
        self.event_manager = EventManager()
        self.theme_manager = ThemeManager()
        self.THEME = self._initialize_theme()
        self.gui = GUIManager(self, self.THEME)
        self._initialize_components()
        self._setup_window()
        self._subscribe_events()
        self.play_startup_sound()

    def _initialize_theme(self):
        themes = self.theme_manager.get_available_themes()
        settings = load_settings()
        return self.theme_manager.load_theme(settings.get("current_theme", themes[0]))

    def _initialize_components(self):
        self.animation_manager = AnimationGifHandler(
            root=self.gui.root,
            canvas_frame=self.gui.face_label_frame,
            text_color=self.THEME["TEXT_COLOR"],
            background_color=self.THEME["BACKGROUND_COLOR"]
        )
        self.animation_manager.animate_ascii()

        settings = load_settings()
        self.system_monitor = SystemMonitor(
            root=self.gui.root,
            canvas_frame=self.gui.graph_frame,
            background_color=self.THEME["BACKGROUND_COLOR"],
            text_color=self.THEME["TEXT_COLOR"],
            cpu_trend_color=self.THEME["CPU_TREND_COLOR"],
            memory_trend_color=self.THEME["MEMORY_TREND_COLOR"]
        )
        
        show_monitor = settings.get("show_monitor", False)
        if show_monitor:
            self.gui.graph_frame.pack(pady=(100, 5))
            self.system_monitor.start()
        else:
            self.gui.graph_frame.pack_forget()

        self.chatbot_handler = ChatbotHandler(
            event_manager=self.event_manager,
            animation_manager=self.animation_manager
        )

    def _setup_window(self):
        self.AI_NAME = self.chatbot_handler.ai_name
        self.gui.root.title(f"{self.AI_NAME} Assistant")
        self.gui.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _subscribe_events(self):
        event_mappings = {
            "DISPLAY_USER_MESSAGE": self._handle_user_message,
            "AI_THINKING_START": self._handle_thinking_start,
            "AI_RESPONSE_CHUNK": self._handle_response_chunk,
            "AI_RESPONSE_COMPLETE": self._handle_response_complete
        }
        for event, handler in event_mappings.items():
            self.event_manager.subscribe(event, handler)

    def _handle_user_message(self, message):
        self.gui.update_chat_window(f"You: {message}\n", "user")

    def _handle_thinking_start(self, _=None):
        pass

    def _handle_response_chunk(self, chunk):
        if not hasattr(self, '_response_started'):
            self.gui.update_chat_window(f"\n{self.AI_NAME}: ", "ai_name")
            self._response_started = True
        self.gui.update_chat_window(chunk, "ai_name")

    def _handle_response_complete(self, _=None):
        self.gui.update_chat_window("\n", "ai_name")
        delattr(self, '_response_started')

    def play_startup_sound(self):
        try:
            settings = load_settings()
            volume = settings.get("global_volume", 75) / 100
            sound_path = Path(__file__).parent / "Sounds/Start.mp3"
            if sound_path.exists():
                mixer.init()
                mixer.music.set_volume(volume)
                mixer.music.load(str(sound_path))
                mixer.music.play()
        except Exception as e:
            print(f"Error playing startup sound: {e}")

    def on_submit(self):
        user_input = self.gui.get_user_input()
        if user_input:
            self.gui.clear_input_field()
            self.event_manager.publish("USER_INPUT_READY", user_input)

    def apply_theme(self, theme_name):
        self.THEME = self.theme_manager.load_theme(theme_name)
        self.gui.apply_theme_to_gui(self.THEME)
        self._update_component_colors()

    def _update_component_colors(self):
        if hasattr(self, 'system_monitor'):
            self.system_monitor.update_colors(
                background_color=self.THEME["BACKGROUND_COLOR"],
                text_color=self.THEME["TEXT_COLOR"],
                cpu_trend_color=self.THEME["CPU_TREND_COLOR"],
                memory_trend_color=self.THEME["MEMORY_TREND_COLOR"]
            )
        if hasattr(self, 'animation_manager'):
            self.animation_manager.update_colors(
                text_color=self.THEME["TEXT_COLOR"],
                background_color=self.THEME["BACKGROUND_COLOR"]
            )

    def on_close(self):
        self._stop_model()
        self._cleanup_callbacks()
        if hasattr(self, 'animation_manager'):
            self.animation_manager.stop_all_animations()
        if hasattr(self, 'system_monitor'):
            self.system_monitor.stop()
        self.gui.root.update()
        self.gui.root.after(3000, self._safe_exit)

    def _stop_model(self):
        try:
            subprocess.run(["ollama", "stop", "gemma2:2b"], check=True)
        except Exception as e:
            print(f"Error stopping model: {e}")

    def _cleanup_callbacks(self):
        for key, after_id in list(self.after_ids.items()):
            try:
                self.gui.root.after_cancel(after_id)
            except Exception:
                pass
        self.after_ids.clear()

    def _safe_exit(self):
        for widget in [self.gui.root]:
            for after_id in widget.tk.call('after', 'info'):
                try:
                    widget.after_cancel(after_id)
                except Exception:
                    pass
                    
        for thread in threading.enumerate():
            if thread is not threading.main_thread():
                try:
                    thread.join(timeout=1)
                except Exception:
                    pass

        try:
            self.gui.root.quit()
            self.gui.root.destroy()
        except Exception:
            pass
            
        import os
        os._exit(0)

    def run(self):
        self.animation_manager.set_face_state("WELCOME")
        self.gui.root.after(5000, lambda: self.animation_manager.set_face_state("IDLE"))
        self.gui.root.mainloop()

if __name__ == "__main__":
    app = AdaMiniApp()
    app.run()