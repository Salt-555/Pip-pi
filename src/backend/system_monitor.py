from collections import deque
import psutil
from .settings_manager import load_settings

class SystemMonitor:
    def __init__(self, gui_components):
        # Initialize core components
        self.canvas = gui_components["canvas"]
        self.fig = gui_components["figure"]
        self.ax = gui_components["ax"]
        self.colors = gui_components["colors"]
        
        # Load settings and initialize state
        settings = load_settings()
        self.update_rate = settings.get("monitor_update_rate", 2) * 1000
        self.is_running = False
        self.after_id = None
        self.root = None

        # Initialize data storage
        self.cpu_usage_trend = deque([0] * 50, maxlen=50)
        self.memory_usage_trend = deque([0] * 50, maxlen=50)
        
        self._initialize_plot()

    def _initialize_plot(self):
        """Initialize plot appearance and styling"""
        self.ax.set_facecolor(self.colors["background"])
        self.fig.patch.set_facecolor(self.colors["background"])
        self._update_plot_style()
        self.canvas.draw()

    def start(self):
        """Start monitoring system resources"""
        if not self.is_running:
            self.is_running = True
            self.root = self.canvas.get_tk_widget().winfo_toplevel()
            self.update()

    def stop(self):
        """Stop monitoring system resources"""
        self.is_running = False
        if self.after_id is not None:
            try:
                if self.root:
                    self.root.after_cancel(self.after_id)
            except Exception as e:
                print(f"Error canceling update: {e}")
            self.after_id = None

    def set_update_rate(self, rate_ms):
        """Set the update rate for monitoring"""
        self.update_rate = rate_ms
        if self.is_running:
            self.stop()
            self.start()

    def update(self):
        """Update system metrics and plot"""
        if not self.is_running:
            return

        try:
            # Get current system metrics
            self.cpu_usage_trend.append(psutil.cpu_percent())
            self.memory_usage_trend.append(psutil.virtual_memory().percent)
            
            # Clear and redraw plot
            self.ax.clear()
            cpu_line = self.ax.plot(
                list(range(len(self.cpu_usage_trend))),
                list(self.cpu_usage_trend),
                color=self.colors["cpu"],
                linewidth=1.0
            )[0]
            
            mem_line = self.ax.plot(
                list(range(len(self.memory_usage_trend))),
                list(self.memory_usage_trend),
                color=self.colors["memory"],
                linewidth=1.0
            )[0]
            
            # Configure legend
            self.ax.legend(
                [cpu_line, mem_line],
                ["CPU", "Memory"],
                loc="upper right",
                fontsize=6,
                frameon=False,
                labelcolor=self.colors["text"],
                handlelength=1.0,
                handletextpad=0.4,
                borderpad=0.2,
                borderaxespad=0.2
            )
            
            self._update_plot_style()
            self.canvas.draw()
            
            if self.root:
                self.after_id = self.root.after(self.update_rate, self.update)
        except Exception as e:
            print(f"Error updating system monitor: {e}")
            self.stop()

    def _update_plot_style(self):
        """Configure plot styling and appearance"""
        # Configure spine appearance
        for spine in self.ax.spines.values():
            spine.set_color(self.colors["text"])
            spine.set_linewidth(0.8)

        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        # Configure axis appearance
        self.ax.tick_params(
            axis='both',
            colors=self.colors["text"],
            labelsize=6,
            width=0.8,
            length=3,
            direction='out'
        )

        # Set axis limits and labels
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, self.cpu_usage_trend.maxlen - 1)
        
        self.ax.set_ylabel(
            "Usage (%)", 
            color=self.colors["text"], 
            fontsize=6,
            labelpad=2
        )
        
        self.ax.set_xlabel(
            "Time",
            color=self.colors["text"],
            fontsize=6,
            labelpad=2
        )
        
        # Configure title
        self.ax.set_title(
            "System Monitor",
            fontsize=8,
            fontweight="bold",
            color=self.colors["text"],
            pad=2
        )

        # Adjust subplot layout
        self.fig.subplots_adjust(
            left=0.15,
            right=0.95,
            bottom=0.25,
            top=0.85
        )
        
        # Set background colors
        self.ax.set_facecolor(self.colors["background"])
        self.fig.patch.set_facecolor(self.colors["background"])
        
        # Add grid
        self.ax.grid(
            True,
            linestyle=':',
            alpha=0.1,
            color=self.colors["text"]
        )

    def update_colors(self, new_colors):
        """Update color scheme of the plot"""
        self.colors = new_colors
        self._initialize_plot()
        if self.is_running:
            self._update_plot_style()
            self.canvas.draw()