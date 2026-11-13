# Writing a NAVI script

How Claude writes the script for a demo: the **talking version** the voice reads and the **clean caption version**, section by section, with the browser actions pinned to words. The rules themselves are in `voice-rules.md` (read it first). This page is the format and the order of work.

## The steps

1. **Explore first.** Know every screen, click, field and slow load of the task before writing a word (SKILL.md step 2). Note what's hard to find; those are the only places a hunt ("where is it,") belongs.
2. **Plan the sections.** About 15 to 35 seconds of talk each (at Alex's pace, about 3 words a second: 45 to 105 words). One step of the task per section. Page loads and other waits fall **between** sections, never inside one. The opening section is short (10 to 12 s) and starts on the app doing something.
2b. **Draw three styles and write three drafts** (`docs/variety-spec.md`, sections 4 and 10 to 12).
`.venv/bin/python scripts/script/drafts.py styles script.template.json` draws three styles far apart (different
openings, different leanings), away from the record of recent scripts (`$NAVI_DATA/script-history.jsonl`) and the
videos already picked in the batch, and writes `draft1.json` to `draft3.json` next to it. Write all three (steps 3
to 5 for each: the same video, the same facts and actions, three different days of the same narrator). Then
`.venv/bin/python scripts/script/drafts.py pick <folder>/draft*.json --base <folder>` scores them (quality first,
then difference from recent videos) and writes the best as `script.json`. In a batch, do the videos in order. Each
style also says which of the narrator's habits (`config/narrators/`) come out today.
3. **Write the talking version** of each section (`voice-rules.md` section 1): talk, don't read, with opinions
and reasons where the screen earns them. Write to the style: open the way it says; start most sections on their
content with no marker, and no two with the same word; put a filler or a repair only where the screen earns one,
in the places and kinds the style leans to, and leave most sections without either. Never more than one repair
in a section. The last line ends low and plainly, often just on the action. Start each section with `[relaxed]`
and no other tag.
4. **Pin the actions.** **Spread the pointing out** (`crowded` in the checker): a click or hover keeps the cursor busy for about 1.2 s on a slow page, so two or three in a row with only a word or two between them each start late, and the lateness adds up until the take fails (12 Nov 2026: Pricing, Apps, Settings, Generate within about 4 s, on whop's slow create page, landed up to 0.8 s late). Leave a clause or a comma pause between pointing actions, and when a page lists several things, point at two or three of them, not every one.

    Every browser action names the word it lands on (`"on"`) and its kind (`explain`, `click`, `hunt` or `wait`). The cue word must appear in the talk, in order. **Something must happen on screen at least every 5 seconds**, so a long explanation needs a hover or a scroll inside it, or it gets cut or split.
4b. **Never claim a state the page doesn't show.** Don't say something is hidden, unpublished, private or a draft unless the explored page says so (Andy, 13 Nov 2026: whop has no draft for products; NAVI Test being briefly visible is fine, a voice that says otherwise is not).
5. **Write the caption version:** clean, short and correctly spelled, with no fillers, restarts, swears or tags. Keep the important words the voice says (button and page names: "Clear completed", "Enter"). Captions are timed by matching those words to the voice, and **a caption only shows while its own words are spoken**, so a caption about something the voice never says won't have anywhere to sit.
5b. **Positions are checked, or loose.** Every position the script gives ("top right", "up top", "at the bottom of the form") is checked against the explored page by the checker: it looks the target up in the explore data (`explore/**/explore.json` next to the script, or the folders in the script's `"explore"`) and compares it with where it really is, on screen and in the panel it sits in. A form that fills the left of the screen has its button at the *bottom right of the form* but the *bottom left of the screen*: say which ("at the bottom of the form"), or leave the position out. Positions that can't be checked are errors too. *(Andy, 10 Nov 2026: the whop video said "bottom left" for the bottom right of the form.)*
6. **Run the checker** and fix every error: `.venv/bin/python scripts/script/check_script.py script.json`. It
checks the script by itself, against the record of recent scripts, and, in a batch, against the other scripts in
the batch (`--batch`). A repeat of a recent video is an error like any other. Read the warnings too.
7. **Show it side by side** and get the user's approval before any credits are spent: `.venv/bin/python scripts/script/show_script.py script.json` prints the talking and caption versions next to each other, with the actions and the checker's findings.

## The file

```json
{
  "title": "A simple to-do list",
  "site": "demo.playwright.dev/todomvc",
  "kind": "saas",
  "voice_id": "hLygPNd2gK6Azddorc5W",
  "privacy": {"preset": "standard", "show": [], "blur": [], "hide_words": []},
  "captions": "burn",
  "style": {"opening": "reason", "markers_on": ["then", "and"], "markers_resting": ["okay", "right"], "breath_sections": [],
            "filler_rate": 0.7, "filler_slots": ["unit", "tail"], "repair_kinds": ["fresh", "reph"], "sentences": "long", "gaps": [0.34, 0.52]},
  "sections": [
    {
      "name": "open",
      "talk": "[relaxed] Quickest way to show you this is to just use it, so I'll click in the box up top, call the dentist, and hit Enter.",
      "caption": "This is a simple to-do list. Type a task in the box at the top and press Enter to add it.",
      "actions": [
        {"on": "start", "do": "goto", "kind": "wait", "target": "https://demo.playwright.dev/todomvc"},
        {"on": "this", "do": "hover", "kind": "explain", "target": "placeholder=What needs to be done?"},
        {"on": "box", "do": "click", "kind": "click", "target": "placeholder=What needs to be done?"},
        {"on": "call", "do": "type", "kind": "click", "text": "Call the dentist"},
        {"on": "Enter", "do": "press", "kind": "click", "key": "Enter"}
      ]
    }
  ]
}
```

- `do` is one of `goto` (first section, `"on": "start"`; a later section may open another page or site with a `goto` on its `"start"`), `click`, `type` (with `text`, and `into` for a field to click first), `press` (with `key`), `hover`, or `highlight` (the cursor goes there; NAVI never adds a spotlight).
- `target` uses the recorder's way of naming things: `text=…`, `placeholder=…`, `role=button[name='…']`, `label=…`, `testid=…`, or a CSS selector.
- Optional settings: `privacy` (see `privacy.md`), `captions` (`burn`, `file` or `off`), `corner_label` + `corner_text`, `caption_look`, `speed_copy` (for example `1.35`), `export_to` (the folder for the files).
- This is one script, not the pattern: the next one must not open this way (voice-rules.md, Variety). `examples/test-todo-b.json` was recorded and approved before the variety rules and is written to the old recipe ("Right, so,", "Okay. So now,"); `examples/variety/` holds it and three others next to their rewrites.
- `"style"` is the style of the day (`scripts/script/style.py`); the checker and the voice step read it.
- **Two or more logins in one video** (X and Google Sheets, Claude and Grok): `"seats": [{"site": "x.com", "seat": "owner"}, {"site": "google.com", "seat": "owner"}]`, and every section names the site whose login its steps use (`"seat": "google.com"`). One browser holds every login (`scripts/seats/seats.py` merged_login), the action guard checks each site with its own pack, and the batch preflight checks every login. The checker refuses a section with no seat, or one that opens the other login's site. A video that must show public pages as a visitor uses the seat `"logged-out"`.
- **House rules** (`scripts/script/house_rules.py`): `"never_name"` lists words the voice and captions must never say (a course that never names the tools its videos are made with); `"spelling": "UK"` or `"US"` holds the captions to one spelling.
- **A batch from a rich list** (`batch.py new --list videos.json`): one object per video with its own start page, logins, privacy, length, spelling, never_name, lesson file (copied into the video's folder) and brief (what it's for, start to end, what gets created, what never shows); the planner, explorer and writer all get the brief.

## What the checker can't judge

It catches the patterns that were heard as fake in the listening rounds, but it can't hear. Whether a line sounds like a person explaining their screen is still decided by ear, after the voice is generated (`voice-rules.md` section 8).
