# Pip-Pi Assistant

A desktop AI assistant built with Python, featuring real-time system monitoring, theme customization, and an animated ASCII face interface.

## Features

- Interactive chat interface combining the strengths of multiple LLM's
- Easily configurable to use your favorite model for it's brains.
- Customizable themes, easy to add new styles.
- Animated ASCII face expressions.
- Audio feedback.
- Cross-platform compatibility.

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running locally

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pip-pi.git
cd pip-pi
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Install required Ollama models:
```bash
ollama pull gemma2:2b
ollama pull deepseek-r1:7b
```

## Running the Application

1. Ensure Ollama is running:
```bash
ollama serve
```

2. Start Pip-Pi:
```bash
python ada_mini.py
```

## Key Dependencies

- customtkinter
- matplotlib
- pygame
- Pillow
- psutil
- requests

## Configuration

- Settings are stored in `settings.json`
- Theme configurations are located in the `themes` directory
- AI personalities can be configured in `personalities/ai_config.json`

## License

GNU General Public License v3.0

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
