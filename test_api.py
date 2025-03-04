#!/usr/bin/env python3

import requests
import json
import os
import time
import argparse

# Default API URL
API_URL = "http://localhost:5002"
API_KEY = os.getenv('KOKORO_API_KEY', 'your-secret-key-here')

def test_health_check(api_url):
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{api_url}/v1/audio/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_list_models(api_url):
    """Test the list models endpoint"""
    print("\n=== Testing List Models ===")
    response = requests.get(f"{api_url}/v1/audio/speech/models")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_list_voices(api_url):
    """Test the list voices endpoint"""
    print("\n=== Testing List Voices ===")
    response = requests.get(f"{api_url}/v1/audio/speech/voices")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_speech_generation(api_url, api_key, voice, model, output_file):
    """Test speech generation"""
    print(f"\n=== Testing Speech Generation (Voice: {voice}, Model: {model}) ===")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "input": "Hello, this is a test of the Kokoro text-to-speech API. Is it working correctly?",
        "voice": voice,
        "response_format": "mp3",
        "speed": 1.0
    }
    
    start_time = time.time()
    response = requests.post(
        f"{api_url}/v1/audio/speech",
        headers=headers,
        json=data
    )
    end_time = time.time()
    
    print(f"Status Code: {response.status_code}")
    print(f"Generation Time: {end_time - start_time:.2f} seconds")
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Audio saved to {output_file}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test the Kokoro TTS API')
    parser.add_argument('--api-url', default=API_URL, help='API URL')
    parser.add_argument('--api-key', default=API_KEY, help='API Key')
    parser.add_argument('--voice', default='alloy', help='Voice to test')
    parser.add_argument('--model', default='tts-1', help='Model to test')
    parser.add_argument('--output', default='test_output.mp3', help='Output file')
    
    args = parser.parse_args()
    
    # Run tests
    health_ok = test_health_check(args.api_url)
    models_ok = test_list_models(args.api_url)
    voices_ok = test_list_voices(args.api_url)
    
    if health_ok and models_ok and voices_ok:
        speech_ok = test_speech_generation(
            args.api_url, 
            args.api_key, 
            args.voice, 
            args.model, 
            args.output
        )
        
        if speech_ok:
            print("\n✅ All tests passed successfully!")
        else:
            print("\n❌ Speech generation test failed!")
    else:
        print("\n❌ API endpoint tests failed!")

if __name__ == "__main__":
    main()