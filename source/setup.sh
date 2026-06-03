#!/bin/bash

cd "$(dirname "$0")"

source ../.venv/bin/activate

pip install customtkinter

python3 setup.py