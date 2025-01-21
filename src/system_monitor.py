from collections import deque
import psutil
from settings_manager import load_settings

class SystemMonitor:
    def __init__(self, gui_components):
        """Initialize the system monitor with GUI components from GUIManager.
        
        Args:
            gui_components (dict): Dictionary containing:
                - canvas: FigureCanvasTkAgg instance
                - figure: matplotlib Figure instance
                - ax: matplotlib Axes instance
                - colors: dict with theme colors
        """
        # Store GUI components
        self.canvas = gui_components["canvas"]
        self.fig = gui_components["figure"]
        self.ax = gui_components["ax"]
        self.colors = gui_components["colors"]
        
        # Initialize monitoring state
        settings = load_settings()
        self.update_rate = settings.get("monitor_update_rate", 2) * 1000  # Convert to milliseconds
        self.is_running = False
        self.after_id = None

        # Initialize data collections
        self.cpu_usage_trend = deque([0] * 50, maxlen=50)
        self.memory_usage_trend = deque([0] * 50, maxlen=50)

    def start(self):
        """Start monitoring system resources."""
        if not self.is_running:
            self.is_running = True
            self.update()

    def stop(self):
        """Stop monitoring system resources."""
        self.is_running = False
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception as e:
                print(f"Error canceling update: {e}")
            self.after_id = None

    def set_update_rate(self, rate_ms):
        """Set the update rate in milliseconds."""
        self.update_rate = rate_ms
        if self.is_running:
            self.stop()
            self.start()

    def update(self):
        """Update CPU and memory usage trends and redraw the graph."""
        if not self.is_running:
            return
            
        # Collect system metrics
        self.cpu_usage_trend.append(psutil.cpu_percent())
        self.memory_usage_trend.append(psutil.virtual_memory().percent)
        
        # Clear and redraw the plot
        self.ax.clear()
        
        # Plot CPU usage
        self.ax.plot(
            list(self.cpu_usage_trend),
            label="CPU",
            color=self.colors["cpu"]
        )
        
        # Plot memory usage
        self.ax.plot(
            list(self.memory_usage_trend),
            label="Memory",
            color=self.colors["memory"]
        )
        
        # Style the plot
        self._update_plot_style()
        
        # Draw the canvas
        self.canvas.draw()
        
        # Schedule next update
        # Get the root window from the canvas widget
        self.root = self.canvas.get_tk_widget().winfo_toplevel()
        self.after_id = self.root.after(self.update_rate, self.update)

    def _update_plot_style(self):
        """Update the plot styling."""
        # Configure spines
        for spine in self.ax.spines.values():
            spine.set_color(self.colors["text"])

        # Configure ticks
        self.ax.tick_params(colors=self.colors["text"], labelsize=8)

        # Configure axes
        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel("Usage (%)", color=self.colors["text"], fontsize=8)
        self.ax.set_xlabel("Time", color=self.colors["text"], fontsize=8)
        
        # Configure title
        self.ax.set_title(
            "System Monitor",
            fontsize=10,
            fontweight="bold",
            color=self.colors["text"]
        )
        
        # Configure legend
        self.ax.legend(
            loc="upper right",
            fontsize=8,
            frameon=False,
            labelcolor=self.colors["text"]
        )

        # Adjust layout
        self.fig.subplots_adjust(left=0.2, bottom=0.3)

    def update_colors(self, new_colors):
        """Update the plot colors when theme changes.
        
        Args:
            new_colors (dict): Dictionary containing:
                - background: Background color
                - text: Text color
                - cpu: CPU line color
                - memory: Memory line color
        """
        self.colors = new_colors
        
        # Update plot background colors
        self.ax.set_facecolor(self.colors["background"])
        self.fig.patch.set_facecolor(self.colors["background"])
        
        # Redraw with new colors if running
        if self.is_running:
            self._update_plot_style()
            self.canvas.draw()