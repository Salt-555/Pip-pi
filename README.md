# Pip-Pi AI Assistant

Pip-Pi is a desktop AI assistant application built with Python, featuring a customizable GUI, system monitoring capabilities, and an animated ASCII face interface. It uses the Gemma 2B model through Ollama for natural language processing and conversation.

## Features

- **Interactive Chat Interface**: Engage in conversations with an AI assistant powered by Gemma 2B
- **Animated ASCII Face**: Dynamic facial expressions that react to different conversation states
- **System Monitoring**: Real-time CPU and memory usage visualization
- **Customizable Themes**: Multiple theme options for the user interface
- **Settings Management**: Configurable options for volume, monitoring, and interface preferences
- **File Management**: Built-in capability to read and manage AI-related files
- **Sound Effects**: Audio feedback for enhanced user experience

## Prerequisites

- Python 3.8+
- Ollama with Gemma 2B model installed
- Required Python packages:
  - customtkinter
  - tkinter
  - pygame
  - matplotlib
  - pillow
  - psutil
  - requests

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pip-pi.git
cd pip-pi
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is installed and the Gemma 2B model is pulled:
```bash
ollama pull gemma2:2b
```

## Usage

To start the application:

```bash
python pip_pi.py
```

### Key Features:

- **Chat**: Type messages in the input field and press Enter or click Send
- **System Monitor**: Toggle the system monitoring graph in settings
- **Theme Customization**: Change themes via the settings menu
- **Volume Control**: Adjust sound effects volume in settings

## Project Structure

- `pip_pi.py`: Main application entry point
- `gui_manager.py`: GUI implementation and management
- `chatbot_handler.py`: AI conversation handling
- `system_monitor.py`: System resource monitoring
- `theme_manager.py`: Theme management and customization
- `settings_manager.py`: User settings management
- `animation_manager.py`: ASCII face animation control
- `ASCII_Face.py`: ASCII face frame definitions

## Configuration

### Themes
Themes are stored in JSON format in the `themes` directory. Each theme defines:
- Background colors
- Text colors
- Button styles
- Text box styles
- Accent colors

### Settings
User settings are stored in `settings.json` and include:
- Volume preferences
- Monitor visibility
- Update rate
- Current theme

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using CustomTkinter for modern UI elements
- Powered by Gemma 2B model through Ollama
- Matplotlib for system monitoring visualization
- Pygame for audio handling

## Known Issues

- Some theme changes may require application restart
- System monitor updates may impact performance on slower systems

## Future Improvements

- Additional theme options
- More customizable face animations
- Enhanced file management capabilities
- Expanded system monitoring features
- Support for additional AI models

---

For bug reports and feature requests, please open an issue on the GitHub repository.
