# Phase 3 recording review, 8 November 2026

What Andy watched: `output/test-todo-v4/recording/recording.mp4` (now kept as `recording-v1-zoomed/`). This was the first live recording of the practice to-do app, with the approved Alex v4 voice and automatic zoom on clicks (up to 1.6×). Join checks passed: all 15 actions landed within 0.28 s of their words.

## Andy's notes (verbatim, voice dictation)

> Okay, cool. This is going to be a voice dictation as I review this. Review this video.
>
> What I don't like about this year: the voice is fine. It could have some improvement, but it's fine. It's good, it's okay, and I think it sounds normal. It sounds human. This is a very casual demo, so why are we doing these unnecessary zooms? There are so many unnecessary zooms, these special effects or things trying to be special effects, and zoom-ins on certain buttons that aren't needed. There are so many zooms where it's unnatural.
>
> For a casual demo like this, if it's not really needed, take a look at this. It should just be normal throughout, with that same screen size throughout, damn near. I remember it zoomed in so many times, and it was so unneeded. It was just tacky to look at.
>
> Also, by the way, this dictation should be verbatim. We're also going to be testing out potentially using Recordly as the video system. We could switch between Recordly, this, or this thing here. I think we could use Recordly since it is open source as well. We'll just do that in the download, so we could have alternatives, I guess.
>
> Recordly is open source. Let me try and look at examples. I'm seeing some called RR Web or Recordly. Pretty sure Recordly as well. Recordly looks hella smooth, bro. Hella smooth. We could be using Recordly. It's open source on GitHub.
>
> Add this to my thing, please. The voice is okay. It's bearable, and it's good. I have no real complaints about it. I'm not blown away, though, but it's good.
>
> The video is just super unnecessary and super choppy. There are too many zooms that just look unnatural. I think we should be using Recordly. I think we actually should be using Recordly. I don't think we should be using whatever we're using, like FFMPEG or whatever the fuck. That's my review.

## What changed because of it

- **Zoom off.** `config/defaults.json` now has `recording.zoom_on_click: "none"`, so the frame stays the same size for the whole video. `recording-rules.md` rule 11 was changed at its source (rule 12).
- **60 fps output** (`recording.fps`), so the drawn cursor moves more smoothly. It was 30 fps.
- **The choppiness was checked.** The browser capture is change-driven: it sends frames only when the page changes, up to 60 a second. Its frames line up with the clicks, and no page changes were missing. The jerky feel came from the camera zooming in and out, plus the 30 fps cursor.
- **Recordly looked into** (see the Phase 3 report in chat). It is AGPLv3 and only has buttons: no command line, headless mode or API. Recording means capturing the real Mac screen (ScreenCaptureKit) while someone presses record. Its signature feature is auto-zoom. It fails recording-rules.md rule 20 as an automated recorder, so it stays a possible manual alternative for later. rrweb (MIT) records page changes rather than video and has no MP4 export of its own.
- **Voice:** no change asked ("not blown away, though, but it's good").

## Andy's follow-up after watching A (1920 wide) and B (1440 wide, scaled up), both without zoom (verbatim)

> Okay, cool. Also add this to notes for them. The smaller browser thing that you just did is good. I like that. I think we obviously have to add this to notes for them, but I think we should add something where you can pick this kind of style: one where there's not a lot of movement, or the Recordly style.
>
> Like the Recordly open-source style, where you click somewhere in the NAVI UI. Which kind of one do you want? More casual, like NAVI, with the motion blurs and all the animations that come with Recordly, obviously. Add that as well.
>
> Yeah, that looks good, so there are two options.

> By the way, don't say MotionBlur and Zooms, just say the Recordly style.
> Which we are going to use: Recordly, the open source

## Decisions

- **B wins:** browser 1440×810, scaled up to the 1920×1080 video. Now the default (`recording.viewport`).
- **Two video styles, picked in the app:** "NAVI" (the calm, same-size frame, built) and "Recordly style" (uses Recordly, the open-source recorder; not wired up yet). Added to `docs/UI_BRIEF.md` item 7b for the UI thread. In the app it's called just "Recordly style".

## Recordly style test (10 s, Recordly's cursor, camera and motion-blur code on NAVI's recording): Andy's notes (verbatim)

> That Recordly style is perfect. Good use of taking Recordly's code. Perfect. We don't even really need to make iterations to Recordly style because Recordly has already been made. Recordly is damn near perfect as it is. So many people at the highest level use it, and its code is just there to take, and obviously, legally taking Recordly's code. It's open source for a reason. So many people use it. We know that that code is damn near perfect, so we don't even need to make iterations.
>
> For Navi style, let's not name it Navi style. Obviously, when we do the UI, like input in the UI, we'll name it something like casual style, but we will reference Recordly style.
>
> The one thing I don't like about the Navi style is that it shouldn't be like the Navi style. It shouldn't be moving or doing these special animations. One thing that's bad about the Navi style is that when the mouse clicks, it has this weird circular animation that looks really ugly. It should never do that.
>
> Take a look at Recordly. When they do the clicking motion, it doesn't have that. Recordly's clicking animation is perfect. We could take the clicking animation from Recordly. Other than that, Recordly has always been perfect.

## Decisions

- **Recordly style approved as it is:** Recordly's own defaults, with no tuning rounds. Its click has no ring: the cursor dips briefly (`clickEffect: "none"`, click bounce 2.5).
- **The calm style is now called "Casual style"** (it was "NAVI style"). It has no zoom and no camera movement, and it uses Recordly's cursor and click. The circular click ripple is gone everywhere, for good.
- ~~Casual style keeps the cursor on screen (idle-hide off).~~ **Reverted.** That was my change, not Recordly's. Andy's note below.

## Andy, after the casual clip (verbatim)

> Are you sure that doesn't match Recordly's cursor at all? Let's review that clip. Analyse what Recordly does, because in Recordly clicks, the cursor goddamn disappears. That's what it needs to do. I told you to match it exactly, bro. You didn't match it exactly.

## What didn't match, and the fix

The test had copied cursor numbers by hand, from Recordly's "Focused" preset plus my own guesses. Compared with a fresh Recordly project (Recordly's `normalizeProjectEditor({})`, saved as `output/test-todo-v4/recordly-test/harness/recordly-new-project-defaults.json`), six things were off: cursor look (macos instead of **tahoe**), cursor size (smaller than **2.5**), sway (0 instead of **0.4**), idle-hide (off in Casual instead of **on, 2 s**), zoom depth (2 instead of **3**), and the camera springs (left out instead of **1 / 1.13 / 1.12**). Now every setting is read from Recordly's own defaults object and wired the way Recordly's exporter does it. Nothing is hand-copied any more. Both styles use the identical Recordly cursor; Casual style just has no zoom.

## Andy, after the exact-match clips (verbatim)

> Okay, they both look good. Remember, don't fuck with Recordly's code too much. When I say make changes to casual and I say to dissect certain pieces from Recordly, those are the only changes we're making. We're mainly making changes to casual, okay? Recordly, we don't touch. It's good enough.

**Decision:** both v2 clips approved. Recordly's code is used as it is: no edits to its files and no changes to its settings. Changes happen only in Casual style, and only by taking the Recordly pieces Andy names.

## Andy, Phase 3 sign-off (verbatim)

> 1. Yes, install pixi.js and pixi-filters. Make sure they're gitignored (node_modules), not committed.
> 2. Phase 3 approved. Build the polish step, then Phase 4.
>
> Before any Recordly file goes into git:
> - Switch NAVI's licence to AGPL-3.0 (I'm never selling it), keep Recordly's copyright notices, and credit Recordly in the README.
> - Pin the exact Recordly version or commit the code came from. It's a 2.0 beta, so a future update could change how it looks. We stay on the version I approved unless I say otherwise.

**Phase 3 approved, 8 November 2026.**

## What was done

- **Installed** pixi.js 8.14.0 and pixi-filters 6.1.5 (the exact versions in Recordly's lockfile) in `recorder/polish/node_modules`: 81 MB, gitignored. web-demuxer (Recordly uses it only for video wallpapers and webcams) was not installed; a stand-in replaces it at build time.
- **Pinned:** Recordly 2.0.0-beta.1, commit `b2b2f2b` (8 Nov 2026). All 139 files behind the approved test clips matched this commit exactly. The build refuses to run if any of the 181 copied files changes (`recorder/polish/check-recordly.mjs`). Rule 11c.
- **Licence:** NAVI is now AGPL-3.0. Recordly's `LICENSE.md`, `THIRD_PARTY_NOTICES.md` and the cursor themes' licences are copied in with its files, and the README credits Recordly. agent-screenplay's MIT notice is kept too.
- **Polish step built** on Recordly's own `FrameRenderer` (its exporter's renderer), not a hand-wired copy. Re-rendering the two approved 10 s clips this way matched them frame for frame: 58.5 dB and 60.5 dB on average, which is visually identical.
- **Recordly style's zooms** are the ones Recordly's own auto-zoom button adds. At this version, Recordly doesn't add zooms by itself; the app suggests them and you press the button. The approved test clip used one hand-placed zoom instead.
- **Sharper capture:** the browser frames were really 1440×810, scaled up. With `--force-device-scale-factor=2` they're 2880×1620 at about 56 frames a second. 3× only manages about 25 a second. Rule 11d.
- **Real cursor shape:** the recorder now reads the page's own CSS cursor along each move. Recordly draws the matching tahoe cursor: arrow, I-beam over the text box, hand over links.
- **Kept from Phase 3, not Recordly's defaults:** 1920×1080 at 60 fps. Recordly's own default export is 30 fps at a "medium" size, but Andy approved 60 fps.
