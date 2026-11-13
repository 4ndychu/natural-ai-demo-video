# Disfluency: fillers, repeats and restarts

Research pass, 5 November 2026. **Findings only: not yet applied to `voice-rules.md` or `config/defaults.json`.** Full citations in [sources.md](sources.md). Read alongside [casual-vs-scripted.md](casual-vs-scripted.md): pace and pitch matter more than anything in this file.

## How much

| Source | Setting | Fillers per 100 words | Repeats | Restarts / other repairs | All disfluencies |
|---|---|---|---|---|---|
| Bortfeld et al. 2001 | Conversation, all | 2.56 | 1.47 | 1.94 | 5.97 |
| Bortfeld et al. 2001 | The person giving instructions ("director") | 3.30 | | | 7.00 |
| Oviatt 1995 (cited in Bortfeld) | Monologue | | | | 3.60 |
| Map Task (measured here) | Instruction giver, all | 1.50 (uh 0.66, um 0.76) | 1.32 | 1.77 restarts, 0.62 substitutions | 4.14 |
| Map Task (measured here) | Instruction giver, "instruct" moves only | 1.31 | 1.24 | 1.64 restarts | 4.03 |
| DisfluencySpeech (measured here) | US phone chat, re-performed | 3.04 (uh 2.27, um 0.45) | 1.97 | 1.41 + 0.19 fresh starts | |
| **Real casual screen demos (measured here)** | One person narrating their screen | **2.8** [0–6.1] (uh 1.6, um 1.2) | 0.56 | 0.24 cut-off words | |
| **Real scripted walkthroughs (measured here)** | Scripted narrator | **0** [0–0.6] | 0.05 | 0 | |
| Alex test take | Phase 1 | 0.8 | 0.8 | 0 | |

- People differ hugely. Clark & Fox Tree found 1.2 to 88.5 fillers per 1000 words (median 17.3). Map Task givers run from 0 to 7.45 per 100 words (middle 80%: 0.29 to 3.29). Two of the ten casual narrators used no fillers at all.
- A partner who can't see the screen raises rates: instruction givers are about 40% higher than followers (Bortfeld). A demo narrator is an instruction giver, but with no live listener, which pushes the other way (monologue 3.6 vs dialogue 5.5 to 8.8).
- Speech aimed at a machine is very fluent (0.78 to 1.87 disfluencies per 100 words, Oviatt). That is the register a TTS voice falls into by default.

## Where fillers go

- **At the start of a unit, or just before the name of a thing.** Map Task: 53% of um and 39% of uh are the first word of a dialogue move. Clark & Fox Tree: 43 per 1000 words at an intonation-unit boundary, 27 after the first word, 13 later. In the casual demos about a third of fillers come right after "the", "to", "about" or "into", just before the noun naming something on screen ("go to the, uh, Chrome store").
- **Um opens; uh interrupts.** Um is 56% of boundary fillers but only 37 to 39% of fillers inside a unit (Clark & Fox Tree).
- **Fillers attach to the word before** ("and-uh", "the, uh"), never to the word after (Clark & Fox Tree §8). That's why a filler written as its own sentence sounds wrong (voice-rules.md, round 2).
- **Uh vs um mix.** Casual demos: about 58% uh. Clark & Fox Tree: the median speaker splits 52/48, but on answering machines (closest to talking at a recorder) 76% uh. DisfluencySpeech (US): about 5 uh per um.

## What follows a filler

| | After uh | After um | Source |
|---|---|---|---|
| Followed by a delay | 29% | 61% | Clark & Fox Tree (London-Lund) |
| Followed by a delay | 33% | 69% | Clark & Fox Tree (answering machines) |
| Pause after, median | 0 ms | **342 ms** | Map Task, measured here |
| Pause after, mean | 237 ms | 530 ms | Map Task |
| Pause after > 200 ms | 29% | 60% | Map Task |
| Pause before, median | 110 ms | 256 ms | Map Task |
| Filler length | 327 to 344 ms | 384 to 527 ms | cited in Clark & Fox Tree |

- **Um means "a real pause is coming"; uh runs straight on.** Listeners recognise the next word faster after an uh (Fox Tree 2001).
- A drawn-out filler ("u:m") is preceded by a pause 48% of the time vs 28% for a short one: it signals "I've already been stuck for a bit."

## Repeats

- **Repeat small words, never nouns.** Function words are repeated 25.2 per 1000 vs 2.4 for content words; "I'm" 56 per 1000, subject pronouns 54, object pronouns about 0 (Clark & Wasow). Most repeated in Map Task: the, you, I, a, just, it's, to, I'm, you're. In DisfluencySpeech: I, and, the, it's, that. In the casual demos: and, the, I, on, that, it's.
- **One word, mostly.** 68% of Map Task repetitions are one word, 21% two. 82% one word in DisfluencySpeech.
- **The stall goes between the two copies.** Pauses per 1000 repeats: 43 before the first copy, 218 between, 43 after the second (Clark & Wasow). The first copy is drawn out, about 2.5 times the length of the second (Shriberg). "and book the, uh, book the train tickets" fits exactly, and was the line Andy rated "really realistic".
- **Repeats cluster at the start of complex phrases and before negatives** (twice as often before can't, wasn't), and right after a filler or pause: with a filler, the next function word is repeated 21 to 47% of the time (Clark & Wasow).
- The gap between the copies in Map Task: median 92 ms, mean 220 ms.

## Restarts and cut-off words

- **Restarts happen at the start of a unit.** In Map Task, 47% of restarts are on the first word of a move (vs 14.5% of all words): three times over-represented.
- Speakers restart from the start of the phrase, not mid-phrase (Clark & Wasow).
- Cut-off words: 1.45 per 100 words in Map Task, 0.24 in the casual demos (with YouTube editing). They often end in 20 to 50 ms of creak (Shriberg 1999).

## What this suggests for NAVI (proposed, not applied)

1. **Fillers per style come from the real demos:** quick SaaS demo 1.5 to 2.8 per 100 words (start low), course walkthrough 0 to 1, product tour 0 to 0.5. Never more than the real casual median (2.8), because a written filler gets over-pronounced (round 3).
2. Write **uh** inside a phrase, attached to the word before, just ahead of naming something on screen ("go to the, uh, settings"). Write **um** only at the start of a clause, where a real pause should follow.
3. One **repeat** per section is about right for a casual demo (casual narrators: 1 per minute). Repeat a small word (the, I, it's, you, and), stall between the copies, and land on the content word. Never repeat nouns.
4. Put restarts at the start of a sentence or clause, and at hard moments (naming something, a negative), not in easy connecting phrases.
