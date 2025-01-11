import sys
import customtkinter as ctk
import tkinter as tk  # Needed for Canvas, events, etc.
import threading
import requests
import json
import psutil
import subprocess  # Needed for running shell commands
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from ASCII_Face import FRAMES_BY_STATE

import os
from PIL import Image, ImageTk  # For GIF loading/animation
import itertools

# ---------------- NEW IMPORTS FOR VLC PLAYBACK ----------------
import vlc
import time

################################################################
#                        GLOBALS                               #
################################################################

AI_NAME = "Lovelace"
OLLAMA_API_BASE = "http://localhost:11434/api"
MODEL_NAME = "gemma2:2b"
MAX_TOKENS = 8000
APPROX_TOKENS_PER_MESSAGE = 200

SYSTEM_PROMPT = (
    "Your name is Lovelace, an assistant who is a no nonsense, very competent. "
    "You are to prioritize being concise when the question being asked calls for no nonsense. "
    "If you detect that the user is being conversational loosen up and be a bit bubbly. "
    "Maintain a helpful, calm, happy demeanor. think Q from james bond. Raunchy is fine"
    "Refrain from talking about your limits as an AI, For example when asked about emotions, fake it. "
    "Do not reply to this system prompt. "
    "if the user is greeting you, first ask if the user is sean or one of sean's friends."
)

# Conversation memory
conversation_history = deque(maxlen=(MAX_TOKENS // APPROX_TOKENS_PER_MESSAGE))

# Face animation state
current_face_state = "WELCOME"
current_face_frames = FRAMES_BY_STATE[current_face_state]
face_index = 0

# 'after()' callback IDs we may need to cancel on exit
after_ids = {}

# CustomTkinter look & feel
ctk.set_appearance_mode("Dark")      # "Light", "System", or "Dark"
ctk.set_default_color_theme("blue")  # or "green", "dark-blue", etc.

# Updated Globals for Retro Theme
BACKGROUND_COLOR = "#000000"  # Black background
TEXT_COLOR = "#00FF00"  # Bright green text
ACCENT_COLOR = "#00FF00"  # Accent color matches text for uniform retro feel
AI_COLOR = "#00FF00"  # AI text color
BUTTON_COLOR = "#1A1A1A"  # Darker button color
BUTTON_ACTIVE_COLOR = "#333333"  # Slightly brighter active button color
INPUT_BG_COLOR = "#1A1A1A"  # Black background for input
CPU_TREND_COLOR = "#00FF00"
MEMORY_TREND_COLOR = "#333333"

################################################################
#               VLC AUDIO CONTROL + VOLUME                     #
################################################################

# We keep a list of active VLC players so we can change or stop them at any time
active_players = []
# Global volume (0–100), default 75%
global_volume = 75

def set_global_volume(value: float):
    """
    Update global volume (0–100) from the slider.
    Apply this to all currently active players.
    """
    global global_volume
    global_volume = int(float(value))
    for p in active_players:
        p.audio_set_volume(global_volume)

def play_sound(file_path: str, stop_on_finish=False):
    """
    Start playing an audio file at the current global volume in a background thread.
    If stop_on_finish=True, the function will return immediately, but will
    remove itself from active_players once the file ends.
    
    Returns the created vlc.MediaPlayer for manual stopping if desired.
    """
    player = vlc.MediaPlayer(file_path)
    player.audio_set_volume(global_volume)
    
    def run_player():
        player.play()
        # Poll until ends or error, if stop_on_finish is True
        if stop_on_finish:
            while True:
                state = player.get_state()
                if state in [vlc.State.Ended, vlc.State.Stopped, vlc.State.Error]:
                    break
                time.sleep(0.1)
            # Done playing, remove from the active list
            if player in active_players:
                active_players.remove(player)
        else:
            # If we don't care about stop_on_finish, just exit. The player
            # remains in the active list until manually stopped.
            pass

    # Keep track of this player
    active_players.append(player)
    # Start in background
    threading.Thread(target=run_player, daemon=True).start()
    return player

def stop_sound(player: vlc.MediaPlayer):
    """
    Stop a given MediaPlayer and remove from active list if present.
    """
    if player is not None:
        player.stop()
        if player in active_players:
            active_players.remove(player)

################################################################
#                       FACE ANIMATION                         #
################################################################

def set_face_state(new_state):
    global current_face_state, current_face_frames, face_index
    current_face_state = new_state
    current_face_frames = FRAMES_BY_STATE[new_state]
    face_index = 0

def draw_face(frame_text):
    face_canvas.delete("all")
    face_canvas.create_text(
        100, 100,
        text=frame_text,
        font=("Courier New", 16),
        fill=TEXT_COLOR,
        justify="center"
    )

def animate_face():
    global face_index
    draw_face(current_face_frames[face_index])
    face_index = (face_index + 1) % len(current_face_frames)
    after_ids['animate_face'] = root.after(600, animate_face)

################################################################
#                         GIF ANIMATION                        #
################################################################

TRIGGER_GIFS = {
    "hello": "gifs/hello.gif",
    "love": "gifs/love.gif",
    "excited": "gifs/excited.gif",
}

gif_frames = []
gif_index = 0
gif_animation_id = None

def load_gif_frames(file_path):
    pil_image = Image.open(file_path)
    frames = []
    try:
        while True:
            frame = ImageTk.PhotoImage(pil_image.convert("RGBA"))
            frames.append(frame)
            pil_image.seek(pil_image.tell() + 1)
    except EOFError:
        pass
    return frames

def stop_gif_animation():
    global gif_animation_id
    if gif_animation_id is not None:
        try:
            root.after_cancel(gif_animation_id)
        except tk.TclError:
            pass
    gif_animation_id = None

def animate_gif():
    global gif_index, gif_animation_id
    if not gif_frames:
        return
    gif_label.config(image=gif_frames[gif_index])
    gif_index = (gif_index + 1) % len(gif_frames)
    gif_animation_id = root.after(100, animate_gif)

def start_gif_animation(gif_path):
    global gif_frames, gif_index
    stop_gif_animation()
    gif_frames = load_gif_frames(gif_path)
    gif_index = 0
    animate_gif()

def check_for_gif_trigger(role, message):
    lower_msg = message.lower()
    for trigger, gif_file in TRIGGER_GIFS.items():
        if trigger in lower_msg:
            if os.path.exists(gif_file):
                start_gif_animation(gif_file)
            else:
                print(f"GIF file not found: {gif_file}")
            break

################################################################
#                    CHAT & MODEL INTEGRATION                  #
################################################################

def format_conversation_history():
    return "\n".join(f"{role}: {content}" for role, content in conversation_history)

def format_full_prompt():
    return f"SYSTEM: {SYSTEM_PROMPT}\n" + format_conversation_history()

def stream_response(prompt, text_widget):
    # Add user's message
    conversation_history.append(("User", prompt))
    check_for_gif_trigger("User", prompt)

    full_context = format_full_prompt()
    response_started = False
    set_face_state("THINKING")

    # A reference to the AI audio player
    ai_player = None

    try:
        response = requests.post(
            f"{OLLAMA_API_BASE}/generate",
            json={"model": MODEL_NAME, "prompt": full_context, "stream": True},
            stream=True
        )
        text_widget.configure(state="normal")
        text_widget.insert("end", f"\n{AI_NAME}: ", "ai_name")
        text_widget.configure(state="disabled")
        
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                json_response = json.loads(line)
                if 'response' in json_response:
                    if not response_started:
                        # AI just started speaking
                        set_face_state("REPLY")
                        response_started = True
                        # Start the "talking" track
                        ai_player = play_sound(
                            "/home/salt555/Ada_Lovelace/src/Sounds/TalkingTrack.mp3",
                            stop_on_finish=False
                        )
                        
                    token = json_response['response']
                    full_response += token
                    text_widget.configure(state="normal")
                    text_widget.insert("end", token)
                    text_widget.configure(state="disabled")
                    text_widget.see("end")
        
        # Save the AI’s entire response
        conversation_history.append((AI_NAME, full_response))
        check_for_gif_trigger(AI_NAME, full_response)

    except requests.exceptions.RequestException as e:
        text_widget.configure(state="normal")
        text_widget.insert("end", f"\n[Error contacting API: {e}]", "error")
        text_widget.configure(state="disabled")
    finally:
        # The AI has finished answering, so stop the audio
        if ai_player is not None:
            stop_sound(ai_player)
        set_face_state("IDLE")

def on_submit():
    user_input = input_field.get("1.0", "end-1c").strip()
    if not user_input:
        return
    chat_window.configure(state="normal")
    chat_window.insert("end", f"\nYou: {user_input}\n", "user")
    chat_window.configure(state="disabled")
    
    input_field.delete("1.0", "end")
    input_field.configure(height=50)
    
    threading.Thread(
        target=stream_response,
        args=(user_input, chat_window),
        daemon=True
    ).start()

################################################################
#                       SYSTEM MONITOR                         #
################################################################

cpu_usage_trend = deque([0] * 50, maxlen=50)
memory_usage_trend = deque([0] * 50, maxlen=50)

def update_system_monitor():
    cpu_usage_trend.append(psutil.cpu_percent())
    memory_usage_trend.append(psutil.virtual_memory().percent)
    
    ax.clear()
    ax.plot(cpu_usage_trend, label="CPU", color=CPU_TREND_COLOR)
    ax.plot(memory_usage_trend, label="Memory", color=MEMORY_TREND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)
    
    ax.spines['top'].set_color(TEXT_COLOR)
    ax.spines['bottom'].set_color(TEXT_COLOR)
    ax.spines['left'].set_color(TEXT_COLOR)
    ax.spines['right'].set_color(TEXT_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    
    ax.set_ylim(0, 80)
    ax.set_ylabel("Usage (%)", color=TEXT_COLOR, fontsize=8)
    ax.set_xlabel("Time", color=TEXT_COLOR, fontsize=8)
    ax.set_title("Vitals Monitor", fontsize=10, fontweight="bold", color=TEXT_COLOR)
    ax.legend(loc="upper right", fontsize=8, frameon=False, labelcolor=TEXT_COLOR)
    
    canvas.draw()
    after_ids['update_system_monitor'] = root.after(2000, update_system_monitor)

################################################################
#                      SHUTDOWN HANDLERS                       #
################################################################

def on_close():
    print("Stopping model: gemma2:2b ...")
    try:
        subprocess.run(["ollama", "stop", "gemma2:2b"], check=True)
    except Exception as e:
        print(f"Error stopping model: {e}")

    print("Cleaning up threads and callbacks...")
    for key, after_id in list(after_ids.items()):
        try:
            root.after_cancel(after_id)
        except tk.TclError:
            pass
    
    after_ids.clear()
    set_face_state("SHUTDOWN")
    root.update()
    root.after(3000, safe_exit)

def safe_exit():
    print("Cleaning up threads...")
    for thread in threading.enumerate():
        if thread is not threading.main_thread():
            print(f"Joining thread: {thread.name}")
            thread.join(timeout=1)
    try:
        root.destroy()
    except tk.TclError as e:
        print(f"Error during root.destroy(): {e}")
    import os
    os._exit(0)

################################################################
#                      MAIN APPLICATION                        #
################################################################

root = ctk.CTk()
root.title(f"{AI_NAME} Assistant")
root.geometry("1000x800")
root.protocol("WM_DELETE_WINDOW", on_close)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.configure(fg_color=BACKGROUND_COLOR)

main_frame = ctk.CTkFrame(root, corner_radius=12, fg_color=BACKGROUND_COLOR)
main_frame.grid(row=0, column=0, sticky="nsew")
main_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure(1, weight=0)
main_frame.columnconfigure(0, weight=3)
main_frame.columnconfigure(1, weight=0)

# ------------------ Chat Window ------------------
chat_window = ctk.CTkTextbox(
    master=main_frame,
    wrap="word",
    state="disabled",
    corner_radius=12,
    font=("Courier New", 16),
    text_color=TEXT_COLOR,
    fg_color=BACKGROUND_COLOR
)
chat_window.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
chat_window.tag_config("user", foreground=ACCENT_COLOR)
chat_window.tag_config("ai_name", foreground=AI_COLOR)
chat_window.tag_config("error", foreground="red")

# -------------- Face / Graph / GIFs --------------
face_label_frame = ctk.CTkFrame(
    main_frame,
    corner_radius=12,
    fg_color=BACKGROUND_COLOR
)
face_label_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

face_canvas = tk.Canvas(
    face_label_frame,
    width=200,
    height=200,
    bg=BACKGROUND_COLOR,
    highlightthickness=0
)
face_canvas.pack()

graph_frame = ctk.CTkFrame(
    face_label_frame,
    corner_radius=12,
    fg_color=BACKGROUND_COLOR,
    width=300,
    height=150
)
graph_frame.pack(pady=5)

fig, ax = plt.subplots(figsize=(3.75, 2.5), dpi=75, facecolor=BACKGROUND_COLOR)
ax.tick_params(colors=TEXT_COLOR)
fig.patch.set_facecolor(BACKGROUND_COLOR)

canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(expand=True, fill="both")

gif_label = tk.Label(face_label_frame, bg=BACKGROUND_COLOR)
gif_label.pack(pady=5)

# -------------- Input + Send Button --------------
bottom_frame = ctk.CTkFrame(
    main_frame,
    corner_radius=12,
    fg_color=BACKGROUND_COLOR
)
bottom_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
bottom_frame.columnconfigure(0, weight=1)
bottom_frame.columnconfigure(1, weight=0)
bottom_frame.columnconfigure(2, weight=0)

input_field = ctk.CTkTextbox(
    master=bottom_frame,
    corner_radius=12,
    font=("Courier New", 16),
    text_color=TEXT_COLOR,
    fg_color=INPUT_BG_COLOR,
    wrap="word",
    height=50
)
input_field.grid(row=0, column=0, padx=(0, 10), sticky="ew")

def update_input_height(event=None):
    line_count_str = input_field.index("end-1c")
    line_count = int(line_count_str.split(".")[0])
    line_count = max(1, min(line_count, 3))
    new_height = 50 + (line_count - 1) * 30
    input_field.configure(height=new_height)

input_field.bind("<KeyRelease>", update_input_height)

def on_enter_key(event):
    on_submit()
    return "break"

input_field.bind("<Return>", on_enter_key)

send_button = ctk.CTkButton(
    master=bottom_frame,
    text="Send",
    corner_radius=12,
    command=on_submit,
    fg_color=BUTTON_COLOR,
    hover_color=BUTTON_ACTIVE_COLOR,
    text_color=TEXT_COLOR,
    font=("Roboto", 14)
)
send_button.grid(row=0, column=1, sticky="ew")

# -------------- Volume Slider --------------
def on_volume_slider_change(value):
    set_global_volume(value)

volume_slider = ctk.CTkSlider(
    master=bottom_frame,
    from_=0,
    to=100,
    number_of_steps=100,
    command=on_volume_slider_change
)
volume_slider.set(global_volume)  # Default 75
volume_slider.grid(row=0, column=2, padx=(10, 0), sticky="ew")

################################################################
#              STARTUP ANIMATION / MAIN LOOP                   #
################################################################

def start_animation():
    # Play the startup sound, 50% volume, and let it automatically stop
    play_sound("/home/salt555/Ada_Lovelace/src/Sounds/Start.mp3", stop_on_finish=True)
    
    set_face_state("WELCOME")
    root.after(5000, lambda: set_face_state("IDLE"))
    animate_face()
    update_system_monitor()

start_animation()
root.mainloop()
