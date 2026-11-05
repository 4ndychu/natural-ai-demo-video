# Listening notes: Phase 1 voice test ("A simple to-do list")

Date: 5 November 2026. Listener: Andy. Status: **not approved yet.** Andy is deciding, with his own Claude chat, whether NAVI needs more study of real human speech and behaviour patterns before going further. No rules or defaults have been changed from these notes yet.

## Andy's note, verbatim

> After the box up top, between, and then it says "Call the dentist," right? The voice sounds like it's okay. It's not exceptional. It sounds quite... "Call the dentist." I guess it could sound a lot more natural, and I guess there could be some mouth sounds before that. I don't know. I think we might need to get some more training on human speech and behaviour patterns.
>
> "Hit Enter." "Okay, it's on the list." Sounds incredibly AI. After "Hit Enter," the "it's on the list" quote, "I'll add a couple more," seems AIish as well. "Okay, pay the gas bill" sounds AI, but then the "book the" sentence sounds really realistic. The way it drags out, it sounds really good.
>
> "Okay, the book the train ticket section sounds really good. No complaints." The "click the little circle next to it" sounds incredibly AI. The tone's completely off. "Okay, down at the bottom, you could switch to just the active ones." That sentence sounds really good.
>
> "Okay, everything else, like the 27- to 30-second range, sounds pretty decent. It's okay, it's okay, it's nothing good." The "to see what's done after that," I like the little mouth sound drag it did. The "where is it" sentence, the way that fits in, is really good, and even a little bit of mouth sound to that as well. It sounds exceptional. It's good.
>
> Over on the right, "Okay, yeah, now it's just okay." That's my current verdict for these things. Take this note down, and we will also send this note down verbatim and put it somewhere. Let me know where you listen to it, and I'll talk to my Claude chat. I think we may need, potentially, what could boost this. Me and my Claude chat will decide whether we need more training on human data and speech patterns as well, potentially more lessons, maybe.

(The note was spoken and transcribed, so some quotes are approximate; for example "you could switch" is "you can switch" in the script.)

## What was played

- Script: `examples/test-todo.json` (3 sections). Track: `output/test-todo/voice.wav`, 39.5 s. Audio stays on Andy's Mac (output/ is not in git).
- Voice: Alex ("Alex - Warm Conversational Business", `hLygPNd2gK6Azddorc5W`), eleven_v3, `[relaxed]` only, stability 0.7, speed 1.0, one continuous read per section, 2 takes each.
- Takes used: section 1 take 1, section 2 take 2, section 3 take 2 (auto-picked by the most finished ending). Edit: no pauses shortened (none over 0.8 s), gaps 0.39 s and 0.35 s, treated to -16.4 LUFS, synthetic room tone at -62 LUFS.

## Each comment against the track

Times are word starts in `voice.wav`. The verdicts are Andy's; the "what was happening" column is Claude's reading of the timings.

| Time | Words | Andy's verdict | What was happening |
|---|---|---|---|
| 3.1-4.5 s | "box up top, call the dentist" | OK, not exceptional; wants it more natural, maybe mouth sounds before "call the dentist" | Read straight through at an even rate; 0.5 s between "top," and "call" |
| 5.2-6.5 s | "hit Enter and it's on the list" | Incredibly AI | Fast, even, tidy; section 1 runs at 3.9 words/s, the quickest of the three |
| 7.5-9.6 s | "I'll add a couple more so there's something to work with" | AI-ish | Even, clean delivery |
| 10.7-11.6 s | "Pay the gas bill" | AI | Even, clean delivery |
| 12.9-16.0 s | "and book the, uh, book the train tickets" | **Really realistic; the drag sounds really good. No complaints.** | Uneven timing: 1.2 s from "the," to "uh," and 0.7 s from "uh," to the repeated "book". The one restart in the script. |
| 18.7-23.3 s | "click the little circle next to it and it gets crossed out" | Incredibly AI; tone completely off | Even, clean delivery |
| 24.0-28.3 s | "Down at the bottom you can switch to just the active ones" | **Really good** | |
| ~27-30 s | "or just the completed ones. I'd just leave it on Active" | Pretty decent, "okay", nothing special | |
| 31.3-31.9 s | "to see what's done" | **Likes the small mouth-sound drag** | The model's own mouth sound; no tag asked for it |
| 34.2-35.8 s | "there's, where is it, Clear completed" | **Exceptional**, fits in really well, with a little mouth sound | The hunt written into the line (voice-rules.md section 6); 0.9 s from "there's," to "where" |
| 36.8-38.9 s | "over on the right. Now it's just the two left." | Just okay | |

## Pattern (Claude's reading, for discussion, not yet a rule)

Every moment Andy praised is somewhere the timing goes uneven: a restart, a hunt, a drag, or a mouth sound the model added on its own. Every moment he called AI is a clean, evenly paced instruction or a tidy wrap-up line. This matches what `reference/voice-rules.md` sections 1 and 6 already say ("The variation in speed based on what the demo is showing is what we're missing"), and suggests the plain instruction lines are now the weakest part.
