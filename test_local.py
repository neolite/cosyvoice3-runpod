#!/usr/bin/env python3
"""
Local test script for CosyVoice3 RunPod handler
Run the container first, then execute this script
"""

import requests
import base64
import sys

LOCAL_URL = "http://localhost:8000/runsync"

def test_zero_shot():
    """Test zero-shot synthesis with default voice"""
    print("Testing zero-shot mode...")

    response = requests.post(LOCAL_URL, json={
        "input": {
            "text": "Hello! This is a test of CosyVoice3 text to speech synthesis.",
            "mode": "zero_shot"
        }
    }, timeout=120)

    save_result(response, "test_zero_shot.wav")


def test_chinese():
    """Test Chinese synthesis"""
    print("Testing Chinese...")

    response = requests.post(LOCAL_URL, json={
        "input": {
            "text": "你好，这是CosyVoice3语音合成测试。",
            "mode": "zero_shot"
        }
    }, timeout=120)

    save_result(response, "test_chinese.wav")


def test_instruct():
    """Test instruct mode with speed control"""
    print("Testing instruct mode (fast speech)...")

    response = requests.post(LOCAL_URL, json={
        "input": {
            "text": "这是一段快速语音测试。",
            "mode": "instruct",
            "instruct": "You are a helpful assistant. 请用尽可能快地语速说。<|endofprompt|>"
        }
    }, timeout=120)

    save_result(response, "test_instruct.wav")


def test_with_voice(audio_path: str, text: str):
    """Test voice cloning with custom audio"""
    print(f"Testing voice cloning with {audio_path}...")

    with open(audio_path, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()

    response = requests.post(LOCAL_URL, json={
        "input": {
            "text": text,
            "mode": "zero_shot",
            "prompt_audio_base64": audio_base64,
            "prompt_text": "You are a helpful assistant.<|endofprompt|>"
        }
    }, timeout=120)

    save_result(response, "test_cloned.wav")


def save_result(response, filename):
    """Save API response to WAV file"""
    try:
        result = response.json()

        if "output" in result:
            output = result["output"]
            if "audio_base64" in output:
                audio_bytes = base64.b64decode(output["audio_base64"])
                with open(filename, "wb") as f:
                    f.write(audio_bytes)
                print(f"  ✓ Saved: {filename}")
                return
            elif "error" in output:
                print(f"  ✗ Error: {output['error']}")
                return

        print(f"  ✗ Unexpected response: {result}")

    except Exception as e:
        print(f"  ✗ Exception: {e}")
        print(f"    Response: {response.text[:500]}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Voice cloning mode
        audio_path = sys.argv[1]
        text = sys.argv[2] if len(sys.argv) > 2 else "This is a voice cloning test."
        test_with_voice(audio_path, text)
    else:
        # Run all tests
        test_zero_shot()
        test_chinese()
        test_instruct()

        print("\nDone! Check the generated WAV files.")
