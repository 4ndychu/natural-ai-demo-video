# Phase 5 export review, 8 November 2026

What Andy watched: `~/Movies/NAVI/A simple to-do list (version B).mp4` (burned-in captions, Helvetica Neue on square boxes) and the same with a corner label.

## Andy's notes (verbatim)

> Phase 5 nearly approved. Fix before I approve:
>
> 1. Captions must never stay up while the voice has moved on. Each caption shows only while its own words are spoken; if the clean caption is much shorter than the speech, split it into more caption lines that follow the speech, or end it when its words end. Max 2 lines on screen.
> 2. Add an export option for a sped-up copy at a chosen speed (I use 1.35× for my course; pitch must stay natural). Off by default; when on, export both the normal and the sped-up file.
> 3. Show me one frame with two caption looks side by side: the current one (Helvetica Neue, square boxes) and Mona Sans with slightly rounded boxes. I'll pick.
>
> Then on to Phase 6.

## What changed because of it

1. **Captions follow the speech** (`scripts/render/captions.py`):
   - Each caption starts 0.1 s before its first word and ends 0.3 s after its last.
   - A caption word that the voice doesn't say sits next to the word it belongs with, for about as long as it takes to say. It's never stretched over other speech. Before this fix, "tasks." was stretched over 8 s of "Pay the gas bill, and book the train tickets".
   - Where the voice says other things for more than 1.5 s between two caption words, the caption splits there. Joining words ("and press") go with the words after them.
   - While the voice says things the clean caption leaves out, nothing is on screen.
   - At most 2 lines. Checked: every caption is gone 0.2 s after it ends.
2. **Sped-up copy** (`export.py --speed 1.35`, or `"speed_copy": 1.35` in the script; `export.speed_copy` in the settings, off by default):
   - Exports both files: `<title>.mp4` and `<title> (1.35x).mp4`, plus a sped-up `.srt`.
   - The voice keeps its pitch through ffmpeg `atempo`. Measured: 138 Hz becomes 139 Hz (+0.16 semitones). A plain speed-up would be +5.2 semitones.
   - Rubber Band would sound slightly better at high speeds, but it isn't in this ffmpeg and would need an install. Not done; to ask Andy if 1.35x doesn't sound natural.
3. **Two caption looks** (`on_screen.caption_look`):
   - `helvetica-square`: drawn by ffmpeg's subtitle renderer. The default until Andy picks.
   - `mona-rounded`: Mona Sans on slightly rounded boxes, drawn by the browser (`scripts/render/caption_png.mjs`).
   - Both are matched in text size and box colour. The side-by-side frame is `output/phase5/caption-looks-side-by-side.png`.

## Andy's decision (verbatim)

> 1. Caption look: B (Mona Sans, rounded). Make it the default.
> 2. Phase 5 approved.
> 3. Phase 6 approved.

**Phase 5 and Phase 6 approved, 8 November 2026.** The caption look is now `mona-rounded` by default (`config/defaults.json` `on_screen.caption_look`). Helvetica Neue on square boxes stays as an option.
