FROM python:3.11-slim

WORKDIR /app

RUN apt update && apt install -y \
    build-essential \
    android-tools-adb \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY .bin/app/ .

EXPOSE 8080

CMD ["python", "Server.py"]