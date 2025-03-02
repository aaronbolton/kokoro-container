#!/usr/bin/env python3

import os
import sys
import numpy as np
import soundfile as sf
import argparse
import wave

def analyze_audio_file(file_path):
    """Analyze an audio file and print detailed information about it."""
    print(f"\n=== Analyzing audio file: {file_path} ===")
    
    if not os.path.exists(file_path):
        print(f"ERROR: File does not exist: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")
    
    if file_size == 0:
        print("ERROR: File is empty")
        return False
    
    try:
        # Try to read with soundfile first
        print("\n--- SoundFile Analysis ---")
        try:
            data, samplerate = sf.read(file_path)
            print(f"Sample rate: {samplerate} Hz")
            print(f"Duration: {len(data) / samplerate:.2f} seconds")
            print(f"Channels: {1 if len(data.shape) == 1 else data.shape[1]}")
            print(f"Data shape: {data.shape}")
            print(f"Data type: {data.dtype}")
            print(f"Min value: {data.min()}")
            print(f"Max value: {data.max()}")
            print(f"Mean value: {data.mean()}")
            print(f"RMS value: {np.sqrt(np.mean(data**2))}")
            
            # Check if audio is silent
            if np.abs(data).max() < 0.01:
                print("WARNING: Audio appears to be silent or nearly silent!")
            
            # Plot histogram of values
            hist, bins = np.histogram(data, bins=10)
            print("\nValue distribution:")
            for i in range(len(hist)):
                print(f"  {bins[i]:.3f} to {bins[i+1]:.3f}: {hist[i]} samples")
                
        except Exception as e:
            print(f"SoundFile error: {type(e).__name__}: {e}")
        
        # Also try with wave module for more details
        print("\n--- Wave Module Analysis ---")
        try:
            with wave.open(file_path, 'rb') as wav:
                n_channels = wav.getnchannels()
                sampwidth = wav.getsampwidth()
                framerate = wav.getframerate()
                n_frames = wav.getnframes()
                comp_type = wav.getcomptype()
                comp_name = wav.getcompname()
                
                print(f"Number of channels: {n_channels}")
                print(f"Sample width: {sampwidth} bytes")
                print(f"Frame rate: {framerate} Hz")
                print(f"Number of frames: {n_frames}")
                print(f"Compression type: {comp_type}")
                print(f"Compression name: {comp_name}")
                print(f"Duration: {n_frames / framerate:.2f} seconds")
                
                # Read a small sample of frames
                wav.rewind()
                sample_frames = wav.readframes(min(1000, n_frames))
                print(f"First {min(1000, n_frames)} frames byte length: {len(sample_frames)}")
                if len(sample_frames) > 0:
                    print(f"First few bytes: {sample_frames[:20]}")
                else:
                    print("No frames read!")
                    
        except Exception as e:
            print(f"Wave module error: {type(e).__name__}: {e}")
        
        return True
    except Exception as e:
        print(f"Error analyzing file: {type(e).__name__}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Debug audio files')
    parser.add_argument('--dir', type=str, help='Directory containing audio files to analyze')
    parser.add_argument('--file', type=str, help='Specific audio file to analyze')
    parser.add_argument('--create-test', action='store_true', help='Create a test audio file')
    parser.add_argument('--output', type=str, default='test_audio.wav', help='Output path for test audio file')
    
    args = parser.parse_args()
    
    if args.create_test:
        create_test_audio(args.output)
        analyze_audio_file(args.output)
        return
    
    if args.file:
        analyze_audio_file(args.file)
        return
    
    if args.dir:
        if not os.path.exists(args.dir):
            print(f"Directory does not exist: {args.dir}")
            return
        
        audio_files = []
        for root, _, files in os.walk(args.dir):
            for file in files:
                if file.endswith('.wav'):
                    audio_files.append(os.path.join(root, file))
        
        if not audio_files:
            print(f"No .wav files found in {args.dir}")
            return
        
        print(f"Found {len(audio_files)} .wav files")
        for file in audio_files:
            analyze_audio_file(file)
        
        return
    
    print("Please specify either --dir, --file, or --create-test")

def create_test_audio(output_path):
    """Create a test audio file with a simple sine wave."""
    print(f"Creating test audio file: {output_path}")
    
    # Parameters
    sample_rate = 24000
    duration = 2.0  # seconds
    frequency = 440.0  # Hz (A4 note)
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Add fade in/out
    fade_samples = int(0.1 * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    audio[:fade_samples] *= fade_in
    audio[-fade_samples:] *= fade_out
    
    # Save as WAV file
    sf.write(output_path, audio, sample_rate)
    print(f"Created test audio file: {output_path}")

if __name__ == "__main__":
    main()