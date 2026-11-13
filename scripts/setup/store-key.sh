#!/bin/sh
# Stores the ElevenLabs key in the macOS Keychain (service "navi-elevenlabs").
# macOS asks for the key twice; what you type or paste is hidden and never shown, logged or saved anywhere else.
# Running it again replaces the stored key.
set -e
if [ "$(uname)" != "Darwin" ]; then
  echo "This command is for macOS. On Linux, set NAVI_ELEVENLABS_KEY instead." >&2
  exit 1
fi
echo "Paste your ElevenLabs API key and press Return (it stays hidden), then paste it again to confirm."
security add-generic-password -U -a "$USER" -s navi-elevenlabs -l "NAVI ElevenLabs key" -w
echo "Saved in the Keychain. Now run: python3 scripts/setup/check.py"
