# Mouth sounds, breaths and creak

Research pass, 5 November 2026. **Findings only: not yet applied to `voice-rules.md` or `config/defaults.json`.** Citations in [sources.md](sources.md). The existing rule stands: human sounds come from the model, never from tags or effects (voice-rules.md, section 3).

## Breaths

| | Value | Source |
|---|---|---|
| Speech between breaths (breath group), reading | 3.50 s | Wang et al. 2010 |
| Breath group, spontaneous | 4.35 s | Wang et al. 2010 |
| In-breath length | 0.55 s (reading), 0.58 s (spontaneous) | Wang et al. 2010 |
| Pause around a breath | 0.65 to 0.70 s | Wang et al. 2010 |
| Breaths in grammatically odd places | 1.8% reading vs 13% spontaneous (3.2% vs 15.3%, Winkworth, cited) | Wang et al. 2010 |
| Breaths per minute, real casual demos | **10.3** [2.0–15.5] (that survived YouTube editing) | measured here |
| Breaths per minute, real scripted walkthroughs | 5.8 [2.2–10.5] | measured here |
| Breaths per minute, Alex test take | **1.5** | measured here |

- Most breaths fall before clause boundaries, and speakers breathe in more deeply before longer stretches (Winkworth et al.). Louder in-breaths come before longer speech, quieter ones before short bits (Włodarczak & Heldner).
- A breath taken to keep talking is shorter (about 0.35 s shorter, Hammarsten et al.) and quieter than one before a new turn.
- New turns start right at the start of the out-breath: about 65% within its first quarter (Rochet-Capellan & Fuchs).
- Adding breath noises to synthetic speech made it sound more natural and easier to remember (Whalen et al. 1995, Braunschweiler & Chen 2013, cited by Włodarczak et al.).

**The gap:** the Alex take has about one breath every 40 s; real casual narrators about one every 6 s, even after editing. Andy's best-rated moments in every round included the model's own breaths and mouth sounds.

## Tongue clicks

| | Value | Source |
|---|---|---|
| Average English speaker | about 4 per min (max 11) | Gold et al. 2013, cited |
| Keynote speaker with slides | 9.2 per min (top 3%) | Trouvain & Malisz 2016 |
| Real casual demos | 2.1 per min [0–7.2] | measured here |
| Real scripted walkthroughs | 0.5 per min [0–3.4] | measured here |
| Alex test take | 1.5 per min | measured here |

- **Clicks happen in pauses, late in the pause, just before speaking again** (Trouvain & Malisz). More than a third of the keynote's pauses had one. Never mid-phrase.
- **They travel with breaths and fillers:** 46% sat next to an in-breath (62% in Wright's data), 43% next to a filler.
- **They mark a new step:** 19 of 23 slide changes had a click within 2 s. Clicks also mark "I'm about to speak", the start of a new sequence, and a word search (Ogden 2013, 2018, 2020; Wright 2011).
- They are tiny: mean 40 ms, max 145 ms.
- Ogden separates planning clicks (getting ready to speak, word search) from stance clicks (disapproval). A demo voice wants only the first kind.

## Creak (vocal fry)

- **Creak marks phrase and turn ends** ("I'm done"), and longer stretches of creak mark sentence ends (Redi & Shattuck-Hufnagel, via secondary sources; Garellek). Ogden 2001: creak gives up the turn; a glottal stop holds it.
- More common in conversation than reading, more than twice as common in one study (Dallaston & Docherty review). Frequency varies a lot by speaker and dialect; no reliable single figure.
- Cut-off words often end in 20 to 50 ms of creak (Shriberg 1999).
- Not measured in the demos (no reliable detector here).

## Where these sounds come from in eleven_v3

The model makes them on its own when the text gives it reasons to: a pause it has to fill, a restart, a search, a section start. The two moments Andy liked most for mouth sounds were "to see what's done" (end of a thought, low and flat) and "there's, where is it" (a hunt). Breath and mouth sounds can't be added with tags (round 5). So the open question is which **wording** makes eleven_v3 breathe and click, which is what the experiments in the plan test.

## What this suggests for NAVI (proposed, not applied)

1. Write sections as breath groups of about 3.5 to 5 s of speech, each ending at a clause boundary, so the model has natural places to breathe. One slightly odd breath per section is realistic (13% of spontaneous breaths are in odd places).
2. Start a new step on a fresh sentence after a full stop ("Okay. So now…"), the spot where a click and an in-breath naturally go. *(Note, 2026-11-11: applied to every section this produced the same breath at every start; use it for at most one section a video. reference/listening/2026-11-11-everything-sounds-the-same.md)*
3. Keep the edit from removing any of it: never trim after a sentence (already a rule), and check that the 0.8 s pause cap isn't cutting breaths or clicks out of long pauses.
4. Wrap-up lines go low and flat at the end, where creak belongs. Don't put a bright, rising line last.
5. Measure breaths per minute on every take (target: at least 4 to 6 per minute; casual narrators 10).
