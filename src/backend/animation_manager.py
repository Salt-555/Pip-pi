import os
import tkinter as tk
from PIL import Image, ImageTk
from .ASCII_Face import FRAMES_BY_STATE
import time

class ResponsiveAnimationHandler:
    def __init__(self, canvas, theme_data):
        self.canvas = canvas
        self.theme_data = theme_data
        self.current_mode = "ascii"
        self.current_frame = None
        
    def calculate_font_size(self, frame_text):
        if not self.canvas.winfo_exists():
            return ("Courier New", 16)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        char_width = len(max(frame_text.split('\n'), key=len))
        char_height = len(frame_text.split('\n'))
        
        width_based_size = (canvas_width * 0.8) / (char_width * 0.6)
        height_based_size = (canvas_height * 0.8) / (char_height * 1.2)
        
        base_size = max(int(min(width_based_size, height_based_size)), 2)
        return ("Courier New", base_size)
            
    def draw_frame(self, frame_text, mode=None):
        if mode:
            self.current_mode = mode
        self.current_frame = frame_text
        
        if not self.canvas.winfo_exists():
            return
            
        self.canvas.delete("animation")
        font = self.calculate_font_size(frame_text)
        
        self.canvas.create_text(
            self.canvas.winfo_width() / 2,
            self.canvas.winfo_height() / 2,
            text=frame_text,
            font=font,
            fill=self.theme_data["TEXT_COLOR"],
            justify="center",
            tags="animation"
        )

    def draw_image(self, image):
        if not self.canvas.winfo_exists():
            return
        self.canvas.delete("animation")
        self.canvas.create_image(
            self.canvas.winfo_width() / 2,
            self.canvas.winfo_height() / 2,
            image=image,
            tags="animation"
        )

    def update_theme(self, theme_data):
        self.theme_data = theme_data
        self.canvas.configure(bg=theme_data["BACKGROUND_COLOR"])
        self.canvas.itemconfigure("animation", fill=theme_data["TEXT_COLOR"])

class AnimationGifHandler:
    def __init__(self, root, canvas, theme_data):
        self.root = root
        self.theme_data = theme_data
        self.animation_handler = ResponsiveAnimationHandler(canvas, theme_data)
        
        self.current_face_state = "WELCOME"
        self.current_face_frames = FRAMES_BY_STATE[self.current_face_state]
        self.face_index = 0
        self.after_id = None
        self.last_update_time_ascii = time.time()
        
        self.gif_frames = []
        self.gif_index = 0
        self.gif_animation_id = None
        self.last_update_time_gif = time.time()
        
        self.ascii_fps = 2
        self.gif_fps = 5
        
        self.animate_ascii()

    def set_face_state(self, new_state):
        if new_state in FRAMES_BY_STATE:
            self.current_face_state = new_state
            self.current_face_frames = FRAMES_BY_STATE[new_state]
            self.face_index = 0

    def animate_ascii(self):
        current_time = time.time()
        if not self.gif_frames and (current_time - self.last_update_time_ascii >= 1 / self.ascii_fps):
            if self.current_face_frames:
                self.animation_handler.draw_frame(
                    self.current_face_frames[self.face_index], 
                    "ascii"
                )
                self.face_index = (self.face_index + 1) % len(self.current_face_frames)
                self.last_update_time_ascii = current_time
        
        self.after_id = self.root.after(10, self.animate_ascii)

    def load_gif_frames(self, file_path):
        canvas = self.animation_handler.canvas
        pil_image = Image.open(file_path)
        frames = []
        try:
            while True:
                frame = pil_image.copy().resize((
                    canvas.winfo_width(),
                    canvas.winfo_height()
                ), Image.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame.convert("RGBA")))
                pil_image.seek(pil_image.tell() + 1)
        except EOFError:
            pass
        return frames

    def animate_gif(self):
        if self.gif_frames and (time.time() - self.last_update_time_gif >= 1 / self.gif_fps):
            self.animation_handler.draw_image(self.gif_frames[self.gif_index])
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.last_update_time_gif = time.time()
        self.gif_animation_id = self.root.after(10, self.animate_gif)

    def start_gif_animation(self, gif_path):
        self.stop_gif_animation()
        self.gif_frames = self.load_gif_frames(gif_path)
        if self.gif_frames:
            self.animate_gif()

    def stop_gif_animation(self):
        if self.gif_animation_id:
            try:
                self.root.after_cancel(self.gif_animation_id)
            except tk.TclError:
                pass
            self.gif_animation_id = None
            self.gif_frames = []
            self.gif_index = 0

    def stop_all_animations(self):
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None
        self.stop_gif_animation()

    def update_colors(self, theme_data):
        self.theme_data = theme_data
        self.animation_handler.update_theme(theme_data)