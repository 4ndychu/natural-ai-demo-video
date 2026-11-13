# Seats and the action guard: before/after check (10 Nov 2026)

Andy asked for seats (step 1), the seat picker (2) and the action guard (3) **without changing recorder, privacy or
render output**. The same clips were recorded with the code before the change (a frozen copy of main at 5273cd7)
and after, on the same voice tracks, and compared with `scripts/focus/compare_takes.py`.

## To-do clip (no login, no guard pack): no change

Every measure the same or better after: frame timing, frame gaps, page response, cursor travel, scheduler lateness,
actions against their words, cursor shapes, join checks (pass / pass), privacy (0 blurred / 0 blurred).

## whop clip (owner seat in NAVI Test, guard on), two takes each

| | Before 1 | Before 2 | After 1 | After 2 |
|---|---|---|---|---|
| Length | 52.8 s | 48.8 s | 52.8 s | 48.8 s |
| Join checks | fail* | pass | fail* | pass |
| Page frames per second while moving | 7.7 | 8.5 | 7.8 | 8.2 |
| Frame gaps over 50 ms while moving | 17 | 16 | 20 | 16 |
| Repeated frames while moving (of 3,166) | 49 | 56 | 60 | 77 |
| Action vs its word, average / worst (ms) | 89 / 193 | 77 / 205 | 75 / 201 | 80 / 212 |
| Cursor shapes along every move | 18 steps | identical | identical | identical |
| Privacy blurs in the video | 3 | 3 | 3 | 3 (same list) |

\* the same 5 s still at the very end in both: the script's last line runs past its last action (an old script problem, not this change).

### 11 Nov 2026: the guard moved to Chrome's own interception (CDP Fetch), so the cache stays on

| | No guard 1 | No guard 2 | Playwright guard 1 | Playwright guard 2 | **CDP guard 1** | **CDP guard 2** |
|---|---|---|---|---|---|---|
| Page frames per second while moving | 7.7 | 8.5 | 7.8 | 8.2 | 8.5 | 8.6 |
| Frame gaps over 50 ms while moving | 17 | 16 | 20 | 16 | 18 | 16 |
| Repeated frames while moving | 49 | 56 | 60 | 77 | 65 | 58 |
| Action vs its word, average / worst (ms) | 89 / 193 | 77 / 205 | 75 / 201 | 80 / 212 | 74 / 203 | 71 / 193 |
| Join checks | fail* | pass | fail* | pass | pass | pass |

`compare_takes.py` no guard 2 vs CDP guard 2: **no worse on any measure**. CDP guard 1 had 65 repeated frames
against 56, less than the difference between the two no-guard takes themselves (49 and 56). Same verdicts as the
Playwright version: `test_guard.mjs --live` passes, including new live checks that a change from the page, a
cross-site frame or a popup is blocked and that a reload is served from cache.

Later takes the same evening drifted by seconds with every version, including a re-run of the code that had just
passed: the Mac was running Roblox at 90–200% CPU (load average up to 84). Live recording needs a quiet Mac.

The ending fix (11 Nov 2026): every take now ends on the voice's schedule, about 0.7 s after the last word, as a
quiet page always did (record.py adds an empty last step; the recorder's wait for a busy page to go quiet ends when
it's due). whop clip: 48.3 s, no still at the end, join checks pass (it was 52.8 s with a 5 s still); to-do clip:
44.5 s, the same as before the fix, join checks pass. A first try (1.3 s after the voice) left the to-do clip still
for 1.6 to 2 s at the end and failed its join check; the batch test caught it.

### 10 Nov 2026, the Playwright version

The one measure that moved: **repeated frames while moving** (the page didn't repaint while the cursor, drawn later
by Recordly, moved over it): about 53 before, 69 after. Playwright's route interception switches the browser cache off for as long as it's on, which is why the guard
moved to Chrome's own interception (above).

## Privacy

- `scripts/privacy/test_privacy.py`: PASS (every fake private value unreadable, every public one readable, both styles).
- The start-page check blurs 4 or 5 profile photos run to run, with the old code and the new alike (page variation).
- New, only on payout, balance, billing, bank, card and API key pages: every number, field and account detail is
  blurred (checked on Real Biz's real balance and API key pages). Other pages blur exactly as before.

## Render

No render code changed (`scripts/render/`, `recorder/polish/`, `config/defaults.json` identical to main).

## Guard checks

`node scripts/guard/test_guard.mjs --live`: every dangerous category blocked for every seat, reads and background
traffic allowed everywhere, changes allowed in NAVI Test and blocked in Real Biz
unless the job asks, and on a buyer's member pages; live, with NAVI Test treated as real, "Create product" was stopped before it reached whop and
nothing was created.
