FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

WORKDIR /app

# Install system dependencies
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

# Install Python dependencies (exclude heavy packages for space)
RUN grep -v -E "^(tensorrt|deepspeed|onnxruntime)" requirements.txt > req.txt \
    && pip install --no-cache-dir -r req.txt \
    && rm req.txt

# Install RunPod SDK
RUN pip install --no-cache-dir runpod

# Copy handler and model downloader
COPY handler.py /app/handler.py
COPY download_model.py /app/download_model.py

ENV PYTHONUNBUFFERED=1
ENV MODEL_DIR=/runpod-volume/Fun-CosyVoice3-0.5B

CMD ["python", "-u", "handler.py"]
