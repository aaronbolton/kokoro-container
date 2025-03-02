#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t kokoro-tts .

# Create input and output directories if they don't exist
mkdir -p input output

# Copy example text file to input directory
cp example.txt input/

# Run the Docker container with the example text file
echo "Running Kokoro TTS with example text..."
docker run --rm -v "$(pwd)/input:/input" -v "$(pwd)/output:/output" kokoro-tts --text-file /input/example.txt

# Check if any audio files were generated
echo "Checking generated audio files..."
if [ -z "$(find output -name '*.wav' -type f)" ]; then
  echo "WARNING: No audio files were generated!"
else
  echo "Audio files were generated. Analyzing..."
  # Copy debug script to the container and run it
  docker run --rm -v "$(pwd)/debug_audio.py:/app/debug_audio.py" -v "$(pwd)/output:/output" kokoro-tts python /app/debug_audio.py --dir /output
fi

echo "Done! Check the output directory for generated audio files."