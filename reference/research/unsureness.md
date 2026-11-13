# Unsureness: how not knowing sounds

Research pass, 5 November 2026. **Findings only: not yet applied to `voice-rules.md` or `config/defaults.json`.** Citations in [sources.md](sources.md).

## What the research says

- **Unsureness is mostly timing.** In Smith & Clark 1993, correct answers came after 1.08 s and wrong ones after 6.16 s. A filler before the answer added 5.06 s on average. 24% of answers had a filler before them: 17% of correct answers, 39% of wrong ones.
- **Um signals a longer wait than uh.** At the very start of an answer:

  | | uh | um |
  |---|---|---|
  | silence before | 2.54 s | 3.70 s |
  | silence after | 1.00 s | 4.12 s |
  | time to the answer | 2.65 s | 8.83 s |

- **A slight rise.** Rising intonation on 44% of wrong answers vs 21% of right ones (Smith & Clark). Listeners rated speakers as less sure after a filled pause, a rise or a longer delay (Brennan & Williams 1995). Unsure adults also used more fillers and delays and higher intonation (Krahmer & Swerts 2005).
- **Hedges are rare.** "I guess" in 11 of 1000 answers, "I think" in 4, "or something" in 4 (Smith & Clark).
- **Self-talk while searching is the real pattern:** comments to yourself ("oh, who was that?"), repeating part of the question, and a trial answer before the real one.

## What the real demos show

- Self-talk and hedges: **0.9 per minute** in casual demos (range 0.4 to 2.6), **0** in scripted walkthroughs.
- The most common by far is **"actually"** (36 times in 63 minutes), then "I think" (15), "probably" (6) and "maybe" (3). Searching phrases are rare: "let's see" twice, "where did the" once, "how do I" once. A real "where is it" moment comes up about once every 20 to 30 minutes of casual narration.
- Long pauses (over 1 s) in mid-clause: **1.4 per minute** in casual demos, 0.2 in scripted, **0 in the Alex take**. That's the timing that signals searching or thinking, and the Alex take has none.

## Against Andy's verdict

"there's, where is it, Clear completed" was rated "exceptional". In the take it runs at 2.5 words a second (the take's average is about 4), 3.1 semitones below the take's average pitch, with a 0.44 s pause. Slow, low, a short pause: the timing profile the research describes, which the model produced by itself from the wording.

## What this suggests for NAVI (proposed, not applied)

1. Write a hunt as **self-talk**, then land the target cleanly ("there's, where is it, Clear completed"). It worked first time. Use it at real hunting moments only: once or twice per video, matching how rare it is in real demos.
2. Prefer **"actually"** and the odd **"I think"** for small unsure moments. Real narrators use them about once a minute in casual demos. Avoid stacking hedges.
3. Let the pause before a found target run long. Real casual narrators have about 1.4 pauses over 1 s per minute. The current 0.8 s pause cap (voice-rules.md, section 4) may be shortening exactly these: check before cutting any pause next to a hunt.
4. A slight rise on the first try at a name ("Clear completed?") then a flat confirmation is the natural pattern, but don't write a "?" on every hunt; the model over-lifts.
