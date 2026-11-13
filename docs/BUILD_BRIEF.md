# NAVI build brief (for Claude Code / T3 Code)

You're building **NAVI**, a Claude skill that makes natural-sounding, faceless demo videos. The repo is `~/Developer/natural-ai-demo-video` (GitHub: `4ndychu/natural-ai-demo-video`, public). Andy owns it and judges every output by ear and eye. He is new to the terminal: explain anything he has to do in plain words, one step at a time.

## Read first, in this order

1. `SKILL.md`: the flow NAVI runs for a user.
2. `docs/engine.md`: the pipeline you're building.
3. `reference/voice-rules.md`, `reference/recording-rules.md`, `reference/privacy.md`: the rules. They come from five voice listening rounds and two video drafts. **They override your own instincts.** If a rule seems wrong, say so and ask; don't quietly do something else.
4. `config/defaults.json`: every default value and slider range.
5. `ui/`: the finished local app (open `ui/index.html`). It runs on sample data now; you'll wire it to the engine.

Everything you need is in this repo. Some pieces already exist and work: `scripts/audio/` (audio toolkit, take ranking, treatment), `scripts/voice/generate.py` (the voice method; adapted, not yet run against the API) and `recorder/` (agent-screenplay plus a patch that records live to the voice). Read their READMEs and build on them rather than rewriting them. The rules in `reference/` were distilled from an earlier pilot; you don't need the pilot itself. Build NAVI from scratch, with generic code and generic examples.

## Ground rules

- **Ask before installing anything** (say what and roughly how big).
- **ElevenLabs:** Phase 0 asks Andy for his key once and stores it in the macOS Keychain. Never print, log or commit it, and never ask him to paste it into chat; give him a command or prompt that reads it into the Keychain directly. **Show the estimated credit cost before every generation** and wait for a yes on anything over about 1,000 characters.
- **Logins:** Andy logs in himself in a headed browser, once per seat (owner). Never type passwords or codes. Each video picks its seat (owner on the member-facing pages for a buyer's view, owner in the test business, owner in a real business only when the job names it and needs its dashboard). Any page may be opened and filmed, with the privacy blur on every number and key; the action guard blocks withdrawing, transfers, refunds, bank/payout details, API keys, team or ownership changes and deleting (except NAVI's own "NAVI test" products in a test business), and in a real business every other change the job didn't ask for. Never publish or sell.
- **Git:** commit and push after each phase with a clear message. Never commit keys, audio, video or browser profiles. Outputs go to a gitignored `output/` folder in the repo.
- **Don't call a phase done because the code runs.** Each phase ends with its checks passing and, where marked, Andy's review.

## Build order

Build in this order. Stop at the end of each phase, report in plain words, and wait for Andy.

### Phase 0: setup
- Folder layout: `scripts/` (engine), `output/` (gitignored), keep `ui/`, `reference/`, `config/`, `docs/` as they are.
- One command that checks everything is ready: Playwright + Chromium, ffmpeg, a local Whisper-family model for word timings, Node/Python versions, and that the ElevenLabs key works (show credits left, not the key).
- **Check:** the readiness command passes on Andy's Mac.

### Phase 1: voice
- Generate one continuous take per section from a talking script, with the settings in `config/defaults.json` (eleven_v4 by default, `[relaxed]` only, stability 0.7, no other tags; speed from the pace slider only when the user picks eleven_v3).
- 2 takes per section; save both; let Andy pick or auto-pick the one closest to a reference take in pace.
- Audio edit exactly as `voice-rules.md` section 4: no trimming after sentences, shorten silences over 0.8 s from the middle, short fade only if clipped, light treatment, room tone, no music.
- **Check:** a test script with generic content, 3 short sections. **Andy listens and approves** before Phase 2.

### Phase 2: timing
- Word timestamps from the finished take, locally (no API call).
- Map each `{cue}` in the script to its word time. Tag each action explain / click / hunt / wait.
- **Check:** a timing table per section; every cue mapped; waits fall at section boundaries.

### Phase 3: recording
- Playwright, headed, 1920×1080, saved session per site, eased cursor paths, no zoom by default (same frame size throughout; Andy, Phase 3). The final video is drawn by Recordly's own renderer (pinned, unedited) in Casual or Recordly style.
- Record **live to the voice**: each action starts at its word. No retiming afterwards (see `recording-rules.md`).
- Automated join checks: no frozen frame over 1.5 s unless the voice is on that step, no still screen over 5 s, no cut within 1.5 s of a click.
- **Check:** a short generic demo on a public test site or Andy's test account. **Andy watches and approves.**

### Phase 4: privacy
- Pre-record blur stylesheet driven by the three tiers and hide words in `reference/privacy.md`. Check it on the live page before the first take.
- Post-record text scan on sampled frames; list every blur and every uncertain hit with timestamps for Review.
- **Check:** a page seeded with fake emails, money figures and a fake API key: tier 1 always blurred, tier 2 blurred by default, nothing leaks when the camera zooms or scrolls.

### Phase 5: render and export
- ffmpeg render: video + takes + room tone. Captions burned in / .srt only / off. Corner label off by default, or the user's text in their chosen corner. No other overlays.
- Export MP4 1080p, .srt (unless captions are off), transcript .txt, optional 720p preview. Name files after the demo title. Save them to the folder the user names in the brief or chat (for example their own project folder), defaulting to `~/Movies/NAVI`. Never inside the skill's repo.
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
- **Test key must really call ElevenLabs** (Welcome and Settings). The prototype only fakes it. Wire it to `GET https://api.elevenlabs.io/v1/user/subscription` with the `xi-api-key` header, then show the app's four states:
  - **Checking:** while the request is out (time out after about 10 s).
  - **Works:** a 200 response, with credits left (`character_limit − character_count`).
  - **Wrong key:** a 401 or 403 response.
  - **No connection:** a network error or a timeout.

  Save the key to the Keychain only once it works. The credit count in the header comes from the same call.
- Home's All demos: deleting a demo or a batch removes it from NAVI's list with an Undo toast. It never deletes exported videos in Movies/NAVI.
- **Batch mode, for real (Andy, 8 Nov 2026):** a list in (pasted, one video per line, or a file). Every script is written and shown in **one list to approve together**, then the videos are recorded one after another without anyone watching. Before starting, show the total credit estimate against credits left; **pause the batch if credits run low** (before a generation would go below what's needed) and say so, never part-generate a video. Finished videos go into a **review queue** (Review one by one, with the blur list and marks). Export each approved video plus **a list file** of everything exported (title, file names, length, folder). **Never auto-publish:** nothing is uploaded or posted anywhere.
- **Check:** the full flow from New demo to Export works end to end with real data, and a batch of at least 3 videos runs from list to export, including a pause for low credits (simulated).

### Phase 8: first real video
- Andy picks a real demo and gives the brief. NAVI runs the whole flow on its own: brief, script, voice, recording, review, export.
- **Check:** Andy's review. His notes become new rules in `reference/` or values in `config/defaults.json`, committed and pushed, before the next video.

### Before mass-producing: 2 to 3 real sites
- Before any batch or mass production, run a short demo (about 1 minute) on **2 to 3 different real sites**, using Andy's test accounts (he logs in himself). Different kinds of site, so the recorder, timing, privacy blur and both video styles are tried on real pages, not just test pages.
- **Check:** show Andy all of them. Fix what he flags (as rules or defaults) before mass-producing.

## The quality bar

The bar is Andy's ear and eye, not "it rendered". A video is done when he can't point to the moment it gives itself away as AI. Every complaint he makes becomes a rule or a default, so it can't happen again.
