from collections import deque
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SystemMonitor:
    def __init__(self, root, canvas_frame, background_color, text_color, cpu_trend_color, memory_trend_color):
        self.root = root
        self.canvas_frame = canvas_frame
        self.background_color = background_color
        self.text_color = text_color
        self.cpu_trend_color = cpu_trend_color
        self.memory_trend_color = memory_trend_color

        self.cpu_usage_trend = deque([0] * 50, maxlen=50)
        self.memory_usage_trend = deque([0] * 50, maxlen=50)

        self.fig, self.ax = plt.subplots(figsize=(3.75, 1.5), dpi=100)
        self.ax.set_facecolor(self.background_color)
        self.fig.patch.set_facecolor(self.background_color)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(expand=True, fill="both")

        self.after_id = None
        self._style_plot()
        self.update()

    def _style_plot(self):
        """Apply consistent styling to the plot."""
        self.ax.spines['top'].set_color(self.text_color)
        self.ax.spines['bottom'].set_color(self.text_color)
        self.ax.spines['left'].set_color(self.text_color)
        self.ax.spines['right'].set_color(self.text_color)
        self.ax.tick_params(colors=self.text_color, labelsize=8)

        self.ax.set_ylim(0, 100)  # Y-axis range: 0 to 100%
        self.ax.set_ylabel("Usage (%)", color=self.text_color, fontsize=8)
        self.ax.set_xlabel("Time", color=self.text_color, fontsize=8)
        self.ax.set_title("System Monitor", fontsize=10, fontweight="bold", color=self.text_color)
        self.ax.legend(loc="upper right", fontsize=8, frameon=False, labelcolor=self.text_color)

    def update(self):
        """Update CPU and memory usage trends and redraw the graph."""
        # Update CPU and memory usage data
        self.cpu_usage_trend.append(psutil.cpu_percent())
        self.memory_usage_trend.append(psutil.virtual_memory().percent)

        # Clear and redraw the plot
        self.ax.clear()
        self.ax.plot(self.cpu_usage_trend, label="CPU", color=self.cpu_trend_color)
        self.ax.plot(self.memory_usage_trend, label="Memory", color=self.memory_trend_color)

        self._style_plot()  # Reapply styles after clearing
        self.fig.subplots_adjust(left=0.2, bottom=0.3)
        
        # Add the legend after plotting the data
        self.ax.legend(loc="upper right", fontsize=8, frameon=False, labelcolor=self.text_color)
        
        self.canvas.draw()

        # Schedule the next update
        self.after_id = self.root.after(2000, self.update)

    def stop(self):
        """Cancel the scheduled updates."""
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception as e:
                print(f"Error canceling update: {e}")
            self.after_id = None

    def update_colors(self, background_color, text_color, cpu_trend_color, memory_trend_color):
        self.background_color = background_color
        self.text_color = text_color
        self.cpu_trend_color = cpu_trend_color
        self.memory_trend_color = memory_trend_color

        self.ax.set_facecolor(self.background_color)
        self.fig.patch.set_facecolor(self.background_color)
        self._style_plot()
        self.canvas.draw()
