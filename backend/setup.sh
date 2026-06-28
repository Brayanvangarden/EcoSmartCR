#!/bin/bash

echo "Creating virtual environment..."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Backend setup completed."