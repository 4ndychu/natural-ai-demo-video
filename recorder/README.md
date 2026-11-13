# Recorder: agent-screenplay with NAVI's additions

NAVI drives the browser with [agent-screenplay](https://github.com/gmpetrov/agent-screenplay) (MIT, by gmpetrov), plus a small local patch. The upstream code was reviewed before use: it makes no analytics or upload calls, and logins stay in a local storage-state file.

## What the patch adds

| Addition | What it does | Used by NAVI |
|---|---|---|
| `startAt` | Each step starts at a set time (seconds after the first step) while the voice plays. The browser waits live; nothing is retimed in the edit. | **Yes: this is how NAVI records live to the voice.** |
| `landAt` | Recording to a voice: the moment each step's cursor should arrive on its target. The step still starts at its `startAt` to find the target; the cursor then waits and sets off its own travel time (0.42 to 1.05 s, by distance) before that moment. | **Yes: every click and hover lands on its word in the first take, so one take is enough.** |
| `record --take-only` | Film only: keep the take (frames, cursor log, step times) and skip this editor's own draft video. | **Yes: NAVI's renderer draws the video from the take; the draft was thrown away and took as long again as the recording.** |
| `realtime` | The edit plays the whole recording at normal speed (page loads and waits are not sped up). | **Yes** |
| `css` | A stylesheet injected into every page, used for the in-page privacy blur. | **Yes** |
| `files` on a click | The click opens a file chooser and these files are chosen. | Yes, for upload steps |
| `dragTo` on a click | Press on one element and drag it onto another, on an eased path. | Yes, for drag steps |
| `schedule` | Older approach: retime the footage afterwards so each action lands on its word (hold frames, speed up). | **No. It looked glitchy in testing.** Kept only so the patch applies cleanly. |
| `--force-device-scale-factor` | Headless Chromium's screencast sends 1× frames whatever the page's pixel ratio; this launch flag makes the frames really 2× (2880×1620). | **Yes** |
| `initScript` + `__screenplayReport` | JavaScript run in every page before its own scripts (NAVI's privacy blur), and a function it can call to log what it did; the log is kept in the take with times on the recording's clock. | **Yes: the privacy blur and its Review list.** |
| `cursorShapes` | While the cursor travels, the page's own CSS cursor is read along the way (arrow, I-beam, hand...) and logged in the take. | **Yes: Recordly draws the matching cursor.** |
| Background flags | `--disable-background-timer-throttling`, `--disable-backgrounding-occluded-windows`, `--disable-renderer-backgrounding` on every launch (Playwright passes them too; listed so an update can't drop them). | **Yes: nothing slows down when the browser isn't in front.** |
| Login save without helper tabs | `login` saves cookies plus each open page's storage itself, instead of Playwright's `storageState()`, which opens a helper tab for sites the tab already left. In the visible login window that tab brought the browser to the front every 2 seconds. | **Yes: the login window never pulls itself back in front** (recording-rules.md rule 22). |
| Waits end on the voice's schedule | Recording to a voice, the wait after a click for the network to go quiet (up to 4 s) and the 0.7 s hold after each action both end when the next step is due. The next step still waits for its own target to appear. | **Yes: on apps that never go quiet (whop.com keeps live connections open) every click was 4 s late and the lateness added up (a 47 s voice became a 73 s video).** No change on pages that go quiet before the next step. |

## Install

```bash
git clone https://github.com/gmpetrov/agent-screenplay.git
cd agent-screenplay
git apply ../recorder/agent-screenplay-navi.patch
npm install
```

The patch was made against upstream as of November 2026. If it doesn't apply cleanly to a newer version, re-apply the additions above by hand; each one is small.

## How the video is drawn

The recorder's own video is only a draft. NAVI keeps the raw frames and the cursor log, and Recordly's own renderer
draws the final video in Casual or Recordly style (see [`polish/README.md`](polish/README.md)). The recorder's
built-in voice, captions, cursor and zoom are not used.

The recorder is MIT ([`agent-screenplay.LICENSE`](agent-screenplay.LICENSE)).

## Privacy blur, example

```css
img[alt*="avatar" i], [class*="Avatar"] { filter: blur(9px) !important; }
[data-private], [data-blur] { filter: blur(9px) !important; }
```

Real blur rules are generated per site from the privacy tiers in `reference/privacy.md`.
