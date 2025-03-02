#!/bin/bash

# Ensure directories exist
mkdir -p input output templates static/css static/js

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Flask if not already installed
if ! python -c "import flask" &> /dev/null; then
    echo "Installing Flask..."
    pip install flask
fi

# Run the Flask application
echo "Starting Kokoro TTS Web UI..."
echo "Open your browser and navigate to http://localhost:5001"
python app.py

# Deactivate virtual environment when done
deactivate