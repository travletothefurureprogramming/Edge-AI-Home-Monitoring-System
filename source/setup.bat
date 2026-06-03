@echo off
cd /d "%~dp0"

powershell -ExecutionPolicy Bypass -Command "& '..\.venv\Scripts\Activate.ps1'"


powershell -ExecutionPolicy Bypass -Command "irm https://ollama.com/install.ps1 | iex"

type nul > .env

pip install customtkinter

python "setup.py"

pause
