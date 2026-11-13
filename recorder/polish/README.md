# Polish: Recordly's renderer on NAVI's recording

NAVI records the browser live (agent-screenplay plus NAVI's patch). That gives raw browser frames with no cursor drawn
on them, plus a log of where the cursor went, when it clicked, and which shape it had. This step hands those to
**[Recordly](https://github.com/webadderallorg/Recordly)'s own export renderer**. Recordly draws the cursor, the click,
the zooms, the motion blur and the frame, exactly as its desktop app would export them, at 1920×1080, 60 fps.

| Style | What Recordly gets |
|---|---|
| **Casual** (default) | no zooms |
| **Recordly** | the zooms Recordly's own auto-zoom button adds (`buildInteractionZoomSuggestions`, depth 3) |

Every setting comes from a fresh Recordly install (`DEFAULT_EDITOR_PREFERENCES`, which is `normalizeProjectEditor({})`
plus app settings), passed through Recordly's own `buildExportRenderOptions` and into its `FrameRenderer`. NAVI copies
none of Recordly's numbers by hand.

## Recordly's files: unedited and pinned

- `recordly/` holds 172 of Recordly's source files (the ones the renderer imports) plus its `LICENSE.md`,
  `THIRD_PARTY_NOTICES.md`, the default wallpaper and the community cursor themes' licences. **Never edit them.**
- They come from **Recordly 2.0.0-beta.1, commit `b2b2f2b`** (8 Nov 2026), the version Andy approved.
  `recordly/PINNED.json` lists every file with its git hash.
- `node check-recordly.mjs` checks every file against the pin, and `build.mjs` runs it first and refuses to build
  if anything differs. `node check-recordly.mjs --fetch` re-downloads a missing or changed file from GitHub at the
  pinned commit.
- Moving to a newer Recordly is a decision for Andy, not a routine update. It's a beta, so a newer version could
  change the look. To update: fetch the new commit's files, update `PINNED.json`, re-render the approved test clips,
  and show them before switching.

## What NAVI adds (only input, in `src/` and `render.mjs`)

- `src/entry.ts` builds Recordly's settings, asks Recordly for its auto-zooms (Recordly style), creates Recordly's
  `FrameRenderer`, and gives it each raw frame as a `VideoFrame`.
- `render.mjs` turns the take's cursor log into Recordly's cursor telemetry. It renders every frame in headless
  Chromium (on the Mac's graphics chip, about 30 to 40 frames a second) and encodes the MP4 with ffmpeg.
- `src/web-demuxer-stub.ts` stands in for `web-demuxer`. Recordly only uses it for video wallpapers and webcam clips,
  so it isn't installed.

Input facts (not tweaks): the cursor moves on agent-screenplay's eased straight line, not a hand-drawn path. The
cursor shape is read from the page's CSS along that line, and the recorder logs it. Clicks get a mouse-up 90 ms
later.

## Install and run

```bash
cd recorder/polish && npm install      # pixi.js 8.14.0 + pixi-filters 6.1.5 (Recordly's versions), about 81 MB, gitignored
node build.mjs                         # checks the pin, bundles to dist/ (gitignored)
node render.mjs <take dir> out.mp4 --style casual|recordly [--seconds N]
```

`scripts/record/record.py` does all of this itself after recording. `--restyle recordly` re-renders an existing
recording in the other style without recording again.

## Licence

Recordly is AGPL-3.0, Copyright (C) 2026 webadderall. Because NAVI includes it, NAVI is AGPL-3.0 too (see the
repository `LICENSE` and `README.md`). pixi.js and pixi-filters are MIT.
