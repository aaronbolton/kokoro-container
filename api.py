from flask import Flask, request, jsonify, send_file
import os
import tempfile
import hashlib
from functools import wraps
import soundfile as sf
import numpy as np
from kokoro_tts import create_text_based_audio

app = Flask(__name__)

# Configure this with your desired API key
API_KEY = os.getenv('KOKORO_API_KEY', 'your-secret-key-here')

# Voice mapping from OpenAI to Kokoro voices
VOICE_MAPPING = {
    'alloy': 'af_alloy',    # American female alloy
    'echo': 'am_echo',      # American male echo
    'fable': 'bf_fable',    # British female fable
    'onyx': 'am_onyx',      # American male onyx
    'nova': 'af_nova',      # American female nova
    'shimmer': 'af_shimmer' # American female shimmer
}

# Model mapping from OpenAI to Kokoro language codes
MODEL_MAPPING = {
    'tts-1': 'a',      # American English
    'tts-1-hd': 'a',   # American English HD
    'tts-1-en-gb': 'b', # British English
    'tts-1-hd-en-gb': 'b' # British English HD
}

# Try to import Kokoro for direct TTS
try:
    from kokoro import KPipeline
    KOKORO_AVAILABLE = True
    print("Kokoro TTS module loaded successfully")
except ImportError:
    KOKORO_AVAILABLE = False
    print("Kokoro TTS module not available, using fallback")

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid API key'}), 401
        
        api_key = auth_header.split(' ')[1]
        if api_key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/v1/audio/speech', methods=['POST'])
@require_api_key
def create_speech():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('input'):
            return jsonify({'error': 'input field is required'}), 400
        
        # Get parameters with defaults
        text = data['input']
        voice = VOICE_MAPPING.get(data.get('voice', 'alloy'), 'af_alloy')
        model = MODEL_MAPPING.get(data.get('model', 'tts-1'), 'a')
        speed = float(data.get('speed', 1.0))
        response_format = data.get('response_format', 'mp3')
        
        # Validate speed
        if not 0.25 <= speed <= 4.0:
            return jsonify({'error': 'speed must be between 0.25 and 4.0'}), 400
            
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_path = temp_wav.name
        
        success = False
        
        # Try to use Kokoro TTS directly if available
        if KOKORO_AVAILABLE:
            try:
                # Initialize the pipeline with the appropriate language model
                pipeline = KPipeline(lang_code=model)
                
                # Generate audio with the specified voice and speed
                generator = pipeline(
                    text,
                    voice=voice,
                    speed=speed,
                    split_pattern=r'\n+'
                )
                
                # Process audio segments
                all_audio = []
                sample_rate = 24000
                
                for _, _, audio in generator:
                    # Convert PyTorch tensor to NumPy array if needed
                    if hasattr(audio, 'numpy'):
                        audio = audio.numpy()
                    
                    if audio.dtype != np.float32:
                        audio = audio.astype(np.float32)
                    
                    all_audio.append(audio)
                
                if all_audio:
                    # Concatenate all audio segments
                    combined_audio = np.concatenate(all_audio)
                    
                    # Normalize
                    if np.max(np.abs(combined_audio)) > 0:
                        combined_audio = combined_audio / np.max(np.abs(combined_audio)) * 0.9
                    
                    # Save the combined audio
                    sf.write(temp_path, combined_audio, sample_rate)
                    success = True
            except Exception as e:
                print(f"Error using Kokoro TTS: {str(e)}")
                # Fall back to text-based audio generation
        
        # If Kokoro TTS failed or is not available, use the fallback
        if not success:
            success = create_text_based_audio(temp_path, text, duration=None)
        
        if not success:
            return jsonify({'error': 'Failed to generate audio'}), 500
            
        # Convert to requested format if needed
        if response_format != 'wav':
            try:
                import pydub
                audio = pydub.AudioSegment.from_wav(temp_path)
                
                with tempfile.NamedTemporaryFile(suffix=f'.{response_format}', delete=False) as temp_out:
                    output_path = temp_out.name
                    
                export_format = {
                    'mp3': 'mp3',
                    'opus': 'ogg',
                    'aac': 'adts',
                    'flac': 'flac'
                }.get(response_format)
                
                audio.export(output_path, format=export_format)
                os.unlink(temp_path)  # Remove WAV file
                temp_path = output_path
                
            except ImportError:
                # Fallback to WAV if pydub not available
                response_format = 'wav'
        
        # Send the file
        return send_file(
            temp_path,
            mimetype={
                'mp3': 'audio/mpeg',
                'opus': 'audio/ogg',
                'aac': 'audio/aac',
                'flac': 'audio/flac',
                'wav': 'audio/wav'
            }.get(response_format, 'audio/wav'),
            as_attachment=True,
            download_name=f'speech.{response_format}'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Cleanup temporary files
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass

# List available models endpoint (compatible with OpenAI API)
@app.route('/v1/audio/speech/models', methods=['GET'])
def list_models():
    models = [
        {
            "model_id": "tts-1",
            "name": "TTS-1",
            "description": "Standard American English TTS model",
            "kokoro_lang_code": MODEL_MAPPING["tts-1"]
        },
        {
            "model_id": "tts-1-hd",
            "name": "TTS-1-HD",
            "description": "High-definition American English TTS model",
            "kokoro_lang_code": MODEL_MAPPING["tts-1-hd"]
        },
        {
            "model_id": "tts-1-en-gb",
            "name": "TTS-1-EN-GB",
            "description": "Standard British English TTS model",
            "kokoro_lang_code": MODEL_MAPPING["tts-1-en-gb"]
        },
        {
            "model_id": "tts-1-hd-en-gb",
            "name": "TTS-1-HD-EN-GB",
            "description": "High-definition British English TTS model",
            "kokoro_lang_code": MODEL_MAPPING["tts-1-hd-en-gb"]
        }
    ]
    
    return jsonify({"models": models})

# List available voices endpoint (compatible with OpenAI API)
@app.route('/v1/audio/speech/voices', methods=['GET'])
def list_voices():
    voices = [
        {
            "voice_id": "alloy",
            "name": "Alloy",
            "description": "American female voice with a natural and versatile tone",
            "preview_url": None,
            "kokoro_voice": VOICE_MAPPING["alloy"]
        },
        {
            "voice_id": "echo",
            "name": "Echo",
            "description": "American male voice with a natural and versatile tone",
            "preview_url": None,
            "kokoro_voice": VOICE_MAPPING["echo"]
        },
        {
            "voice_id": "fable",
            "name": "Fable",
            "description": "British female voice with a natural and versatile tone",
            "preview_url": None,
            "kokoro_voice": VOICE_MAPPING["fable"]
        },
        {
            "voice_id": "onyx",
            "name": "Onyx",
            "description": "American male voice with a deep and authoritative tone",
            "preview_url": None,
            "kokoro_voice": VOICE_MAPPING["onyx"]
        },
        {
            "voice_id": "nova",
            "name": "Nova",
            "description": "American female voice with a natural and versatile tone",
            "preview_url": None,
            "kokoro_voice": VOICE_MAPPING["nova"]
        },
        {
            "voice_id": "shimmer",
            "name": "Shimmer",
            "description": "American female voice with a bright and melodic tone",
            "preview_url": None,
            "kokoro_voice": VOICE_MAPPING["shimmer"]
        }
    ]
    
    return jsonify({"voices": voices})

# Health check endpoint
@app.route('/v1/audio/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'kokoro-tts-api',
        'kokoro_available': KOKORO_AVAILABLE
    })

if __name__ == '__main__':
    # Add these to requirements.txt:
    # flask
    # pydub (optional, for format conversion)
    app.run(host='0.0.0.0', port=5002)