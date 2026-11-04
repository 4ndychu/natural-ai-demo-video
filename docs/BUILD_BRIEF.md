# NAVI build brief (for Claude Code / T3 Code)

You're building **NAVI**, a Claude skill that makes natural-sounding, faceless demo videos. The repo is `~/Documents/natural-ai-demo-video` (GitHub: `4ndychu/natural-ai-demo-video`, public). Andy owns it and judges every output by ear and eye. He is new to the terminal: explain anything he has to do in plain words, one step at a time.

## Read first, in this order

1. `SKILL.md`: the flow NAVI runs for a user.
2. `docs/engine.md`: the pipeline you're building.
3. `reference/voice-rules.md`, `reference/recording-rules.md`, `reference/privacy.md`: the rules. They come from five voice listening rounds and two video drafts. **They override your own instincts.** If a rule seems wrong, say so and ask; don't quietly do something else.
4. `config/defaults.json`: every default value and slider range.
5. `ui/`: the finished local app (open `ui/index.html`). It runs on sample data now; you'll wire it to the engine.

Everything you need is in this repo. The rules in `reference/` were distilled from an earlier pilot; you don't need the pilot itself. Build NAVI from scratch, with generic code and generic examples.

## Ground rules

- **Ask before installing anything** (say what and roughly how big).
- **ElevenLabs:** Phase 0 asks Andy for his key once and stores it in the macOS Keychain. Never print, log or commit it, and never ask him to paste it into chat; give him a command or prompt that reads it into the Keychain directly. **Show the estimated credit cost before every generation** and wait for a yes on anything over about 1,000 characters.
- **Logins:** Andy logs in himself in a headed browser. Never type passwords or codes. Test accounts and test businesses only. Never publish, sell, delete, or open payouts, balances or settings.
- **Git:** commit and push after each phase with a clear message. Never commit keys, audio, video or browser profiles. Outputs go to a gitignored `output/` folder in the repo.
- **Don't call a phase done because the code runs.** Each phase ends with its checks passing and, where marked, Andy's review.

## Build order

Build in this order. Stop at the end of each phase, report in plain words, and wait for Andy.

### Phase 0: setup
- Folder layout: `scripts/` (engine), `output/` (gitignored), keep `ui/`, `reference/`, `config/`, `docs/` as they are.
- One command that checks everything is ready: Playwright + Chromium, ffmpeg, a local Whisper-family model for word timings, Node/Python versions, and that the ElevenLabs key works (show credits left, not the key).
- **Check:** the readiness command passes on Andy's Mac.

### Phase 1: voice
- Generate one continuous take per section from a talking script, with the settings in `config/defaults.json` (`[relaxed]` only, stability 0.7, speed from the pace slider, no other tags).
- 2 takes per section; save both; let Andy pick or auto-pick the one closest to a reference take in pace.
- Audio edit exactly as `voice-rules.md` section 4: no trimming after sentences, shorten silences over 0.8 s from the middle, short fade only if clipped, light treatment, room tone, no music.
- **Check:** a test script in generic content (not XRM), 3 short sections. **Andy listens and approves** before Phase 2.

### Phase 2: timing
- Word timestamps from the finished take, locally (no API call).
- Map each `{cue}` in the script to its word time. Tag each action explain / click / hunt / wait.
- **Check:** a timing table per section; every cue mapped; waits fall at section boundaries.

### Phase 3: recording
- Playwright, headed, 1920×1080, saved session per site, standard black cursor on eased paths, subtle click feedback, gentle zoom.
- Record **live to the voice**: each action starts at its word. No retiming afterwards (see `recording-rules.md`).
- Automated join checks: no frozen frame over 1.5 s unless the voice is on that step, no still screen over 5 s, no cut within 1.5 s of a click.
- **Check:** a short generic demo on a public test site or Andy's test account. **Andy watches and approves.**

### Phase 4: privacy
- Pre-record blur stylesheet driven by the three tiers and hide words in `reference/privacy.md`. Check it on the live page before the first take.
- Post-record text scan on sampled frames; list every blur and every uncertain hit with timestamps for Review.
- **Check:** a page seeded with fake emails, money figures and a fake API key: tier 1 always blurred, tier 2 blurred by default, nothing leaks when the camera zooms or scrolls.

### Phase 5: render and export
- ffmpeg render: video + takes + room tone. Captions burned in / .srt only / off. Corner label off by default, or the user's text in their chosen corner. No other overlays.
- Export MP4 1080p, .srt (unless captions are off), transcript .txt, optional 720p preview. Name files after the demo title.
- Redo only the sections marked in Review.
- **Check:** all three caption modes and a corner label render correctly. Changing them re-renders without new voice or recording.

### Phase 6: script writing
- Claude writes the talking version and clean captions per `voice-rules.md`.
- Add a script checker that flags: cheerful one-word lines ("Easy.", "There we go.", "There it is"), "…" used as a hesitation, any performance tag other than `[relaxed]`, more than one restart per section, fillers written as their own sentence, and any stretch likely to leave the screen still over 5 s.
- **Check:** the checker catches each banned pattern in a test script.

### Phase 7: the app
- Serve `ui/` locally (a `localhost` address; nothing on the web) and replace the sample data with the engine's real state: demos, script, voices, sliders, privacy, recording progress, review marks, export.
- Clicks in the app reach Claude through a "wait for the app" command that blocks until the user acts, then returns what they did.
- Settings: key in the macOS Keychain, saved logins per site, defaults, and the "Your data" controls (remove key, forget logins, reset, delete everything; never touch videos).
- **Check:** the full flow from New demo to Export works end to end with real data.

### Phase 8: first real video
- Andy picks a real demo and gives the brief. NAVI runs the whole flow on its own: brief, script, voice, recording, review, export.
- **Check:** Andy's review. His notes become new rules in `reference/` or values in `config/defaults.json`, committed and pushed, before the next video.

## The quality bar

The bar is Andy's ear and eye, not "it rendered". A video is done when he can't point to the moment it gives itself away as AI. Every complaint he makes becomes a rule or a default, so it can't happen again.
