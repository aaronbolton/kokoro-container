# Kokoro TTS Web UI Docker

This Docker container provides a web interface for the Kokoro Text-to-Speech system, allowing you to generate audio from text using various languages and voices.

## Features

- Text input or file upload options
- Choice between Kokoro TTS and espeak-ng engines
- Support for multiple languages:
  - American English
  - British English
  - Spanish
  - French
  - Hindi
  - Italian
  - Brazilian Portuguese
- Adjustable speech speed
- Voice selection
- Audio playback directly in the browser
- Download options for generated audio files

## Getting Started

### Prerequisites

- Docker installed on your system

### Running the Web UI

1. Make sure the run script is executable:
   ```bash
   chmod +x run_webui_docker.sh
   ```

2. Run the Docker container:
   ```bash
   ./run_webui_docker.sh
   ```

3. Open your web browser and navigate to:
   ```
   http://localhost:5001
   ```

## Usage

1. Choose your input method:
   - **Text Input**: Type or paste text directly into the text area
   - **File Upload**: Upload a .txt file containing the text to convert

2. Configure the TTS options:
   - **TTS Engine**: Choose between Kokoro TTS or espeak-ng (fallback)
   - **Language**: Select the desired language from the dropdown
   - **Voice**: Enter the voice name (default: af_heart)
   - **Speed**: Adjust the speech speed using the slider

3. Click "Generate Audio" to create the audio file(s)

4. Once generated, you can:
   - Play the audio directly in the browser
   - Download individual audio files
   - Download all generated files (if multiple segments were created)

## Docker Details

The Docker container:
- Uses Python 3.9 with Flask for the web server
- Includes espeak-ng for speech synthesis
- Mounts the local input and output directories to persist files
- Exposes port 5001 for the web interface

## File Structure

- `Dockerfile.webui`: Defines the Docker image for the web UI
- `app.py`: The Flask application that serves the web UI and processes requests
- `kokoro_tts_espeak.py`: Python script that handles text-to-speech conversion
- `templates/index.html`: The HTML template for the web interface
- `static/css/style.css`: CSS styles for the web interface
- `static/js/script.js`: JavaScript for handling form submission and audio playback
- `run_webui_docker.sh`: Script to build and run the Docker container
- `requirements.txt`: Python dependencies for the web UI

## Notes

- Generated audio files are saved in the `output` directory, organized by session ID
- Uploaded text files are saved in the `input` directory
- Each generation session creates a unique session ID to keep files organized