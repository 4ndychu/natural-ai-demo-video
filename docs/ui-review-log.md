# UI review log

The hill climb from `docs/UI_BRIEF.md`. Each round, three reviewer subagents (first-time user, visual design, interaction QA; Opus, medium effort) score every screen out of 10 from screenshots at 1440 px wide @2x in light and dark, plus 390 px. A judge (Opus, high effort) settles disagreements and ranks the fixes. Target: every screen 8.5 or higher from all three reviewers.

Screenshots: `docs/screens/before/` (round 0) and `docs/screens/after/` (final round).

## Round 0: before the redesign

| Screen | User | Visual | QA | Min |
|---|---|---|---|---|
| welcome | 7.0 | 7.5 | 7.0 | 7.0 |
| home | 6.0 | 5.5 | 5.5 | 5.5 |
| new | 4.5 | 4.5 | 4.0 | 4.0 |
| script | 4.5 | 4.0 | 4.0 | 4.0 |
| voice | 5.0 | 5.0 | 4.0 | 4.0 |
| privacy | 4.5 | 4.5 | 3.5 | 3.5 |
| record | 6.0 | 5.5 | 5.0 | 5.0 |
| review | 3.5 | 4.0 | 3.5 | 3.5 |
| export | 6.5 | 7.0 | 6.5 | 6.5 |
| settings | 6.0 | 6.0 | 5.0 | 5.0 |

Cross-cutting problems: the chat bar covered content on six screens (including the Remove and Forget all buttons in Settings); every screen broke at 390 px; dark-mode switches and segmented controls didn't show their state; there were two black primary buttons; the focus ring was weak. Welcome, export and settings had no 390 px shots in this round.

Main fixes the judge ranked (on top of the brief's eight changes): reserve a band for the chat bar; a real phone layout; one primary button (header New demo is now an outline pill); fixed switch and segment states in dark mode; footers that match their buttons and give the reason for a disabled button; a darker focus ring that isn't white in dark mode; state-dependent primary on Review; a corner picker instead of a five-option segment; Settings split into trays with the key shown once.
