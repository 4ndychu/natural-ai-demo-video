# Casual vs scripted: what real demo narration measures like

Research pass, 5 November 2026. **Findings only: nothing here has been applied to `voice-rules.md` or `config/defaults.json` yet.** Sources and licences: [sources.md](sources.md).

## The short version

**Pace and pitch are the main lever, not fillers.** Compared with real narrators, the Alex test take reads one phrase after another at the same speed, with the same wide "presenting" pitch swing inside each phrase and too few pauses. Casual narrators vary their speed and pitch level a lot from phrase to phrase but keep each phrase fairly flat, and they pause unevenly. Fillers matter for the casual style, but even there they come out of hesitation and naming things, not decoration.

## What was measured

- **20 real screen demos**, all CC BY on YouTube: 10 casual and unscripted (one person narrating their own screen, mostly developers and teachers) and 10 polished, scripted walkthroughs (one narrator: WordPress, Moodle, Audacity, Blender, Zotero, Range, PurelyHR and others). About 63 min casual and 53 min polished. The first 10 min of each video were used; 8 videos used the first 5 min only (transcription ran slower than expected).
- **Verbatim transcripts** from CrisperWhisper 2.0 (keeps uh, um, repeats and cut-off words, with word timings).
- **From the audio:** phrases are stretches between pauses over 0.3 s. Pace = words per second per phrase. Pitch tracked every 10 ms. Breaths and tongue clicks found inside pauses (rough; see caveats).
- **Baseline:** the Phase 1 Alex take (`examples/test-todo.json`, 40 s), measured the same way.

Flags: Sascha D. Kasper's Obsidian video sounds partly read, and CMU's Zotero video had no fillers at all; both are counted as casual as planned, and both sit at the polished end of the casual range.

## The numbers

Median across the videos in each group, with the range in brackets.

| | Casual (n=10) | Scripted (n=10) | Alex test take |
|---|---|---|---|
| **Pace variation** between phrases (coefficient of variation) | **0.25** [0.20–0.34] | 0.19 [0.16–0.21] | **0.15** |
| **Pitch level change** from phrase to phrase (SD, semitones) | **2.35** [1.84–3.07] | 1.85 [1.15–2.83] | **1.76** |
| **Pitch swing inside a phrase** (10th–90th percentile, semitones) | **5.3** [3.0–8.6] | 8.2 [4.7–10.2] | **8.8** |
| Overall pitch range (semitones) | 8.4 [6.1–11.5] | 9.4 [6.4–11.7] | 9.6 |
| Words per minute, including pauses | 161 [128–200] | 156 [135–209] | **186** |
| Words per second inside a phrase | 4.19 [3.52–4.84] | 3.83 [3.27–4.42] | 4.12 |
| Share of word gaps over 200 ms | 0.20 [0.17–0.35] | 0.18 [0.10–0.25] | **0.13** |
| Pause after a sentence, median | 0.41 s [0.13–1.18] | 0.82 s [0.62–1.39] | 0.36 s |
| How uneven those pauses are (coefficient of variation) | **0.93** [0.75–1.49] | 0.49 [0.32–0.82] | 0.71 |
| Sentences run straight on (pause under 150 ms) | 23% [10–55%] | 0% [0–16%] | 18% |
| Long pauses (over 1 s) in mid-clause, per min | **1.4** [0–2.8] | 0.2 [0–0.6] | **0** |
| Fillers per 100 words (uh + um) | **2.8** [0–6.1] | **0** [0–0.6] | 0.8 |
| of which uh / um | 1.6 / 1.2 | 0 / 0 | 0.8 / 0 |
| Fillers per minute | 5.1 [0–9.0] | 0 [0–1.2] | 1.5 |
| Repeats per minute ("the the", "I I") | 1.0 [0–3.0] | 0.1 [0–0.6] | 1.5 |
| Cut-off words per 100 words ("m-", "th-") | 0.24 [0–0.85] | 0 [0–0.2] | 0 |
| Self-talk and hedges per minute | 0.9 [0.4–2.6] | 0 [0–1.2] | 1.5 |
| Breaths per minute (that survived editing) | **10.3** [2.0–15.5] | 5.8 [2.2–10.5] | **1.5** |
| Tongue clicks before speaking, per minute | 2.1 [0–7.2] | 0.5 [0–3.4] | 1.5 |

What stands out:
1. **Alex varies less than even the scripted narrators.** Pace variation 0.15 is below every scripted video (lowest 0.16), and far below casual (0.25). Pitch level from phrase to phrase (1.76) is at the scripted level.
2. **Alex swings pitch like a presenter inside every phrase** (8.8 semitones, the scripted profile), where casual narrators stay flatter inside a phrase (5.3) but move the whole phrase up or down. This matches Blaauw's finding that read speech has a stable, middle-of-the-road prosody, and that casual talk is narrower in range ([sources.md](sources.md)).
3. **Alex is fast overall (186 wpm) because it barely pauses** (13% of gaps over 200 ms vs 20%, and no long mid-clause pauses at all). Inside phrases it isn't faster than casual narrators.
4. **Real casual pauses are uneven:** a quarter of sentences run straight into the next one, others get a second or more. Scripted narrators leave a tidy 0.8 s after almost every sentence.
5. **Breaths: 10 a minute in casual demos vs 1.5 in the Alex take.**

## What the papers say about read vs spontaneous speech

- **Listeners spot read speech from its prosody alone:** 77 to 79% correct on fluent utterances with no disfluencies at all (Blaauw 1995). Read speech has a stable, middle-of-the-road prosody; spontaneous speech departs from it in either direction, and the departure itself sounds spontaneous.
- In spontaneous **instruction monologues** (closest to a demo), speech was slower than the same words read back (5.2 vs 5.8 syllables a second), with more pitch range (13.9 vs 11.7 semitones). In casual interviews it was the other way round: faster and narrower. The real demos here look like the second kind (flatter phrases, more variation between them).
- **Swapping the whole prosody** (pitch, durations and loudness) between read and spontaneous versions flipped what listeners heard; swapping only one of them weakened it (Laan 1992).
- How phrase boundaries are spread out and marked (pause, pitch movement, or both) predicts whether speech is heard as read (Blaauw 1994).

## The Alex take, line by line, against Andy's verdict

From Andy's listening note ([../listening/2026-11-05-phase1-test-todo.md](../listening/2026-11-05-phase1-test-todo.md)). Pitch is relative to the take's median; swing is inside the line.

| Line | Andy | Words/s | Pauses in it | Pitch | Swing |
|---|---|---|---|---|---|
| hit Enter and it's on the list | incredibly AI | 3.95 | 0 s | +0.3 st | 7.6 st |
| I'll add a couple more so there's something to work with | AI-ish | 4.47 | 0.30 s | −0.4 st | 10.1 st |
| Pay the gas bill | AI | 4.08 | 0 s | +2.4 st | 8.9 st |
| click the little circle next to it and it gets crossed out | incredibly AI | 4.23 | 0.42 s | +0.8 st | 7.4 st |
| and book the, uh, book the train tickets | really realistic | **1.73** | **1.40 s** | −1.4 st | **2.4 st** |
| Down at the bottom you can switch to just the active ones | really good | 4.41 | 0 s | +0.8 st | **5.4 st** |
| to see what's done | likes the mouth-sound drag | 3.85 | 0 s | **−2.6 st** | **5.2 st** |
| there's, where is it, Clear completed | exceptional | **2.50** | 0.44 s | **−3.1 st** | 8.7 st |

Every line Andy called AI is quick (about 4 to 4.5 words a second) with a wide, presenting pitch swing. Every line he praised is either much slower, or lower and flatter, or both. Wording isn't what separates them: "you just click the little circle" uses the most common casual action phrasing of all (below). The delivery is.

## How people phrase actions while doing them

Per minute of narration.

| Phrasing | Casual | Scripted |
|---|---|---|
| "you can / you just / you'll / you want to X" | 0.75 | 0.63 |
| "I'm going to / I'm gonna / I'll / let me X" | **0.33** | 0.11 |
| "let's X" ("let's go ahead and add…") | **0.32** | 0.13 |
| "if / when I click X, (then) Y" | **0.32** | 0.17 |
| bare imperative ("click X", "go to X") | 0.11 | **0.38** |
| "we can / we'll X" | 0.11 | 0.04 |
| narrating the result ("there it is", "now it's open") | 0.11 | 0.02 |

- **Casual narrators talk about what they are doing** ("so if I go into, uh, say the home page, we should see the logs"; "and if I click on options, then I can configure…"). **Scripted narrators give instructions** ("click on login"). Bare imperatives are 3.5 times more common in scripted videos.
- **"There it is" and "there we go" are rare in both** (about once every 9 minutes in casual demos), which backs the existing rule against cheerful one-word lines.
- **"Go ahead and"** is a common casual filler phrase ("let's go ahead and add some insights from here").
- **Fillers land on the name of the thing on screen.** About a third of casual fillers come right after "the", "to", "about" or "into" and before the noun: "go to the, uh, Chrome store", "it's about, uh, YouTube", "go into, uh, say the home page". The speaker is finding the word for what they're looking at.

Verbatim examples (casual set):
- "So from here, um, let's go down and find our line chart insight." (Dasheroo)
- "And it's gonna show me, um, the diff, the the difference between what's on GitHub currently and what I have on my side." (Totally Unscripted)
- "So, uh, first things first, I'm gonna show you how to record video." (Bryce Vandegrift)
- "That's also simple, uh, you th- firstly you open up the notes with open." (nobiot)
- "These are all fake numbers, um, that, uh, Google automatically randomized for me." (Dasheroo)

## Proposed numbers per kind of demo (not applied; for Andy to agree)

| | Quick SaaS demo (casual) | Course walkthrough | Product tour |
|---|---|---|---|
| Pace variation between phrases | ≥ 0.22 (casual 0.25) | ≥ 0.20 | ≥ 0.19 (scripted 0.19) |
| Pitch swing inside a phrase | ≤ 6 st | ≤ 7 st | ≤ 8 st |
| Pitch level change phrase to phrase | ≥ 2.2 st | ≥ 2.0 st | ≥ 1.85 st |
| Mid-clause pauses over 1 s | 1 per min | about 1 per 2 min | rare |
| Fillers per 100 words | 1.5 to 2.8 (Map Task instruction-giver 1.5, casual median 2.8) | 0 to 1 | 0 to 0.5 |
| Repeats or restarts | 1 to 2 per min | about 1 per min | under 0.5 per min |

Filler numbers come from the real demos, but start at the low end: a written filler is read by the model as a word, so it gets more weight than a real one (round 3). The pace and pitch targets are what to check every take against.

## Caveats

- 20 videos is a small sample, mostly men, with various accents. YouTube editing removes some pauses and breaths, so the casual "run-on sentences" share (23%) and breath counts partly reflect editing.
- CrisperWhisper assigns pauses around fillers to the filler itself, so filler-pause lengths here read near 0; use the Map Task figures in [disfluency.md](disfluency.md) for those.
- Breath and click detection is a rough acoustic heuristic (no ground truth). Music beds and mouse or keyboard clicks can leak in; clicks are only counted in the last 0.6 s before speech resumes.
- The Alex take is 40 s, so its numbers are less stable than the 5-to-10-minute videos.
