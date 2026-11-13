---
name: natural-ai-demo-video
description: NAVI (natural AI demo video) makes natural-sounding, faceless demo videos, walkthroughs, product tours, tutorials, screencasts and course lessons of any website or web app, with an AI voiceover that doesn't sound robotic. Claude explores the site, writes a talking script and clean captions, voices it with ElevenLabs, records the browser clicking in time with the voice, blurs private data, and exports an MP4 with captions. Use whenever someone wants a demo or explainer video, a screen recording with voiceover, a narrated walkthrough or a faceless tutorial, even if they don't name this skill. Needs Claude Code running on the user's own computer.
license: AGPL-3.0
---

# NAVI: natural AI demo videos

NAVI turns "make a demo of X" into a finished MP4 with captions: no face, no microphone, and a voice that sounds like a person explaining something, not reading it.

> **Status:** the engine (voice takes, timing, recording, blur, render, export, batches) runs for real, and the local app is wired to it: start it with `.venv/bin/python scripts/app/server.py --open`, then follow what the user does with `scripts/app/wait.py` (`docs/app-api.md`). Tell the user plainly if a step fails. Never pretend a step ran.

**Where NAVI lives:** the folder the user cloned it into (any folder; `~/Developer/natural-ai-demo-video` is a good choice). `scripts/setup/install.sh` installs everything inside that folder and links `~/.claude/skills/natural-ai-demo-video` to it, so Claude Code finds NAVI in any session. Run every command from that folder. NAVI's own data (settings, saved logins, the key's status) lives outside it, in `~/Library/Application Support/NAVI`.

## First: check where you're running

NAVI has to run on the user's own computer: it opens a local app in their browser, opens a second browser window for them to log in to a test account, records the screen and keeps the key in their keychain. That works in Claude Code (terminal, IDE or the desktop app's Code tab).

If you are running in a cloud sandbox instead (a normal claude.ai chat, or any session without access to the user's own machine), say so straight away, in one or two sentences: NAVI needs Claude Code on their computer to record, and here you can still write and refine the script (talking version plus captions) so it's ready to record later. Don't attempt installs, recordings or ElevenLabs calls from the sandbox.

## When to use

- "Make a demo video / walkthrough / product tour / tutorial of <site or app>"
- "Record how to <task> in <web app> with a voiceover"
- "Redo section 3 of my demo", "make it calmer", "blur the email at 1:20"

Not for: desktop apps, videos with a real person on camera, voice cloning.

## Ground rules (always)

1. **Never type passwords, codes or keys into a site.** The user logs in themselves, once per seat, from Settings > Logins (the only window NAVI ever shows). NAVI films in its own invisible browser while the user keeps working.
2. **Never print, log or commit the ElevenLabs key.** Read it only from the keychain or the user's local key file. Only ever send it to ElevenLabs.
3. **Ask before installing anything** (Playwright, ffmpeg, the timing model). Say what and roughly how big.
4. **Show the credit cost before spending credits** (samples, recording, redos).
5. **Privacy tiers are not optional.** Tier 1 is always blurred. Warn when the user switches on money figures or other people's data.
6. **Never pause or speed up the voice to fit the video.** The video holds or stretches instead.
7. **Say plainly that blurring reduces risk, not to zero.** The user must watch before publishing.

## When NAVI may interrupt the user

Only for: the first login per account, a login the batch preflight found expired, a batch that would spend over the user's credit limit, and the Go click (which they can switch off in Settings). Everything else happens without them: a batch checks every login and page and the credits **before** it starts (`batch.py go`), then never asks anything; a video that breaks or is blocked by the action guard is skipped with the reason, and the morning report (`batch-report.md`, and the app's batch screen) says what's done, what was skipped and why. They can watch any recording live in the app (Watch live). For a batch: `batch.py write <batch>` writes every script (each with its seat) through the job subagents, then run `batch.py sheet <batch>`, then `batch.py go <batch> --auto`: it starts straight away when the user switched off the Go click and the preflight passes; otherwise the batch waits on the app's Go screen (videos, the seat for each, the cost, the logins needed, then Go).

## Which model does which job

Every job that needs a model runs as its own subagent, on the model and effort `config/defaults.json` names for it (`"jobs"`): **planning** claude-fable-5-2 / high, **explore** claude-haiku-5-5 / medium, **writing** claude-opus-5-5 / medium, **checks** claude-sonnet-5-5 / medium, **batch_qa** claude-opus-5-5 / high. Run one with `.venv/bin/python scripts/jobs/jobs.py run <job> --prompt-file <file>` (add `--attended` only when the user is at the session); `jobs.py show` lists them. Always full model IDs, never an alias. If a model is unavailable the job's next fallback runs and the batch report carries a warning; a run nobody is watching never falls back to Fable. For a batch, `batch.py write <batch>` does all of it: one plan, then for each video explore, three drafts and the pick, and the checks; `batch.py run` ends with the last check (`batch_qa`). The batch report (`batch-report.md`, "Models") lists every job run with its model, effort, time and tokens.

## A started batch runs by itself

**Before every batch, check the Mac** (`.venv/bin/python scripts/batch/batch.py mac`) and tell the user in one line which apps to quit (any app using more than a quarter of a core) and whether iCloud is busy syncing; the Go screen shows the same line with the Mac's load. A busy Mac makes takes land late and renders slow. It never stops a batch.

Start a batch with `.venv/bin/python scripts/batch/runner.py start <batch>` straight after `batch.py new` (the app's Go click does the same with `--go`). The batch then belongs to macOS, not to this session: it keeps going if T3 Code or Claude Code closes or the session times out, it keeps the Mac awake itself while it works (never ask the user to run caffeinate), and after a restart it carries on at the next login from where it stopped. It writes the scripts, waits for the plan pick and the Go click, records, waits for A/B/C picks and records each as it is picked. Don't run `batch.py write`, `go` or `run` by hand for a batch that has a runner. `runner.py status <batch>` says what it is doing; `stop` pauses it ("paused at video 7 of 30"), `resume` carries on. A video whose script can't be written, or still has checker errors, is skipped with its reason; it never blocks Go for the others. Before the user's first overnight batch, walk them through the 2-minute real-restart test (`docs/before-first-overnight-batch.md`).

## Blind tests (off by default)

Blind tests compare models inside real work instead of separate test rounds (`scripts/batch/blind.py`). They are off by default. A user who wants them switches them on in their own `$NAVI_DATA/jobs.json` (outside the repo; it overrides `config/defaults.json` → `jobs`), e.g. `{"planning": {"blind_test": {"enabled": true}}}`. **Planning:** a real batch's outline is planned once per arm (the arms in `jobs.planning.blind_test`); the user sees the plans as A, B, C, unlabelled, and picks one before anything is explored or written (`batch.py blind <batch>`, `batch.py pick-plan <batch> B`). **Writing:** for the first videos of a real batch, each arm in `jobs.writing.blind_test` writes one draft to the same style and facts; each is voiced once (show the extra credits first); the user hears A, B, C, shuffled, the arm hidden, and picks (`batch.py pick <batch> <video> A`, or the app's review queue). The picked draft and its one take are what gets recorded. Never tell the user which model made which letter until every pick in the batch is made; then the batch report shows it. Picks add up in `$NAVI_DATA/blind-picks.jsonl` (`batch.py blind-results`). A batch that isn't real work is made with `batch.py new --no-blind`.

## The flow

### 0. First run (once)

When the user says "install this", or asks for a first demo:

1. Run `python3 scripts/setup/check.py` from the NAVI folder (any python3 works; it changes nothing). Tell the user in plain words what's missing.
2. Ask before installing, with the sizes: everything goes inside the NAVI folder, about 500 MB, plus about 1 GB of shared downloads (the recording browser and the word-timing model). Nothing system-wide, no password. Then run `sh scripts/setup/install.sh`.
   - If it says **uv** is needed (it sets up NAVI's own Python 3.12), show the user the one-line command it prints, ask, run it, and run install.sh again in a new shell.
   - If it says **Node.js** 20+ or **git** is needed, the user installs that themselves (nodejs.org; `xcode-select --install` for git and Swift on a Mac). Don't install system software for them.
3. The ElevenLabs key (Starter plan or above, text to speech access): the user stores it themselves, never in chat. Either `sh scripts/setup/store-key.sh` in their own terminal (macOS Keychain; the paste is hidden), or the app's Settings › ElevenLabs. On Linux, `NAVI_ELEVENLABS_KEY` in their environment.
4. Run the check again with `.venv/bin/python scripts/setup/check.py` until it says Ready, and show the credits left.
- Ask which site they'll demo first. The user logs in from Settings › Logins (one row per site and seat, status checked live, one Log in button). The login window opens only when they click Log in, ticks "remember me" where offered, and is the only window NAVI ever shows. Save the session per site and seat.
- Returning users skip all of this. Only the site changes per demo.

### 1. Brief

Get, in as few questions as possible: what to show, which site, who's watching (beginners / some experience / pros), length (1, 3, 5 or 8 minutes), anything to keep off screen, and which voice. Captions and corner label come from the user's saved defaults (captions burned in, no corner label) unless they say otherwise. **Never add a watermark, brand name, "Illustrative" tag or any other overlay the user didn't ask for.** Use sensible defaults rather than asking about everything. A new site means a one-time login.

If the user changes direction mid-way ("make it a demo of the payouts page instead"), keep the current demo as a draft and start a new brief from what they said.

### 2. Explore

Explore with `node scripts/explore/explore.mjs --url <page> --site <site> --seat <seat> --out output/demos/<id>/explore [--steps steps.json]`: a headless browser with the seat's saved login, the recording's size and user agent; a screenshot and the list of buttons, links and fields after each step. Map the screens, the exact clicks and fields for the task, and anything that loads slowly. Anything a demo creates is named as a test ("NAVI test 1") and left hidden. **Never take over the Mac** (`reference/recording-rules.md` rule 22): no visible browser except the login window, nothing that comes to the front.

**Seats** (`scripts/seats/seats.py`, rule 13b): every video records in one saved login, picked from the job's own words. *Owner on the member-facing pages* for anything a buyer sees (opening courses, modules, lessons; never the dashboard, and nothing may change there); *owner in the test business* for "how to build X" demos; *owner in a real business* only when the job names that business and needs its owner dashboard. Put the pick in the script as `"seat": {"seat", "view", "business", "allow", "why"}` (`seats.py pick <site> "<job>"`), and show it in the script preview. **The action guard** (`scripts/guard/guard.mjs`, rule 13d) runs in every browser NAVI opens: any page may be opened and filmed (payouts, balances, billing, bank, API keys, with every number and key blurred); withdrawing, transfers, refunds, bank and payout details, API keys, team or ownership changes and deleting are blocked in code, and in a real business so is every other change the job didn't ask for. A blocked action fails that video with the reason; never ask the user mid-run.

### 3. Script

Split the video into short sections (about 15 to 35 seconds each). For each section write two lines:

- **Talking version** (what the voice says): how a person actually explains it out loud. Small restarts, reactions and opinions where the screen earns them; very few fillers.
- **Caption version** (what's shown): clean, short, no fillers.

**Draft three, keep the best.** Draw three styles of the day (`.venv/bin/python scripts/script/drafts.py styles script.template.json`), write the video once to each (the same facts and actions; three different days of the same narrator), then score them and keep the best (`.venv/bin/python scripts/script/drafts.py pick <folder>/draft*.json --base <folder>`, which writes `script.json`). No two videos open, start their steps, hesitate or slip the same way (why: `reference/listening/2026-11-11-everything-sounds-the-same.md`), but the narrator stays recognisable: his few habits (`config/narrators/alex.json`) come out now and then, at their own rate. In a batch, write the videos in order so each is scored against the ones already picked. Follow `reference/voice-rules.md`, in the format and order in `reference/script-writing.md`. The checker refuses a script that repeats a recent video's openings, step starts, fillers, repairs, endings or phrases (`script-history.jsonl`), or another script in its batch. Every position ("top right", "at the bottom of the form") is checked against the explored page by the checker, so keep the explore folder next to the script. Run the checker (`scripts/script/check_script.py`) and fix every error. Then show both versions side by side (`scripts/script/show_script.py`) and get approval before spending any credits. The voice step refuses a script with checker errors.

### 4. Voice

- Start with the voice's recommended settings for the kind of demo (course walkthrough, quick SaaS demo, product tour).
- Sliders and their safe ranges: casualness 3 to 8, energy 1 to 6, pace 0.94x to 1.08x, hesitations 0 to 3, breaths 0 to 2, swearing 0 to 2 (never inside instructions; captions clean unless the user asks).
- Text preview is free. An audio sample costs about 300 credits; hearing a voice for the first time about 120.
- Lean calm: higher stability and a relaxed delivery. Avoid bright one-word lines. Don't add breath tags.
- If the user wants one voice for a whole series, lock it for the project.

### 5. Privacy

Apply the tiers before recording:

- **Always blurred:** API keys and tokens, passwords, 2FA and recovery codes, card and bank numbers, ID numbers, private keys, login links.
- **Blurred unless allowed:** emails, phone numbers, real names and photos, addresses, money figures, customer details, follower and member counts.
- **Shown unless blurred:** usage stats, public prices, dates.
- Plus the user's own hide words.

### 6. Record

See `docs/engine.md`. In a test business, NAVI deletes its own "NAVI test" products before and after every take so each starts clean (never in a real business; `reference/recording-rules.md` 13c). In short: generate one continuous take per section, get word timestamps, schedule each browser action at its word, record, hold frames when an action runs long, never pause the audio. Then scan the frames for anything the page-level blur missed.

**Speed** (`docs/engine.md` 4a): a video is recorded live once (a second take only if the join check fails); in a batch the scripts are rehearsed before any voice is paid for, one video is drawn while the next is made, and a site explored before isn't explored again from scratch.

### 7. Review

Open the local app on the Review step. The user marks moments (sounds like AI, needs a blur, too fast) or types notes. Show the redo cost, then redo only the marked sections. Log marks with the settings used so the voice defaults improve over time.

### 8. Export

Apply the demo's caption setting (burned in, separate .srt, or off) and corner label (off, or the user's text in the chosen corner); changing either is a re-render only, no credits. Render the MP4 (1080p), captions (.srt unless captions are off) and a transcript, plus an optional 720p preview, into the folder the user names (default `~/Movies/NAVI`), so a video can land straight in the project it belongs to. Name the files after the demo title.

## Your data

From Settings the user can remove the key (remind them to revoke it at ElevenLabs too), forget saved logins, reset settings, or delete everything NAVI saved. Finished videos are never touched. Uninstalling means deleting the NAVI folder and the link `~/.claude/skills/natural-ai-demo-video`.

## Files

- `reference/voice-rules.md`: how to write the talking script and generate a human-sounding voice. **Read before step 3.**
- `reference/script-writing.md`: the script file, the order of work, and the checker. **Read before step 3.**
- `reference/recording-rules.md`: how to record the screen in time with the voice. **Read before step 6.**
- `reference/privacy.md`: the blur tiers and warnings. **Read before step 5.**
- `config/defaults.json`: slider ranges, presets, per-voice settings, on-screen defaults and each job's model (`jobs`)

- `ui/index.html`: the local app (open in a browser; `?start=home|voice|review|settings`, `&theme=light|dark`)
- `ui/app.js`: screens, state and sample data
- `ui/engine.js`: connects the app to the engine when NAVI's server serves it
- `docs/engine.md`: how recording, timing, blur and rendering work
