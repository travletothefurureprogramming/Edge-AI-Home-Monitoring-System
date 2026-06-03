@echo off
cd /d "%~dp0"

powershell -ExecutionPolicy Bypass -Command "& '..\.venv\Scripts\Activate.ps1'"


pip install customtkinter

python "setup.py"

pause