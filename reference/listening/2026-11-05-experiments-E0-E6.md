# Listening notes: voice experiments E0 to E6

Date: 5 November 2026. Listener: Andy. Texts: `examples/experiments/2026-11-05.json`. Audio stays on Andy's Mac in `output/experiments/2026-11-05/` (not in git). Voice: Alex, `[relaxed]` only, stability 0.7 unless the variant says otherwise. E1 to E6 on eleven_v3, E0 compares eleven_v3 with eleven_v4. Each file was the best of 2 takes as ranked by `scripts/research/measure_speech.py`, played under blind labels.

**No rules or defaults have been changed from these notes yet.**

## Andy's picks

- E0: X overall. Open: X, both good. Add and tick: both good, Y's ending is the problem. Filter and clear: X (Y's beginning and ending are off, its middle is good).
- E1: A is my favourite. B unnatural. C too enthusiastic. D: I like the "and yeah" phrasing, but "it's crossed out" goes high-pitched and AI-enthusiastic.
- E2: A is my favourite (the breaths sound like a byproduct of talking). B and C sound good, but the noise repeats too often. C is the weakest.
- E3: A and C. B is meh.
- E4: A, B and D good, D best. C no.
- E5: A and D, both amazing. C is okay. B had no unsure moment to judge.
- E6: L1 X, much better than Y. L2 both fine (good to have variation). L3 Y.

## Andy's note, verbatim

(Dictated and transcribed, so some wording may be off: "and year" is "and yeah", "anti-Y" is "and tick, Y", "why" is "Y".)

> Let's go with E0. I am edging more towards X for E0, but they're both okay. They're both pretty good. X is definitely over Y. For open and tick for E0, both of them are good, X and Y. The E0 and Y, the anti-Y section, the end of it is the only problem thing I've got a problem with, just by the ending.
>
> Okay, now for E0 filter and clear. For filter and clear, I am edging a bit more towards X for E0, but for Y, it's only just the ending that I'm not fucking with. Y was good as well, and also the beginning. I don't like the beginning of the filter and clear for why, and also the end, but the middle was pretty good.
>
> Okay, now E1: click the little circle line in four wordings. B sounds unnatural, A sounds good. C is weird sounding, a bit too enthusiastic. I do like the "and year" phrasing for E1D, but then it's crossed out and sounds really weird, high-pitched, and AI-enthusiastic. A for E1 is pretty good. That's kind of what I think is my favourite.
>
> E2: B sounds good. B and C sound good, but the kind of noise it makes is good every now and then. It happened too many times, repeatedly. I do like the A as well. I love bits and pieces from all three. I love how, with A, when he's talking, you could kind of hear the breaths almost as a byproduct of him speaking. I do like that. I like A. I like kind of all of them, but I don't like C. I like parts of C. I believe I forgot my opinions about B, but I like A.
>
> I like C for E3, and I also like A for E3. B is meh, and it's okay.
>
> E4: A and B sound good for E4. I don't like C, and I love D. I love B, and I love A for the restarts.
>
> E5: A sounds good. There wasn't really any unsure thing to judge for B. B sounds good, but there is no unsure sound. E5C is kind of okay. E5A sounds good. Amazing. E5D sounds amazing as well. I love A and D.
>
> E6: For the call the dentist line, X is superior, way more superior than Y. For E6 L2, X and Y both work. It's good to have variation. They're both good. E6 L3, this is a hard one. Y sounds better for sure.

## What each label was

| Label | Variant | Andy | Meter rank in its experiment |
|---|---|---|---|
| E0 open X / Y | **eleven_v4** / eleven_v3 | X, both good | meter preferred v3 |
| E0 add X / Y | **eleven_v4** / eleven_v3 | both good, Y's ending off | meter preferred v3 |
| E0 filter X / Y | **eleven_v4** / eleven_v3 | X | meter preferred v4 |
| E1 A | "you just click the, uh, little circle…" (filler before the noun) | **favourite** | 1st |
| E1 B | original line | unnatural | 3rd |
| E1 C | "if I click the little circle… it just gets crossed out" | too enthusiastic | 4th |
| E1 D | "…next to it, and yeah, it's crossed out" | likes "and yeah"; "it's crossed out" goes high | 2nd |
| E2 A | sentence ending on a spoken web address | **favourite**, breaths as a byproduct of talking | 3rd |
| E2 B | one long run-on, then a full stop | good, breath noise too repeated | 2nd |
| E2 C | short clipped sentences | weakest | 1st |
| E3 A | "Right, so, …" | good | 2nd |
| E3 B | "So now, …" | meh | 1st |
| E3 C | "Okay. So now, …" | good | 3rd |
| E4 A | "the, the menu" | good | 3rd |
| E4 B | "it's, it's in the left column" | good | 4th |
| E4 C | "You- you just drag" (cut-off word) | no | 2nd |
| E4 D | "I'm, uh, I'm gonna" | **best** | 1st |
| E5 A | "there's, where is it, Clear completed" | **amazing** | 2nd |
| E5 B | "there's actually a button for it" (no hunt, by design) | no unsure moment | 4th |
| E5 C | "there's, hang on, it's, yeah, Clear completed" | okay | 1st |
| E5 D | "there's, where's the, um, Clear completed" | **amazing** | 3rd |
| E6 L1 X / Y | stability **0.7** / 0.8 | X much better | meter preferred 0.7 |
| E6 L2 X / Y | stability 0.8 / 0.7 | both fine | meter preferred 0.8 |
| E6 L3 X / Y | stability 0.7 / **0.8** | Y | meter preferred 0.7 |

## What it shows (Claude's reading, for discussion)

- **eleven_v4 won E0 by ear** (preferred or equal in all three sections). Alex is fully trained for v4 and not for v3.
- **The meter and the ear agreed on the top pick in E1 and E4 only.** It ranked Andy's least favourite first in E2 (short sentences) and E3 ("So now"), and missed the two "amazing" hunts in E5. On single lines it rewards low, flat, slow delivery, and that isn't enough to tell natural from flat. Use it to flag problems (a clean instruction line that's fast and swingy), not to choose the best take.
- **Stability 0.8 is not a fix for pitch swing:** better on one line, worse on one, equal on one. 0.7 stays.
- Wording that worked: a filler just before the noun being named ("the, uh, little circle"); "I'm, uh, I'm gonna" and "the, the" restarts; a hunt written as self-talk ("where is it", "where's the, um"); "Okay. So now" and "Right, so" to start a step; a sentence that runs on into something spoken like an address.
- Wording that didn't: cut-off words ("You- you"); "if I click…" framing; "and yeah, it's X" as the last words (goes high); clipped short sentences.
