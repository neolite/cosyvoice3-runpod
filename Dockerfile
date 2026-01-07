FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

WORKDIR /app

# Install system dependencies and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libsndfile1 \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Clone CosyVoice repository
RUN git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git /app \
    && rm -rf .git third_party/*/.git

# Install packages that depend on torch with --no-deps
RUN pip install --no-cache-dir --no-deps \
    conformer==0.3.2 \
    lightning==2.2.4 \
    torchvision==0.20.1

# Install other Python dependencies (exclude torch-dependent and heavy packages)
RUN grep -v -E "^(torch|torchaudio|tensorrt|deepspeed|onnxruntime|conformer|lightning)" requirements.txt > req.txt \
    && pip install --no-cache-dir -r req.txt \
    && rm req.txt

# Install RunPod SDK
RUN pip install --no-cache-dir runpod

# Copy handler and model downloader
COPY handler.py /app/handler.py
COPY download_model.py /app/download_model.py

# Models will be downloaded at runtime or mounted via Network Volume
# Set model path via environment variable
ENV PYTHONUNBUFFERED=1
ENV MODEL_DIR=/runpod-volume/models/cosyvoice3

CMD ["python", "-u", "handler.py"]
