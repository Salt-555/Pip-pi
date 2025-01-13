Pip Pi - Mini Assistant

Pip Pi is a lightweight Python-based AI agent application designed to run on a Raspberry Pi. It features a customizable GUI, animated ASCII faces, and theme support. The current version requires you have Ollama downloaded on your machine.

---

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/Salt-555/Pip-pi.git
cd Pip-pi
```

### Step 2: Set Up a Virtual Environment

Python virtual environments help manage dependencies and avoid conflicts.

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```

### Step 3: Install Requirements

Install the necessary Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Additionally, the app requires the [Ollama](https://ollama.ai/) model server. Install Ollama and ensure it is running:

1. Follow the installation instructions on the [Ollama website](https://ollama.ai/).
2. Start the server by running:
   ```bash
   ollama serve
   ```

---

## Features

- **Chatbot Integration**:  Powered by a local AI model, currently managed through ollama (model swappable via                             one variable in chatbot_manager.py).
- **Custom Themes**:        Load and apply different themes for the GUI.
  
- **Animated Faces**:       ASCII and GIF-based animations for interactive feedback.
  
- **System Monitor**:       Real-time CPU and memory usage graphs.
  
- **Settings Menu**:        Control volume and theme preferences.
  
- **Startup Sound**:        Customizable sound played on launch.

---

## File Structure

- `ada_mini.py`: Main application entry point. (run this)
- `settings_menu.py`: Settings menu logic.
- `settings_manager.py`: Handles loading and saving settings.
- `theme_manager.py`: Manages themes.
- `system_monitor.py`: Monitors system vitals.
- `ada_animation_manager.py`: Handles ASCII and GIF animations.
- `chatbot_handler.py`: Manages chatbot interactions.
- `read_write_manager.py`: Handles file reading and writing operations.
- `ASCII_Face.py`: ASCII animation frames.

---

## Running the Application

After setting up the environment and installing the requirements:

```bash
python ada_mini.py
```

---

## Customizing Themes

1. Create a new JSON file in the `themes/` directory.
2. Define the theme properties, including colors and font settings.
3. Select the theme from the settings menu.

---

## Troubleshooting

- **Virtual Environment Issues**:
  Ensure the virtual environment is activated before running any commands.

- **Missing Dependencies**:
  Double-check that all required packages are installed:
  ```bash
  pip install -r requirements.txt
  ```

- **Ollama Not Found**:
  Ensure that Ollama is installed and the server is running:
  ```bash
  ollama serve
  ```

- **Startup Sound Not Playing**:
  Ensure the `Sounds/Start.mp3` file exists and is properly formatted.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or suggestions.

