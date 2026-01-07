#!/usr/bin/env python3
"""
Download CosyVoice3 models from HuggingFace
Run this during Docker build or separately to cache models
"""

from huggingface_hub import snapshot_download
import os

def main():
    print("Downloading Fun-CosyVoice3-0.5B model...")
    snapshot_download(
        'FunAudioLLM/Fun-CosyVoice3-0.5B-2512',
        local_dir='pretrained_models/Fun-CosyVoice3-0.5B'
    )
    print("✓ Fun-CosyVoice3-0.5B downloaded")

    print("Downloading CosyVoice-ttsfrd (text frontend)...")
    snapshot_download(
        'FunAudioLLM/CosyVoice-ttsfrd',
        local_dir='pretrained_models/CosyVoice-ttsfrd'
    )
    print("✓ CosyVoice-ttsfrd downloaded")

    print("\nAll models downloaded successfully!")

if __name__ == "__main__":
    main()
