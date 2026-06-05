
@echo off
cd /d "%~dp0"


where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo Ollama is NOT installed! Running installation script...
    powershell -ExecutionPolicy Bypass -Command "irm https://ollama.com/install.ps1 | iex"
) else (
    echo [Ollama] Is already installed! Skipping installation...
)

type nul > .env

pip install customtkinter

python "setup.py"

pause
