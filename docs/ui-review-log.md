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

## Round 7: 8 fixes, decided by blind A/B

The previous accepted version is commit 6303112 (round 6 with its four losing screens reverted). The candidate is R7 fixes 1–8 (up to 09d37ab).

**A blindness leak, and the fix.** The user reviewer could see the scoring folder. It hashed the images, so it knew which side of each pair was new. Its A/B was thrown out and re-run blind in a separate pass. That re-run changed two verdicts, Export and Export (before export): the non-blind pass called them "same". The rubric now requires two steps: blind A/B first, with no access to the scoring folder, and scoring after.

| Screen | User (blind) | Visual | QA | Verdict |
|---|---|---|---|---|
| new-batch | new | new | new | New stays |
| new | same | new | new | New stays |
| review | new | same | new | New stays |
| settings, welcome | old | new | new | New stays (2 of 3) |
| voice | new | new | old | New stays (2 of 3). QA's reason: switching to Eleven v3 moves Back and Use Alex down 60 px. That gets fixed in round 8 |
| export, export (before export) | old | new | old | **Reverted.** User preferred the old hint "in a corner of the video"; QA flagged a 55 px shift at 390 with 720p plus a separate captions file |
| new-options | old | old | new | **Reverted.** The "Who's watching" track at 390 left a blank third; "Hide" read worse than "Hide options" |
| batch, home, privacy, record, script | same | same | same | Tie. The Batch fix stays: Pause, Back and the toast fix three verified bugs |

**Scores (candidate; rows for reverted screens score the losing candidate)**

| Screen | User | Visual | QA | Min | vs round 6 |
|---|---|---|---|---|---|
| welcome | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| home | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options (reverted) | 8.5 | 8.5 | 9.0 | 8.5 | 0 |
| new-batch | 9.0 | 9.0 | 9.0 | 9.0 | +1.0 |
| batch | 8.5 | 9.0 | 8.5 | 8.5 | 0 |
| script | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| voice | 8.5 | 8.5 | 8.0 | 8.0 | −0.5 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| record | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| review | 9.0 | 9.0 | 8.5 | 8.5 | 0 |
| export (before export, reverted) | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| export (reverted) | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| settings | 9.0 | 9.0 | 8.5 | 8.5 | +0.5 |

The average minimum is 8.68, flat for three rounds. The lens averages are User 8.89, Visual 8.89 and QA 8.75. No screen got 9.5.

**Convergence (the judge's reading, rounds 4–7):**
- Screen comparisons won: 13, 12, 8, 6. Lost: 0, 2, 4, 3. Tied: 1, 0, 2, 5.
- This round's wins are mostly behaviour fixes: controls that hold still, focus after an empty click, a working folder field, and Back returning to the batch.
- All three reverts were visual trade-offs at 390.
- The judge recommends making round 8 the last polish round. If Voice reaches QA 8.5, every screen meets the brief's 8.5 floor on all three lenses.

**Round 8 plan (judge, ranked):**
1. Voice: switching model moves nothing (Pace gets a fixed slot).
2. Voice at 390: the first Play sample doesn't shift.
3. Batch at 390: Pause doesn't move the list.
4. Review: focus after the Redo confirm and after removing the last mark.
5. Settings and Welcome: focus after Run again and after a bad key.
6. One Corner label hint everywhere: "Your name or brand in a corner".
7. New options at 390: Who's watching gets label-sized columns with no gap; "Walkthrough" becomes the name at every width.
8. Voice at 390: More voices fills the empty cell beside George.

## Round 8: 3 reverts plus 8 fixes, first round under the two-step blind protocol

The previous accepted version is commit 918baca (round 7 with Export, Export (before export) and New options reverted). The candidate is R8 fixes 1–8 (up to 559d253). Each reviewer saved its A/B table before it saw the scoring folder.

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| new, new-options, new-batch, voice, export (before export), export | new | new | new | New stays (unanimous) |
| review, settings, welcome | same | same | new | Fixes stay: verified focus fixes that only show when you click (Redo confirm, removing the last mark, Run again, bad key) |
| batch | old | new | same | **Reverted** (no majority). The 21.8 px Pause shift at 390 comes back for one round; round 9 re-lands the fix with the user reviewer's wording |
| home, privacy, script, record | same | same | same | Tie |

No reviewer found a guard hit on the candidate.

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 7 |
|---|---|---|---|---|---|
| welcome | 9.0 | 9.0 | 9.5 | 9.0 | 0 |
| home | 9.0 | 9.0 | 9.5 | 9.0 | 0 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options | 9.0 | 9.0 | 9.5 | 9.0 | +0.5 |
| new-batch | 9.0 | 8.5 | 9.0 | 8.5 | −0.5 |
| batch (reverted) | 8.5 | 9.0 | 8.5 | 8.5 | 0 |
| script | 9.0 | 8.5 | 9.5 | 8.5 | 0 |
| voice | 8.5 | 8.5 | 9.0 | 8.5 | +0.5 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| record | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| review | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| export (before export) | 9.0 | 8.5 | 9.5 | 8.5 | 0 |
| export | 9.0 | 8.5 | 9.5 | 8.5 | 0 |
| settings | 9.0 | 9.0 | 9.5 | 9.0 | +0.5 |

**What moved:**
- The average minimum is **8.75**, up from 8.68 after three flat rounds.
- Lens averages: User 8.93, Visual 8.82, QA 9.18.
- The first 9.5s of the second climb came this round, all from QA (7 screens).
- Every screen is now 8.5 or higher on every lens.
- The two −0.5 rows aren't regressions: the screens are unchanged, and the reviewers newly noticed crowded pills on New batch at 390 and an unconfirmed Record again.

**Convergence (rounds 4–8):**

| | R4 | R5 | R6 | R7 | R8 |
|---|---|---|---|---|---|
| Screens won | 13 | 12 | 8 | 6 | 6 |
| Lost or reverted | 0 | 2 | 4 | 3 | 1 |
| Tied | 1 | 0 | 2 | 5 | 7 |
| Mean minimum | 8.61 | 8.68 | 8.68 | 8.68 | 8.75 |

**What's left to reach 9.5.** The User and Visual reviewers sit at about 9.0. Their remaining asks are mostly structural calls for Andy:
- the chat bar on New and Record;
- whether space is reserved or grows (the 130 px gap on Export at 390);
- the half-empty columns on Voice, Home and Script.

**Round 9 plan (judge, ranked):**
1. Batch recording line in the user's voice, on 2 lines at 390 (re-lands the Pause fix).
2. Batch watch: Back holds still when the button label changes.
3. Batch at 390: Pause sits beside the count.
4. Record again asks first (it costs credits).
5. Three-option pills at 390 sized to their labels everywhere.
6. New and New batch: no "5 / min" splits, the count line doesn't jump while pasting, and a disabled Write focuses its field.
7. Export: the Corner label hint sits under its title, with a hairline above the file list.
8. Voice: More voices tile at 390, v4 note spacing, reset badge clear of the focus ring.
9. Script, dark: the selected section turns lighter than the sheet.
10. Toasts: Undo holds still, and one Undo restores several removed marks.

## Round 9: 10 fixes, decided by blind A/B (two-step protocol)

The previous accepted version is commit 379d6f3 (round 8 with Batch's recording line reverted). The candidate is R9 fixes 1–10 (up to ca30c43).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| new, new-batch, batch, script | new | new | new | New stays (unanimous) |
| voice, export (before export), export | new | new | same | New stays |
| privacy, record, review, settings | same | same | new | The fixes stay. They're verified click-time fixes: Undo holds still, Record again asks first (it costs credits), one Undo restores several marks |
| new-options | new (slightly) | old | old | **Reverted** at 390. Picking an audience resized the Length pills (66→84 px), a guard hit. Label-sized pills stay on New batch, Export and Who's watching |
| welcome, home | same | same | same | Tie |

**Scores (candidate; QA scores the candidate app)**

| Screen | User | Visual | QA | Min | vs round 8 |
|---|---|---|---|---|---|
| welcome | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| home | 9.0 | 9.0 | 9.5 | 9.0 | 0 |
| new | 9.5 | 9.0 | 9.0 | 9.0 | 0 |
| new-options (390 reverted) | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| new-batch | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| batch | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| script | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| voice | 8.5 | 8.5 | 8.5 | 8.5 | 0 |
| privacy | 9.0 | 9.0 | 9.5 | 9.0 | 0 |
| record | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| review | 9.0 | 9.0 | 9.5 | 9.0 | 0 |
| export (before export) | 9.0 | 9.0 | 9.5 | 9.0 | +0.5 |
| export | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| settings | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |

**Results**
- The average minimum is **8.86**, up from 8.75. The lens averages are User 9.00, Visual 8.96 and QA 9.00.
- User gave its first 9.5 of this climb (New).
- The three −0.5 rows are bugs QA newly found in both versions, so they aren't regressions:
  - Welcome's install confirm scrolls sideways at 390.
  - Forgetting two logins leaves only one Undo.
  - New options' Length pills resize at 1440.

**Convergence (rounds 4–9):**

| | R4 | R5 | R6 | R7 | R8 | R9 |
|---|---|---|---|---|---|---|
| Screens won | 13 | 12 | 8 | 6 | 6 | 7 |
| Lost or reverted | 0 | 2 | 4 | 3 | 1 | 1 (part) |
| Tied | 1 | 0 | 2 | 5 | 7 | 6 |
| Mean minimum | 8.61 | 8.68 | 8.68 | 8.68 | 8.75 | 8.86 |

**Checkpoint after 9 rounds:** shown to Andy (`docs/screens/climb2/r9-*`, before = the round 6 checkpoint, after = round 9).

**Decisions only Andy can make (each blocks 9.5):**
1. **Voice:** keep Fine-tune open as is (User and Visual stay at 8.5), fold it into one line, or fold everything except Pace and Casualness.
2. **Reserve space or let it grow:** Export, phone Privacy and the Corner label hint. Keep the empty room so nothing jumps, let it grow (buttons move), or restructure so the growing part sits below the buttons.
3. **Half-empty columns** on Home, Script, Review and Voice: leave them, rebalance the layouts, or narrow the left columns.
4. **Chat bar on every step:** keep it, hide it on New and while recording, or give it a prompt for each step.
5. **"Change / Hide options" at 390** grows 30 px when opened. Accept it, use "Change" with an arrow that flips, or use a fixed box.

**Round 10 plan (judge, ranked; real bugs first):**
1. Welcome: the install confirm fits at 390.
2. Settings: one Undo for several forgotten logins.
3. New options at 1440: the Length pills don't resize.
4. Batch: Watch next holds still when the first video is ready.
5. Script: the time readout holds still.
6. Voice: the Pace reset badge sits inside the bar.
7. Export: the primary keeps one box.
8. Record: the Record again confirm keeps Back in place.
9. New batch: the primary holds still after a paste; "top up" becomes "add credits".
10. Plain words on Home, Privacy and Review.

## Round 10: 10 fixes, real bugs first, decided by blind A/B

The previous accepted version is commit 0234177 (round 9 with New options at 390 reverted). The candidate is R10 fixes 1–10 (up to 0f01b67).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| batch, privacy, record | new | new | new | New stays |
| welcome, new-batch | new | new | new | New stays. Visual preferred the old 390 shot on both, and New batch's cut path "…l/Whop course" gets fixed in round 11 |
| home, export (before export) | new | new / same | same / new | New stays |
| script | same | new | new | New stays |
| export | old | new | new | New stays (2 of 3). The hint copy goes back to "Saved to Movies/NAVI. Change a setting to export again, free.", the line User preferred |
| voice | same | same | new | The fixes stay: the Pace reset badge sits inside the bar, and Hear no longer shifts |
| new-options | old | old | new | **Reverted.** The 83 px Length pills and the dropped "5 min for now." hint both lost |
| settings | old | old | new | **Forget goes back to a pill.** The merged "2 logins forgotten" Undo and the focus fix stay |
| review | new (slightly) | same | same | **Reverted.** The 390 wording "first" had only one vote |
| new | same | same | same | Tie |

**Scores (candidate; QA scores the candidate app; reverted rows score the losing candidate)**

| Screen | User | Visual | QA | Min | vs round 9 |
|---|---|---|---|---|---|
| welcome | 9.0 | 9.0 | 9.5 | 9.0 | +0.5 |
| home | 9.0 | 9.0 | 9.5 | 9.0 | 0 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options (reverted) | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| new-batch | 9.0 | 8.5 | 9.0 | 8.5 | −0.5 |
| batch | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| script | 9.0 | 8.5 | 9.5 | 8.5 | −0.5 |
| voice | 8.5 | 8.5 | 9.5 | 8.5 | 0 |
| privacy | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| record | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| review | 9.0 | 8.5 | 8.5 | 8.5 | −0.5 |
| export (before export) | 9.0 | 8.5 | 9.5 | 8.5 | −0.5 |
| export | 9.0 | 8.5 | 9.5 | 8.5 | −0.5 |
| settings (Forget reverted) | 9.0 | 9.0 | 8.5 | 8.5 | 0 |

The average minimum is 8.61, down from 8.86, though this round won the most screens since round 5. The drop isn't the candidate's doing:
- Visual took 0.5 off five layouts it had scored 9.0 last round. One of them, Review at 1440, is pixel-identical to round 9.
- QA newly found click-time bugs on five screens, and every one of them is in both versions.

The judge's reading is that the scores have reached their noise floor: a 0.5 swing on identical pixels is as large as a round's gains.

**Convergence (rounds 4–10):**

| | R4 | R5 | R6 | R7 | R8 | R9 | R10 |
|---|---|---|---|---|---|---|---|
| Screens won | 13 | 12 | 8 | 6 | 6 | 7 | 9 |
| Lost or reverted | 0 | 2 | 4 | 3 | 1 | 1 (part) | 3 (part) |
| Tied | 1 | 0 | 2 | 5 | 7 | 6 | 2 |
| Mean minimum | 8.61 | 8.68 | 8.68 | 8.68 | 8.75 | 8.86 | 8.61 |

**Screenshot setup:** the Script and Voice shots now open as a first visit (`max:0` and `max:1`), so the step rail no longer shows later steps as done. Both sides of the comparison were reshot with this setup.

**Round 11 plan (judge, ranked; click-time bugs first):**
1. Record: Back holds still when a recording is stopped.
2. Review: the "Approve anyway" confirm keeps the primary's box.
3. Privacy: Undo focuses the restored word.
4. Settings: the bad-key message has a slot at 390.
5. Batch: no jump when the list starts summarizing.
6. New / New batch: "+ New site" closes on a second click.
7. New options: the ★ stops resizing the Length pills.
8. New batch at 390: the path is cut at a slash.
9. Welcome: plainer Text to Speech wording.
10. Script: the length line appears once.

## Round 11: 10 fixes (click-time bugs first), decided by blind A/B, no losses

The previous accepted version is commit 41065e4 (round 10 after its partial reverts). The candidate is R11 fixes 1–10 (up to 6a4842b).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| welcome, new-batch, batch, script, review, settings | new | new | new | New stays |
| privacy | new | new | same | New stays |
| new, new-options, record | same | same | new | The fixes stay. They're verified click-time fixes: "+ New site" toggles, the ★ no longer resizes the Length pills, and Back holds after Slide to stop |
| home, voice, export (before export), export | same | same | same | Tie |

This is the first round since round 4 with no losses. No reviewer found a guard hit on the candidate. One cost: the Record "Stopped" footer has an empty 146 px slot at 1440, which round 12 fills.

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 10 |
|---|---|---|---|---|---|
| welcome | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| home | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| new-batch | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| batch | 9.0 | 9.0 | 8.0 | 8.0 | −0.5 |
| script | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| voice | 8.5 | 8.5 | 9.0 | 8.5 | 0 |
| privacy | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| record | 9.0 | 9.0 | 8.0 | 8.0 | −0.5 |
| review | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| export (before export) | 9.5 | 8.5 | 9.0 | 8.5 | 0 |
| export | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| settings | 9.0 | 9.0 | 8.5 | 8.5 | 0 |

The average minimum is 8.57. The judge re-ran every bug behind QA's lower scores (Batch 8.0, Record 8.0, Welcome 8.5), and each one is in the old version too:
- Clicking a disabled button drops focus.
- The batch credit pause shows the wrong state, and its footer drops.
- After Stop → Back, recording doesn't resume.

**The scores are now within reviewer noise:**
- QA took 0.5 off Home, Voice and both Export screens, whose pixels and behaviour are identical to round 10.
- User added 0.5 to Export (before export) on identical pixels.

Swings that size are as big as a round's real gains. The blind A/B still separates good rounds from bad ones; the average minimum no longer does.

**Convergence (rounds 4–11):**

| | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 |
|---|---|---|---|---|---|---|---|---|
| Screens won | 13 | 12 | 8 | 6 | 6 | 7 | 9 | 7 |
| Lost or reverted | 0 | 2 | 4 | 3 | 1 | 1 (part) | 3 (part) | 0 |
| Tied | 1 | 0 | 2 | 5 | 7 | 6 | 2 | 7 |
| Mean minimum | 8.61 | 8.68 | 8.68 | 8.68 | 8.75 | 8.86 | 8.61 | 8.57 |

**The judge's recommendation:**
- Run round 12 to fix the bugs behind Batch and Record (below the brief's 8.5 floor).
- Then show Andy the round 12 shots against the round 9 checkpoint, and pause until he makes the five decisions.
- Without them, the ceiling is an average minimum of about 8.8.
- Decisions 1–3 (Voice Fine-tune, reserve or grow, half-empty columns) would unlock most of the Visual reviewer's remaining 8.5s.

**Round 12 plan (judge, ranked):**
1. Disabled buttons keep focus and point at the reason already on screen.
2. Batch credit pause: the right state, and the footer holds still.
3. Record "Stopped" matches "Recorded", and Privacy's primary resumes the recording.
4. The Batch "Yes, record all" confirm keeps the primary's box.
5. Script at 390 shows the length once.
6. Key errors are tied to their field for screen readers.
7. Privacy: Add with an empty field focuses the field.
8. New options: the Corner label switch holds still.
9. Welcome at 1440: the status sits level with Done, and the help is plainer.
10. Batch: "Watch next" becomes "Watch #5".

## Round 12: 10 fixes (bugs behind QA's low scores), decided by blind A/B. Checkpoint 4, paused for Andy

The previous accepted version is commit e452695. The candidate is R12 fixes 1–10 (up to b0f7f66).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| welcome, batch, script | new | new | new | New stays |
| record | old | same | new | Split. **The 1440 slide hint goes back** to "Finished sections are kept" (1f9e485). The fixes stay: Record again in the Stopped state, focus on blocked buttons, and Privacy resumes the recording |
| new-options, voice, privacy, settings | same | same | new | The fixes stay: blocked buttons keep focus, key errors are tied to their field, Add with an empty field focuses it, and the Corner switch holds still |
| home, new, new-batch, review, export (before export), export | same | same | same | Tie |

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 11 |
|---|---|---|---|---|---|
| welcome | 9.0 | 9.0 | 9.5 | 9.0 | +0.5 |
| home | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new | 9.0 | 9.0 | 9.5 | 9.0 | 0 |
| new-options | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-batch | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| batch | 9.0 | 9.0 | 9.0 | 9.0 | +1.0 |
| script | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| voice | 8.5 | 8.5 | 8.5 | 8.5 | 0 |
| privacy | 9.0 | 9.0 | 8.0 | 8.0 | −0.5 |
| record | 9.0 | 9.0 | 8.0 | 8.0 | 0 |
| review | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| export (before export) | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| export | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| settings | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |

The average minimum is 8.71, up from 8.57. The lens averages are User 8.96, Visual 8.89 and QA 8.82.

The judge ran each defect behind QA's 8.0 and 8.5 scores on both app copies. All of them are in the old version too:
- Locked steps in the step list drop focus when clicked.
- At 390, the Privacy Customize rows move 1–2 px when a warning appears.
- At 390, the stop toast covers the Record footer.

The judge has prototyped fixes for all three for round 13; they aren't applied yet.

**Convergence (rounds 4–12):**

| | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 |
|---|---|---|---|---|---|---|---|---|---|
| Screens won | 13 | 12 | 8 | 6 | 6 | 7 | 9 | 7 | 3 |
| Lost or reverted | 0 | 2 | 4 | 3 | 1 | 1 (part) | 3 (part) | 0 | 1 (part) |
| Tied | 1 | 0 | 2 | 5 | 7 | 6 | 2 | 7 | 10 |
| Mean minimum | 8.61 | 8.68 | 8.68 | 8.68 | 8.75 | 8.86 | 8.61 | 8.57 | 8.71 |

**Why the climb paused here.** Neither stop condition is met. But wins have fallen 9 → 7 → 3, and this round's were all planned bug and copy fixes. Reviewers' scores now move ±0.5 on identical pixels. Without Andy's decisions, the judge puts the ceiling at an average minimum of about 8.9.

**Checkpoint after 12 rounds:** shown to Andy (`docs/screens/climb2/r12-*`, before = round 9 checkpoint, after = round 12).

**What each of Andy's decisions would change (judge):**
1. **Fold Voice's Fine-tune.** Voice is the only screen at 8.5 on all three lenses. Folding should lift it to about 9.0 on every lens.
2. **Reserve space or let it grow.** Affects the empty space at 390 on Privacy, both Export screens and Record. It is now a lever for 9.5, not for the minimum.
3. **Half-empty columns.** Lifts Visual on Script from 8.5 to 9.0, and on Review and Home from 9.0 to 9.5.
4. **Chat bar on every step.** Lifts QA on New options from 9.0 to 9.5, and part of Voice.
5. **"Change / Hide options" at 390.** No reviewer named it this round.

With the round 13 bug fixes plus decisions 1 and 3, the average minimum should reach about 9.0. A minimum of 9.5 needs decision 2 plus the Visual reviewer's craft asks.

**Next fixes, if Andy says keep going** (none depend on his decisions):
1. Locked steps keep focus.
2. Privacy rows hold their height.
3. Stopping a recording shows no toast.
4. Batch: focus stays on Export after exporting.
5. "Finished sections are kept" at both widths.
6. New summary: "For beginners · …".
7. Batch list status in grey.
8. One selection style for site chips.

## Andy's decisions after round 12 (owner baseline, not A/B'd)

Andy decided the five open questions and added four notes of his own. They're applied as owner changes (commits Owner 1–9 and 3b, f1f6b28…1214117) and listed in the rubric under "Owner decisions", so reviewers judge how well each is done, not whether to do it.

1. **Voice:** Fine-tune folds into one line, "All recommended for Alex", with Change. The sliders open on click.
2. **Export, phone Privacy and Record** reserve their space, so nothing moves. Privacy rows are 64 px, and stopping a recording gives no toast.
3. **Home, Script, Review and Voice** shrink to fit their content:
   - Home: shorter covers.
   - Script: the sections in two columns.
   - Review: video and marks side by side, timeline full width.
   - Script's Show captions and Change this line open in place, so the footer no longer drops 79 / 56 px.
4. **The chat bar** hides on New demo and while recording.
5. **New demo options** reads "Change" with a flipping arrow.
6. **Welcome's image** is the first version again: the statue on its own with NAVI on it, no blue band (`docs/screens/climb2/owner-welcome-*.jpg`).
7. **Delete demos and batches** from All demos, with an Undo toast. Deletes in a row merge into one Undo.
8. **Test key** shows checking, works (with credits left), wrong key and no connection. The build plan (`docs/BUILD_BRIEF.md`, Phase 7) says it must call ElevenLabs for real.
9. **New batch** sits next to New demo on Home. The batch setup says in one line how batching works.

**Baseline scores** (no A/B): average minimum **8.54**.
- Welcome got 8.0 from Visual: the small "Natural AI demo video" line doesn't read over the statue. Andy's call, see below.
- QA measured old bugs:
  - locked steps drop focus;
  - Privacy custom mixes move the switches;
  - Review's reasons overlap at 390;
  - Settings shows the old key ending.

## Round 13: 11 fixes (QA's bugs first), decided by blind A/B

The previous version is the owner baseline (fb8ceef). The candidate is R13 fixes 1–11 (up to 9d88c64).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| home, new, export-pre | new | new | new | New stays |
| script | same | new | new | New stays |
| record | new | new at 1440, old at 390 (hint length) | new | New stays. In round 14 the hint becomes "Finished sections stay" |
| review | old (390 lost its "4:56") | new | new | New stays, with a patch: at 390, Cancel moved 37 px when Other… opened (f11c5ea). "4:56" comes back in round 14 |
| batch | same | old (weak: narrower 390 Export) | new | Kept. The narrower button is what jumped 79 px under the pointer |
| voice, privacy, settings, export | same | same | new | The fixes stay: no "Alex is set" toast; Privacy holds in all 1024 mixes; the key row shows the new key's ending; one Open folder |
| welcome, new-options, new-batch | same | same | same | Tie |

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs baseline |
|---|---|---|---|---|---|
| welcome | 8.5 | 8.5 | 8.5 | 8.5 | +0.5 |
| home | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| new-options | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-batch | 9.0 | 8.5 | 9.0 | 8.5 | −0.5 |
| batch | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| script | 9.0 | 9.0 | 8.5 | 8.5 | +0.5 |
| voice | 9.0 | 9.0 | 8.5 | 8.5 | +0.5 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | +1.0 |
| record | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| review | 8.5 | 9.0 | 8.5 | 8.5 | +0.5 |
| export-pre | 9.5 | 9.0 | 9.0 | 9.0 | +0.5 |
| export | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| settings | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |

The average minimum is **8.79**, up from 8.54 at the baseline and 8.71 in round 12. Every screen now gets 8.5 or better from every reviewer.

There were 6 wins, so the stop rule isn't met: Andy's rule is to stop when a round wins fewer than 2.

**Waiting on Andy:**
- **Welcome's small line** under NAVI doesn't read over the halftone, at any size or position the judge tried. The options are to drop it at 390 only, or at both widths.
- **Voice at 1440:** Fine-tune opens partly under the chat bar. The options are to scroll it into view (Change then moves under the pointer), or to hide the bar while Fine-tune is open.

**Round 14 plan (judge, ranked):**
1. New demo: one message per error, and the summary never breaks after "label:".
2. Welcome: a blocked Done focuses the first unfinished step.
3. Privacy: focus goes back to the field after a duplicate.
4. Locked steps leave the Tab order.
5. Review at 390: both times sit under the track, and "4:56" is back.
6. 390 footers line up with the content column.
7. Record: the hint reads "Finished sections stay".
8. Script at 390: the picker drops "3 ·".

## Round 14: 8 fixes, decided by blind A/B

The previous accepted version is d1e0ac7 (round 13 plus the Review Cancel patch). The candidate is R14 fixes 1–8 (up to db59daa).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| batch, script, voice, privacy, record, review, export-pre, export | new | new | new | New stays. The 390 footers line up with the content column. The Script picker drops "3 ·". The Record hint reads "Finished sections stay". At 390, Review shows both times under a longer track. Locked steps leave the Tab order |
| welcome, new, new-options | same | same | new | The fixes stay. A blocked Done focuses the first unfinished step. The footer message matches the field. "label top right" stays together |
| home, new-batch, settings | same | same | same | Tie |

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 13 |
|---|---|---|---|---|---|
| welcome | 8.5 | 8.5 | 9.0 | 8.5 | 0 |
| home | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| new-options | 9.0 | 8.5 | 9.0 | 8.5 | −0.5 |
| new-batch | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| batch | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| script | 9.0 | 9.0 | 8.5 | 8.5 | 0 |
| voice | 9.0 | 9.0 | 8.5 | 8.5 | 0 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| record | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| review | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| export-pre | 9.5 | 9.0 | 9.0 | 9.0 | 0 |
| export | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| settings | 9.0 | 9.0 | 8.0 | 8.0 | −1.0 |

The average minimum is 8.68, down from 8.79, even though the round won 8 comparisons. The judge found no regression in the new version. The drops come from three things:
- **Settings.** QA newly found two bugs that are in the old version too: at 390, Remove key pushes Saved logins down 21.8 px, and after Undo on Forget, focus sometimes lands on Change.
- **Batch.** The 304 px scroll QA reported was a test artifact. The five-line toast at 390 is real, and also in the old version.
- **New options.** The pixels are identical to round 13, so the 0.5 drop is noise.

8 wins, so the stop rule is not met.

**Round 15 plan (judge, ranked; the judge prototyped and tested all of them together):**
1. Settings: Undo keeps focus on the restored row.
2. Settings at 390: Remove key moves nothing.
3. The step strip stays where you swiped it.
4. New at 390: the new-site hint and its error take the same room.
5. Toasts at 390 use the full width.
6. New at 390: no line ends with a "·".
7. The New and New batch footers line up with the content column.
8. One selection style for site chips.
9. The Script header shows only "3 of 11".
10. Step footers at 1440 line up with the content column.
11. One name for one place: "All demos" and "Erase data".
12. Copy corrections on Privacy Standard and the Batch time left.

## Round 15: 12 fixes, decided by blind A/B. Checkpoint 5

The previous accepted version is 52b0b45. The candidate is R15 fixes 1–12 (up to 34b5602).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| new, new-options, new-batch, script, privacy, settings | new | new | new | New stays: one segmented site picker, aligned footers, "3 of 11", "Erase data", focus after Undo, Remove key holds |
| home | new | same | new | New stays ("All demos") |
| voice, record, review, export-pre, export | same | new | new | New stays: footers line up at 1440; the step strip stays where you swiped it |
| batch | new | new at 1440, old at 390 | old (guard hit) | Split. **"about 2 hours left" goes back to "about 2 h left"** (c14a1f4). At 390 the longer wording took 3 lines, so Pause/Resume moved 21.8 px; now 0 px. The aligned footer and full-width toast stay |
| welcome | same | same | same | Tie |

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 14 |
|---|---|---|---|---|---|
| welcome | 8.5 | 8.5 | 9.0 | 8.5 | 0 |
| home | 9.0 | 9.0 | 9.5 | 9.0 | 0 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| new-options | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| new-batch | 9.0 | 9.0 | 8.5 | 8.5 | 0 |
| batch | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| script | 9.0 | 9.0 | 9.5 | 9.0 | +0.5 |
| voice | 9.0 | 8.5 | 9.5 | 8.5 | 0 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| record | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| review | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| export-pre | 9.5 | 9.0 | 9.0 | 9.0 | 0 |
| export | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| settings | 9.0 | 9.0 | 8.5 | 8.5 | +0.5 |

The average minimum is **8.86**, the best of the second climb. Lens averages: User 9.00, Visual 8.93, QA 9.04. No minimum fell.

**Convergence (rounds 12–15):**

| | R12 | Owner baseline | R13 | R14 | R15 |
|---|---|---|---|---|---|
| Won | 3 | – | 6 | 8 | 12 |
| Kept on a QA-only win | 4 | – | 5 | 3 | 0 |
| Lost or reverted | 1 (part) | – | 0 (patched) | 0 | 1 (part) |
| Tied | 6 | – | 3 | 3 | 1 |
| Mean minimum | 8.71 | 8.54 | 8.79 | 8.68 | 8.86 |

There were 12 wins, so the stop rule isn't met. Checkpoint images: `docs/screens/climb2/r15-*.jpg` (before = round 12, after = round 15).

**Round 16 plan (judge, all prototyped together):**
1. Settings: no delayed close after a good key, so nothing below moves 120 px.
2. New batch: the new-site field keeps its width on an error.
3. Every confirm opens on its safe button.
4. New and New batch footers fit one line at 390.
5. Export: the optional files list after the transcript.
6. New summary: "Label: Acme Studio, top right".
7. Voice: More voices drops its dashed border, and the help line is shorter.
8. Review footer: "About 840 credits to redo."
9. Privacy wording: Strict names customers.
10. Settings: the reset line names what it resets.

## Round 16: 10 fixes, decided by blind A/B

The previous accepted version is 8af9479. The candidate is R16 fixes 1–10 (up to 28d519c).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| new, new-options, new-batch, voice, review | new | new | new | New stays: one-line footers at 390, a site field that keeps its width, More voices without the dashed box, a shorter Voice help line, "About 840 credits to redo." |
| privacy, settings | new | same | new | New stays: Strict names customers. Settings no longer closes the key editor by itself (everything below used to move 120 px). The reset line names what it resets |
| welcome, batch, record | same | same | new | The fixes stay: every confirm opens on its safe button |
| home, script, export-pre, export | same | same | same | Tie. Export's file order changed (the .txt row no longer moves), which no still shows |

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 15 |
|---|---|---|---|---|---|
| welcome | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| home | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-batch | 9.0 | 9.0 | 8.5 | 8.5 | 0 |
| batch | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| script | 9.0 | 9.0 | 9.5 | 9.0 | 0 |
| voice | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| record | 9.5 | 9.0 | 9.0 | 9.0 | 0 |
| review | 9.0 | 9.0 | 8.0 | 8.0 | −1.0 |
| export-pre | 9.5 | 9.0 | 9.0 | 9.0 | 0 |
| export | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| settings | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |

The average minimum is 8.79, down from 8.86. Lens averages: User 9.07, Visual 8.96, QA 8.82.

The judge checked every new QA defect on both versions, and all of them were already there before this round:
- On Review, Go back on "Export without redos" sends focus to the 840-credit Redo button.
- On Export, after a change, Open folder jumps 126 px.
- On Welcome, Open browser accepts "notasite".
- On New batch, the footer doesn't say why Write is blocked.
- On Home, the New tiles shrink when the batch card is deleted. This isn't ranked, because padding the cards to keep the height would go against Owner decision 3.

The round had 7 wins, so the stop rule is not met.

**Round 17 plan (judge; all ten prototyped together):**
1. Review: Go back returns focus to its own button.
2. Export: one button in one place ("Export again" replaces Open folder after a change).
3. Welcome: Open browser checks the address.
4. New batch: the footer says why Write is blocked.
5. Review: a second mark at the same moment changes its reason, with Undo.
6. Settings: after "Works", focus goes to Done.
7. Voice: More voices uses the cards' exact tone.
8. Review: drop the bare section name beside Mark this moment.
9. Privacy summary: say "usage, prices", the same words as the cards.
10. Review: "2 blurs to check".

## Round 17: 10 fixes, decided by blind A/B

The previous accepted version is c180757. The candidate is R17 fixes 1–10 (up to 3a5914b).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| voice, privacy, review | new | new | new | New stays. More voices uses the cards' tone, the Privacy summary uses the cards' words, and Review drops the bare section name and reads "2 blurs to check" |
| welcome, new-batch, export, settings | same | same | new | The fixes stay. Open browser checks the address, the New batch footer says why Write is blocked, Export has one button in one place, and focus goes to Done after a key works |
| the other 7 | same | same | same | Tie |

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 16 |
|---|---|---|---|---|---|
| welcome | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| home | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-batch | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| batch | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| script | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| voice | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| record | 9.5 | 9.0 | 9.0 | 9.0 | 0 |
| review | 9.0 | 9.0 | 9.0 | 9.0 | +1.0 |
| export-pre | 9.5 | 9.0 | 9.0 | 9.0 | 0 |
| export | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| settings | 9.0 | 9.0 | 9.0 | 9.0 | 0 |

**Average minimum: 8.89, the best of the second climb.** Lens averages: User 9.07, Visual 8.96, QA 8.89.

Neither drop is a regression; both defects are in the old version too:
- **Batch:** the "Paused…" toast stays up after Resume.
- **Voice:** the chat bar covers Fine-tune at 1440, which waits on Andy.

The round won 3 comparisons, so the stop rule is not met.

**Round 18 plan (judge).** Only two real bugs are left, so the round has four fixes:
1. Welcome: site errors show inline under the field, not as a toast.
2. Batch: Resume clears the "Paused…" toast.
3. Home at 390: the delete chip is dark, so it reads on any cover.
4. Batch: "Leave your Mac on overnight." becomes "Keep your Mac on."

## Round 18: 4 fixes, decided by blind A/B. Checkpoint 6

The previous accepted version is 33d83a8. The candidate is R18 fixes 1–4 (up to 1de37eb).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| home, batch | new | new | new | New stays. At 390 the delete chips are dark. Batch says "Keep your Mac on." and Resume clears the "Paused" toast |
| welcome | same | same | new | The fix stays: site errors show in red under the field, not as a toast that covered Done at 390 |
| the other 11 | same | same | same | Tie |

**Scores (candidate)**

| Screen | User | Visual | QA | Min | vs round 17 |
|---|---|---|---|---|---|
| welcome | 8.5 | 8.5 | 9.0 | 8.5 | 0 |
| home | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-batch | 8.5 | 8.5 | 8.5 | 8.5 | −0.5 (noise: identical pixels; QA's "jump" didn't reproduce) |
| batch | 9.0 | 8.5 | 8.5 | 8.5 | 0 |
| script | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| voice | 9.0 | 8.5 | 9.0 | 8.5 | 0 |
| privacy | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| record | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 (old defect: after Stop the help still says "NAVI keeps going") |
| review | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| export-pre | 9.5 | 9.0 | 9.0 | 9.0 | 0 |
| export | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| settings | 9.0 | 9.0 | 9.0 | 9.0 | 0 |

The average minimum is 8.82, down from 8.89. No drop is a regression: two are noise on identical pixels, and one is an old defect found this round. The new version had no guard hits.

**Convergence (rounds 12–18):**

| | R12 | Owner | R13 | R14 | R15 | R16 | R17 | R18 |
|---|---|---|---|---|---|---|---|---|
| Won | 3 | – | 6 | 8 | 12 | 7 | 3 | 2 |
| Kept on a QA-only win | 4 | – | 5 | 3 | 0 | 3 | 4 | 1 |
| Lost or reverted | 1 (part) | – | 0 (patched) | 0 | 1 (part) | 0 | 0 | 0 |
| Tied | 6 | – | 3 | 3 | 1 | 4 | 7 | 11 |
| Mean minimum | 8.71 | 8.54 | 8.79 | 8.68 | 8.86 | 8.79 | 8.89 | 8.82 |

Round 18 won 2 comparisons and the stop rule needs fewer than 2, so it isn't met. Checkpoint images are `docs/screens/climb2/r18-*.jpg` (before = round 16, after = round 18).

**Round 19 plan (judge; only three real fixes are left):**
1. Record: after Stop, the help line names the two buttons instead of saying NAVI keeps going.
2. Batch: after Export, focus goes to the next action.
3. Home: one dark delete chip at every width.

## Round 19: 3 fixes, decided by blind A/B. The climb stops here

The previous accepted version is b99ab01. The candidate is R19 fixes 1–3 (up to 4c9a02b).

| Screen | User | Visual | QA | Verdict |
|---|---|---|---|---|
| home | new | new | new | New stays: one dark delete chip at every width |
| batch, record | same | same | new | The fixes stay: after Export, focus goes to Watch #3; after Stop, the help line names the two buttons |
| the other 11 | same | same | same | Tie |

**Final scores**

| Screen | User | Visual | QA | Min | vs round 18 |
|---|---|---|---|---|---|
| welcome | 8.5 | 8.5 | 9.0 | 8.5 | 0 |
| home | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-options | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| new-batch | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| batch | 8.5 | 9.0 | 9.0 | 8.5 | 0 |
| script | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| voice | 8.5 | 9.0 | 9.0 | 8.5 | 0 |
| privacy | 8.5 | 9.0 | 8.5 | 8.5 | −0.5 |
| record | 9.0 | 9.0 | 9.0 | 9.0 | +0.5 |
| review | 8.5 | 9.0 | 9.0 | 8.5 | −0.5 |
| export-pre | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| export | 9.0 | 9.0 | 9.0 | 9.0 | 0 |
| settings | 9.0 | 9.0 | 8.5 | 8.5 | −0.5 |

The average minimum is **8.79**, and the average across all lenses is 8.90, the same as round 18. The lens averages are User 8.82, Visual 8.96 and QA 8.93.

The drops are not regressions:
- The User drops are noise on byte-identical pixels.
- QA's two drops are old click-time scrolls, found for the first time this round. Closing Customize on Privacy scrolls 32 px. Forget all on Settings scrolls 455 px.

**Convergence (rounds 12–19):**

| | R12 | Owner | R13 | R14 | R15 | R16 | R17 | R18 | R19 |
|---|---|---|---|---|---|---|---|---|---|
| Won | 3 | – | 6 | 8 | 12 | 7 | 3 | 2 | 1 |
| Kept on a QA-only win | 4 | – | 5 | 3 | 0 | 3 | 4 | 1 | 2 |
| Lost or reverted | 1 (part) | – | 0 (patched) | 0 | 1 (part) | 0 | 0 | 0 | 0 |
| Tied | 6 | – | 3 | 3 | 1 | 4 | 7 | 11 | 11 |
| Mean minimum | 8.71 | 8.54 | 8.79 | 8.68 | 8.86 | 8.79 | 8.89 | 8.82 | 8.79 |

**Stop rule met.** Round 19 won 1 blind comparison, and Andy's rule stops when a round wins fewer than 2.

**Where the second climb ended.**
- **Score:** the average minimum went from 7.4 (round 1 of this climb) to 8.79. Every screen has scored 8.5 or better from every reviewer for four rounds running.
- **9.5 not reached:** no screen gets 9.5 from all three reviewers. The judge's view of the remaining gap:
  - QA counts five different focus styles across the app.
  - The User reviewer finds one wording repeat per screen.
  - Visual flags small craft points: selected-state strokes of 1.5, 2 and 3 px, faint switch knobs in dark mode, and half step discs at the edge of the 390 strip.
  - Scores move ±0.5 on identical pixels.
- **Possible next pass:** one more pass per lens, A/B'd as a set, might reach an average minimum of about 9.0–9.2.

**Waiting on Andy:**
1. **Welcome tagline:** "Natural AI demo video" can't be read over the statue. At 390 it's cut to "Natural AI demo vi". The judge recommends removing the line and keeping the statue and wordmark, which is decision 6.
2. **Voice at 1440×900:** opening Fine-tune puts the sliders under the chat bar. The judge recommends hiding the chat bar while Fine-tune is open, the same rule as decision 4.

**Old defects worth a follow-up:**
- Privacy: closing Customize scrolls 32 px. The fix is to drop the scroll on close.
- Settings: Forget all scrolls 455 px. The fix is to scroll only by the overlap with the chat bar.
- Record: Pause still says "NAVI keeps going…".
- Voice: picking Jessica on v3 disables "Use Jessica", although the help line says NAVI switches the model if needed.
- Batch: the rail shows sample privacy and length. Phase 7's engine replaces that sample data.

## After the climb: Andy's last decisions, four fixes, and in-between widths (no A/B)

Andy closed the climb ("no more climb rounds") and asked for these before merging.

**Decisions:**
1. Welcome: the tagline under NAVI is gone. The statue and wordmark stay.
2. Voice: the chat bar hides while Fine-tune is open. Edit brief stays enabled; it now follows the recording lock instead of the chat bar.

**Fixes:**
- Privacy: opening or closing Customize no longer scrolls the page (was 32 px on close).
- Settings: Forget all logins keeps the page still, with focus on the Saved logins heading (was a 455 px scroll).
- Record: while paused, the help line reads "Recording is paused. Resume carries on from section 5, and finished sections are kept." The help line keeps its height, so nothing moves.
- Voice: a voice on the wrong model no longer disables its button. "Use Jessica" on Eleven v3 switches to v4 and goes on, with a toast. Beforehand, the footer says "Jessica needs Eleven v4. NAVI switches to it when you go on."

**In-between widths.** At about 1,050 px, Andy found:
- Script's title was squeezed to 0 px wide and spelled one letter per line.
- Review's timeline ran into Your marks.
- Export's caption switch covered "Captions".

The rounds only tested 1440 and 390. Two changes fix this:
- **The layout check.** A new automatic check (`ui/tests/layout-check.js`) runs 20 screens and states at 9 widths in light and dark, 360 runs. It fails on sideways scroll, overlaps, clipped or cut-off text, broken words, squeezed text, boxes that hide part of their content, and anything under the chat bar.
  - Its first run found 284 problems.
  - Besides Andy's three, it found broken Voice cards (names cut, Hear over the names, the reader squeezed) and the Record and batch rows cut off from 900 to 1280 px.
- **The layouts.** The step area now sizes its insides to the room it has (container queries). Below 860 px of step width, which means windows under about 1,240 px, the side panel moves under the main column.
  - Script: the reader sits under the section list.
  - Review: Your marks sits under the timeline.
  - Export: the settings sit under the video. They keep their reserved height, so no switch moves Export video.
  - Voice: the reader and length sit under Fine-tune.
  - Record: progress sits under the video.

  At narrower widths:
  - Under 620 px, voice cards go two across and sliders one across.
  - Under 640 px, the step footer puts its line on its own row.
  - Under 700 px, batch rows use the two-line layout.

  The phone layout is unchanged. Record's quote now shows the whole line, in a box sized to the longest line, so it never changes height between sections.

**Result:** 360 runs, 0 problems. Screenshots of Script, Review and Export at 1024 and 1100, in light and dark, are in `docs/screens/widths/`.

**Still open** (not blocking):
- At every width below 1,240 px, as on phones, adding a mark on Review makes the marks list grow, so the footer moves down 75 px. The buttons you click don't move.
- The batch side panel shows sample settings until Phase 7.
