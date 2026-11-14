# The app's engine interface (Phase 7)

The local app talks to NAVI's engine through a small server on the user's own Mac. The app (`ui/`) is wired to it through `ui/engine.js`: served by this server it shows the real state and sends every click here; opened as a file (or with `?sample`) it keeps its sample data, which the layout check uses. Checks: `scripts/app/test_app.py`, `scripts/batch/test_batch.py`.

Start it: `.venv/bin/python scripts/app/server.py --open` serves the app at `http://127.0.0.1:4747/`, on this Mac only.

## Reading: `GET /api/state`

Everything the app shows, in one object. Poll it every second or two while something is running.

| Field | What it is |
|---|---|
| `settings` | The user's defaults: `voice`, `voice_model` (v4, v3), `kind` (saas, course, tour), `privacy_preset` (strict, standard, test_account), `privacy_custom` (true/false per category when it's a custom mix), `hide_words`, `sliders` (the Fine-tune values), `video_style` (casual, recordly), `captions` (burn, file, off), `caption_look` (mona-rounded, helvetica-square), `corner_label` (off, tl, tr, bl, br), `corner_text`, `export_to`, `preview_720p`, `speed_copy` (null or a speed like 1.35), `credit_limit` (the most a batch may spend without asking), `auto_go` (start a batch without the Go click), `keep_apps` (apps the busy-Mac check never names or counts; Google Chrome and Wispr Flow by default) |
| `tools_ready` | NAVI's Python, ffmpeg and the recorder are installed |
| `choices` | The allowed values for each of those settings |
| `voices`, `sliders`, `privacy.presets` | From `config/defaults.json` |
| `key` | `{stored, where, works, credits_left, credits_limit, plan, resets, problem}`. **Never the key itself.** |
| `logins` | `[{site, seat, label, account, businesses: [{key, name, test}], home, saved, status, checked}]`: one per site and seat (`scripts/seats/`). `status` is checked live, headless: `working`, `needs login`, `unreachable` or `unchecked` (no check since the last login). |
| `logins_checking` | A live check is running (`logins.check`) |
| `demos` | Newest first. See below. |
| `batches` | `[{id, name, state, reason, items: [demo ids], shared, log, plan, preflight, results, report}]`. `state` is writing, ready (waiting for Go), needs you (Go was refused up front: `reason` says why, nothing was spent), approved, running, review or exported. `results` per video: `{status: done or skipped, why}`; `report`: the morning report (`done`, `skipped` with why, `jobs`: every model job run as `{job, demo, model, effort, seconds, tokens_in, tokens_out, ok, warning}`, and `warnings`: model fallbacks and dated model warnings to show). `written` per video: `{checked, errors}` or `{why}` from `batch.py write`; `qa`: the last check's verdict per video (`ready`, `watch closely`, `redo`) and a summary. |
| `batches[].mac` | On a batch that hasn't started: how busy the Mac is, averaged over 30 s (`{others, navi, seconds, load, cores, busy, quiet_under, heavy: [{app, cpu}], kept: [{app, cpu}], icloud_syncing, line}`; `others`: cores used by everything except NAVI and the kept apps); show `line` on the Go screen. |
| `batches[].runner` | The batch's own background job (`scripts/batch/runner.py`), when it has one: `alive`, `phase` (writing, go, recording, done), `doing`, `waiting_for` (what it needs from the user, or null), `awake` (it is keeping the Mac awake), `paused`, `position` (`{done, total, at}`) and `line` ("paused at video 7 of 30", for the resume prompt). `plan.skipping` on the Go screen lists the videos that will be skipped because they have no script. |
| `batches[].blind_view` | The blind A/B/C picks of a batch, by letter only: `plan` (`{status: waiting or picked, picked, options: [{letter, plan}]}`), `lessons` (`[{demo, title, status: written, waiting or picked, picked, options: [{letter, audio, seconds, sections: [{name, talk, caption}]}]}]`; play `audio` from `GET /media/<demo>/blind/<letter>.mp3`), and `revealed` (null until every pick in the batch is made; then which model and effort each letter was, and the tally). Never show or guess an arm before `revealed`. |
| `jobs`, `job_warnings` | Each job's model for Settings, read only: `[{job, label, model, effort, fallback}]`, and any dated model warnings to show under the list. |
| `steps` | `["Script", "Voice", "Privacy", "Record", "Review", "Export"]` |

A demo (`GET /api/demo/<id>` returns one) has:
- **Brief:** `id`, `title`, `site`, `what`, `kind`, `length_min`, `audience`, `voice`, `batch`, and `settings` (its own, merged over the defaults).
- **Progress:** `step` (0 to 5) and `step_name`, plus `status`, a plain line like "Writing script", "Script ready to read", "Recording", "Ready to watch", "Paused: low credits" or "Exported".
- **Script:** `written`, `script_check` (`{errors, warnings}`), `script_approved`, `sections`, and `script_sections` (`[{name, title, talk, caption, start, seconds, cost}]`: the talking line without tags, the caption, its length from the voice once there is one, and its credits for 2 takes).
- **Credits:** `voice_cost`, the exact credits the voice still needs (characters of every take not made yet).
- **Voice and recording:** `voiced`, `recorded`, `length_s`, `checks_pass`, `video` (the recording, played from `GET /media/<id>/<video>` with byte ranges).
- **Review:** `marks` (`[{t, section, text}]`), `blurs` (the Review list: `[{id, t, what, preview, unsure, s}]`, unsure ones first), `unsure_blurs` (how many still need keep or show), `privacy_reminder` (show it at the top of the blur list), `review`.
- **Export:** `exports` (`[{t, folder, files}]`), `exported`.

Watch live: `GET /api/live/<demo id>` is the newest frame of that demo's recording in progress (JPEG), or 204 when nothing is recording. The page's privacy blur is already on it.

## Doing: `POST /api/action` with `{"type": ..., ...}`

Send JSON with `Content-Type: application/json` from the app's own page (other origins are refused). Every action is passed to Claude through "wait for the app". The ones marked *applied* are also done by the server straight away, and the reply carries the result.

| type | Fields | Applied? |
|---|---|---|
| `settings.set` | `patch` (any of the settings above) | applied (checked first: an export folder inside NAVI's own folder is refused) |
| `demo.new` | `title`, `site`, `kind`, `length_min`, `audience`, `what` | applied; Claude then explores and writes the script |
| `demo.approve_script` | `demo` | applied (refused while the checker finds errors); Claude then makes the voice (showing credits) |
| `demo.update` | `demo`, `patch` (title, site, what, kind, length_min, audience, voice, settings, hidden) | applied: the app's own edits. `hidden` is how All demos deletes a demo with Undo; nothing on disk goes |
| `batch.hide` | `batch`, `hidden` | applied: All demos deletes a batch with Undo |
| `key.test` | `key` | applied: checks it with ElevenLabs (`GET /v1/user/subscription`) and saves it to the Keychain only if it works. Replies `result` (ok, bad or offline) and `credits_left`. Never queued with the key |
| `app.open_folder` | `folder` (optional) | applied: opens the export folder in Finder (a folder in the user's home only) |
| `demo.line`, `demo.brief`, `demo.sample`, `demo.pause`, `demo.resume`, `demo.stop` | `demo`, plus `section` and `request` for a line | Claude: rewrite one line, rewrite after the brief changed, make a voice sample (show the credits first), or control a recording |
| `demo.mark` / `demo.unmark` | `demo`, `t`, `section`, `text` / `demo`, `index` | applied |
| `demo.blur` | `demo`, `id`, `s` (keep, show or empty) | applied |
| `demo.approve_review` | `demo`, `anyway` | applied (refused while unsure blurs aren't sorted, unless `anyway`) |
| `demo.settings` | `demo`, `patch` (captions, corner label, caption look, style, speed copy...) | applied; Claude re-exports (no credits) |
| `demo.record` | `demo`, `credits` (the exact cost the app showed) | Claude: voice (`generate.py --yes`), timing, recording, reporting progress |
| `demo.redo` | `demo`, `sections`, `credits`, `other_take` | Claude: shows the credits, then `scripts/render/redo.py` |
| `demo.export` | `demo` | Claude: `scripts/render/export.py` |
| `batch.new` | `name`, `list` (one video per line), `site`, and any shared settings | Claude: `batch.py new`, then writes every script |
| `batch.approve_all` | `batch` | applied (every script at once) |
| `batch.go` | `batch` | applied: the Go click. The batch becomes its own background job owned by macOS (it outlives the app and the session, keeps the Mac awake while it works, resumes after a restart): approve every script, preflight (every login it needs checked live, each start page opened with its login, credits against the limit), then the whole batch, never asking anything; a video that breaks or is blocked is skipped with the reason. Refused up front (state `needs you`) for a login to redo, a page that doesn't open, or spending over the limit. |
| `batch.pause` / `batch.resume` | `batch` | applied: pause the batch's background job where it is, or carry on from there. Replies `runner` (as above) |
| `blind.pick_plan` | `batch`, `letter` | applied: that plan becomes the batch's; writing starts in the background |
| `blind.pick` | `batch`, `demo`, `letter` | applied: that version's script and its one voice take become the video's; once no pick is waiting, the batch records them in the background |
| `batch.run` / `batch.export` | `batch` | Claude: `batch.py run` / `batch.py export` |
| `login.start` | `url`, `seat` | applied: a visible browser opens for the user to log in themselves, to that seat; it ticks "remember me" where offered, and the session is saved when they close it. **Only ever sent from a click on Log in** (Settings › Logins, Welcome); nothing else opens a login window. |
| `logins.check` | `site`, `seat` (both optional) | applied: checks the logins live in the background, headless, guard on (`scripts/seats/check_logins.mjs`); the app sends it when Settings is open and a check is over 10 minutes old |
| `login.forget` | `site`, `seat` (no seat: every login for the site) | applied |
| `key.store` | `key` | applied: piped straight into the Keychain. Never queued, logged or sent back. A field that hides what's typed. |
| `data.plan_delete` | `what` (key, logins, settings, work or everything) | applied: **nothing is deleted yet.** It returns `items` (what would go) and a `token`. Show the list. |
| `data.confirm_delete` | `token` | applied: deletes exactly that list. Tokens work once and expire after 5 minutes. Finished videos are never on the list. |

The reply is `{seq, ...result}`, or `{error}` with HTTP 400.

## Claude's side: "wait for the app"

`.venv/bin/python scripts/app/wait.py` blocks until the user does something, then prints `{"actions": [...], "last": N}`. Each action includes what the server already did with it (`ok`, `result`). Pass `--after N` next time so nothing is missed between waits. The engine reports progress to the app with `POST /api/progress {"demo": id, "text": "Recording 4 of 9"}` (batch.py sets it directly).

## Safety

- The server listens on `127.0.0.1` only. It refuses other `Host` names (DNS rebinding) and POSTs from any other web page.
- It serves `ui/` read-only and nothing outside it.
- The key goes in once, from the app, into the Keychain, and never comes back out.
- Saved logins live in `~/Library/Application Support/NAVI/logins/`, readable only by the user.
- Nothing is ever uploaded or published.
