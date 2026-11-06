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

---

# Second climb (from 5 Nov 2026)

New setup, following Andy's instructions:
- The reviewers and the judge run on Claude Opus at high effort.
- References are studied first (`docs/ui-references.md`), and the rubric and prompts are fixed (`docs/ui-review-rubric.md`).
- The reviewers were calibrated on the reference sites (`docs/ui-review-calibration.md`).
- Blind A/B comparisons decide what stays, with an overdesign guard on every round.
- The interaction reviewer clicks through the real flows with Playwright.
- Target: 9.5+ from every reviewer on every screen. Stop when that's reached, or after 3 rounds in a row with no comparison wins.

**Baseline:** Andy's four fixes, applied before round 1:
1. One sample demo, "Build it in Whop", on every step.
2. The chat bar is pinned in one place.
3. "Some experience" is back.
4. No swearing by default, and no swear in the copy.

## Round 1: baseline scores (no A/B yet)

| Screen | User | Visual | QA | Min |
|---|---|---|---|---|
| welcome | 9.0 | 9.0 | 7.5 | 7.5 |
| home | 8.5 | 8.5 | 8.0 | 8.0 |
| new | 9.0 | 8.5 | 8.0 | 8.0 |
| new-options | 8.0 | 8.0 | 8.5 | 8.0 |
| new-batch | 8.5 | 8.0 | 8.5 | 8.0 |
| batch | 8.0 | 8.0 | 6.5 | 6.5 |
| script | 8.5 | 8.0 | 7.5 | 7.5 |
| voice | 8.0 | 7.5 | 6.5 | 6.5 |
| privacy | 9.0 | 8.0 | 6.5 | 6.5 |
| record | 9.0 | 7.5 | 6.0 | 6.0 |
| review | 8.5 | 8.0 | 6.5 | 6.5 |
| export | 8.5 | 8.0 | 8.0 | 8.0 |
| settings | 8.5 | 8.0 | 7.0 | 7.0 |

Clicking through the real flows found bugs that the screenshots hid, and the judge reproduced all but one. Examples:
- Privacy's cost confirm was skipped.
- Batch "Watch" opened the wrong video.
- Focus was lost after pop-ups closed.
- Layout shifted on Voice and Record.

The judge ranked 15 fixes for round 2, interaction bugs first.

## Round 2: the judge's 15 fixes, decided by blind A/B

Each reviewer compared 44 shot pairs (old vs new, unlabelled, random order). The interaction reviewer also used two unlabelled copies of the app.

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| welcome | old | old | new | **Old wins: candidate reverted** |
| home | new | new | same | New stays |
| new | old | new | new | New stays |
| new-options | new | new | guard loss | New stays |
| new-batch | new | new | old | New stays |
| batch | old | new | new | New stays |
| script | old | new | new | New stays |
| voice | new | new | new | New stays |
| privacy | new | new | new | New stays |
| record | old | new | new | New stays |
| review | new | new | new | New stays |
| export (before export) | new | new | same | New stays |
| export | new | new | new | New stays |
| settings | new | new | new | New stays |

**Why Welcome lost:** a reserved empty band under the key field, and the card pinned high (far down a blank screen at 390). Round 3 restores the old Welcome layout and keeps the focus and Enter-key fixes.

**Scores (candidate)**

| Screen | User | Visual | QA | Min |
|---|---|---|---|---|
| welcome (reverted) | 8.0 | 8.0 | 8.5 | 8.0 |
| home | 8.5 | 8.5 | 9.0 | 8.5 |
| new | 8.5 | 8.5 | 8.5 | 8.5 |
| new-options | 8.5 | 8.5 | 8.5 | 8.5 |
| new-batch | 8.5 | 8.0 | 8.0 | 8.0 |
| batch | 8.0 | 7.5 | 8.0 | 7.5 |
| script | 8.5 | 8.5 | 8.5 | 8.5 |
| voice | 8.0 | 8.0 | 8.0 | 8.0 |
| privacy | 9.0 | 8.5 | 8.5 | 8.5 |
| record | 8.0 | 8.5 | 9.0 | 8.0 |
| review | 9.0 | 8.5 | 8.5 | 8.5 |
| export (before export) | 8.5 | 8.5 | 8.5 | 8.5 |
| export | 8.5 | 8.5 | 8.5 | 8.5 |
| settings | 9.0 | 9.0 | 8.5 | 8.5 |

The minimums moved from 6.0–8.0 to 7.5–8.5. Using the app, QA scored the new version much higher than the old one: record 6.0 → 9.0, review 5.5 → 8.5, batch 5.5 → 8.0. Round 3: the Welcome revert plus 12 ranked fixes.

## Round 3: Welcome revert plus 12 fixes, decided by blind A/B

The previous accepted version is round 2 with Welcome reverted (commit 3d3ed4e). The candidate is that plus fixes 1–12. The connection dropped during QA's review, but its file had already been saved in full (44 A/B rows), so it wasn't re-run.

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| new, new-options, batch, record, export (before export), export | new | new | new | New stays |
| new-batch | new | new | new | New stays (but all three preferred the old image at 390: a regression, fixed in round 4) |
| voice | new | new | guard loss | New stays (2 of 3). QA's guard: picking Swearing pushed content 60 px at 390 |
| script | new | old | new | New stays (2 of 3) |
| settings | old | new | new | New stays (2 of 3) |
| home, privacy, review, welcome | same | same | same | Tie. The images are identical; the behaviour fixes stay because they fix verified bugs and no reviewer found a regression |

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 2 |
|---|---|---|---|---|---|
| welcome | 9.0 | 8.0 | 8.5 | 8.0 | 0 |
| home | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| new | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| new-options | 8.5 | 8.0 | 8.5 | 8.0 | −0.5 |
| new-batch | 8.0 | 7.0 | 7.5 | 7.0 | −1.0 |
| batch | 8.5 | 8.5 | 8.5 | 8.5 | +1.0 |
| script | 9.0 | 8.0 | 9.0 | 8.0 | −0.5 |
| voice | 9.0 | 8.5 | 8.5 | 8.5 | +0.5 |
| privacy | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| record | 9.0 | 8.5 | 8.5 | 8.5 | +0.5 |
| review | 8.5 | 8.5 | 8.5 | 8.5 | 0 |
| export (before export) | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| export | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| settings | 9.0 | 8.5 | 9.0 | 8.5 | 0 |

The User reviewer now gives 9.0 to 12 of 14 screens. The gap to 9.5 is mostly Visual (corner radii, weights, dark contrast) and QA (one click-time shift per screen).

The New batch drop comes from one round-3 regression: an inline `flex-basis` that turns into a 440 px tall row on phones. It is fix 1 for round 4.

**Checkpoint after 3 rounds:** shown to Andy (`docs/screens/climb2/`).

## Round 4: 12 fixes, decided by blind A/B

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| welcome, new-options, script, record, review, export (before export), export | new | new | new | New stays |
| new, new-batch, batch, voice | old | new | new | New stays (2 of 3) |
| privacy | new | old | new | New stays (2 of 3) |
| settings | new | new | old | New stays (2 of 3) |
| home | same | same | same | Tie |

No guard hits on the candidate. Every dissent was traced to a specific cause. Each is fixed in round 5, except one:
- **Batch (U):** the list starts at #3, and the footer is cut off at 390.
- **New (U):** the defaults line lost "Using:". It comes back at 1440 only.
- **Voice (U):** the greyed captions switch had no explanation.
- **Privacy (V):** an empty band at 390.
- **Settings (Q):** focus landed under the chat bar.
- **New batch (U):** wanted a faded 8th line back as a scroll cue. Not a regression, so nothing changes; V and Q prefer whole lines.

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 3 |
|---|---|---|---|---|---|
| welcome | 9.0 | 9.0 | 9.0 | 9.0 | +1.0 |
| home | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| new-options | 8.5 | 9.0 | 9.0 | 8.5 | +0.5 |
| new-batch | 9.0 | 8.5 | 8.5 | 8.5 | +1.5 |
| batch | 8.5 | 8.5 | 8.5 | 8.5 | 0 |
| script | 9.0 | 9.0 | 9.0 | 9.0 | +1.0 |
| voice | 8.5 | 9.0 | 9.0 | 8.5 | 0 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| record | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| review | 8.5 | 9.0 | 9.0 | 8.5 | 0 |
| export (before export) | 9.0 | 9.0 | 8.5 | 8.5 | 0 |
| export | 9.0 | 9.0 | 8.5 | 8.5 | 0 |
| settings | 9.0 | 9.0 | 8.0 | 8.0 | −0.5 |

The average minimum rose from 8.3 to 8.6. Four screens score 9.0 on every lens.

The Visual reviewer's main block to 9.5 is type weights: it wants two weights only, 400 plus 560 for the wide caps. QA's is the last few click-time shifts (Export, Settings).

## Round 5: 12 fixes (including two-weight type), decided by blind A/B

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| batch, new-options, voice, settings, export (before export), export | new | new | new | New stays |
| new, script, record, privacy | new | new | same | New stays (2 of 2, with one same) |
| new-batch, review | old | new | new | New stays (2 of 3) |
| home | old | new | same | **No majority: reverted** |
| welcome | same | new | same | **Only one vote for new: reverted** |

**What was reverted:**
- **Home:** the stretched setup card (User: big gaps between its rows), and the two-weight type on Home. The radius cleanup, the balanced title wraps at 390, the "All set · Check setup" line at 390 and the proportional credit figures stay. They fix earlier verified defects, and no reviewer saw them as regressions.
- **Welcome:** the "Optional." and hairline changes, and the two-weight type on Welcome.

**Override by Claude, per Andy's explicit instruction:**
- **"Some experience":** round 5 shortened this pill to "Some" at 390, against Andy's fix 3. Round 6 restores "Some experience" at every width.
- **"Familiar":** the judge suggested this as a replacement. It is rejected for the same reason.

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 4 |
|---|---|---|---|---|---|
| welcome (reverted) | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| home (partly reverted) | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| new-batch | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| batch | 9.0 | 9.0 | 8.5 | 8.5 | 0 |
| script | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| voice | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| record | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| review | 8.5 | 9.0 | 8.5 | 8.5 | 0 |
| export (before export) | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| export | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| settings | 9.0 | 9.0 | 9.0 | 9.0 | +1.0 |

The average minimum rose from 8.61 to 8.68, and the average across all lenses is 8.85. The two drops are QA finding defects that also exist in the old app, not regressions: Escape doesn't cancel the Install confirm on Welcome, and the page scrolls sideways at 390 during a line rewrite on Script.

## Round 6: Home/Welcome revert, "Some experience" restored, then 10 fixes, decided by blind A/B

The previous accepted version is commit 4b91518 (round 5 + the two reverts + "Some experience").

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| welcome, batch, export (before export), export | new | new | new | New stays |
| new-batch | new | new | old | New stays (2 of 3); QA's reason, an inert folder field, is fixed in round 7 |
| new-options | old | new | new | New stays (2 of 3) |
| settings, review | new | old | new | New stays (2 of 3) |
| voice | old | old | new | **Reverted** (the greyed "Pace · Only with Eleven v3" row read as a dead control) |
| new | same | old | new | **Reverted** (closed state at 390) |
| record | same | old | same | **Reverted** |
| home | same | new | same | **Reverted** |
| privacy, script | same | same | same | Tie; Script's sideways-scroll fix stays |

**Scores (candidate; rows for reverted screens score the losing candidate)**

| Screen | User | Visual | QA | Min | vs round 5 |
|---|---|---|---|---|---|
| welcome | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| home (reverted) | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new (reverted) | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| new-batch | 9.0 | 8.5 | 8.0 | 8.0 | −0.5 |
| batch | 8.5 | 8.5 | 8.5 | 8.5 | 0 |
| script | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| voice (reverted) | 8.5 | 8.5 | 8.5 | 8.5 | 0 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| record (reverted) | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| review | 9.0 | 9.0 | 8.5 | 8.5 | 0 |
| export (before export) | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| export | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| settings | 9.0 | 8.5 | 8.0 | 8.0 | −1.0 |

The average minimum is 8.68 (flat on round 5).
- **Settings −1.0:** QA newly found two defects that are in both versions, so this isn't a regression.
- **New batch −0.5:** a real regression, the inert folder field.

**Convergence (the judge's reading, rounds 4–6):**
- Screen comparisons won fell 13 → 12 → 8; reverts rose 0 → 2 → 4.
- The average minimum went 8.61 → 8.68 → 8.68, and no reviewer has given any screen 9.5.
- It's levelling off around 8.7–9.0. The fixes are now small tweaks, and each lens's taste trades off against another's.
- Reaching 9.5 would likely need app-wide rules decided once (what may grow when clicked vs what reserves space, a fixed primary-button slot, one 390 row pattern, one focus ring) plus a structural pass on Voice and Batch.

**Checkpoint after 6 rounds:** shown to Andy (`docs/screens/climb2/r6-*`).
