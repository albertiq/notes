#!/bin/bash

# Copy static files to build directory
cp -R src/static build/

# Build FastAPI app
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload