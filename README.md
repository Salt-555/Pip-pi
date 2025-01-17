Pip Pi - Mini Assistant
Pip Pi is a lightweight Python-based AI agent application designed to run on a Raspberry Pi 5 or stronger hardware. It features a customizable GUI, animated ASCII faces, theme support, and system monitoring capabilities, powered by the Ollama model server running Gemma2 2B.
Features

Local AI Integration: Powered by Ollama with Gemma2 2B (configurable in chatbot_handler.py)
Real-time System Monitoring: CPU and memory usage tracking with matplotlib visualization
Advanced Animation System: ASCII character animations and GIF support
Theme Management: Customizable UI themes via JSON configuration
Event-driven Architecture: Robust event management system for UI updates
Resource Management: Efficient file I/O and settings persistence
Sound Support: Configurable audio feedback with volume control

Setup Instructions

Clone the repository:

bashCopygit clone https://github.com/Salt-555/Pip-pi.git
cd Pip-pi

Create and activate virtual environment:

bashCopypython3 -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate

Install dependencies:

bashCopypip install -r requirements.txt

Install and start Ollama:


Follow installation instructions at Ollama's website
Start the server:

bashCopyollama serve
Core Components

ada_mini.py: Main application entry point with event management
system_monitor.py: Real-time system metrics visualization
ada_animation_manager.py: Animation system with ASCII/GIF support
chatbot_handler.py: Ollama integration and conversation management
gui_manager.py: CustomTkinter-based UI with theme support
theme_manager.py: JSON-based theme configuration system
settings_manager.py: Persistent settings and configuration
read_write_manager.py: File operations management

Running the Application
bashCopypython ada_mini.py
Theme Customization
Create new themes by adding JSON files to the themes/ directory with the following structure:
jsonCopy{
    "BACKGROUND_COLOR": "#hex",
    "TEXT_COLOR": "#hex",
    "ACCENT_COLOR": "#hex",
    "AI_COLOR": "#hex",
    "BUTTON_COLOR": "#hex",
    "BUTTON_ACTIVE_COLOR": "#hex",
    "CPU_TREND_COLOR": "#hex",
    "MEMORY_TREND_COLOR": "#hex",
    "BUTTON_STYLE": {
        "font": ["font_name", size],
        "additional_properties": "values"
    }
}
Troubleshooting

Environment Issues: Verify virtual environment activation
Missing Packages: Run pip install -r requirements.txt
Ollama Connection: Ensure Ollama server is running (ollama serve)
Audio Issues: Check Sounds/Start.mp3 exists
Theme Loading: Verify JSON theme files are properly formatted

Contributing
Contributions welcome via issues or pull requests. Please follow existing code style and include tests when applicable.
