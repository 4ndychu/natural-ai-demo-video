# Recorder: agent-screenplay with NAVI's additions

NAVI drives the browser with [agent-screenplay](https://github.com/gmpetrov/agent-screenplay) (MIT, by gmpetrov), plus a small local patch. The upstream code was reviewed before use: it makes no analytics or upload calls, and logins stay in a local storage-state file.

## What the patch adds

| Addition | What it does | Used by NAVI |
|---|---|---|
| `startAt` | Each step starts at a set time (seconds after the first step) while the voice plays. The browser waits live; nothing is retimed in the edit. | **Yes: this is how NAVI records live to the voice.** |
| `realtime` | The edit plays the whole recording at normal speed (page loads and waits are not sped up). | **Yes** |
| `css` | A stylesheet injected into every page, used for the in-page privacy blur. | **Yes** |
| `files` on a click | The click opens a file chooser and these files are chosen. | Yes, for upload steps |
| `dragTo` on a click | Press on one element and drag it onto another, on an eased path. | Yes, for drag steps |
| `schedule` | Older approach: retime the footage afterwards so each action lands on its word (hold frames, speed up). | **No. It looked glitchy in testing.** Kept only so the patch applies cleanly. |

## Install

```bash
git clone https://github.com/gmpetrov/agent-screenplay.git
cd agent-screenplay
git apply ../recorder/agent-screenplay-navi.patch
npm install
```

The patch was made against upstream as of November 2026. If it doesn't apply cleanly to a newer version, re-apply the additions above by hand; each one is small.

## Style NAVI uses

```json
"style": { "cursor": "macos", "accent": "#1d1d1f", "click": "ripple", "captions": false, "padding": 0, "radius": 0, "shadow": false, "maxZoom": 1.6 }
```

- `cursor: macos` is the standard black arrow. The default blue cursor and click colour read as generated.
- Captions are off in the recorder; NAVI renders its own captions afterwards.
- NAVI plays its own voice takes; the recorder's built-in text-to-speech is never used.

## Privacy blur, example

```css
img[alt*="avatar" i], [class*="Avatar"] { filter: blur(9px) !important; }
[data-private], [data-blur] { filter: blur(9px) !important; }
```

Real blur rules are generated per site from the privacy tiers in `reference/privacy.md`.
