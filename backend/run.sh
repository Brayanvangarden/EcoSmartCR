#!/bin/bash

source .venv/bin/activate
uvicorn api.main:app --reload --port 8000