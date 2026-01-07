# CosyVoice3 RunPod Serverless

Serverless deployment of CosyVoice3 0.5B on RunPod.

## Local Development

### 1. Build Docker image

```bash
docker build -t cosyvoice3-serverless .
```

### 2. Run locally

```bash
# With GPU
docker run --gpus all -p 8000:8000 cosyvoice3-serverless

# Test with RunPod local server
docker run --gpus all -e RUNPOD_DEBUG=true -p 8000:8000 cosyvoice3-serverless
```

### 3. Test locally

```bash
curl -X POST http://localhost:8000/runsync \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "Hello, this is a test of CosyVoice3.",
      "mode": "zero_shot"
    }
  }'
```

## Deploy to RunPod

### 1. Push to Docker Hub

```bash
docker tag cosyvoice3-serverless your-dockerhub/cosyvoice3-serverless:v1
docker push your-dockerhub/cosyvoice3-serverless:v1
```

### 2. Create RunPod Endpoint

1. Go to [RunPod Console](https://www.runpod.io/console/serverless)
2. Click **New Endpoint**
3. Set Docker image: `your-dockerhub/cosyvoice3-serverless:v1`
4. Select GPU (RTX 4090 recommended)
5. Configure workers (min: 0, max: 3)
6. Deploy

## API Usage

### Python Client

```python
import requests
import base64

RUNPOD_API_KEY = "your-api-key"
ENDPOINT_ID = "your-endpoint-id"

def generate_speech(text, mode="zero_shot", prompt_audio_path=None):
    payload = {
        "input": {
            "text": text,
            "mode": mode
        }
    }

    # Optional: add custom voice
    if prompt_audio_path:
        with open(prompt_audio_path, "rb") as f:
            payload["input"]["prompt_audio_base64"] = base64.b64encode(f.read()).decode()

    response = requests.post(
        f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync",
        headers={"Authorization": f"Bearer {RUNPOD_API_KEY}"},
        json=payload,
        timeout=120
    )

    result = response.json()

    if "output" in result and "audio_base64" in result["output"]:
        audio_bytes = base64.b64decode(result["output"]["audio_base64"])
        with open("output.wav", "wb") as f:
            f.write(audio_bytes)
        print("Saved to output.wav")
    else:
        print("Error:", result)

# Example usage
generate_speech("Привет, это тест CosyVoice3!")
```

### cURL Examples

**Zero-shot (default voice):**
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "Hello world!",
      "mode": "zero_shot"
    }
  }'
```

**Instruct mode (with dialect/style):**
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "你好世界",
      "mode": "instruct",
      "instruct": "You are a helpful assistant. 请用广东话表达。<|endofprompt|>"
    }
  }'
```

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | Text to synthesize |
| `mode` | string | No | `zero_shot`, `cross_lingual`, or `instruct` (default: `zero_shot`) |
| `prompt_text` | string | No | Transcript of prompt audio for zero-shot cloning |
| `prompt_audio_base64` | string | No | Base64 encoded WAV file for voice cloning |
| `instruct` | string | No | Instruction for instruct mode (dialect, speed, etc.) |
| `stream` | bool | No | Stream output (default: `false`) |

## Output

```json
{
  "output": {
    "audio_base64": "UklGRi...",
    "sample_rate": 22050,
    "format": "wav"
  }
}
```

## Tips

- **Network Volume**: Store models on RunPod Network Volume for faster cold starts
- **GPU**: RTX 4090 or A100 recommended for best latency
- **Min workers = 1**: Set if you need instant responses (costs more)
- **Timeout**: Set to 120s+ for longer texts
