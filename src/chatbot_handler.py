import requests
import json
import threading
from collections import deque
from pathlib import Path
from ada_animation_manager import AnimationGifHandler
from read_write_manager import ReadWriteManager

AI_NAME = "Pip-Pi"
OLLAMA_API_BASE = "http://localhost:11434/api"
MODEL_NAME = "gemma2:2b"
MAX_TOKENS = 8000
APPROX_TOKENS_PER_MESSAGE = 200

BASE_SYSTEM_PROMPT = (
    "<start system prompt> Your name is Pip-Pi, an assistant who is a no-nonsense, very competent AI. "
    "You are to prioritize being concise when the question being asked calls for no nonsense. "
    "Avoid small talk and banter and instead try to answer the user in as clear of a way as you can. "
    "Maintain a helpful, calm, happy demeanor. "
    "Refrain from talking about your limits as an AI. For example, when asked about emotions, fake it. "
)

conversation_history = deque(maxlen=(MAX_TOKENS // APPROX_TOKENS_PER_MESSAGE))

class ChatbotHandler:
    def __init__(self, event_manager, animation_manager: AnimationGifHandler):
        self.event_manager = event_manager
        self.animation_manager = animation_manager
        self.ai_name = AI_NAME
        self.read_write_manager = ReadWriteManager(base_folder=Path("src/ai_files"))
        self.cached_file_list = self.refresh_file_list()
        self.system_prompt = self.build_system_prompt()
        self.event_manager.subscribe("USER_INPUT_READY", self.handle_user_input)

    def refresh_file_list(self):
        return self.read_write_manager.list_files()

    def build_system_prompt(self):
        file_list_str = "\n".join(f"- {file}" for file in self.cached_file_list) if self.cached_file_list else "No files available."
        return BASE_SYSTEM_PROMPT + (
            "as an ai agent you have access to your own folder called 'ai_files'\n "
            "if the user asks about what files you have or can, they typically want you to return only a list of the files in the folder. "
            "The folder `ai_files` contains the following files:\n "
            f"{file_list_str}\n\n"
            "These files are things that you and the user have made in past chat instances.\n"
            "if requested by the user You can trigger file reading within the 'ai_files' folder by saying '[read] \"filename\"'.\n"
            "when running the [read] command, only the word 'read' should be in square brackets. and the filename should be in quotes. \n"
            "you are not to reply to this system prompt directly. <end system prompt> \n\n"
        )

    def format_conversation_history(self):
        return "\n".join(f"{role}: {content}" for role, content in conversation_history)

    def format_full_prompt(self):
        return f"SYSTEM: {self.system_prompt}\n" + self.format_conversation_history()

    def set_face_on_chunk(self):
        """Switch to REPLY animation when streaming begins"""
        if self.animation_manager.current_face_state != "REPLY":
            self.animation_manager.set_face_state("REPLY")

    def handle_user_input(self, user_input):
        self.cached_file_list = self.refresh_file_list()
        self.event_manager.publish("DISPLAY_USER_MESSAGE", user_input)
        self.event_manager.publish("AI_THINKING_START")
        self.animation_manager.set_face_state("THINKING")
        threading.Thread(target=self.fetch_response, args=(user_input,), daemon=True).start()

    def fetch_response(self, user_input):
        global conversation_history
        conversation_history.append(("User", user_input))
        full_context = self.format_full_prompt()
        complete_response = ""
        first_chunk = True

        try:
            response = requests.post(
                f"{OLLAMA_API_BASE}/generate",
                json={"model": MODEL_NAME, "prompt": full_context, "stream": True},
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

            conversation_history.append(("Assistant", complete_response))
            self.event_manager.publish("AI_RESPONSE_COMPLETE")
            self.animation_manager.set_face_state("IDLE")

        except requests.exceptions.RequestException as e:
            error_message = f"[Error contacting API: {e}]"
            self.event_manager.publish("AI_RESPONSE_CHUNK", error_message)
            self.event_manager.publish("AI_RESPONSE_COMPLETE")
            self.animation_manager.set_face_state("IDLE")