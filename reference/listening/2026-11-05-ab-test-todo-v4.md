# Listening notes: A/B of the test script on eleven_v4

Date: 5 November 2026. Listener: Andy. Spec: `examples/experiments/2026-11-05-ab.json`. A = original text (`examples/test-todo.json`), B = version B (`examples/test-todo-b.json`). Both: Alex, eleven_v4, stability 0.7, `[relaxed]`, raw takes (no edit, treatment or room tone), best of 2 takes by `measure_speech.py`, played blind as X/Y per section. Audio in `output/experiments/2026-11-05-ab/` (not in git).

**No rules or defaults have been changed from these notes yet.**

## Ratings

| Section | X | Y | Andy's score | Andy's issue |
|---|---|---|---|---|
| 1 Open | B | A | both about 7 to 8 / 10 | "it's on the list" ending a bit too enthusiastic in both |
| 2 Add and tick | B | A | both about 8.5 to 9 / 10 | can't hear much difference |
| 3 Filter and clear | A | B | A about 8 to 8.5, B about 8 / 10 | none named; "I'd just leave it on Active" in X still sounds good |

Phase 1 (eleven_v3, same text as A) was rated "okay, not exceptional", with several lines called "incredibly AI".

## Andy's note, verbatim

(Dictated and transcribed, so some wording may be off.)

> Okay, let's dictate this ship. Let's go with section 1.
>
> X and Y sound very similar. They're both good. The main issue with both is the ending. The "it's on the list" sentence is always, I don't know. It still sounds human, but it's a bit too enthusiastic for my liking. I guess that's just down to taste. I give it around 7 to 8 out of 10 for both.
>
> Now let's see section 2. X is like an 8.5 to 9. I like it. The same for Y. They sound quite similar. Maybe it's just my hearing. I can't really spot too much of a difference.
>
> Now let's see section 3. The middle of section 3 on X: the limiter pinpoints the phrase, but I just leave it on active. It still sounds good. It maybe is just down to my preference. I still give X for section 3 maybe an 8.5 or 8. For Y, I'd give it an 8 as well. It's really hard to judge because they're all so good in their own ways. By the way, I'm pretty sure all of these are good. I forgot my other ratings for the previous sections, but all of them sound good.

## What it shows (Claude's reading, for discussion)

- **A and B tie.** On eleven_v4 the wording changes made no clear difference; all six files scored 7 to 9.
- **The model switch is what moved it.** The same text as A went from "okay, not exceptional" with lines called "incredibly AI" (eleven_v3, Phase 1) to 7 to 9 out of 10 on eleven_v4. Alex is fully trained for v4 and not for v3.
- **One remaining giveaway:** "hit Enter and it's on the list" ends too enthusiastically, in both versions. It's the last words of section 1, a bright, up-ending wrap-up line.
