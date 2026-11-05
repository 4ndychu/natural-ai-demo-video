# NAVI scripts

| Path | Status | What it does |
|---|---|---|
| `setup/check.py` | Working | Readiness check: Node, NAVI's Python, ffmpeg, recorder + Playwright + Chromium, local word timings (a spoken test phrase), the ElevenLabs key and credits left. Installs nothing, spends nothing. `python3 scripts/setup/check.py` |
| `setup/install.sh` | Working | Installs everything above inside the repo (`.venv/`, `recorder/agent-screenplay/`). Ask the user first. |
| `setup/store-key.sh` | Working | Stores the ElevenLabs key in the macOS Keychain; the key is typed hidden, never shown. |
| `audio/dsp.py` | Working (from the pilot) | Pure-Python audio toolkit: WAV I/O, filters, BS.1770 loudness, de-esser, compressor, limiter, pitch tracker (YIN). No dependencies. |
| `audio/finality.py` | Working (from the pilot) | Scores how "finished" a take's last sentence sounds (pitch near the floor, energy draining). Used to rank takes. |
| `audio/treat.py` | Working (from the pilot) | The gentle voice treatment chain and room tone. |
| `voice/generate.py` | Adapted, not yet run against the API | One continuous read per section on eleven_v3, 2 takes, finality ranking, edge shaping, treatment. Prints the credit estimate and stops unless run with `--yes`. |
| `research/measure_speech.py` | Working | Measures a voice track like a real narrator: pace and pitch variation per phrase, pauses, fillers, repeats, breaths, clicks. Used for the research in `reference/research/` and for scoring new takes. |
| `research/transcribe_verbatim.py` | Working | Verbatim transcript (CrisperWhisper 2.0, keeps uh/um/repeats) with word timings. Model is non-commercial-research only. |
| `timing/timing.py` | Working (Phase 2) | Word timings from the finished voice track, locally (faster-whisper, one section at a time with its script as a hint, so restarts keep their real timing). Pins each action to its cue word, tags it explain / click / hunt / wait, checks every cue is heard, waits sit at section boundaries and the screen never sits still over 5 s. Writes `timing.json`, `timing.md` and, with `--preview`, a watchable `timing-preview.mp4`. |
| `record/record.py` | Working (Phase 3) | Records the browser live to the voice with the patched recorder: each step starts at a set time so its click or first key lands on its word; real-time footage, never retimed; the voice is laid over afterwards. Re-records (locally) to calibrate cursor travel, then runs the join checks. Writes `recording/recording.mp4` and `report.md`. |
| blur, render, app server | To build | See `docs/BUILD_BRIEF.md`. |

The recorder (agent-screenplay plus NAVI's patch) is in `../recorder/`.

Requirements: run `scripts/setup/install.sh` once. NAVI's Python is `.venv/bin/python` (3.12) and its ffmpeg is `.venv/bin/ffmpeg`, linked from the recorder's ffmpeg-static; nothing is installed system-wide. Run engine scripts with `.venv/bin/python`. The ElevenLabs key is read from the macOS Keychain (service `navi-elevenlabs`) or the `NAVI_ELEVENLABS_KEY` environment variable, never from a file in the repo.
