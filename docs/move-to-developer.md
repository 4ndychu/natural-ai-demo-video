# Moving the repo out of iCloud (after `production-ready` merges)

**Why:** `~/Documents` is synced by iCloud (Desktop & Documents is on; checked 12 Nov 2026). iCloud made 23 " 2" copies of
repo files in one afternoon, and it uploads everything in `output/` and `.venv/` (about 2 GB) for nothing. The repo
moves to `~/Developer/natural-ai-demo-video`, which iCloud doesn't touch. NAVI's own data
(`~/Library/Application Support/NAVI`: settings, saved logins, seats, script history) stays exactly where it is.

**When:** only once the `production-ready` PR is merged, no batch is running and no other session has the folder open.
Never mid-branch.

**Until then (12 Nov 2026):** the work folder is already out of iCloud's reach. `output` is a link to `output.nosync` (iCloud skips names ending in `.nosync`), because iCloud was using a whole processor core syncing every recorded frame while videos were being recorded. After the move, turn it back into a plain folder: `rm output && mv output.nosync output`.

## Steps

1. **Check nothing is in flight:** `git status` clean on `main`, pulled; no batch running (`batch.py status`); the app's
   server stopped; any background batch job unloaded (step 3 of the production-ready work installs one per running batch).
2. **Remove the old T3 worktrees** that point at the old folder (`git worktree list`, then `git worktree remove` each,
   after checking none has unpushed work).
3. **Move the folder as it is:** `mv ~/Documents/natural-ai-demo-video ~/Developer/natural-ai-demo-video`. Same disk, so
   it's instant and keeps `.git`, `output/` (finished takes and recordings), `.venv/` and the recorder's installs.
4. **Rebuild what stores its own path:**
   - `.venv` (Python environments hold absolute paths): `rm -rf .venv && scripts/setup/install.sh` (it re-links ffmpeg
     from the recorder and rebuilds `navi-ocr` / `navi-focuswatch` on first use), then `python3 scripts/setup/check.py`.
   - `git worktree prune`.
5. **Fix the paths written in the repo** (one commit):
   - `ui/tests/layout-check.js` line 17 (Playwright path) → resolve from the file's own folder.
   - `scripts/research/transcribe_verbatim.py` lines 5 and 6 → resolve from the file's own folder.
   - `docs/BUILD_BRIEF.md`, `docs/ui-review-rubric.md` → the new folder name.
6. **Old work in `output/`:** `timing.json`, `report.md` and the recorder's `scenario.json` of already-recorded demos
   hold the old absolute path. Finished videos still play and export; to redo a section of an old demo, run its timing
   step again first (free) so the paths are rewritten.
7. **Outside the repo:**
   - T3 Code: point the project at the new folder (or add it again).
   - Claude Code's memory for this project is keyed by the folder path
     (`~/.claude/projects/-Users-andychu-Documents-natural-ai-demo-video/`): copy its `memory/` folder to the new
     project's folder so the notes carry over, and update the "work in main folder" note to the new path.
   - Nothing in `~/Library/Application Support/NAVI` holds the repo's path (checked), so it needs no change.
8. **Prove it:** `scripts/setup/check.py`, `scripts/jobs/test_jobs.py`, `node ui/tests/layout-check.js`,
   `scripts/app/test_app.py`, then one short real recording. Only then delete anything left in `~/Documents`.
