FROM python:3.11-slim

WORKDIR /app


RUN apt update && apt install -y \
    build-essential \
    android-tools-adb \
    ffmpeg \
    openssl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .bin/app/ .

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]