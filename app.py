import os
import subprocess
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder='static')

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_audio():
    data = request.form
    
    # Generate a unique session ID for this request
    session_id = str(uuid.uuid4())
    session_output_dir = os.path.join('output', session_id)
    os.makedirs(session_output_dir, exist_ok=True)
    
    # Build command
    cmd = ['python3', 'kokoro_tts.py']
    
    # Handle text input
    if data.get('inputType') == 'text' and data.get('text'):
        cmd.extend(['--text', data.get('text')])
    elif data.get('inputType') == 'file' and request.files.get('textFile'):
        # Save uploaded file
        file_path = os.path.join('input', f"{session_id}.txt")
        os.makedirs('input', exist_ok=True)
        request.files['textFile'].save(file_path)
        cmd.extend(['--text-file', file_path])
    
    # Add other parameters
    if data.get('langCode'):
        cmd.extend(['--lang-code', data.get('langCode')])
    
    if data.get('voice'):
        cmd.extend(['--voice', data.get('voice')])
    
    if data.get('speed'):
        cmd.extend(['--speed', data.get('speed')])
    
    # Set output directory to the session-specific directory
    cmd.extend(['--output-dir', session_output_dir])
    
    # Execute command
    try:
        print(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"Command exit code: {result.returncode}")
        print(f"Command stdout: {result.stdout}")
        print(f"Command stderr: {result.stderr}")
        
        # Get list of generated files
        generated_files = []
        if os.path.exists(session_output_dir):
            print(f"Checking output directory: {session_output_dir}")
            for file in os.listdir(session_output_dir):
                if file.endswith('.wav'):
                    file_path = os.path.join(session_output_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"Found WAV file: {file}, size: {file_size} bytes")
                    generated_files.append(file)
            
            if not generated_files:
                print(f"No WAV files found in {session_output_dir}")
        else:
            print(f"Output directory does not exist: {session_output_dir}")
        
        response_data = {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'session_id': session_id,
            'files': generated_files,
            'command': ' '.join(cmd)  # Include the command for debugging
        }
        
        print(f"Sending response: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'command': ' '.join(cmd) if 'cmd' in locals() else 'Command not defined'
        })

@app.route('/output/<session_id>/<filename>')
def serve_audio(session_id, filename):
    return send_from_directory(os.path.join('output', session_id), filename)

@app.route('/output/<session_id>')
def list_session_files(session_id):
    session_dir = os.path.join('output', session_id)
    if not os.path.exists(session_dir):
        return jsonify({'files': []})
    
    files = [f for f in os.listdir(session_dir) if f.endswith('.wav')]
    return jsonify({'files': files})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)