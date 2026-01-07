#!/usr/bin/env python3
"""
CosyVoice3 RunPod API Test Script

Usage:
    python test_api.py "Hello world"
    python test_api.py "Привет мир" --mode instruct --instruct "говори медленно"
    python test_api.py "你好" --mode instruct --instruct "请用广东话表达"
"""

import requests
import base64
import sys
import os
import argparse
import time
from datetime import datetime

ENDPOINT_ID = os.environ.get("RUNPOD_ENDPOINT_ID", "YOUR_ENDPOINT_ID")
API_KEY = os.environ.get("RUNPOD_API_KEY", "YOUR_API_KEY")
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"


def generate_speech(
    text: str,
    mode: str = "zero_shot",
    instruct: str = None,
    prompt_text: str = None,
    voice_sample: str = None,
    output_file: str = None
):
    """Generate speech from text using CosyVoice3 API"""

    print(f"📝 Text: {text}")
    print(f"🎯 Mode: {mode}")
    if instruct:
        print(f"💬 Instruct: {instruct}")
    if voice_sample:
        print(f"🎤 Voice sample: {voice_sample}")
    print("📤 Submitting job...")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Build payload
    payload = {
        "input": {
            "text": text,
            "mode": mode
        }
    }

    if instruct:
        payload["input"]["instruct"] = f"You are a helpful assistant. {instruct}<|endofprompt|>"

    if prompt_text:
        payload["input"]["prompt_text"] = f"You are a helpful assistant.<|endofprompt|>{prompt_text}"

    # Voice cloning - load audio file
    if voice_sample:
        with open(voice_sample, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        payload["input"]["prompt_audio_base64"] = audio_b64

    # Submit job
    response = requests.post(
        f"{BASE_URL}/run",
        headers=headers,
        json=payload,
        timeout=30
    )

    result = response.json()
    job_id = result.get("id")

    if not job_id:
        print(f"❌ Error submitting job: {result}")
        return None

    print(f"🆔 Job ID: {job_id}")

    # Poll for status
    while True:
        response = requests.get(
            f"{BASE_URL}/status/{job_id}",
            headers=headers,
            timeout=30
        )
        result = response.json()
        status = result.get("status")

        if status == "IN_QUEUE":
            print("⏳ In queue (worker starting)...")
            time.sleep(5)
        elif status == "IN_PROGRESS":
            print("🔄 In progress...")
            time.sleep(2)
        elif status == "COMPLETED":
            print("✅ Completed!")
            break
        elif status == "FAILED":
            print(f"❌ Failed: {result.get('error')}")
            return None
        else:
            print(f"⏳ Status: {status}")
            time.sleep(3)

    output = result.get("output", {})

    if "error" in output:
        print(f"❌ Error: {output['error']}")
        return None

    if "audio_base64" not in output:
        print(f"❌ Unexpected response: {result}")
        return None

    # Decode audio
    audio_bytes = base64.b64decode(output["audio_base64"])

    # Generate filename
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output_{timestamp}.wav"

    # Save file
    with open(output_file, "wb") as f:
        f.write(audio_bytes)

    print(f"💾 Saved: {output_file}")
    print(f"🎵 Sample rate: {output.get('sample_rate', 'unknown')} Hz")
    print(f"📦 Size: {len(audio_bytes) / 1024:.1f} KB")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="CosyVoice3 Text-to-Speech API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_api.py "Hello world"
  python test_api.py "Привет мир"
  python test_api.py "说话快一点" --mode instruct --instruct "请用尽可能快地语速说"
  python test_api.py "你好" --mode instruct --instruct "请用广东话表达"
  python test_api.py "Hello" -o my_audio.wav
        """
    )

    parser.add_argument("text", nargs="?", default="Привет! Это тест голосового синтеза.", help="Text to synthesize")
    parser.add_argument("--mode", "-m", choices=["zero_shot", "cross_lingual", "instruct"], default="zero_shot", help="Synthesis mode")
    parser.add_argument("--instruct", "-i", help="Instruction for instruct mode (dialect, speed, style)")
    parser.add_argument("--voice", "-v", help="Path to voice sample WAV file (3-10 sec) for cloning")
    parser.add_argument("--prompt-text", "-p", help="Transcript of the voice sample (improves quality)")
    parser.add_argument("--output", "-o", help="Output WAV filename")

    args = parser.parse_args()

    # Auto-switch to instruct mode if instruct is provided
    mode = args.mode
    if args.instruct and mode == "zero_shot":
        mode = "instruct"

    generate_speech(
        text=args.text,
        mode=mode,
        instruct=args.instruct,
        voice_sample=args.voice,
        prompt_text=args.prompt_text,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
