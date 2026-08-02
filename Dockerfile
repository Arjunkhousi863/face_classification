FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    ORT_NUM_THREADS=1 \
    FACE_MODEL_NAME=buffalo_sc \
    FACE_DET_SIZE=256 \
    FACE_MAX_IMAGE_SIDE=640 \
    INSIGHTFACE_HOME=/root/.insightface

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download smallest InsightFace pack during build
RUN mkdir -p /root/.insightface/models \
    && curl -L "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_sc.zip" \
       -o /tmp/face_model.zip \
    && unzip -q /tmp/face_model.zip -d /root/.insightface/models \
    && rm /tmp/face_model.zip \
    && ls -la /root/.insightface/models

COPY app ./app

ENV PORT=8000
EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1
