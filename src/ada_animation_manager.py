import os
import tkinter as tk
from PIL import Image, ImageTk
from ASCII_Face import FRAMES_BY_STATE
import time

class AnimationGifHandler:
    def __init__(self, root, canvas_frame, text_color, background_color):
        self.root = root
        self.text_color = text_color
        self.background_color = background_color

        # Canvas for ASCII or GIF animation
        self.canvas = tk.Canvas(
            canvas_frame,
            width=200,
            height=200,
            bg=background_color,
            highlightthickness=0
        )
        self.canvas.pack()

        # ASCII animation state
        self.current_face_state = "WELCOME"
        self.current_face_frames = FRAMES_BY_STATE[self.current_face_state]
        self.face_index = 0
        self.after_id = None
        self.last_update_time_ascii = time.time()

        # GIF animation state
        self.gif_frames = []
        self.gif_index = 0
        self.gif_animation_id = None
        self.last_update_time_gif = time.time()

        # FPS settings
        self.ascii_fps = 2  # Default FPS for ASCII animations (slower)
        self.gif_fps = 5    # Default FPS for GIF animations (slower)

    def set_face_state(self, new_state):
        # Update ASCII face animation state
        self.current_face_state = new_state
        self.current_face_frames = FRAMES_BY_STATE[new_state]
        self.face_index = 0

    def draw_face(self, frame_text):
        # Draw a single ASCII frame on the canvas
        self.canvas.delete("all")
        self.canvas.create_text(
            100, 100,
            text=frame_text,
            font=("Courier New", 16),
            fill=self.text_color,
            justify="center"
        )

    def animate_ascii(self):
        # Animate ASCII frames if no GIF is playing
        current_time = time.time()
        if not self.gif_frames and (current_time - self.last_update_time_ascii >= 1 / self.ascii_fps):
            self.draw_face(self.current_face_frames[self.face_index])
            self.face_index = (self.face_index + 1) % len(self.current_face_frames)
            self.last_update_time_ascii = current_time
        self.after_id = self.root.after(10, self.animate_ascii)  # Check frequently for smoother timing

    def load_gif_frames(self, file_path):
        # Load frames from a GIF file and resize dynamically to fit the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        pil_image = Image.open(file_path)
        frames = []
        try:
            while True:
                frame = pil_image.copy().resize((canvas_width, canvas_height), Image.ANTIALIAS)
                frames.append(ImageTk.PhotoImage(frame.convert("RGBA")))
                pil_image.seek(pil_image.tell() + 1)
        except EOFError:
            pass
        return frames

    def stop_gif_animation(self):
        # Stop the GIF animation
        if self.gif_animation_id is not None:
            try:
                self.root.after_cancel(self.gif_animation_id)
            except tk.TclError:
                pass
        self.gif_animation_id = None
        self.gif_frames = []
        self.gif_index = 0

    def animate_gif(self):
        # Animate GIF frames
        current_time = time.time()
        if self.gif_frames and (current_time - self.last_update_time_gif >= 1 / self.gif_fps):
            self.canvas.delete("all")
            self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, image=self.gif_frames[self.gif_index])
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.last_update_time_gif = current_time
        self.gif_animation_id = self.root.after(10, self.animate_gif)  # Check frequently for smoother timing

    def start_gif_animation(self, gif_path):
        # Start a GIF animation, overriding ASCII
        self.stop_gif_animation()
        self.gif_frames = self.load_gif_frames(gif_path)
        if self.gif_frames:
            self.animate_gif()

    def check_for_gif_trigger(self, message):
        # Trigger a GIF based on specific keywords
        triggers = {
            "hello": "gifs/hello.gif",
            "love": "gifs/love.gif",
            "excited": "gifs/excited.gif",
        }
        lower_msg = message.lower()
        for trigger, gif_file in triggers.items():
            if trigger in lower_msg and os.path.exists(gif_file):
                self.start_gif_animation(gif_file)
                break

    def stop_all_animations(self):
        # Stop both ASCII and GIF animations
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.stop_gif_animation()
        self.after_id = None

    def update_colors(self, text_color, background_color):
        self.text_color = text_color
        self.background_color = background_color
        # Redraw the canvas with the new colors
        self.canvas.configure(bg=self.background_color)