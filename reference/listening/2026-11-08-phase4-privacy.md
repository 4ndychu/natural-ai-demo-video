# Phase 4 privacy review, 8 November 2026

What Andy checked: the privacy test videos (`output/privacy-test/casual.mp4`, `recordly.mp4`), made from the fake dashboard in `examples/privacy-test/`, plus the to-do demo in both styles.

## Andy's notes (verbatim)

> I'm liking Casual style a lot. Make Casual the default video style; Recordly style stays as an option.
>
> Phase 4 approved (I had the privacy videos checked independently with a different OCR at 10 fps: nothing private was readable). Add a plain reminder in Review to watch every video before publishing, and suggest test accounts plus the hide-words box.
>
> I'll record a 10-second Recordly clip with default settings for the side-by-side comparison when I get a chance. Carry on with the next phase meanwhile.

**Phase 4 approved, 8 November 2026.** It was checked twice: by NAVI's own test (Apple's text recognition, 6 frames a second) and independently by Andy (a different OCR, 10 frames a second). Nothing private was readable either time.

## What changed because of it

- **Casual style is the default** (`config/defaults.json` `recording.style`). Recordly style stays as an option (`record.py --style recordly`, or `--restyle recordly` from the same recording).
- **Reminder in Review:** `privacy.md` and `privacy.json` (`reminder`) start with: watch every video before publishing, use a test account with fake data, and add names or words that must never show to the hide-words box. Passed to the UI thread in `docs/UI_BRIEF.md` 7c.
- **Still to do:** compare NAVI's Recordly style with Andy's 10-second clip from the real Recordly app (default settings) once he records it.
