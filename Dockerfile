# Use Python 3.10 as the base image
FROM python:3.10

# Add metadata
LABEL maintainer="Kokoro TTS"
LABEL version="1.0"
LABEL description="Kokoro Text-to-Speech System Docker Image"

# Set working directory
WORKDIR /app

# Copy the example script and requirements
COPY example.txt /app/
COPY kokoro_tts.py /app/
COPY requirements.txt /app/

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libsndfile1 \
    build-essential \
    espeak-ng \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy soundfile scipy && \
    pip install --no-cache-dir -q git+https://github.com/hexgrad/kokoro.git && \
    pip install --no-cache-dir -q misaki[ja] misaki[zh]

# Create directories for input and output
RUN mkdir -p /input /output && \
    chmod 777 /input /output

# Set volumes for input and output
VOLUME ["/input", "/output"]

# Set the entrypoint to run the Kokoro TTS script
ENTRYPOINT ["python", "/app/kokoro_tts.py"]

# Default command if no arguments are provided
CMD ["--help"]