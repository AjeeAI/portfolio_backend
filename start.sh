#!/bin/bash
echo "Starting FastAPI..."
uvicorn main:app --host 0.0.0.0 --port $PORT