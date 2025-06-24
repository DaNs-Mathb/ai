FROM python:3.12.9-slim AS base

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей отдельно (кэш)
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
