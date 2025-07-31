#!/bin/bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download voice model (10MB)
VOICE="en_US-lessac-medium"
if [ ! -f "$VOICE.onnx" ]; then
  echo "Downloading voice model..."
  curl -LO "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/us/$VOICE/$VOICE.onnx"
fi

# Run service
python piper_tts.py --api
