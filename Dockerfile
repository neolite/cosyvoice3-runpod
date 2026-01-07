FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone CosyVoice repository
RUN git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git /app

# Install Python dependencies (skip torch since it's in base image)
RUN pip install --no-cache-dir -r requirements.txt --ignore-installed torch torchaudio

# Install RunPod SDK
RUN pip install --no-cache-dir runpod>=1.6.0

# Download models (or use Network Volume for faster cold start)
COPY download_model.py /app/download_model.py
RUN python download_model.py

# Copy handler
COPY handler.py /app/handler.py

ENV PYTHONUNBUFFERED=1
ENV NVIDIA_VISIBLE_DEVICES=all

CMD ["python", "-u", "handler.py"]
