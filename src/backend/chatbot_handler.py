import requests
import json
import threading
import subprocess
from collections import deque
from pathlib import Path
from .animation_manager import AnimationGifHandler
from .settings_manager import load_settings, save_settings

OLLAMA_API_BASE = "http://localhost:11434/api"
DEFAULT_PERSONALITY = "conversational"

class ChatbotHandler:
    def __init__(self, event_manager, animation_manager: AnimationGifHandler):
        self.event_manager = event_manager
        self.animation_manager = animation_manager
        self.personalities_path = Path(__file__).parent.parent / "personalities/ai_config.json"
        self.personalities = self._load_personalities()
        
        settings = load_settings()
        self.current_personality = settings.get("personality", DEFAULT_PERSONALITY)
        self._configure_personality()
        
        self.event_manager.subscribe("USER_INPUT_READY", self.handle_user_input)

    def _load_personalities(self):
        default_config = {
            "conversational": {
                "model_name": "gemma2:2b",
                "ai_name": "Pip-Pi",
                "system_prompt": "Your name is Pip-Pi, an assistant who is a no-nonsense, very competent AI. You are to prioritize being concise when the question being asked calls for no nonsense. Avoid small talk and banter and instead try to answer the user in as clear of a way as you can. Maintain a helpful, calm, happy demeanor.",
                "max_tokens": 8000,
                "approx_tokens_per_message": 200
            },
            "analytical": {
                "model_name": "deepseek-r1:1.5b",                "ai_name": "Pip-Pi",
                "system_prompt": "Your name is Pip-Pi, and you are a highly analytical AI assistant focused on detailed analysis and logical problem-solving. Prioritize accuracy and depth in your responses. Provide thorough explanations with supporting evidence when applicable. Break down complex problems into clear steps.",
                "max_tokens": 8000,
                "approx_tokens_per_message": 200
            }
        }
        
        try:
            with open(self.personalities_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading personalities from {self.personalities_path}: {e}")
            return default_config

    def _configure_personality(self):
        config = self.personalities[self.current_personality]
        self.model_name = config["model_name"]
        self.ai_name = config["ai_name"]
        self.base_system_prompt = config["system_prompt"]
        self.max_tokens = config["max_tokens"]
        self.approx_tokens_per_message = config["approx_tokens_per_message"]
        self.conversation_history = deque(maxlen=(self.max_tokens // self.approx_tokens_per_message))

    def _stop_current_model(self):
        try:
            subprocess.run(["ollama", "stop", self.model_name], check=True)
            print(f"Stopped model: {self.model_name}")
        except Exception as e:
            print(f"Error stopping model {self.model_name}: {e}")

    def switch_personality(self, personality_name):
        if personality_name in self.personalities:
            self._stop_current_model()
            self.current_personality = personality_name
            self._configure_personality()
            settings = load_settings()
            settings["personality"] = personality_name
            save_settings(settings)
            self.conversation_history.clear()
            
            if personality_name == "analytical":
                self.animation_manager.set_face_state("ANALYSIS")
                threading.Timer(4.0, lambda: self.animation_manager.set_face_state("IDLE")).start()
            elif personality_name == "conversational":
                self.animation_manager.set_face_state("CHATTING")
                threading.Timer(4.0, lambda: self.animation_manager.set_face_state("IDLE")).start()
            
            return True
        return False

    def build_system_prompt(self):
        return self.base_system_prompt

    def format_conversation_history(self):
        return "\n".join(f"{role}: {content}" for role, content in self.conversation_history)

    def format_full_prompt(self):
        return f"SYSTEM: {self.build_system_prompt()}\n{self.format_conversation_history()}"

    def set_face_on_chunk(self):
        if self.animation_manager.current_face_state != "REPLY":
            self.animation_manager.set_face_state("REPLY")

    def handle_user_input(self, user_input):
        self.event_manager.publish("DISPLAY_USER_MESSAGE", user_input)
        self.event_manager.publish("AI_THINKING_START")
        self.animation_manager.set_face_state("THINKING")
        threading.Thread(target=self.fetch_response, args=(user_input,), daemon=True).start()

    def fetch_response(self, user_input):
        self.conversation_history.append(("User", user_input))
        full_context = self.format_full_prompt()
        complete_response = ""
        first_chunk = True

        try:
            response = requests.post(
                f"{OLLAMA_API_BASE}/generate",
                json={"model": self.model_name, "prompt": full_context, "stream": True},
                stream=True
            )

            for line in response.iter_lines(decode_unicode=True):
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        if first_chunk:
                            self.set_face_on_chunk()
                            first_chunk = False
                        chunk = json_response['response']
                        complete_response += chunk
                        self.event_manager.publish("AI_RESPONSE_CHUNK", chunk)

            self.conversation_history.append(("Assistant", complete_response))
            self.event_manager.publish("AI_RESPONSE_COMPLETE")
            self.animation_manager.set_face_state("IDLE")

        except requests.exceptions.RequestException as e:
            error_message = f"[Error contacting API: {e}]"
            self.event_manager.publish("AI_RESPONSE_CHUNK", error_message)
            self.event_manager.publish("AI_RESPONSE_COMPLETE")
            self.animation_manager.set_face_state("IDLE")