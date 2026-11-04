#!/bin/sh
# Installs what NAVI needs, all inside this repo folder (plus shared caches in your user folder):
#   .venv/                       Python 3.12, faster-whisper (word timings)          ~200 MB
#   ~/.cache/huggingface         the small.en timing model, runs offline after this    ~480 MB
#   recorder/agent-screenplay/   the recorder with NAVI's patch, Playwright, ffmpeg  ~210 MB
#   ~/Library/Caches/ms-playwright  Chromium for Playwright (skipped if already there) ~300 MB
# Nothing system-wide, no Homebrew, no password. Safe to run again.
# Ask the user before running it (docs/BUILD_BRIEF.md ground rules).
set -e
cd "$(dirname "$0")/../.."
command -v uv >/dev/null || { echo "uv is needed (https://docs.astral.sh/uv/)." >&2; exit 1; }
command -v node >/dev/null || { echo "Node.js 20+ is needed." >&2; exit 1; }

[ -x .venv/bin/python ] || uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r scripts/setup/requirements.txt

if [ ! -d recorder/agent-screenplay ]; then
  git clone https://github.com/gmpetrov/agent-screenplay.git recorder/agent-screenplay
  (cd recorder/agent-screenplay && git apply ../agent-screenplay-navi.patch)
fi
(cd recorder/agent-screenplay && npm install --no-fund --no-audit && npm run build && npx playwright-core install chromium)

# NAVI uses the recorder's ffmpeg (has H.264, libass captions, drawtext). Link it next to NAVI's Python.
ln -sf ../../recorder/agent-screenplay/node_modules/ffmpeg-static/ffmpeg .venv/bin/ffmpeg

model=$(.venv/bin/python -c "import json; print(json.load(open('config/defaults.json'))['timing']['model'])")
.venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('$model', device='cpu', compute_type='int8')"

echo "Installed. Now run: python3 scripts/setup/check.py"
