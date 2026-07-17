@echo off
setlocal

```
(
    echo FLASK_ENV=production
    echo OLLAMA_HOST=http://ollama:11434
    echo SECRET_KEY=CHANGE_ME
    echo APP_ADMIN_USER=admin
    echo APP_ADMIN_PASSWORD=
    echo TELEGRAM_BOT_TOKEN=
    echo TELEGRAM_CHAT_ID=
) > "\.bin\app\config\.env"

echo .env created.
```

) else (
echo .env already exists.
)

docker compose up --build

pause
