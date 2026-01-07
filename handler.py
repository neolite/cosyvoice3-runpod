import runpod
import base64
import io
import sys
import os

sys.path.append('third_party/Matcha-TTS')

MODEL = None
MODEL_DIR = os.environ.get('MODEL_DIR', 'pretrained_models/Fun-CosyVoice3-0.5B')


def download_models_if_needed():
    """Download models if not present"""
    model_path = os.path.join(MODEL_DIR, 'config.yaml')
    if os.path.exists(model_path):
        print(f"Models found at {MODEL_DIR}")
        return

    print(f"Models not found at {MODEL_DIR}, downloading...")
    from huggingface_hub import snapshot_download

    os.makedirs(MODEL_DIR, exist_ok=True)

    snapshot_download(
        'FunAudioLLM/Fun-CosyVoice3-0.5B-2512',
        local_dir=MODEL_DIR
    )
    print("Models downloaded successfully")


def load_model():
    """Load CosyVoice3 model once at startup"""
    download_models_if_needed()

    from cosyvoice.cli.cosyvoice import AutoModel
    model = AutoModel(model_dir=MODEL_DIR)
    return model


def handler(job):
    """
    RunPod Serverless handler for CosyVoice3

    Input parameters:
        - text (str): Text to synthesize
        - prompt_text (str): Transcript of the prompt audio (for zero-shot)
        - prompt_audio_base64 (str): Base64 encoded prompt audio file
        - mode (str): "zero_shot", "cross_lingual", or "instruct"
        - instruct (str): Instruction for instruct mode (e.g., "请用广东话表达。")
        - stream (bool): Whether to stream output (default: False)
    """
    global MODEL

    if MODEL is None:
        MODEL = load_model()

    import torchaudio
    import torch

    input_data = job["input"]

    # Required parameters
    text = input_data.get("text", "")
    mode = input_data.get("mode", "zero_shot")
    stream = input_data.get("stream", False)

    # Optional parameters for voice cloning
    prompt_text = input_data.get("prompt_text", "You are a helpful assistant.<|endofprompt|>")
    prompt_audio_base64 = input_data.get("prompt_audio_base64", None)
    instruct = input_data.get("instruct", "You are a helpful assistant.<|endofprompt|>")

    # Handle prompt audio
    prompt_audio_path = None
    if prompt_audio_base64:
        prompt_audio_bytes = base64.b64decode(prompt_audio_base64)
        prompt_audio_path = "/tmp/prompt_audio.wav"
        with open(prompt_audio_path, "wb") as f:
            f.write(prompt_audio_bytes)
    else:
        # Use default prompt audio
        prompt_audio_path = "./asset/zero_shot_prompt.wav"

    # Generate speech based on mode
    audio_segments = []

    try:
        if mode == "zero_shot":
            for i, j in enumerate(MODEL.inference_zero_shot(
                text,
                prompt_text,
                prompt_audio_path,
                stream=stream
            )):
                audio_segments.append(j['tts_speech'])

        elif mode == "cross_lingual":
            for i, j in enumerate(MODEL.inference_cross_lingual(
                prompt_text + text,
                prompt_audio_path,
                stream=stream
            )):
                audio_segments.append(j['tts_speech'])

        elif mode == "instruct":
            for i, j in enumerate(MODEL.inference_instruct2(
                text,
                instruct,
                prompt_audio_path,
                stream=stream
            )):
                audio_segments.append(j['tts_speech'])
        else:
            return {"error": f"Unknown mode: {mode}. Use 'zero_shot', 'cross_lingual', or 'instruct'"}

        # Concatenate all audio segments
        if audio_segments:
            final_audio = torch.cat(audio_segments, dim=1)

            # Save to buffer
            buffer = io.BytesIO()
            torchaudio.save(buffer, final_audio, MODEL.sample_rate, format="wav")
            buffer.seek(0)

            # Encode to base64
            audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')

            return {
                "audio_base64": audio_base64,
                "sample_rate": MODEL.sample_rate,
                "format": "wav"
            }
        else:
            return {"error": "No audio generated"}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
