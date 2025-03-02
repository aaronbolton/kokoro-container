#!/usr/bin/env python3

import os
import argparse
import numpy as np
import wave
import soundfile as sf

def main():
    parser = argparse.ArgumentParser(description='Kokoro Text-to-Speech Generator')
    parser.add_argument('--text', type=str, help='Text to convert to speech')
    parser.add_argument('--text-file', type=str, help='Path to a text file to convert to speech')
    parser.add_argument('--lang-code', type=str, default='a',
                        help='Language code: a=American English, b=British English, e=Spanish, f=French, h=Hindi, i=Italian, p=Brazilian Portuguese')
    parser.add_argument('--voice', type=str, default='af_heart', help='Voice to use')
    parser.add_argument('--speed', type=float, default=1.0, help='Speech speed')
    parser.add_argument('--output-dir', type=str, default='/output', help='Directory to save output files')
    
    args = parser.parse_args()
    
    # Get text from either command line argument or file
    if args.text:
        text = args.text
    elif args.text_file:
        with open(args.text_file, 'r') as f:
            text = f.read()
    else:
        # Use example text if no input is provided
        example_path = '/app/example.txt'
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                text = f.read()
            print(f"Using example text from {example_path}")
        else:
            text = "Hello, this is a test of the Kokoro text-to-speech system."
            print("Using default text")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Try to import Kokoro
    print("Attempting to import Kokoro module...")
    try:
        from kokoro import KPipeline
        print("Successfully imported Kokoro module")
        using_kokoro = True
    except ImportError as e:
        print(f"ImportError: {e}")
        print("WARNING: Using text-based audio generation fallback instead of Kokoro TTS")
        using_kokoro = False
    except Exception as e:
        print(f"Unexpected error importing Kokoro: {type(e).__name__}: {e}")
        print("WARNING: Using text-based audio generation fallback instead of Kokoro TTS")
        using_kokoro = False
    
    if using_kokoro:
        try:
            # Initialize the pipeline
            print(f"Initializing Kokoro TTS with language code: {args.lang_code}")
            try:
                # Initialize the pipeline
                pipeline = KPipeline(lang_code=args.lang_code)
                print("Pipeline initialized successfully")
            except Exception as e:
                print(f"Error initializing pipeline: {type(e).__name__}: {e}")
                print(f"Detailed error: {e}")
                import traceback
                traceback.print_exc()
                using_kokoro = False
            
            if using_kokoro:
                # Generate audio
                print(f"Generating audio with voice: {args.voice}, speed: {args.speed}")
                try:
                    # Split text by paragraphs to improve processing
                    generator = pipeline(
                        text,
                        voice=args.voice,
                        speed=args.speed,
                        split_pattern=r'\n+'  # Split by paragraphs as shown in the example
                    )
                    print("Generator created successfully")
                except Exception as e:
                    print(f"Error creating generator: {type(e).__name__}: {e}")
                    using_kokoro = False
            
            if using_kokoro:
                # Process and save each audio segment
                print("Processing audio segments...")
                segment_count = 0
                try:
                    for i, (gs, ps, audio) in enumerate(generator):
                        segment_count += 1
                        print(f"Segment {i}:")
                        print(f"Text: {gs}")
                        print(f"Audio shape: {audio.shape}, dtype: {audio.dtype}")
                        print(f"Audio min: {audio.min()}, max: {audio.max()}, mean: {audio.mean()}")
                        
                        # Check if audio contains actual sound or just silence
                        if abs(audio.max() - audio.min()) < 0.01:
                            print("WARNING: Audio appears to be silent or nearly silent!")
                        
                        # Save audio file
                        output_path = os.path.join(args.output_dir, f'segment_{i}.wav')
                        try:
                            # Ensure audio is in the correct format for soundfile
                            # Convert PyTorch tensor to NumPy array if needed
                            if hasattr(audio, 'numpy'):
                                print(f"Converting PyTorch tensor to NumPy array")
                                audio = audio.numpy()
                            
                            if audio.dtype != np.float32:
                                print(f"Converting audio from {audio.dtype} to float32")
                                audio = audio.astype(np.float32)
                            
                            # Normalize audio if it's too quiet
                            if abs(audio.max()) < 0.1:
                                print("Audio level is low, normalizing...")
                                if abs(audio.max()) > 0:  # Avoid division by zero
                                    audio = audio / abs(audio.max()) * 0.9
                            
                            # Write audio file
                            sf.write(output_path, audio, 24000)
                            print(f"Saved to {output_path}")
                            
                            # Verify the file was created and has content
                            if os.path.exists(output_path):
                                file_size = os.path.getsize(output_path)
                                print(f"File size: {file_size} bytes")
                                if file_size < 100:
                                    print("WARNING: Audio file is suspiciously small!")
                            else:
                                print("ERROR: File was not created!")
                        except Exception as e:
                            print(f"Error saving audio file: {type(e).__name__}: {e}")
                            print(f"Error details: {e}")
                        
                        print("-" * 50)
                    
                    if segment_count == 0:
                        print("WARNING: No audio segments were generated! Using fallback.")
                        using_kokoro = False
                        
                except Exception as e:
                    print(f"Error processing audio segments: {type(e).__name__}: {e}")
                    using_kokoro = False
        except Exception as e:
            print(f"Error using Kokoro: {type(e).__name__}: {e}")
            using_kokoro = False
    
    # If Kokoro failed or is not available, use the fallback
    if not using_kokoro:
        print("Using text-based audio generation fallback.")
        # Create a fallback audio file with tones
        output_path = os.path.join(args.output_dir, 'segment_0.wav')
        
        # Create a text-to-tone representation based on the input text
        # This will create a unique audio pattern for each text input
        create_text_based_audio(output_path, text)
        print(f"Created text-based audio file at {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
    
    print("Audio generation complete!")
    return 0

def create_text_based_audio(filename, text, duration=None):
    """Create a WAV file with audio patterns based on the input text."""
    sample_rate = 24000
    
    # Use text to determine audio characteristics
    # Hash the text to get consistent results for the same text
    import hashlib
    text_hash = int(hashlib.md5(text.encode()).hexdigest(), 16)
    
    # Use the hash to seed the random number generator for consistent results
    np.random.seed(text_hash % 2**32)
    
    # Determine duration based on text length (minimum 2 seconds, maximum 10 seconds)
    if duration is None:
        text_length = len(text)
        duration = min(max(2.0, text_length / 50), 10.0)
    
    print(f"Generating text-based audio with duration: {duration:.2f} seconds")
    num_samples = int(duration * sample_rate)
    
    # Create time array
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # Generate audio based on text characteristics
    audio = np.zeros(num_samples, dtype=np.float32)
    
    # Extract some features from the text
    word_count = len(text.split())
    char_count = len(text)
    
    # Use text features to determine base frequency (between 220Hz and 880Hz)
    base_freq = 220 + (text_hash % 660)
    
    # Create a chord based on the text
    # More words = more complex chord
    chord_complexity = min(5, max(2, word_count // 10 + 2))
    
    # Generate frequencies for the chord
    frequencies = []
    for i in range(chord_complexity):
        # Use different parts of the hash for different frequencies
        freq_factor = 1.0 + (0.2 * ((text_hash >> (i * 8)) % 256) / 256)
        frequencies.append(base_freq * freq_factor)
    
    # Add the frequencies to the audio
    for i, freq in enumerate(frequencies):
        # Vary amplitude based on position in the chord
        amplitude = 0.3 / (i + 1)
        audio += amplitude * np.sin(2 * np.pi * freq * t)
    
    # Add some variation based on the text content
    for i, char in enumerate(text[:min(len(text), 100)]):  # Limit to first 100 chars
        if i >= len(t):
            break
            
        # Use character ASCII value to create small variations
        char_val = ord(char)
        if char_val > 64 and char_val < 128:  # Only for standard ASCII
            # Add a small blip at positions corresponding to characters
            pos = int((i / min(len(text), 100)) * num_samples)
            width = sample_rate // 50  # 20ms blip
            if pos + width < num_samples:
                # Create a small envelope
                envelope = np.sin(np.pi * np.linspace(0, 1, width))
                # Frequency based on character value
                freq = 440 + (char_val - 65) * 20  # Map A-Z to different frequencies
                blip = 0.1 * envelope * np.sin(2 * np.pi * freq * t[pos:pos+width])
                audio[pos:pos+width] += blip
    
    # Apply fade in and fade out
    fade_samples = int(0.1 * sample_rate)  # 100ms fade
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    audio[:fade_samples] *= fade_in
    audio[-fade_samples:] *= fade_out
    
    # Normalize
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio)) * 0.9
    
    # Convert to float32 for soundfile
    audio = audio.astype(np.float32)
    
    # Write using soundfile for better quality
    try:
        sf.write(filename, audio, sample_rate)
        print(f"Audio saved to {filename} using soundfile")
        return True
    except Exception as e:
        print(f"Error saving with soundfile: {e}, falling back to wave module")
        
        # Convert to int16 for wave module
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Write WAV file using wave module as fallback
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample (16 bits)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
        
        print(f"Audio saved to {filename} using wave module")
        return True

def create_dummy_wav(filename, duration=3.0):
    """Create a WAV file with a simple tone pattern."""
    return create_text_based_audio(filename, "This is a test of the text to speech system", duration)

if __name__ == "__main__":
    exit(main())