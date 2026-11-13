#!/bin/sh
# Installs everything NAVI needs. Run it from the folder you cloned NAVI into; everything goes inside that folder,
# plus shared download caches in your user folder:
#   .venv/                          Python 3.12 and the word-timing package (faster-whisper)    ~200 MB
#   recorder/agent-screenplay/      the recorder, at the commit NAVI's patch is made for,
#                                   with the patch, Playwright and ffmpeg                       ~220 MB
#   recorder/polish/node_modules/   the renderer's two packages (pixi.js, pixi-filters)        ~80 MB
#   Playwright's browser cache      Chromium for recording (~/Library/Caches/ms-playwright)    ~580 MB
#   the timing model                small.en, runs offline after this (~/.cache/huggingface)   ~470 MB
#   ~/.claude/skills/natural-ai-demo-video   a link to this folder, so Claude Code finds NAVI in any session
# Nothing system-wide, no Homebrew, no password. Safe to run again. Claude asks the user before running it.
set -e
cd "$(dirname "$0")/../.."
ROOT=$(pwd -P)
RECORDER_REPO=https://github.com/gmpetrov/agent-screenplay.git
RECORDER_REV=a06347813d65de74d7a228d0bb353ca9e3fdbe37     # the agent-screenplay commit NAVI's patch is made for
SKILLS="${NAVI_SKILL_DIR:-$HOME/.claude/skills}"

stop() { echo "$1" >&2; exit 1; }
command -v git >/dev/null || stop "git is needed. On a Mac: xcode-select --install (Apple's free command line tools)."
command -v node >/dev/null || stop "Node.js 20 or newer is needed: https://nodejs.org"
[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 20 ] || stop "Node.js 20 or newer is needed (this Mac has $(node -v))."
command -v uv >/dev/null || stop "uv is needed: it sets up NAVI's own Python 3.12 inside this folder, without a password.
Install it with:  curl -LsSf https://astral.sh/uv/install.sh | sh
then open a new terminal (so uv is found) and run this again."

echo "1/6  NAVI's Python (.venv)"
[ -x .venv/bin/python ] || uv venv --python 3.12 .venv
uv pip install --quiet --python .venv/bin/python -r scripts/setup/requirements.txt

echo "2/6  The recorder (agent-screenplay ${RECORDER_REV%"${RECORDER_REV#???????}"} + NAVI's patch)"
[ -d recorder/agent-screenplay/.git ] || git clone --quiet "$RECORDER_REPO" recorder/agent-screenplay
(
  cd recorder/agent-screenplay
  if git diff --quiet && git diff --cached --quiet; then          # untouched: move to the pinned commit, then patch
    git cat-file -e "$RECORDER_REV^{commit}" 2>/dev/null || git fetch --quiet origin
    git checkout --quiet "$RECORDER_REV"
    git apply ../agent-screenplay-navi.patch
  elif ! git apply --reverse --check ../agent-screenplay-navi.patch 2>/dev/null; then
    stop "recorder/agent-screenplay has changes that aren't NAVI's patch. Move that folder aside and run this again."
  fi
  [ "$(git rev-parse HEAD)" = "$RECORDER_REV" ] || stop "recorder/agent-screenplay is not at $RECORDER_REV. Move that folder aside and run this again."
  npm ci --no-fund --no-audit --loglevel=error
  npm run --silent build
  npx --no-install playwright-core install chromium
)

echo "3/6  The renderer's packages (recorder/polish)"
(cd recorder/polish && npm ci --no-fund --no-audit --loglevel=error)

echo "4/6  ffmpeg (the recorder's copy: H.264, captions, drawtext)"
ln -sf ../../recorder/agent-screenplay/node_modules/ffmpeg-static/ffmpeg .venv/bin/ffmpeg

echo "5/6  The word-timing model"
model=$(.venv/bin/python -c "import json; print(json.load(open('config/defaults.json'))['timing']['model'])")
.venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('$model', device='cpu', compute_type='int8')" 2>/dev/null

echo "6/6  Claude Code's skill link"
mkdir -p "$SKILLS"
LINK="$SKILLS/natural-ai-demo-video"
if [ -e "$LINK" ] && [ "$(cd "$LINK" && pwd -P)" = "$ROOT" ]; then
  echo "     $LINK is this folder"
elif [ -L "$LINK" ] || [ ! -e "$LINK" ]; then
  ln -sfn "$ROOT" "$LINK"
  echo "     $LINK -> $ROOT"
else
  echo "     $LINK already exists and is another folder; left as it is. Claude Code uses that one."
fi

echo "Installed. Now run: .venv/bin/python scripts/setup/check.py"
