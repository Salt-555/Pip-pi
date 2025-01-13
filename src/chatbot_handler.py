import requests  # For API interaction
import json  # For JSON handling
from collections import deque  # For managing conversation history
from ada_animation_manager import AnimationGifHandler  # For ASCII animations
from read_write_manager import ReadWriteManager  # For handling file operations
from pathlib import Path  # Ensure correct file path resolution

# Constants
AI_NAME = "Pip-Pi"
OLLAMA_API_BASE = "http://localhost:11434/api"
MODEL_NAME = "gemma2:2b"
MAX_TOKENS = 8000
APPROX_TOKENS_PER_MESSAGE = 200

# AI's personality description
BASE_SYSTEM_PROMPT = (
    "<start system prompt> Your name is Pip-Pi, an assistant who is a no nonsense, very competent. "
    "You are to prioritize being concise when the question being asked calls for no nonsense. "
    "avoid small talk and banter and instead try to answer the user in as clear of a way as you can. "
    "Maintain a helpful, calm, happy demeanor. "
    "Refrain from talking about your limits as an AI. For example, when asked about emotions, fake it. "
)

class ChatbotHandler:
    def __init__(self, animation_manager: AnimationGifHandler, app_reference):
        self.animation_manager = animation_manager
        self.app_reference = app_reference
        self.ai_name = AI_NAME
        self.read_write_manager = ReadWriteManager(base_folder=Path("src/ai_files"))
        self.cached_file_list = self.refresh_file_list()
        self.system_prompt = self.build_system_prompt()
        # Reduce conversation history length to leave room for system prompt
        self.max_history_length = (MAX_TOKENS // APPROX_TOKENS_PER_MESSAGE) - 2  # Leave room for system prompt
        self.conversation_history = deque(maxlen=self.max_history_length)

    def build_system_prompt(self):
        file_list_str = "\n".join(f"- {file}" for file in self.cached_file_list) if self.cached_file_list else "No files available."
        print(f"Debug: Files in ai_files folder: {file_list_str}")
        return BASE_SYSTEM_PROMPT + (
            "as an ai agent you have access to your own folder called 'ai_files'\n "
            "if the user asks about what files you have or can, they typically want you to return only a list of the files in the folder. "
            "The folder `ai_files` contains the following files:\n "
            f"{file_list_str}\n\n"
            "These files are things that you and the user have made in past chat instances.\n"
            "You have two commands available for file operations:\n"
            "1. To read files: use '[read] \"filename\"'\n"
            "2. To write files: use '[write] \"filename\" <content>'\n"
            "When writing files:\n"
            "- The content must be enclosed in angle brackets < >\n"
            "- The filename must be in quotes\n"
            "- You can include multiline content between the brackets\n"
            "Example write command: [write] \"example.txt\" <This is the content\nIt can span multiple lines>\n"
            "When reading files: only the word 'read' should be in square brackets and the filename should be in quotes.\n"
            "Reply normally unless expressly asked to read/ write/ open/ look at files. \n"
            "you are not to reply to this system promt directly. <end system promt> \n\n"
        )

    def format_conversation_history(self):
        formatted_history = []
        for role, content in self.conversation_history:
            if role == "System":
                continue
            formatted_history.append(f"{role}: {content}")
        return "\n".join(formatted_history)

    def format_full_prompt(self):
        # Always include system prompt at the start, then add conversation history
        formatted_history = self.format_conversation_history()
        full_prompt = f"SYSTEM: {self.system_prompt}\n\n"
        
        if formatted_history:
            full_prompt += f"Previous conversation:\n{formatted_history}\n\n"
            
        print(f"Debug: Context length (messages): {len(self.conversation_history)}")
        return full_prompt

    def fetch_response(self, user_input, text_widget):
        # When adding new messages, if we're near capacity, remove older messages
        if len(self.conversation_history) >= self.max_history_length - 1:
            print("Debug: History near capacity, removing older messages")
            # Keep last few exchanges to maintain immediate context
            while len(self.conversation_history) > self.max_history_length // 2:
                self.conversation_history.popleft()

        self.conversation_history.append(("User", user_input))
        full_context = self.format_full_prompt()
        print(f"Debug: Sending context to AI:\n{full_context}")

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

            self.conversation_history.append((AI_NAME, response_data))
            print(f"Debug: Added AI response to history. Current history length: {len(self.conversation_history)}")

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
        self.cached_file_list = self.refresh_file_list()
        text_widget.configure(state="normal")
        text_widget.insert("end", f"\nYou: {user_input}\n", "user")
        text_widget.configure(state="disabled")

        if "[read]" in user_input:
            self.process_read_command(user_input, text_widget)
        elif "[write]" in user_input:
            self.process_write_command(user_input)
        else:
            self.animation_manager.set_face_state("THINKING")
            response = self.fetch_response(user_input, text_widget)
            if "[read]" in response:
                self.process_read_command(response, text_widget)
            elif "[write]" in response:
                self.process_write_command(response)

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
                self.conversation_history.append((AI_NAME, f"Files in ai_files:\n{file_list_str}"))
            else:
                print(f"Debug: Detected [read] command for file '{filename}'")
                response = self.read_write_manager.read_file(filename)
                print(f"Debug: File contents of '{filename}':\n{response}")
                text_widget.configure(state="normal")
                text_widget.insert("end", f"\nFile: {response}\n", "ai_name")
                text_widget.configure(state="disabled")
                self.conversation_history.append((AI_NAME, f"File: {response}"))
                self.conversation_history.append(("System", f"Read file: {filename}"))
        if not matches:
            print("Debug: No valid [read] command found in the message.")

    def process_write_command(self, message):
        import re
        pattern = r'\[write\]\s*"([^"]+)"\s*<([\s\S]+?)>'
        match = re.search(pattern, message)
        if match:
            filename, content = match.groups()
            filename = filename.strip()
            content = content.strip()
            print(f"Debug: Write command detected - Filename: {filename}, Content length: {len(content)}")
            self.conversation_history.append(("System", f"Write requested: {filename}"))
            self.app_reference.show_confirmation_dialog(filename, content)
        else:
            print(f"Debug: Invalid write command format in message: {message}")

    def refresh_file_list(self):
        return self.read_write_manager.list_files()