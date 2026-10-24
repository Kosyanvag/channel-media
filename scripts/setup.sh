#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python3 -c "import kokoro_onnx, soundfile" 2>/dev/null || pip install --break-system-packages -q kokoro-onnx soundfile
python3 -c "import sys; sys.path.insert(0,'.'); from engine import voice; voice.ensure_model(); print('voice model ready')"
which ffmpeg >/dev/null && echo "ffmpeg ready"
git config user.name >/dev/null || git config user.name "Claude"
git config user.email >/dev/null || git config user.email "noreply@anthropic.com"
