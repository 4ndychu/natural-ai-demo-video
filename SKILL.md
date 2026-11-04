---
name: natural-ai-demo-video
description: NAVI makes natural-sounding, faceless demo and walkthrough videos of any website or web app. Claude explores the site, writes a talking script and clean captions, voices it with an ElevenLabs voice, records the browser clicking in time with the voice, blurs private data, and exports an MP4 with captions. Use when someone asks for a demo video, product tour, walkthrough, tutorial or course lesson recorded from a browser with an AI voiceover.
license: MIT
---

# NAVI: natural AI demo videos

NAVI turns "make a demo of X" into a finished MP4 with captions: no face, no microphone, and a voice that sounds like a person explaining something, not reading it.

> **Status:** in development. The local app in `ui/` is complete with sample data. The engine (voice takes, timing, recording, blur, render) is being built. Until it ships, tell the user plainly which steps you can run for real and which aren't available yet. Never pretend a step ran.

## When to use

- "Make a demo video / walkthrough / product tour / tutorial of <site or app>"
- "Record how to <task> in <web app> with a voiceover"
- "Redo section 3 of my demo", "make it calmer", "blur the email at 1:20"

Not for: desktop apps, videos with a real person on camera, voice cloning.

## Ground rules (always)

1. **Never type passwords, codes or keys into a site.** A browser opens and the user logs in themselves, ideally to a test account with fake data.
2. **Never print, log or commit the ElevenLabs key.** Read it only from the keychain or the user's local key file. Only ever send it to ElevenLabs.
3. **Ask before installing anything** (Playwright, ffmpeg, the timing model). Say what and roughly how big.
4. **Show the credit cost before spending credits** (samples, recording, redos).
5. **Privacy tiers are not optional.** Tier 1 is always blurred. Warn when the user switches on money figures or other people's data.
6. **Never pause or speed up the voice to fit the video.** The video holds or stretches instead.
7. **Say plainly that blurring reduces risk, not to zero.** The user must watch before publishing.

## The flow

### 0. First run (once)

- Ask for the ElevenLabs API key (Starter plan or above, text to speech access). Test it and show the credits left. Store it in the system keychain (macOS) or a local file outside the skill folder (Linux), readable only by the user.
- Check for Playwright, ffmpeg and the timing model. Ask, then install what's missing.
- Ask which site they'll demo first and open a browser so they can log in. Save the session per site.
- Returning users skip all of this. Only the site changes per demo.

### 1. Brief

Get, in as few questions as possible: what to show, which site, who's watching (beginners / some experience / pros), length (1, 3, 5 or 8 minutes), anything to keep off screen, and which voice. Use sensible defaults rather than asking about everything. A new site means a one-time login.

If the user changes direction mid-way ("make it a demo of the payouts page instead"), keep the current demo as a draft and start a new brief from what they said.

### 2. Explore

Open the site with Playwright using the saved session. Map the screens, the exact clicks and fields for the task, and anything that loads slowly. Don't change real data; stick to the test account.

### 3. Script

Split the video into short sections (about 15 to 35 seconds each). For each section write two lines:

- **Talking version** (what the voice says): how a person actually explains it out loud. Small restarts, reactions and opinions where the screen earns them; very few fillers.
- **Caption version** (what's shown): clean, short, no fillers.

Show both side by side and get approval before spending any credits.

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

See `docs/engine.md`. In short: generate one continuous take per section, get word timestamps, schedule each browser action at its word, record, hold frames when an action runs long, never pause the audio. Then scan the frames for anything the page-level blur missed.

### 7. Review

Open the local app on the Review step. The user marks moments (sounds like AI, needs a blur, too fast) or types notes. Show the redo cost, then redo only the marked sections. Log marks with the settings used so the voice defaults improve over time.

### 8. Export

Render the MP4 (1080p), captions (.srt) and a transcript, plus an optional 720p preview, into the user's videos folder. Name the files after the demo title.

## Your data

From Settings the user can remove the key (remind them to revoke it at ElevenLabs too), forget saved logins, reset settings, or delete everything NAVI saved. Finished videos are never touched. Uninstalling means deleting this skill folder as well.

## Files

- `ui/index.html`: the local app (open in a browser; `?start=home|voice|review|settings`, `&theme=light|dark`)
- `ui/app.js`: screens, state and sample data
- `docs/engine.md`: how recording, timing, blur and rendering work
