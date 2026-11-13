# NAVI app: redesign brief

The app in `ui/` (open `ui/index.html`; jump with `?start=home|voice|review|settings&theme=light|dark`) is the source of truth from now on. Edit it directly. It runs on sample data until Phase 7 wires it to the engine.

## Andy's taste (read first)

- **Look: "Trays".** Grey ground (#E4E4E1 light), white sheets sitting in slightly darker grey trays, big rounded corners, Mona Sans with wide caps for names and headings, Geist Mono for numbers. The colour comes from the voice statues (halftone marble heads, one colour per voice), not from the UI chrome. Keep this look; the redesign is about layout and clarity.
- **References for the vibe only, never their layouts:** rainbrand.com (his favourite: strange liquid colours plus simplicity), macroscope.com (the lilac textured illustration), hermes-agent.nousresearch.com (Greek statue engravings). Component feel: bencho.dev (bar sliders with the label inside, segmented pills, toasts, slide-to-confirm), spaceui.one, boardui.com, inspora.design.
- **He loves:** the steps down the side, the statue voice cards with big names, the bar sliders, the Trays look, light and dark mode.
- **He dislikes:** anything crowded, cluttered or "overbearing"; bold everywhere; eyebrow labels; italic serif for the script; AI-slop tells (purple gradients, glassy cards, the white focus outline, textarea resize grips); layouts that shift or overlap when you click things; confusing navigation.
- **Rules:** high contrast (readable from across a room), light and dark mode, nothing overlaps or moves when you click, basic UX laws (one primary button, always bottom right; progressive disclosure; undo instead of "are you sure" wherever possible; confirm only destructive or costly actions), US/neutral copy (no UK spellings or references), plain words.
- He decides by looking. Show him screenshots, not descriptions.

## What to change (his critiques, 5 Nov 2026)

1. **Script step: too overflowing.** Replace the 11-row three-column table with: a short list of section names on the left (time + name); click one and only its talking line shows, large, on the right. Captions hidden behind a "Show captions" button. A "Change this line" button opens a small input ("What should change?"). Previous/next arrows. The length line stays, small.
2. **Privacy step: make it as easy as possible.** Three preset cards instead of ten switches: **Strict** (blur all personal info), **Standard** (recommended), **Test account** (fake data, so show names and emails; money, customers and counts stay blurred). A two-line summary of what's blurred and shown. The hide-words box stays. Every individual switch moves under a "Customise each item" disclosure, with the warnings kept.
3. **Record step: good, but add a helpful right panel.** Progress, time left, Done / Now / Next sections, what the voice is saying right now, and Pause and Stop buttons (Stop asks first and keeps finished sections).
4. **Review step: really confusing and overbearing.** Just the video and the marks:
   - the player, with the timeline (sections as ticks, marks as red pins);
   - one **Mark this moment** button that opens the reasons (Sounds like AI / Needs a blur / Too fast / type your own) for the current time;
   - on the right, a **Your marks** list (time, reason, section, remove; click the time to jump) with an empty state;
   - unsure blurs collapse into one small warning ("2 blurs to check") that opens the list;
   - the section list goes; the captions and corner label controls move to the Export step.
5. **New demo: "really, really confusing".** Make it one clear question first: "What should the demo show?" (large) and "On which site?" (saved sites plus "New site", which reveals an input). Everything else (audience, length with its suggestion, voice, keep-off-screen, captions, corner label) collapses into one summary line of defaults with a "Change" link that opens them.
6. **New: batch mode, for making many demos at once** (for example every video in a course). At the top of New demo: **One demo | A batch**.
   - **A batch:** paste a list, one video per line, or choose a file (course outline .txt/.md/.csv). Shared settings set once: site, voice, kind of demo, privacy preset, export folder, batch name. Show the count, total minutes and total credit estimate against credits left, before anything starts.
   - Claude writes every script, then you approve them in **one list** ("Approve all", or open any to edit).
   - Records one after another (can run overnight). **Pauses if credits run low** rather than failing.
   - A review queue: watch, mark, approve each.
   - Exports everything to the chosen folder plus a list file (title, file name, which lesson) so the user, or Claude, can upload them wherever they want. **Nothing is ever published automatically.**
   - On Home, a batch shows as one card with progress ("7 of 23 recorded"); opening it shows the batch screen with each demo's status.
7. **Voice model choice (Voice step):** Eleven v4 (recommended) or v3, with one line: "v4 sounds more natural but has no speed control. Pick v3 if you need to set the pace." The Pace slider only shows for v3. Show which model each voice clone is trained for.
7b. **New, 8 Nov 2026: video style choice.** Two options, picked per demo (in New demo's defaults, or the Record step):
   - **Casual style** (default): the frame stays the same size the whole video, with no zoom or camera movement. It uses Recordly's cursor and click (no click ring).
   - **Recordly style**: built from Recordly's own open-source code (github.com/webadderallorg/Recordly) with its default look.
   Use exactly these two names. Don't describe Recordly style as "motion blur and zooms" (Andy, 8 Nov). Engine status (8 Nov, later): **both styles are built** (`record.py --style casual|recordly`). Recordly style adds the zooms Recordly's own auto-zoom button would add. Both styles can be made from the same recording without recording again (`record.py ... --restyle recordly`), so the Review step can offer "see it in the other style" for free (no credits, about 1.5 minutes for a 45 s video).
7c. **New, 8 Nov 2026: privacy engine output.** A recording now writes `privacy.json`, in the shape the Review list already uses: `blurs: [{id, t: "0:41", what, preview, unsure, s}]` with the unsure ones first, plus `warnings`, `preset`, `blurred` and `shown`. The three preset cards map to `config/defaults.json` `privacy.presets` (`strict`, `standard`, `test_account`). The category ids the engine uses are in `scripts/privacy/patterns.json` (`email`, `money`, `count` for customers and followers, and so on), so the Privacy step's switches can use the same ids. `preview` is always masked (for example `j•••m (27 characters)`): never show the real text.
   **Review reminder (Andy, 8 Nov):** show `privacy.json` `reminder` plainly at the top of the Review step's blur list, every time: watch every video before publishing, use a test account with fake data, and add names or words that must never show to the hide-words box (link to that box). Casual style is the default video style; Recordly style stays as an option.
8. **Keep everything else that works.** Onboarding, settings, your data, light/dark, the chat bar (until flaw F5 is decided), undo toasts, and step locking.

## How to work: hill climbing with reviewers

1. Make the changes in `ui/` (`index.html` + `app.js`). Keep the existing petite-vue structure and the Trays CSS tokens.
2. Screenshot every changed screen with Playwright at 1440×900, deviceScaleFactor 2, in **light and dark**, plus 390 px wide for the main screens.
3. Run **three reviewer subagents in parallel**, each rating every screen out of 10 with specific, located fixes:
   - **First-time user:** does a newcomer understand what to do on each screen without help? Where would they hesitate?
   - **Visual design:** does it match the Trays look and Andy's references and dislikes above? Hierarchy, spacing, contrast, type, anything AI-sloppy.
   - **Interaction QA:** overlap, layout shift, crowding, inconsistent controls, primary button placement, focus states, empty and error states, dark mode.
4. A **judge subagent** reads all three reviews, settles disagreements, and picks the fixes worth making (ranked).
5. Apply the fixes, re-screenshot, and repeat until **every screen scores 8.5 or higher** from all three reviewers, or two rounds in a row improve nothing. Keep a score table per round in `docs/ui-review-log.md`.
6. Show Andy the final screenshots and the before/after scores. He has the final say.
7. Commit and push only `ui/`, `docs/` and screenshots in `docs/screens/`. Never commit reference screenshots of other websites.
