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
