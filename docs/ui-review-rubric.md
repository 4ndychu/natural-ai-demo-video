# NAVI review rubric (fixed for every round of the second climb)

Every reviewer uses this rubric unchanged in every round. Calibration notes live at `docs/ui-review-calibration.md`. Reviewers read both before scoring.

## Scale (all lenses)

| Score | Meaning |
|---|---|
| 10 | Nothing to change. On par with the best reference pieces (see calibration). |
| 9 | One or two nitpicks a picky designer would raise; no user would notice. |
| 8 | Clearly good, with a few visible rough edges (a misalignment, a vague label, an awkward phone wrap). |
| 7 | Works, but several rough edges, or one thing that makes people hesitate. |
| 6 | Noticeably unpolished, or confusing in places. |
| ≤5 | Broken, crowded or confusing. |

Use half points. A score of 9.5 or more means "I'd ship this next to the references without hesitation." Scores must be consistent with the calibration anchors: if a screen is as polished as the 9.5 reference, it gets 9.5. If it's clearly below that reference, it can't.

## Lenses

### First-time user (U)
1. Without help, do I know what this screen is for and what to do next?
2. Is the main action obvious, and is it bottom right?
3. Plain words: no jargon, no UK spelling, no vague labels?
4. Do I ever hesitate, misread a control, or wonder what will happen?
5. Does the screen deliver its item from the brief (UI_BRIEF.md "What to change")?

### Visual design (V)
1. The Trays look: grey ground, white sheets in slightly darker trays, big radii, colour only from the statues and covers.
2. Type: Mona Sans with wide caps for names and page titles, regular weight elsewhere, and Geist Mono only for clock times. No "bold everywhere".
3. Hierarchy and spacing: one focal point per area, a consistent rhythm, aligned edges, no dead holes, no crowding.
4. Contrast readable from across a room, in light **and** dark.
5. Craft at the level of the references: bencho controls, rainbrand trays, BoardUI lists.
6. Phone at 390 px looks designed, not squeezed.

### Interaction QA (Q)
1. Click through the real flows (below) with Playwright. Report what happens, not what a screenshot implies.
2. Nothing moves or overlaps when you click: no layout shift, no jumping buttons.
3. One primary button, bottom right. The secondaries are consistent.
4. Focus is visible and keyboard order makes sense. Empty and error states exist.
5. Light and dark both work, and 390 px works with no clipping or sideways scroll.
6. Undo instead of "are you sure", except for destructive or costly actions.

**Flows Q must run each round** (open `ui/index.html` with Playwright, with `?start=welcome|home|…&theme=light|dark`):
- **Single demo:** Home → New demo → type a brief → Change options → Write the script → Script (next/prev, Change this line, Show captions) → Voice (pick, Hear, switch model, drag a slider) → Privacy (each preset, Customize, add a word) → Record (Pause, Stop and confirm, carry on) → Review (scrub, Mark this moment, each reason, remove with undo) → Export (captions, corner label on and off, Export).
- **Batch:** New demo → A batch → paste 12 lines → Write scripts → Approve all → Watch next → Approve → Export.
- **Settings:** Settings (appearance, defaults, key change and remove with undo, forget a login) and Welcome (empty key, bad key, good key, install tools).
- **Variants:** every flow at least once in dark, and the single-demo flow at 390×844.

## The overdesign guard (every reviewer, every screen)

Before scoring, check the screen against Andy's dislikes in UI_BRIEF.md. Each hit counts as a defect, and a change that adds one **loses** its A/B comparison even if it looks better otherwise.
- Crowded, cluttered or "overbearing": too many controls or messages at once.
- Bold everywhere.
- Eyebrow labels: small caps or mono labels sitting above a heading.
- AI-slop tells: purple gradients, glassy cards, glow, a white focus outline, textarea resize grips.
- Things that move or overlap when you click.
- Confusing navigation.
- An italic serif for the script.

## The blind A/B protocol (decides what stays)

For each screen, the reviewer gets two images, **X** and **Y**: the previous accepted version and the new candidate, in a random order the reviewer doesn't know. For each screen they answer:
- **Better:** X, Y, or "same".
- **Why:** one or two concrete reasons, citing the rubric lens.
- **Guard:** does either one hit the overdesign guard? Which?

**Blindness, added after round 7.** In round 7 a reviewer could see the scoring folder and hashed the images, so it could tell which side of each pair was new. From round 8 on, each reviewer works in two steps:
1. **A/B first,** with access only to the A/B folder and the docs. No scoring folder, no keys, no source.
2. **Scoring and fixes after,** once its A/B table is saved.

The interaction reviewer's app copies are labelled X/Y at random as before.

A candidate change stays only if it wins the majority of reviewers' comparisons for that screen (2 of 3, or 2 of 2 with one "same"). A guard hit by the candidate counts as a loss for that reviewer. Changes that lose are reverted before the next round. Scores are recorded too, but the comparisons decide.

## Fixed prompts

### Reviewer prompt (scoring and A/B), per lens
> You are the {LENS} reviewer for NAVI, a desktop app that turns a typed brief into a narrated screen-recording demo video. Read `docs/UI_BRIEF.md`, `docs/ui-review-rubric.md` and `docs/ui-review-calibration.md` in {REPO} first. Use only your lens's criteria and the overdesign guard.
> Part A, the blind comparisons: in {AB_DIR}, each screen has `{screen}__X.png` and `{screen}__Y.png` (light 1440, dark 1440, and 390 where present). For each screen, say which is better (X, Y or same), why (1–2 concrete reasons), and any guard hits. You don't know which is old.
> Part B, the scores: score every screen in {NEW_DIR} on the rubric scale against the calibration anchors, with up to 5 located fixes per screen, most important first.
> {Q only: Part C: run the flows listed in the rubric with Playwright (`require('/Users/andychu/Documents/natural-ai-demo-video/recorder/agent-screenplay/node_modules/playwright-core')`) against `file://{REPO}/ui/index.html`, and report each problem with the exact steps to reproduce.}
> Write `{OUT}` with a section "A/B" (a table: screen | better | why | guard), a section "Scores" (a table: screen | score), and "Fixes". Final reply: the A/B table and the score table only.

### Judge prompt
> You are the judge for round {N} of the NAVI hill climb. Read the brief, the rubric, the calibration and the three reviews in {DIR}.
> 1. Tally the A/B votes per screen, and list which candidate changes stay and which are reverted.
> 2. Settle disagreements on fixes, verify every claim against the screenshots or the code, and drop anything that adds clutter (the guard).
> 3. Rank at most 12 fixes for the next round. Each is concrete, has a Verify line, and names the reviewer(s).
> 4. Give the score table (U, V, Q, min). Earlier judge rulings stand unless the A/B results contradict them.
> Write {OUT}; final reply: the A/B tally and the score table.
