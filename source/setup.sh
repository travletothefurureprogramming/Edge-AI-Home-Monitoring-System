#!/bin/bash

cd "$(dirname "$0")"

source ../.venv/bin/activate

curl -fsSL https://ollama.com/install.sh | sh

: > .env

pip install customtkinter

python3 setup.py
