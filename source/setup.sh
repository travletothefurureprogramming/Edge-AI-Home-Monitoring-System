#!/bin/bash

cd "$(dirname "$0")"

source ../.venv/bin/activate

mkdir -p files

curl -fsSL https://ollama.com/install.sh | sh

: > files/.env

pip install customtkinter

python3 setup.py
