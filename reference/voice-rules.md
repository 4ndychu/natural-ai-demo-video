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
- **One small restart or repeated word per section, not more.** Repeat a small word with the stall between the two copies: "book the, uh, book the train tickets", "I'm, uh, I'm gonna", "the, the menu", "it's, it's in the left column". Never cut a word off ("You- you just drag"): it sounded fake. Two slips in a 40-second stretch already sounds nervous. *(Script v2; experiments E4 and A/B, 2026-11-05.)*
- **A filler just before the name of the thing on screen.** "you just click the, uh, little circle next to it" beat every other wording of that line. About a third of real casual narrators' fillers sit there, between "the", "to" or "about" and the noun. *(Experiment E1; reference/research/casual-vs-scripted.md.)*
- **Start a new step with "Okay. So now," or "Right, so,".** Both beat a bare "So now,". *(Experiment E3.)*
- **Write a hunt as self-talk, then land the target cleanly:** "there's, where is it, Clear completed" and "there's, where's the, um, Clear completed" were both rated amazing. Real narrators do this rarely (about once every 20 to 30 minutes), so use it at real hunting moments only. *(Experiment E5; reference/research/unsureness.md.)*
- **Let a sentence run on.** A long sentence that carries into something spoken, like a web address, made the breaths sound "like a byproduct of talking". Clipped short sentences were the weakest. *(Experiment E2.)*

### Fillers
- **Very few, and only where the screen earns them.** Realism comes from pace, reactions, restarts and opinions, not from an "um" in every sentence. *(Rounds 2 to 4.)*
- **A filler is never a word.** Written as its own sentence, or followed by "…", the model gives it weight and length, and it sounds fake. Put it inside the flow of a sentence: "because, uh, it's a demo". *(Round 2: "they're treating the filler words as their own words, which they're not".)*
- **Size fillers and pauses to what's happening on screen.** A quick aside while explaining gets a quick, throwaway filler. Hunting for a button or a tab gets a longer, searching one, written into the line: "scroll down to, where is it, File attachments". *(Round 2: the main point. "The variation in speed based on what the demo is showing is what we're missing.")* See section 6 for how the engine supports this.
- **Mumbling to yourself** ("okay, okay, where are the settings?") is allowed in casual and SaaS demos only, at a real hunting moment, at most once or twice a video. Not in course walkthroughs or product tours. *(Round 5 note.)*

### Lines to avoid
- **Cheerful one-word lines.** "Easy." "There we go." "There it is!" read as fake joy. Use flatter phrasing: "yeah, that's it", "and it's in the left column". *(Rounds 3 to 5.)*
- **Don't announce the result of an action.** "and it's on the list", "so that's on the list now" and "and it's saved" all read as cheerful, whatever their pitch: the screen already shows it. Stop on the action ("…and hit Enter."), understate it ("…so that's one."), or move on. Real narrators rarely narrate a result (about once every 9 minutes in casual demos, almost never in scripted ones). *(Ending test 4, 2026-11-05: "so that's on the list now" measured low and still sounded too upbeat; reference/research/casual-vs-scripted.md.)*
- **Polished, upbeat summary lines.** "and you'll have opened it the way a buyer would" was the most hated line of the project. Plain beats clever: "and you've clicked through it on your laptop and your phone". *(Round 4.)*
- **"and yeah, it's X" as the last words of a line.** "and yeah" is good mid-line, but "it's crossed out" after it went high and enthusiastic. *(Experiment E1.)*
- **"If I click…" framing** sounded unnatural, even though real narrators use it. *(Experiment E1.)*
- **Bright wrap-up lines that end on a rise,** like "hit Enter and it's on the list": still human, but too enthusiastic. *(A/B, 2026-11-05.)*
- **Tacked-on clauses.** A fragment added after a list ("Modules, chapters, lessons, every file's got its home") gets read as a new sentence and sounds bolted on. When a sentence carries on, write it so it leans on the one before. Avoid long runs of added-on clauses. *(v2 review.)*

### The opening
- **The first 30 to 40 seconds decide whether people stay.** Keep the open short (about 10 to 12 seconds), start on the app doing something, and give every sentence its own visual beat. *(v1 and v2 reviews: the opening was the rough part both times.)*
- **Something changes on screen at least every 4 to 5 seconds.** If a line runs longer than that over a still screen, cut it or split it. *(v1: a 21-second talk over one still image.)*

### Punctuation is delivery
- Full stops fall. Commas lift slightly. Every comma tends to become a pause, so use fewer commas in lists and let casual lines run on. *(Stage 1 audit.)*
- Don't use "…" for a hesitation. It stretches the word before it instead of adding a pause. *(Round 2 measurements.)*
- Casual lines and "right?" can lift or trail. Only the last line of a section lands down. *(Round 3.)*
- **The last line of a section ends low.** A plain statement that trails off, not a bright result or a rising wrap-up: "So now there's just the two left up top", "so that's on the list now", "you don't really need to see what's done". Every ending Andy called AI rose at the end ("and it's on the list", "Now it's just the two left", the second one "AI slop"); every one he liked ended low. The end of a step is lower, quieter and a little faster in real direction-giving too. *(Ending tests 1 to 3, 2026-11-05; Hirschberg & Nakatani 1996.)*
- **A closing word is allowed, written falling with a full stop:** "…the two left, okay." or "all right." or "so yeah." Never "okay?": a question mark invites a rise. Real speakers close a step with "okay" or "all right" (61% of Lego build steps, Bangerter & Clark 2003). *(Andy, 2026-11-05.)*
- **Closers can't repeat, and most sections don't need one.** "so that's one", "so yeah", "okay." and "all right." are each used at most once or twice per video, and never the same one twice in a row. Most sections just stop on the action, with no closer at all. *(Andy, 2026-11-05.)*
- **Never a filler as the last word.** "uh" and "um" come before the next thing, so ending on one sounds unfinished. *(Clark & Fox Tree 2002.)*
- **"Ends low" is a guide, not a gate. The ear decides.** In ending test 4 Andy picked "…so that's one." (last word 6.8 semitones above the floor) and "…and hit Enter." (9.1) over "…so yeah." (2.1, the lowest). Measure endings to catch a clear rise (10 semitones or more was always disliked), then judge by ear.
- **Check every ending by measuring it, then by ear.** The same wording can land low in one take and rise in the next. Across the three ending tests, these landed low (within 4 semitones of Alex's floor) in: "so that's … now" 3 of 4 takes; "…, okay." 2 of 2; "…up top" 1 of 2 (picked twice by ear); "…down here" 2 of 2; "…now, so yeah" 1 of 2; "…now." 1 of 2; "…in the list" 0 of 2. `scripts/audio/finality.py` measures it.

### Naming things on screen
- **The first time something comes up, give its name plus where it is or what it looks like:** "Export, the little arrow top right". After that, just the name: "hit Export". Real explainers do this for newcomers and drop it as they go (words per item fell from about 16 to 6); listeners don't mind the extra detail. *(Isaacs & Clark 1987, Engelhardt et al. 2006; reference/research/asides-and-examples.md.)*
- **Add a check on tricky steps:** "you should see a green tick", "if it's greyed out, you haven't saved yet". A video is the case where nobody can ask, and recorded instructions went wrong 39% of the time against 5% face to face. *(Clark & Krych 2004.)*
- Course walkthroughs keep the fuller descriptions longer and add one recap per module. Product tours give one clear description per feature, with no repeats.

### Asides, tangents and examples (PROVISIONAL)
**Starting values, not settled rules.** They rest on our own coding of 18 demo videos (one coder, small sample) plus the research in reference/research/asides-and-examples.md, and haven't been judged by ear yet. Change them freely after the first listening.

| | Quick SaaS demo | Course walkthrough | Product tour |
|---|---|---|---|
| **Asides** | About one per minute, at most one per section. One clause, about 4 s, **right after an action**, reacting to it. | About one every 2 to 3 minutes, flagged ("quick side note,"). | About one per video. |
| **What an aside says** | An opinion, a reason, a warning or a shortcut about what's on screen. Never padding. | A reason or a warning. | A reason or a benefit, plainly. |
| **Way back** | "but", "so" or "anyway", then straight to the next action. | "so" or "anyway". | No marker needed. |
| **Real-world examples** | At most one per video under 5 minutes, one sentence. Personal ("I use this for…") **only if the user's brief gives it.** | One per module: a user or customer case ("say you're a teacher…"), or a personal one from the brief. | About the user ("say you run a small shop…"), never "I". |
| **Tangents** | None in a video under 5 minutes. | None. | None. |

- **Never invent personal history.** A first-person story the user didn't give is a made-up claim in their voice.
- Say "I think" and "you know" inside the phrase, not set off by commas ("it's I think the second tab"): three-quarters of real ones are. *(Dehé 2009.)*
- Real casual narrators: 0.7 asides, 0.25 examples and 0.08 tangents per minute (scripted: 0.2, 0.4, 0.04). Tangents run about 28 s, far past the 4 to 5 s screen-change rule, which is why there are none.
- How to write an aside: see the aside test in section 2.

### Swearing
- **Off by default in every kind of demo.** Real screen-demo narrators almost never swear (one "suck" in 48 minutes of casual demos), and in how-to videos each swear cut engagement by up to 6.5%. *(reference/research/swearing.md.)*
- When the user turns it on: **One** means one per video. **A few** means at most one per 2 minutes, and never more than 2 in a video.
- **Only at a slip or a surprise** ("oh, damn, it's moved"), or for emphasis aimed at the product or the step ("it would suck to lose all that"). In real speech, most swears come right as the speaker catches their own mistake. Never inside an instruction, a number or a warning, and never at the viewer.
- **Quick SaaS demos only.** Course walkthroughs, product tours and sponsored or brand videos: never.
- Mild words only (damn, hell, sucks, "oh my god"). Captions stay clean.

### Names the voice gets wrong
- Respell brand or product names **in the talking version only** when the model mispronounces them, and keep the real spelling in captions. The model guesses pronunciation fresh each time, so the same take can say a name two ways. Test spellings by ear. *(Round 4 and 5: one brand name was said two different ways in one take until respelled.)*
- Read web addresses the way people say them: "whop dot com slash start".

---

## 2. Generating the voice

| Setting | Rule | Why |
|---|---|---|
| Model | **ElevenLabs eleven_v4** by default. eleven_v3 stays as an option for anyone who needs speed control. | 2026-11-05: v4 was preferred over v3 overall in a blind comparison (equal or better in every section). The same text that was "okay, not exceptional" on v3 scored 7 to 9 out of 10 on v4. Alex is fully trained for v4 and not for v3. |
| Reads | **One continuous read per section.** Never split a section into sentence or beat-sized clips. | Round 3: the split "beats" version was rejected outright ("so AI"). Splitting also trims away the breaths and mouth sounds that make it human. |
| Stability | Start at **0.7** for the recommended voice | Round 4: 0.7 beat 0.6. Lower stability added drastic tone swings and fake cheer. 2026-11-05: 0.8 didn't calm the pitch swing (better on one line, worse on one, equal on one). |
| Opening tag | **`[relaxed]`** at the start of each section, nothing else | `[casually]` came out too happy; `[matter-of-fact]` was mixed. |
| Other tags | **None.** No `[inhales]`, `[exhales]`, `[clears throat]`, `[coughs]`, `[sighs]`. Don't rely on `[short pause]`. | Round 5: `[inhales]` was ignored, `[exhales]` came out as a dramatic sigh or the word "Phew", and the forced sounds were judged staged. `[short pause]` worked in only half the takes. |
| Speed | eleven_v4 has no speed setting: pace comes from the script wording. On eleven_v3, 1.0, and the pace slider moves it within 0.94 to 1.08. | Walkthroughs are never sped up afterwards. |
| Takes | 2 per section; keep the one closest to the approved reference in pace and tone | The model varies a lot between takes. |
| Word timings | Get them locally from the finished take (Whisper family), not from a second API call | Needed to time the clicks; avoids extra credits. |
| Context | Never pass `next_text` or neighbouring text, and never generate sentences separately and stitch them | Both make every sentence sound like it's about to carry on, then stops. |
| Picking takes | Rank by how finished the section's last sentence sounds (`scripts/audio/finality.py`), then confirm by ear | Pitch checks alone passed takes a listener heard as unfinished. |
| Asides | **Write an aside between commas, inside the sentence:** "So you click Export, which honestly took me ages to find, and pick MP4 from the list." Use its own sentence only when it should stand apart more. | Aside test, 2026-11-05 (2 takes each, eleven_v4; measured, not yet judged by ear): in every take the aside dropped 2.7 to 4.0 semitones below the main line, its pitch swing halved (about 5 st against 10), and the voice stepped back up 2 to 4 st after it, as real asides do. Between commas it ran straight in with no pause and slightly faster than the main line, the closest to real speech; as its own sentence it dropped most but added 0.4 to 0.6 s pauses either side; dashes sat in between. |
| Measuring takes | `scripts/research/measure_speech.py` flags problems (a clean line that's fast with a wide pitch swing, no pauses, no breaths). It doesn't pick the best take. | 2026-11-05: it agreed with Andy's top pick in only 3 of 7 experiments. On short lines it rewards flat and slow, which isn't the same as natural. |

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
- **Never shorten a pause at a hunt moment** ("where is it", "where's the, um", "hang on"). Real casual narrators have about 1.4 pauses over 1 s per minute, mostly when searching, and the long pause is what makes the search sound real. *(reference/research/casual-vs-scripted.md; agreed 2026-11-05.)*
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
| Quick SaaS demo | Casual, a bit quicker, like showing a friend | More hesitations; a quick mumble at a real hunt is fine; a light swear only if the user turns it on (section 1, Swearing) |
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

- **Recommended now: Alex** (a professional voice clone in the ElevenLabs library), eleven_v4, stability 0.7, `[relaxed]`. Best of every voice tested. Check which models a voice clone is trained for before using it (`/v1/voices/<id>`, `fine_tuning`): Alex is trained for v4 and not for v3.
- Tested and rejected for sounding read, hyped or announcer-like: Will, Chris, Liam, and four shared-library conversational voices.
- Open issue: Alex can sound "too perfect", like a polished YouTube voice most people don't have. A rougher voice or lighter processing may fix it. Untested.
- Female voices haven't been tested yet. Any new voice starts at Alex's settings and is judged by ear before it's offered as recommended.

---

## 8. The quality bar

A section is done when someone who knows it's AI listens and can't point to the moment it gives itself away. Not when the file renders. Every new complaint from a review becomes a rule in this file or a value in `config/defaults.json`, so the same mistake can't come back.
