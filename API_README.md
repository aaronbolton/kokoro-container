# Kokoro TTS API

This API provides a compatible interface with OpenAI's Text-to-Speech (TTS) API, allowing you to use Kokoro's TTS capabilities with the same API format as OpenAI.

## Features

- Compatible with OpenAI's TTS API endpoints
- Supports multiple voices and models
- Fallback to text-based audio generation when Kokoro TTS is not available
- Supports various audio formats (mp3, opus, aac, flac, wav)

## API Endpoints

### Generate Speech

```
POST /v1/audio/speech
```

Generate audio from text input.

**Request Headers:**
- `Authorization: Bearer YOUR_API_KEY`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "model": "tts-1",
  "input": "Your text to convert to speech",
  "voice": "alloy",
  "response_format": "mp3",
  "speed": 1.0
}
```

**Parameters:**
- `model` (string, required): The TTS model to use. Options: `tts-1`, `tts-1-hd`, `tts-1-en-gb`, `tts-1-hd-en-gb`
- `input` (string, required): The text to convert to speech (max 4096 characters)
- `voice` (string, required): The voice to use. Options: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- `response_format` (string, optional): The format of the audio response. Options: `mp3` (default), `opus`, `aac`, `flac`, `wav`
- `speed` (float, optional): The speed of the generated audio. Range: 0.25 to 4.0. Default: 1.0

**Response:**
- Audio file in the requested format

### List Available Voices

```
GET /v1/audio/speech/voices
```

List all available voices.

**Response:**
```json
{
  "voices": [
    {
      "voice_id": "alloy",
      "name": "Alloy",
      "description": "American female voice with a natural and versatile tone",
      "preview_url": null,
      "kokoro_voice": "af_alloy"
    },
    ...
  ]
}
```

### List Available Models

```
GET /v1/audio/speech/models
```

List all available TTS models.

**Response:**
```json
{
  "models": [
    {
      "model_id": "tts-1",
      "name": "TTS-1",
      "description": "Standard American English TTS model",
      "kokoro_lang_code": "a"
    },
    ...
  ]
}
```

### Health Check

```
GET /v1/audio/health
```

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "kokoro-tts-api",
  "kokoro_available": true
}
```

## Voice Mapping

The API maps OpenAI voices to Kokoro voices as follows:

| OpenAI Voice | Kokoro Voice | Description |
|--------------|--------------|-------------|
| alloy        | af_alloy     | American female alloy |
| echo         | am_echo      | American male echo |
| fable        | bf_fable     | British female fable |
| onyx         | am_onyx      | American male onyx |
| nova         | af_nova      | American female nova |
| shimmer      | af_shimmer   | American female shimmer |

## Model Mapping

The API maps OpenAI models to Kokoro language codes as follows:

| OpenAI Model    | Kokoro Language Code | Description |
|-----------------|---------------------|-------------|
| tts-1           | a                   | American English |
| tts-1-hd        | a                   | American English HD |
| tts-1-en-gb     | b                   | British English |
| tts-1-hd-en-gb  | b                   | British English HD |

## Running the API

```bash
# Set your API key
export KOKORO_API_KEY="your-secret-key-here"

# Run the API
python api.py
```

The API will be available at `http://localhost:5000`.

## Testing the API

A test script is provided to verify that the API is working correctly:

```bash
# Run the test script
python test_api.py --api-key "your-secret-key-here"
```

This will test all endpoints and generate a sample audio file.

## Requirements

- Flask
- pydub (optional, for format conversion)
- Kokoro TTS (optional, will fall back to text-based audio generation if not available)