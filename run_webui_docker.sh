#!/bin/bash

# Build the Docker image with no cache to ensure fresh dependencies
echo "Building Docker image for Kokoro TTS Web UI..."
docker build --no-cache -t kokoro-tts-webui -f Dockerfile.webui .

# Run the Docker container
echo "Starting Kokoro TTS Web UI container..."
docker run --rm -p 5001:5001 \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/static:/app/static" \
  -v "$(pwd)/templates:/app/templates" \
  -v "$(pwd)/kokoro_tts.py:/app/kokoro_tts.py" \
  -v "$(pwd)/app.py:/app/app.py" \
  -v "$(pwd)/debug_audio.py:/app/debug_audio.py" \
  kokoro-tts-webui

echo "Web UI is available at http://localhost:5001"
echo "To debug audio files, you can run: docker exec -it \$(docker ps -q -f ancestor=kokoro-tts-webui) python /app/debug_audio.py --dir /app/output"