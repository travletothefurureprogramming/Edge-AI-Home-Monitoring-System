#!/bin/bash

if [ ! -f /config/.env ]; then
    echo "Creating .env..."
    cat > /app/config/.env << EOF
FLASK_ENV=production
OLLAMA_HOST=http://ollama:11434
SECRET_KEY=$(openssl rand -hex 32)
APP_ADMIN_USER=admin
APP_ADMIN_PASSWORD=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EOF
    echo "✓ .env created at /app/config/.env"
else
    echo "✓ .env already exists"
fi

exec python Server.py