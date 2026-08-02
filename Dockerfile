FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download face model during build so first request does not pull 100MB+ at runtime
ENV INSIGHTFACE_HOME=/root/.insightface
ARG FACE_MODEL_NAME=buffalo_s
ENV FACE_MODEL_NAME=${FACE_MODEL_NAME}
ENV FACE_DET_SIZE=320
RUN mkdir -p /root/.insightface/models \
    && curl -L "https://github.com/deepinsight/insightface/releases/download/v0.7/${FACE_MODEL_NAME}.zip" \
       -o /tmp/face_model.zip \
    && unzip -q /tmp/face_model.zip -d /root/.insightface/models \
    && rm /tmp/face_model.zip \
    && ls -la /root/.insightface/models

COPY app ./app

ENV PORT=8000
EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
