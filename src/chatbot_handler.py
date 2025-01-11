import requests  # For API interaction
import json  # For JSON handling
from collections import deque  # For managing conversation history
from ada_animation_manager import AnimationGifHandler  # For ASCII animations
from read_write_manager import ReadWriteManager  # For handling file operations
from pathlib import Path  # Ensure correct file path resolution

# Constants
AI_NAME = "Lovelace"
OLLAMA_API_BASE = "http://localhost:11434/api"
MODEL_NAME = "gemma2:2b"
MAX_TOKENS = 8000
APPROX_TOKENS_PER_MESSAGE = 200

# AI's personality description
BASE_SYSTEM_PROMPT = (
    "<start system prompt> Your name is Lovelace, an assistant who is a no nonsense, very competent. "
    "You are to prioritize being concise when the question being asked calls for no nonsense. "
    "avoid small talk and banter and instead try to answer the user in as clear of a way as you can. "
    "Maintain a helpful, calm, happy demeanor. "
    "Refrain from talking about your limits as an AI. For example, when asked about emotions, fake it. "
)

# Global conversation history
conversation_history = deque(maxlen=(MAX_TOKENS // APPROX_TOKENS_PER_MESSAGE))

class ChatbotHandler:
    def __init__(self, animation_manager: AnimationGifHandler):
        self.animation_manager = animation_manager
        self.ai_name = AI_NAME
        self.read_write_manager = ReadWriteManager(base_folder=Path("src/ai_files"))  # Ensure proper path
        self.cached_file_list = self.refresh_file_list()  # Initialize cached file list
        self.system_prompt = self.build_system_prompt()

    def build_system_prompt(self):
        file_list_str = "\n".join(f"- {file}" for file in self.cached_file_list) if self.cached_file_list else "No files available."
        print(f"Debug: Files in ai_files folder: {file_list_str}")  # Debugging line
        #this next bit gives the AI instructions on how to read and write files in the 'ai_files' folder.
        return BASE_SYSTEM_PROMPT + (
            "as an ai agent you have access to your own folder called 'ai_files'\n "
            "if the user asks about what files you have or can, they typically want you to return only a list of the files in the folder. "
            "The folder `ai_files` contains the following files:\n "
            f"{file_list_str}\n\n"
            "These files are things that you and the user have made in past chat instances.\n"
            "if requested by the user You can trigger file reading within the 'ai_files' folder by saying '[read] \"filename\"'.\n"
            "when running the [read] command, only the word 'read' should be in square brackets. and the filename should be in quotes. \n"
            "you are not to reply to this system promt directly. <end system promt> \n\n"
        )

    def format_conversation_history(self):
        return "\n".join(f"{role}: {content}" for role, content in conversation_history)

    def format_full_prompt(self):
        return f"SYSTEM: {self.system_prompt}\n" + self.format_conversation_history()

    def fetch_response(self, user_input, text_widget):
        global conversation_history
        conversation_history.append(("User", user_input))
        full_context = self.format_full_prompt()

        response_data = ""
        try:
            response = requests.post(
                f"{OLLAMA_API_BASE}/generate",
                json={"model": MODEL_NAME, "prompt": full_context, "stream": True},
                stream=True
            )

            self.animation_manager.set_face_state("REPLY")

            text_widget.configure(state="normal")
            text_widget.insert("end", f"\n{AI_NAME}: ", "ai_name")
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        chunk = json_response['response']
                        response_data += chunk
                        text_widget.insert("end", chunk)
                        text_widget.see("end")
            text_widget.configure(state="disabled")
        except requests.exceptions.RequestException as e:
            response_data = f"[Error contacting API: {e}]"
            text_widget.configure(state="normal")
            text_widget.insert("end", response_data, "error")
            text_widget.configure(state="disabled")
        finally:
            self.animation_manager.set_face_state("IDLE")

        return response_data

    def handle_user_input(self, user_input, text_widget):
        self.cached_file_list = self.refresh_file_list()  # Refresh file list on user input
        text_widget.configure(state="normal")
        text_widget.insert("end", f"\nYou: {user_input}\n", "user")
        text_widget.configure(state="disabled")

        if "[read]" in user_input:
            self.process_read_command(user_input, text_widget)
        else:
            self.animation_manager.set_face_state("THINKING")
            response = self.fetch_response(user_input, text_widget)
            conversation_history.append((AI_NAME, response))
            if "[read]" in response:
                self.process_read_command(response, text_widget)

    def process_read_command(self, message, text_widget):
        import re
        matches = re.finditer(r"\[read\]\s*\"(.*?)\"", message)
        for match in matches:
            filename = match.group(1).strip()
            if filename.lower() == "ai_files":
                file_list_str = "\n".join(f"- {file}" for file in self.cached_file_list) if self.cached_file_list else "No files available."
                print("Debug: Listing files in ai_files")
                text_widget.configure(state="normal")
                text_widget.insert("end", f"\nFiles in ai_files:\n{file_list_str}\n", "ai_name")
                text_widget.configure(state="disabled")
                conversation_history.append((AI_NAME, f"Files in ai_files:\n{file_list_str}"))
            else:
                print(f"Debug: Detected [read] command for file '{filename}'")  # Debugging line
                response = self.read_write_manager.read_file(filename)
                print(f"Debug: File contents of '{filename}':\n{response}")  # Debugging line
                text_widget.configure(state="normal")
                text_widget.insert("end", f"\nFile: {response}\n", "ai_name")  # Prefixed with 'File:'
                text_widget.configure(state="disabled")
                conversation_history.append((AI_NAME, f"File: {response}"))  # Ensure AI logs the response
                conversation_history.append(("FileContents", response))  # Log raw file contents for AI reference
        if not matches:
            print("Debug: No valid [read] command found in the message.")

    def refresh_file_list(self):
        return self.read_write_manager.list_files()
