# Voice rules: how NAVI makes an AI voice sound like a person

Read this before writing any talking script and before generating any voice. Every rule here comes from blind listening rounds on a real walkthrough (five voice rounds, then two full video drafts). Where a rule was tested, the round is noted. Where something is still unsolved, it says so.

The short version: **the text matters more than the voice, the voice reads each section in one go, and the human sounds come from the model, not from tags.**

---

## 1. The talking script (the biggest lever)

Each section has two versions: the **talking version** the voice reads, and a **clean caption version**. Everything below is about the talking version. Captions stay clean, short and correctly spelled.

### Talk, don't read
- Write how someone actually explains their screen out loud: contractions, "gonna", "kind of", "basically", short opinions ("Honestly? Leave it open."). Tidy written prose gets read like written prose. *(Stage 1 audit: the cleanest section sounded least human.)*
- Use the second person and the present: "you hit Add", "it asks what you're here for".
- Give opinions and reasons, not just steps. "Delays kind of just annoy people" sounds like someone who has done this.

### What worked best (keep doing these)
- **Name a common mistake, then correct it from what you checked.** "You'd think the app lives in the app store, right? It, well, it didn't when we checked." *(Loved in the v2 video review.)*
- **Short live reactions to what appears on screen.** Two or three words, said as the thing appears: "Okay, chapters." Flat, not excited. *(Loved in v1 and v2.)*
- **One small restart or repeated word per section, not more.** "You- you just drag the handle." "Each, uh, each module is basically a course card." These read as a real person thinking. *(Script v2, kept through every round.)*

### Fillers
- **Very few, and only where the screen earns them.** Realism comes from pace, reactions, restarts and opinions, not from an "um" in every sentence. *(Rounds 2 to 4.)*
- **A filler is never a word.** Written as its own sentence, or followed by "…", the model gives it weight and length, and it sounds fake. Put it inside the flow of a sentence: "because, uh, it's a demo". *(Round 2: "they're treating the filler words as their own words, which they're not".)*
- **Size fillers and pauses to what's happening on screen.** A quick aside while explaining gets a quick, throwaway filler. Hunting for a button or a tab gets a longer, searching one, written into the line: "scroll down to, where is it, File attachments". *(Round 2: the main point. "The variation in speed based on what the demo is showing is what we're missing.")* See section 6 for how the engine supports this.
- **Mumbling to yourself** ("okay, okay, where are the settings?") is allowed in casual and SaaS demos only, at a real hunting moment, at most once or twice a video. Not in course walkthroughs or product tours. *(Round 5 note.)*

### Lines to avoid
- **Cheerful one-word lines.** "Easy." "There we go." "There it is!" read as fake joy. Use flatter phrasing: "yeah, that's it", "and it's in the left column", "and it's saved". *(Rounds 3 to 5.)*
- **Polished, upbeat summary lines.** "and you'll have opened it the way a buyer would" was the most hated line of the project. Plain beats clever: "and you've clicked through it on your laptop and your phone". *(Round 4.)*
- **Tacked-on clauses.** A fragment added after a list ("Modules, chapters, lessons, every file's got its home") gets read as a new sentence and sounds bolted on. When a sentence carries on, write it so it leans on the one before. Avoid long runs of added-on clauses. *(v2 review.)*

### The opening
- **The first 30 to 40 seconds decide whether people stay.** Keep the open short (about 10 to 12 seconds), start on the app doing something, and give every sentence its own visual beat. *(v1 and v2 reviews: the opening was the rough part both times.)*
- **Something changes on screen at least every 4 to 5 seconds.** If a line runs longer than that over a still screen, cut it or split it. *(v1: a 21-second talk over one still image.)*

### Punctuation is delivery
- Full stops fall. Commas lift slightly. Every comma tends to become a pause, so use fewer commas in lists and let casual lines run on. *(Stage 1 audit.)*
- Don't use "…" for a hesitation. It stretches the word before it instead of adding a pause. *(Round 2 measurements.)*
- Casual lines and "right?" can lift or trail. Only the last line of a section lands down. *(Round 3.)*

### Names the voice gets wrong
- Respell brand or product names **in the talking version only** when the model mispronounces them, and keep the real spelling in captions. The model guesses pronunciation fresh each time, so the same take can say a name two ways. Test spellings by ear. *(Round 4 and 5: one brand name was said two different ways in one take until respelled.)*
- Read web addresses the way people say them: "whop dot com slash start".

---

## 2. Generating the voice

| Setting | Rule | Why |
|---|---|---|
| Model | ElevenLabs eleven_v3 | Best natural delivery in testing |
| Reads | **One continuous read per section.** Never split a section into sentence or beat-sized clips. | Round 3: the split "beats" version was rejected outright ("so AI"). Splitting also trims away the breaths and mouth sounds that make it human. |
| Stability | Start at **0.7** for the recommended voice | Round 4: 0.7 beat 0.6. Lower stability added drastic tone swings and fake cheer. |
| Opening tag | **`[relaxed]`** at the start of each section, nothing else | `[casually]` came out too happy; `[matter-of-fact]` was mixed. |
| Other tags | **None.** No `[inhales]`, `[exhales]`, `[clears throat]`, `[coughs]`, `[sighs]`. Don't rely on `[short pause]`. | Round 5: `[inhales]` was ignored, `[exhales]` came out as a dramatic sigh or the word "Phew", and the forced sounds were judged staged. `[short pause]` worked in only half the takes. |
| Speed | 1.0 (the pace slider moves it within 0.94 to 1.08) | Walkthroughs are never sped up afterwards. |
| Takes | 2 per section; keep the one closest to the approved reference in pace and tone | The model varies a lot between takes. |
| Word timings | Get them locally from the finished take (Whisper family), not from a second API call | Needed to time the clicks; avoids extra credits. |
| Context | Never pass `next_text` or neighbouring text, and never generate sentences separately and stitch them | Both make every sentence sound like it's about to carry on, then stops. |
| Picking takes | Rank by how finished the section's last sentence sounds (`scripts/audio/finality.py`), then confirm by ear | Pitch checks alone passed takes a listener heard as unfinished. |

---

## 3. Human sounds: keep them, never fake them

- **The model's own breaths, tongue clicks, mouth sounds and slight rasp are the strongest "this is a person" signals.** The best-reviewed stretch of the whole project was "amazing, mainly due to the breathing and the mouth sounds". *(v2 review; rounds 3 to 5.)*
- **Keep unprompted breaths.** The single most-liked moment was a small breath the model added on its own after a web address. *(Round 5.)*
- **Never add them with tags or effects.** Tagged breaths, coughs and throat clears sound staged.
- **Exhales must not be dramatic.** A long or sharp exhale sounds like the speaker is fed up with explaining. *(Round 5.)*
- The breaths slider only controls how much of the model's own breathing survives the edit (trimmed, natural, kept). It never adds breaths.

---

## 4. Editing the audio

- **Never trim right after a sentence.** The tongue clicks and breaths live there. *(Round 3: the split version lost almost all of them to edge trimming.)*
- Only shorten silences longer than 0.8 s, cutting from the middle and leaving at least 250 ms after the last word.
- If a take ends while the last word is still sounding, add a short fade (about 150 ms) into room tone. Skip the fade if the take ends cleanly.
- Find the real end of speech from the audio, not the timing data: eleven_v3's timings run the last word to the end of the file. Never add reverb to fake a decay.
- Gentle treatment only (`scripts/audio/treat.py`): de-ess 5 to 8 kHz, high shelf −2.5 dB above 8 kHz, light 2:1 compression, voice at −16.4 LUFS, limiter at −2.5 dBFS.
- Faint room tone under everything (about −62 LUFS, band-limited to 90 Hz to 2.5 kHz), so gaps never drop to digital silence. **No music bed** in a walkthrough. *(v1 review.)*
- Gap between sections: about 0.35 to 0.45 s, placed where the screen changes step.

---

## 5. Kind of demo changes the amount, not the rules

| Kind | Feel | Human touches |
|---|---|---|
| Course walkthrough | Calm, clear, a little more structured | Restarts and reactions yes; few fillers; no mumbling |
| Quick SaaS demo | Casual, a bit quicker, like showing a friend | More hesitations; a quick mumble at a real hunt is fine; one light swear at a natural reaction if the user allows it |
| Product tour | Cleanest takes, fewest mistakes | Still breaths, mouth sounds and the odd reaction; almost no fillers |

In every kind, the human things (breath, voice texture, small restarts, thought changes) stay. Cleaner means fewer mistakes, not a different person. *(Round 5 note.)*

---

## 6. Fillers that follow the screen (engine requirement)

The voice model can't see the screen, so it reads a paragraph at one steady rate. This is the main thing still separating "good" from "human". *(Round 2.)*

How NAVI handles it without splitting reads:
1. When the script is written, tag every browser action as **explain**, **click**, **hunt** or **wait** (page load).
2. Hunt moments get the searching written into the line ("where is it,"), so the model slows down there by itself.
3. Long waits (page loads, processing) fall **at section boundaries**: the section ends, the load plays at real speed under room tone, and the next section starts once the page has settled. The voice is never paused mid-read to wait for the screen.
4. Explain beats are written tight; nothing is padded.

Splitting reads into separately generated beats with a library of filler clips was tried and rejected (round 3). Don't go back to it.

---

## 7. Voices

- **Recommended now: Alex** (a professional voice clone in the ElevenLabs library), stability 0.7, `[relaxed]`. Best of every voice tested.
- Tested and rejected for sounding read, hyped or announcer-like: Will, Chris, Liam, and four shared-library conversational voices.
- Open issue: Alex can sound "too perfect", like a polished YouTube voice most people don't have. A rougher voice or lighter processing may fix it. Untested.
- Female voices haven't been tested yet. Any new voice starts at Alex's settings and is judged by ear before it's offered as recommended.

---

## 8. The quality bar

A section is done when someone who knows it's AI listens and can't point to the moment it gives itself away. Not when the file renders. Every new complaint from a review becomes a rule in this file or a value in `config/defaults.json`, so the same mistake can't come back.
