# Kokoro TTS Web UI

A web interface for the Kokoro Text-to-Speech system that allows you to generate audio from text using various languages and voices.

## Features

- Text input or file upload options
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

- Python 3.6 or higher
- A working installation of the Kokoro TTS system

The run script will automatically:
- Create a Python virtual environment
- Install Flask in the virtual environment

### Running the Web UI

1. Make sure the run script is executable:
   ```bash
   chmod +x run_web_ui.sh
   ```

2. Run the web UI:
   ```bash
   ./run_web_ui.sh
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
   - **Language**: Select the desired language from the dropdown
   - **Voice**: Enter the voice name (default: af_heart)
   - **Speed**: Adjust the speech speed using the slider

3. Click "Generate Audio" to create the audio file(s)

4. Once generated, you can:
   - Play the audio directly in the browser
   - Download individual audio files
   - Download all generated files (if multiple segments were created)

## File Structure

- `app.py`: The Flask application that serves the web UI and processes requests
- `templates/index.html`: The HTML template for the web interface
- `static/css/style.css`: CSS styles for the web interface
- `static/js/script.js`: JavaScript for handling form submission and audio playback
- `run_web_ui.sh`: Script to start the web UI

## Notes

- Generated audio files are saved in the `output` directory, organized by session ID
- Uploaded text files are saved in the `input` directory
- Each generation session creates a unique session ID to keep files organized