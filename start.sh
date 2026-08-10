#!/usr/bin/env bash
set -e

mkdir -p ./.bin/app/config

if [ ! -f ./.bin/app/config/.env ]; then
    echo "Creating .env..."

    cat > ./.bin/app/config/.env <<EOF
FLASK_ENV=production
OLLAMA_HOST=http://ollama:11434
SECRET_KEY=CHANGE_ME
APP_ADMIN_USER=admin
APP_ADMIN_PASSWORD=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EOF

    echo ".env created."
else
    echo ".env already exists."
fi

docker compose up --build
