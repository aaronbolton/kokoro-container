# Kokoro TTS Docker Application

This application provides a containerized version of the Kokoro text-to-speech system, allowing you to generate high-quality speech from text.

## Fixed Issues

- Fixed issue where audio files were created but contained no audio
- Added proper dependencies for all supported languages
- Improved error handling and debugging capabilities

## Requirements

- Docker installed on your system
- Internet connection for initial container build

## Quick Start

### Command Line Usage

```bash
# Build and run the Docker container with example text
./build_and_run.sh
```

### Web UI Usage

```bash
# Build and run the Web UI Docker container
./run_webui_docker.sh
```

Then open your browser to http://localhost:5001

## Supported Languages

- 🇺🇸 'a' => American English
- 🇬🇧 'b' => British English
- 🇪🇸 'e' => Spanish (es)
- 🇫🇷 'f' => French (fr-fr)
- 🇮🇳 'h' => Hindi (hi)
- 🇮🇹 'i' => Italian (it)
- 🇯🇵 'j' => Japanese (requires misaki[ja])
- 🇧🇷 'p' => Brazilian Portuguese (pt-br)
- 🇨🇳 'z' => Mandarin Chinese (requires misaki[zh])

## Voice Options

The default voice is 'af_heart'. Other voices may be available depending on your Kokoro version.

## Debugging Audio Issues

If you encounter issues with audio generation, you can use the included debug tool:

```bash
# For CLI version
docker run --rm -v "$(pwd)/debug_audio.py:/app/debug_audio.py" -v "$(pwd)/output:/output" kokoro-tts python /app/debug_audio.py --dir /output

# For Web UI version
docker exec -it $(docker ps -q -f ancestor=kokoro-tts-webui) python /app/debug_audio.py --dir /app/output
```

## Advanced Usage

### Custom Text Input

```bash
# From command line
docker run --rm -v "$(pwd)/input:/input" -v "$(pwd)/output:/output" kokoro-tts --text "Your text here"

# From a file
echo "Your text here" > input/custom.txt
docker run --rm -v "$(pwd)/input:/input" -v "$(pwd)/output:/output" kokoro-tts --text-file /input/custom.txt
```

### Language and Voice Selection

```bash
docker run --rm -v "$(pwd)/input:/input" -v "$(pwd)/output:/output" kokoro-tts --text "Your text here" --lang-code a --voice af_heart --speed 1.0
```

## Troubleshooting

If you encounter issues:

1. Make sure all dependencies are installed correctly
2. Check the Docker build logs for any errors
3. Use the debug_audio.py script to analyze generated audio files
4. Verify that your input text is properly formatted
5. Try rebuilding the Docker image with `--no-cache` to ensure fresh dependencies