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

## Rounds 1–7: after the redesign

Round 1 is the first full redesign (all eight brief changes). Rounds 2–7 apply the judge's ranked fixes from the round before. From round 1 on there are 13 screens: New demo is split into `new`, `new-options` and `new-batch`, and `batch` is new.

Minimum score per screen (the lowest of the three reviewers) by round:

| Screen | R0 | R1 | R2 | R3 | R4 | R5 | R6 | R7 |
|---|---|---|---|---|---|---|---|---|
| welcome | 7.0 | 7.0 | 8.0 | 8.0 | 8.0 | 8.0 | **8.5** | 8.0 |
| home | 5.5 | 7.0 | 7.5 | 7.5 | 8.0 | 8.0 | 8.0 | 8.0 |
| new | 4.0 | 7.0 | 6.5 | 7.5 | 7.5 | 8.0 | 8.0 | 7.5 |
| new-options | – | 6.5 | 6.5 | 7.0 | 7.5 | 8.0 | 7.5 | 7.5 |
| new-batch | – | 7.0 | 6.5 | 7.0 | 7.5 | 7.5 | 7.5 | 7.0 |
| batch | – | 6.5 | 7.0 | 7.5 | 6.5 | 7.5 | 7.5 | 7.0 |
| script | 4.0 | 6.0 | 7.0 | 7.5 | 7.5 | 7.5 | 7.5 | 7.5 |
| voice | 4.0 | 6.0 | 7.0 | 7.0 | 7.0 | 7.5 | 7.8 | 7.0 |
| privacy | 3.5 | 7.5 | 8.0 | 8.0 | 8.0 | **8.5** | 8.3 | 7.5 |
| record | 5.0 | 7.0 | 7.5 | 7.5 | 7.5 | 7.0 | 7.5 | 7.0 |
| review | 3.5 | 7.0 | 7.0 | 7.5 | 7.5 | 8.0 | 7.8 | 7.0 |
| export | 6.5 | 6.5 | 7.5 | 7.5 | 7.5 | 8.0 | 8.0 | 7.5 |
| settings | 5.0 | 7.0 | 7.0 | 7.5 | 7.5 | 8.0 | 8.0 | 7.5 |
| **Average minimum** | **4.8** | **6.8** | **7.2** | **7.4** | **7.5** | **7.9** | **7.8** | **7.4** |

### Round 7 (final), all three reviewers

| Screen | User | Visual | QA | Min |
|---|---|---|---|---|
| welcome | 8.5 | 8.4 | 8.0 | 8.0 |
| home | 8.5 | 8.2 | 8.0 | 8.0 |
| new | 8.6 | 8.1 | 7.5 | 7.5 |
| new-options | 8.0 | 7.8 | 7.5 | 7.5 |
| new-batch | 8.2 | 8.0 | 7.0 | 7.0 |
| batch | 8.2 | 8.0 | 7.0 | 7.0 |
| script | 8.7 | 8.5 | 7.5 | 7.5 |
| voice | 7.9 | 8.4 | 7.0 | 7.0 |
| privacy | 8.7 | 8.5 | 7.5 | 7.5 |
| record | 8.6 | 8.1 | 7.0 | 7.0 |
| review | 8.4 | 8.3 | 7.0 | 7.0 |
| export | 8.3 | 8.2 | 7.5 | 7.5 |
| settings | 8.6 | 8.3 | 7.5 | 7.5 |

### Why it stopped

The stop rule was "every screen 8.5 from all three reviewers, or two rounds in a row improve nothing." Round 6 was flat (7.9 → 7.8) and round 7 dropped (7.8 → 7.4), so the climb stopped there. No screen reached 8.5 from all three in the final round.

- **What dropped in round 7:** almost all of it came from the interaction QA reviewer, who scored nearly every screen 0.5–1 point lower than in round 6. The first-time-user and visual reviewers stayed flat or rose.
- **What QA got right:** some round 6 phone fixes had not landed. The step rail still showed a cut-off letter at its left edge, and the welcome image showed only hair. Both are fixed in the final build (verified by measuring in the browser).
- **Changed after the round 7 scores (not re-scored):** the rail edge, the welcome image crop on phones, and removing the Casualness value chip that two reviewers read as a stuck tooltip.

### Open points the reviewers keep raising

- **Phone widths:** the remaining nitpicks are wrapping, empty space on a few screens, and the footer buttons on New batch, Batch, Record and Review.
- **The "nothing moves when you click" rule:** the chat bar sits centered on the content column on step screens, so it shifts sideways between Home and a demo. The judge kept it (it's a page change, not a click on the same page), but it's a taste call for Andy. The button press shrink and the card hover lift were removed.
- **"Some":** the middle "Who's watching" option was shortened from "Some experience" to "Some". One reviewer finds it vague.
