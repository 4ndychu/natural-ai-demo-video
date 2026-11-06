# Reviewer calibration (second climb)

Before scoring NAVI, each reviewer (Opus, high effort) scored the reference pieces on `docs/ui-review-rubric.md`. These anchors fix what a 9, 9.5 and 10 mean for every later round.

| Reference | First-time user | Visual | Interaction QA |
|---|---|---|---|
| bencho.dev Time scrubber block | 9.0 | 9.5 | 9.5 |
| bencho Slide to confirm / Toast stack | – | – | 8.0 / 8.5 |
| BoardUI Agent Progress / Data Table | 8.0 | 9.0 | 8.5 (data table) |
| rainbrand.com home | 8.5 | 9.5 | 9.0 |
| macroscope.com home | 7.5 | 8.5 | – |

Each reviewer's full notes follow, verbatim.

---

## user reviewer

## Calibration: First-time user (U)

Lens criteria (rubric): U1 know what the screen is for and what to do next; U2 main action obvious and bottom right; U3 plain words; U4 no hesitation, misread controls or "what will happen?"; U5 delivers its brief item (not applicable to references, so they're judged on U1 to U4 plus the overdesign guard).

Two of the references are marketing pages, not app screens. For U2 on those I ask whether there is one clear next step and where it sits, not whether it is literally bottom right.

### Scores

| Reference | U score |
|---|---|
| bencho.dev, Time scrubber block | **9.0** |
| rainbrand.com home | **8.5** |
| BoardUI, Agent Progress page | **8.0** |
| macroscope.com home | **7.5** |

---

#### 1. bencho.dev, Time scrubber (refs/bencho_time-scrubber_0.png): 9.0

Why:
- **U1, purpose and next step in one line.** The title "Time scrubber" is followed by one sentence: "Drag the ruler to set a time; fling it and it coasts to the nearest step." It names the verb (drag), the object (the ruler) and what will happen (it coasts to a step). I never have to guess.
- **U2, primary bottom right, done right.** "Add to bench" is the only filled button, full width at the bottom of the right panel. "Share" sits above it as an outline secondary. You can't misread which one matters.
- **U4, controls read their state at a glance.** Each segmented pill (Light/Dark, Off/On, 5/15/30, 12h/24h) shows the selected option as a white chip on grey. The bar sliders put the label inside ("Momentum") and the value at the right end ("50", "20px"), so the fill is the value and nothing floats. The red playhead on the ruler is the obvious drag handle.
- **Calm.** The controls are short, there's one stage and one panel, there are no eyebrows, no bold, and nothing overlaps.

Holding it below 9.5:
- "Add to bench" is in-house jargon. A first-timer doesn't know what a "bench" is, and the "1" chip inside the button is unexplained (a count? a shortcut?).
- Units are missing: "Step 5/15/30" (minutes?), "Momentum 50" (50 of what?). "Corner 20px" shows that the fix is easy.
- The icon-only controls (cube/code toggle top left, bookmark, speaker, the play button on the stage) have no labels. I'd hover each one to find out what it does.

To drop one point (to 8): rename the primary to something vaguer like "Apply"; take out the instruction line under the title; or put the two buttons side by side with equal weight, so I'd have to stop and pick.

#### 2. rainbrand.com home (refs/rainbrand_com_home_top.png, rainbrand_scroll_1..6.png): 8.5

Why:
- **U1, a clear story.** The hero says what it is ("The brand layer for agents") and the sub-line puts the key nouns in soft chips ("shared brand context", "agents", "products"). The manifesto paragraph greys out the problem and blackens the answer, so the eye lands on "Rainbrand is brand infrastructure for your agents".
- **U2, one obvious next step.** "Get started →" is the only black filled button in the hero, with "Connect your agent" as a grey secondary. It's centered rather than bottom right, but nobody hesitates. Every later section ends in exactly one black button ("Use it with your agents") plus a text link.
- **U4, steps you can follow.** "Request a Brief / Generate / Request a Review" puts the verb in a colored chip and a "guide ↗" link under each. The setup card is a numbered 1-2 list with tabs per tool, and the FAQ is numbered 01–06 with a +/– box on the right, the clearest accordion of the four references.
- **U3, mostly plain words**, like "Keep your models, tools and workflow. Rainbrand supplies the brand context."

Holding it at 8.5:
- **Overlap (guard):** the floating "Need help? The team typically replies in under 6h" widget covers the FAQ answer text (scroll_5) and the right edge of other sections. That's a visible defect a user would notice.
- **Eyebrow labels (guard):** "MANIFESTO", "HOW IT WORKS", "FEATURES", "CUSTOMERS", "FREQUENTLY ASKED QUESTIONS", plus "[NOTICE] //", "IN // FILES" and "OUT // MCP". They don't confuse, but they're decoration a newcomer has to read past.
- **Mystery labels:** "CANVAS: 01" and the row of four glyphs (⊕⊖✳◌) under the hero look like controls but do nothing obvious. "Connect your agent" has a dropdown chevron, so it's a menu dressed as a button.
- Jargon for non-developers: "MCP", "REST API", a raw curl block.

To drop one point (to 7.5): add a second filled button in the hero next to "Get started" (two equal primaries), or let the chat widget sit permanently over the primary button.

#### 3. BoardUI, Agent Progress (refs/boardui_agent-progress_0.png): 8.0

Why:
- **The component itself is 9-level for U4.** "4 steps left" with a spinner as the header; finished step struck through with a grey check; the current step in an outlined row with its own spinner; pending steps in faint circles. You know what's done, what's running and what's next without reading a legend. This is the model for NAVI's Record "Done / Now / Next" panel and the batch status list.
- **U1:** the page title plus the first sentence ("A collapsible progress block for multi-step AI work") tells me what it is.
- **The sidebar list** is easy to scan, with indented items, a guide line, and the current page in bold in the breadcrumb.

Holding it at 8:
- **U2: there's no clear next action.** Candidates are "Preview / Code", "Copy Page" with a split dropdown, "Get Pro", GitHub "1,010", and the theme toggle. Nothing is primary, and the page's real goal (install it) is below the fold behind "PRO ACCESS".
- **U3:** the description turns jargon-heavy: "synchronized circular progress", "exposes completion timing for handing the UI back to an agent response".
- **Crowding (guard):** the left sidebar with four "NEW" badges, small-caps group headers (GETTING STARTED, FOUNDATIONS, BASE), a five-button toolbar, an "On this page" TOC and two floating round buttons at the bottom right compete with a small preview.
- The pending circles are almost invisible, and the grey "–" square at the top right of the component is an unlabeled minimize I'd have to guess at.

To drop one point (to 7): remove the "4 steps left" header, or make done and pending rows look the same, so the state has to be read from text.

#### 4. macroscope.com home (refs/macroscope_com_home_top.png, macroscope_scroll_1..6.png): 7.5

Why it is still good:
- **The hero has a clear primary.** "Start Free" (dark, GitHub icon) with "Book Demo" as an outline secondary. The three product cards on the right each give a plain one-line job ("Review every change for correctness, security, tests, and regressions before it lands").
- **Section blocks follow a heading + one sentence + picture pattern.** The Murmur block puts its primary "Apply to beta" at the bottom right of the block, with "Read Docs" to its left as the ghost secondary. That's the right pattern.

Why only 7.5:
- **U1, a vague headline.** "Command your own software factory" is a metaphor, and you only learn what the product does from the cards beside it.
- **U4, duplicate actions with different words:** "Start Free" in the hero vs "Sign up" in the nav, and "Book Demo" twice. Are they the same? I hesitate.
- **U3, invented terms and jargon:** "Approvability", "minimal blast radius", "Self-driving PRs", "CLI/MCP", "48.31% Recall", "Murmur" (product name with no gloss at first sight).
- **U4, misreadable states:** the FAQ shows the open question in dark text and the closed ones in light grey, so they look disabled rather than clickable. The hero product cards look like buttons but have no arrow or affordance.
- **Readability:** the mock-UI pictures have text at roughly 8 px ("Scoped to agent execution in this workspace"), and the hero card copy sits on a speckled lilac texture with lowish contrast. There's also a mono eyebrow, "AUTOMATIC REVIEW AND VALIDATION" (guard).

To drop one point (to 6.5): remove the product cards from the hero, so the only explanation is the metaphor headline.

---

### Anchors (First-time user lens, reused every round)

**10: nothing to change.** None of the four references gets there. It's the bencho Time scrubber with its three nitpicks fixed: the title, then one sentence saying what to do and what will happen; one filled primary at the bottom right whose label is a plain verb phrase about this task ("Write the script", not "Add to bench"); every number carries its unit ("15 min", "Corner 20px"); every icon-only control is either labeled or obvious from its shape and position; no eyebrows; nothing floats over content; nothing changes position when clicked. A newcomer acts in under three seconds and is never surprised by the result.

**9.5: ship next to the references.** The bencho panel with one of its three nitpicks left. For example the instruction line and the clear primary are there, but one value is unitless or one icon is unlabeled. A designer would flag it; a user wouldn't pause.

**9: bencho Time scrubber as it is.** Purpose and next step are clear from one sentence. The primary is bottom right and unmistakable. Segmented pills show the selected option as a white chip, and bar sliders have the label inside and the value at the right. Defects are limited to an in-house word on one button ("bench"), unitless numbers ("Step 15", "Momentum 50") and a few unlabeled icons. For NAVI, a step screen is a 9 if its heading plus one line says what to do, "Continue"/"Record" sits alone at the bottom right, and the only flaws are one vague label or a missing unit.

**8.5: rainbrand home.** A strong path from headline to one black primary, numbered steps, a crystal-clear +/– FAQ, but with one visible defect a user would notice (the chat widget covering FAQ text) plus decoration a newcomer reads past (eyebrows "HOW IT WORKS", mystery labels "CANVAS: 01"). For NAVI: the flow is clear, but there's one overlap or crowding issue, or a non-functional-looking element.

**8: BoardUI Agent Progress page.** The core widget is excellent (struck-through done, outlined current row with spinner, faint pending, "4 steps left"), but the page around it doesn't say what to do next: no primary, five toolbar buttons, NEW badges, a TOC and floating buttons compete, and one sentence is jargon-heavy. For NAVI: each control is understandable on its own, but the screen as a whole has no single obvious next action, or it's busy enough that you scan before you act.

**7.5 (below the bar): macroscope home.** There is a primary, but the headline is a metaphor, two buttons say the same thing in different words ("Start Free" / "Sign up"), invented terms ("Approvability"), closed FAQ rows look disabled, and the text in the pictures is too small to read. For NAVI: someone hesitates at least once per screen about wording or about what a click will do.

Quick test per screen: (1) Can I say what to do in one sentence after a 3-second look? (2) Is there exactly one filled button, at the bottom right, with a task verb on it? (3) Does any word, number or icon make me stop? Zero stops and yes/yes = 9.5–10; one minor stop = 9; one visible defect (overlap, unclear next step) = 8.5; several = 8 or lower.

---

## visual reviewer

## Calibration: Visual design (V)

Lens: rubric "Visual design (V)" items 1–6, plus the overdesign guard. Sources: the screenshots in `scratchpad/refs/`, plus live measurements taken with Playwright at 1440×900 in light and dark (`getComputedStyle` on the elements named below). Dark captures are in `scratchpad/cal/` (`bencho_dark.png`, `boardui_ap_dark.png`).

Note: `refs/boardui_home_dark_0.png` and `_1.png` are actually **light** captures. I checked BoardUI dark mode live on the Agent Progress page (`cal/boardui_ap_dark.png`). Rainbrand and Macroscope have no dark mode: their light and dark captures are identical.

| Reference | V score |
|---|---|
| bencho.dev Time scrubber | **9.5** |
| rainbrand.com home | **9.5** |
| BoardUI Agent Progress | **9.0** |
| macroscope.com home | **8.5** |

---

### 1. bencho.dev: Time scrubber block (9.5)

Measured: Inter only. Two weights: 500 for control labels and values, 400 for row labels ("Fill", "Stroke") and the description. Sizes are tight: title 17px/500 (−0.34px tracking), description 13px/400 in #6F6E68, row labels 13.5px in #3C3B37, segment text 12.5px/500, time readout ~40px with "AM" at 14px in mid-grey. Settings sheet radius **28px** with 18px padding. Segmented track 36px tall, radius 999px, fill rgba(23,24,26,.06), 2px inset. Selected pill 32px, white. Bar sliders **44px** tall, radius **10px**, label inside on the left, value on the right. Buttons 40px, radius 999px. Primary is #17181A, full width, at the bottom.

Why 9.5:
- **Restraint and rhythm.** Four segmented rows at an even 46px pitch, then two 44px bar sliders, then a pinned footer with one primary under one ghost button. One focal point per area: the 9:30 readout in the stage, the black "Add to bench" in the panel. Edges align on one 264px column.
- **Grey steps do the work instead of borders.** There are only three surface values: sheet, 6% black track, white selected pill. No strokes and no shadows. This is the "white sheet in a slightly darker tray" idea at control scale.
- **Type is quiet.** Nothing is above 500 and no weight is used for decoration. The display number gets size, not weight. This is the opposite of "bold everywhere".
- **The controls are the reference for ours.** The bar slider with its label inside and value at the right, the segmented pills and the 40px pill buttons are exactly the bencho controls the rubric names.
- **Dark mode is a clean inversion.** Sheet ~#1E1E1E, stage card ~#2A2A2A, and the primary flips to white with dark text, so it stays the brightest thing on screen.

Nitpicks (why not 10):
- The tick labels ("9 AM", "10 AM") are 11px at about #878787 on white, roughly 3.6:1. They are not readable from across a room.
- In dark, the selected segment (~#3A3A3A on ~#2A2A2A) is too subtle. The selected state is hard to read at a glance.

To drop one point (to 8.5): give the sliders and segments different heights or radii (for example 32px segments next to 48px sliders with 6px corners), or let the gap above the footer swell unevenly so the panel looks unplanned. Or add a border to every control on top of the fill.

---

### 2. rainbrand.com: home (9.5)

Measured: ground **#D9D9D9**. Sheets are white or #0A0A0A, with radius **20px** (inner image trays 20px with 6px padding, so the white sheet sits *in* a grey tray). Notched corners join sheets to a single 1px connector line. The custom grotesk is used at **one weight, 400, for every text node** (54 of 54). Body is 16–17px. Section headings 40–48px/400 with −2% to −3% tracking. The hero uses a wide extended display face in caps. Geist Mono 12px caps for small labels. Text #0A0A0A, secondary #5C5C5C (about 6.7:1 on white) or 60% black. Buttons are pills: 38px in the nav, **46px** for hero CTAs, black primary and #D9D9D9 secondary.

Why 9.5:
- **This is the Trays look.** Grey ground, white sheets with big 20px corners, inner grey trays holding white or image content, and colour that appears *only* in the illustrations (the liquid blobs and fluid images). The UI chrome is strictly black, white and grey. This is rubric V1, and it is the model for "colour only from the statues and covers".
- **Weight discipline.** Every text node is 400. Hierarchy comes only from size (16 → 40 → 48 → hero display), case (wide caps for the brand line) and grey value. It is the strongest "no bold everywhere" example of the four.
- **Wide caps for names, regular elsewhere.** "THE BRAND LAYER FOR AGENTS." and "ON-BRAND, ON REPEAT." are the template for NAVI's names and page titles in Mona Sans wide caps.
- **Generous, even spacing.** Hero content sits in a lot of white. Testimonial sheets share one 30px inset, a hairline above "Read the story" and identical baselines across three columns. FAQ rows have an 85px pitch with mono numerals.
- **Contrast is high everywhere it matters:** near-black on white, white on near-black, with grey reserved for secondary lines.

Nitpicks (why not 10):
- **Eyebrow labels.** MANIFESTO, HOW IT WORKS, FEATURES, CUSTOMERS and FREQUENTLY ASKED QUESTIONS are mono caps sitting above headings. This is a guard item for NAVI. In our app the same element is a defect costing 0.5–1. **Do not import it.**
- The micro mono labels are too small: "CANVAS: 01" is 8.5px and "[READING FILES]" is 9.4px.
- There is no dark mode, so V4 can't be confirmed. It is judged on light only.

To drop one point (to 8.5): mix weights (bold headings over regular body), or shrink the sheet radius to 8px so the trays read as ordinary cards. Or colour the chrome: blue buttons, tinted sheets.

---

### 3. BoardUI: Agent Progress component page (9.0)

Measured: Inter at three weights: 400 (64 nodes), 500 (31), 600 (9, only the 12px caps sidebar group labels). Title 40px/500. Lede 16px/**500** in ~#737373 (about 4.7:1). List rows 14px/500. Radii: 10px buttons and segmented track, 6px nav items, 16px preview frame, pill for the active step row. Header buttons 36–38px with a 1px #EBEBEB border. Light body is white. The segmented control uses a #F7F7F7 track. Dark: body #121212, raised surfaces ~#262626, 1px #444 border.

Why 9.0:
- **The list is the reference for ours.** In the Agent Progress card, each step has a 16px status glyph and 14px text on an even 38px pitch. Done steps are struck through in grey, the active step sits in a 32px outlined pill with a spinner, and pending steps are grey with empty rings. State is shown by tone and one outline, never colour. This is "BoardUI lists" in rubric V5.
- **Small, consistent radii and control heights.** 36/38px header controls, 28px segment buttons in a 36px track, 32px nav rows. Everything snaps to a 4px grid.
- **The sidebar is a tray.** A slightly darker panel with a 1px border holds the navigation tree, with indent guide lines and a single filled active row.
- **Dark mode is complete** and keeps the same structure, with surfaces stepped #121212 → ~#1A1A1A → ~#262626.

Rough edges (why 9, not 9.5):
- Too many weights for the job. The lede is set at **500 in grey**, which makes long copy heavier than needed. 600 caps group labels are a third weight. Bold is creeping in.
- Low-contrast greys. The "On this page" table of contents is ~#A1A1A1 on white (about 2.6:1). In dark, pending steps are ~#737373 on ~#262626 (about 3.6:1).
- Colour in the chrome: blue NEW badges ×5 and the blue "Set up theme switching" link pull the eye away from the component.
- The page is denser than our target, with sidebar, top icon bar and table of contents all competing. The component is calm; the page around it is busier.

To drop one point (to 8.0): bump list text to 600, add a border to every row instead of only the active one, or let the step pitch vary.

---

### 4. macroscope.com: home (8.5)

Measured: Geist and Geist Mono. **Nine weights in use** (300, 400, 450, 500, 550, 560, 600, 650, 700). Hero 64px/500 with −3.7px tracking (about −5.8%, very tight). Product headings 20px/560. Body 14–16px in blue-grey #5D6B98 (about 5.3:1). Mockup text goes down to 6.5–9px. Radii are inconsistent: 6, 7, 9, 10, 10.5, 12, 16, 40 and 999px. Pill CTAs are 45px tall, #191E2D primary.

Why 8.5:
- **The illustration is the point.** The lilac halftone landscape with a figure is textured, quiet and monochrome-ish. It is the vibe Andy wants from the statues: colour carried by an illustration, not by the UI.
- **The type scale is clear at section level.** A big tight display heading, 20px/560 feature titles with a glyph, and 16px body on one column about 1100px wide. Left edges align from section to section.
- **The CTAs are well made:** 45px pills, dark primary next to a translucent secondary, consistent across sections.

Rough edges (why not 9):
- **Guard hits.** The hero feature cards are glassy (white at 15–23% opacity over the illustration). Product shots sit in blue → pink → purple gradient frames. The Code Review section uses a purple and orange glow on black. "AUTOMATIC REVIEW AND VALIDATION" and "+ beta" are eyebrows above headings.
- **Weight soup:** nine weights, including in-between values (450, 550, 560, 650). There is no clear regular/medium rule.
- Mockup text at 6.5–9px is unreadable, which makes it decoration.
- Low-contrast secondary text: collapsed FAQ questions are ~#9698AC on white (about 2.9:1), and the logo strip is washed out.
- Radii come from nine different values, so nothing feels like one family.

To drop one point (to 7.5): add more gradient-framed mockups and glass, or let the hero illustration compete with saturated UI colour.

---

### Anchors for V (reuse every round)

Measure these with `getComputedStyle` when unsure.

#### What a 10 looks like
Bencho's control panel inside rainbrand's trays, with their nitpicks fixed.
- **Ground and trays:** a grey ground (rainbrand #D9D9D9; ours #E4E4E1). White sheets with **20–28px** corners (rainbrand 20, bencho 28). Inner trays are the ground grey with ~6px padding, so the white sits *in* grey. Exactly **three surface steps** per area (ground, tray, sheet). No borders or shadows needed to separate them.
- **Colour:** zero hue in the chrome. Black, white and greys only. Colour appears only in illustrations and covers (rainbrand blobs; our statues).
- **Weights:** body and labels at **400**, with 500 at most for control text (bencho). Page titles and names in **wide caps** (rainbrand hero) and never above 500. No 600 or 700 anywhere except possibly one display.
- **Sizes:** body 15–17px, control labels 13–14px, titles 17px (panel) or 40–48px (page). Nothing below 12px, except Geist Mono times at 12px or more with at least 4.5:1 contrast.
- **Controls:** one family of heights. Bencho uses 32px segments in a 36px track, **44px** bar sliders with the label inside and the value at the right, 40px buttons and 46px hero buttons. One radius per control type: 999px pills, 10px bars.
- **Contrast:** primary text at least 12:1 (#0A0A0A to #17181A on white), secondary at least 4.5:1 (rainbrand #5C5C5C = 6.7:1). The selected state is obvious in both themes. Dark is a deliberate inversion (bencho: primary flips to white) with the same structure.
- **Rhythm:** an even row pitch (bencho 46px, BoardUI 38px), one aligned column edge, one primary at the bottom right or as the footer of the panel, and no dead holes.
- **Guard:** zero hits. No eyebrows, glass, gradients or glow.

#### What a 9 looks like
BoardUI Agent Progress, or bencho/rainbrand with one nitpick left.
- Structure, trays and controls are all at the 10 level, but one or two small slips that only a designer would see:
  - one grey under 4.5:1 for minor text (bencho tick labels at 3.6:1, BoardUI table of contents at 2.6:1);
  - a third weight creeping in (BoardUI 600 group labels, a 500 grey lede);
  - a weak selected state in one theme (bencho's dark segment);
  - a small dose of chrome colour (BoardUI blue NEW badges);
  - a micro label under 11px (rainbrand 8.5px).
- At most one guard-adjacent element, and it isn't prominent.

#### What an 8 looks like
Macroscope with the illustration removed, or any screen with a few visible rough edges.
- Weights drift: four or more weights, or 600 or more used for ordinary labels.
- Radii come from more than three unrelated values (macroscope uses nine). Controls in the same area have mismatched heights.
- Several secondary texts under 4.5:1 (macroscope FAQ at 2.9:1), or tiny decorative text.
- One or two guard hits: an eyebrow over a heading, a glassy card, a gradient frame or glow.
- Still clearly designed, with a clear scale, aligned columns and good CTAs. Nothing broken or crowded.

#### Quick checks for scoring NAVI against these anchors
1. Count font weights on the screen: 2 is a 10, 3 is a 9, 4 or more caps it at 8.5.
2. Count distinct radii: up to 3 is a 10, 4–5 is a 9, 6 or more caps it at 8.5.
3. Find the lightest text that carries meaning. Under 4.5:1 costs 0.5; under 3:1 costs 1. Check light and dark.
4. Count guard hits. Each one costs at least 0.5, and an eyebrow over a page title costs 1.
5. Check that control heights in one panel come from one set (for example 36/40/44).
6. Check for any hue in the chrome outside the statues, covers and the record or mark red. Each instance costs 0.5.

---

## qa reviewer

## Calibration: Interaction QA (Q)

Lens: rubric "Interaction QA (Q)" items 1–6, plus the overdesign guard (only "things that move or overlap when you click" applies here).
Method: Playwright (playwright-core from `recorder/agent-screenplay`), headless Chromium, 1440×900 and 390×844, live sites, 2026-11-05. I drove the pointer step by step, pressed real keys and logged `document.activeElement`, `:focus-visible`, bounding boxes before and after each click, and a `layout-shift` PerformanceObserver. Scripts are in `scratchpad/calq/`; screenshots are in `scratchpad/refs/cal-q/` (83 files, 5.7 MB).

| Reference | Q score |
|---|---|
| bencho time scrubber | **9.5** |
| bencho slide-to-confirm | **8** |
| bencho toast stack | **8.5** |
| BoardUI data table | **8.5** |
| Rainbrand home (nav, FAQ, 390) | **9** |

---

### 1. bencho: time scrubber (9.5)

What worked, as tested:
- **Drag feel.** I pressed on the ruler and moved 80 px left in 10 steps. The readout rolled its digits live (10:02 mid-drag) and snapped to the step on release (10:00). A fast 140 px fling coasted with deceleration (sampled every 120 ms: 502 → 454 → 423 → 413 → 408 → 406 → 405) and settled on a 15-minute step. `ts_dragging.png`
- **Nothing moves on click.** I clicked all 7 segmented pills (Step 5/30, Format 24h/12h, Fill Dark/Light, Stroke On). Every pill group kept an identical bounding box, and so did the ruler card (325×72.5 in 12h and in 24h, so the readout width doesn't change it). The PerformanceObserver logged no shift without input after the first paint. `aria-pressed` flips correctly.
- **Bar sliders.** Dragging Momentum to 85 % updates the number, and the label stays readable over the fill. A plain click sets the value (click at 10 % gives 10). Over-dragging Corner clamps at 32px, and the card radius follows live. Arrow keys step by 2px. `ts_slider_drag.png`
- **State feedback in place.** "Share" turns into a green "✓ Link copied" in the same box (the box is identical before and after) and reverts after about 2 s. `ts_share_click.png`
- **Dialog.** Tab is trapped (Close wraps to the first pill), Escape closes it, and the ruler is `role=slider` with `aria-valuetext` "9:30 AM". The arrow keys step exactly one Step (9:30 → 9:45 → 9:30 → 9:15).
- **390 px.** No sideways scroll (scrollWidth 390). Share and Add to bench sit side by side with the primary on the right. The panel scrolls internally under a fade. `ts_390.png`

What would drop it a point (the nitpicks found):
1. **Three different focus rings.** The pills and Share use a grey double ring. "Add to bench" and the Preview/Code tabs fall back to the browser's default blue `outline:auto`. The ruler uses a blue (34,49,221) inset rectangle. Test: Tab through, read the computed style and screenshot. `ts_focus_addbench.png`, `ts_focus_ruler.png`, `ts_focus_previewtab.png`
2. **Tab order doesn't follow the layout.** It goes pills → sliders → Share → Add to bench → ruler → play → Preview/Code → Save/Sound → Close. On screen, the toolbar and the stage come first.
3. **Some slider keys do nothing.** Home, End, PageUp, PageDown and ArrowUp on the ruler leave the value unchanged.
4. The stage settles with about 0.15 of layout shift during the entrance animation on load. It isn't caused by a click, and the block doesn't move once it's idle.

**To drop to 9:** any shift caused by a click (for example the readout getting wider in 24h and nudging the ruler), or a focus ring missing entirely on one control.

### 2a. bencho: slide-to-confirm (8)

What worked:
- A plain click does nothing, which is the right friction. A partial drag springs back (sampled at 444 → 394 within 160 ms). Vertical wander during the drag is ignored. A full drag squishes the track (350 → 341 px), shows "✓ Confirmed" and resets after about 1.5 s. The grip has resistance: the pointer moved 280 px but the grip moved 252 px. `sc_partial.png`, `sc_confirmed.png`
- Width and Speed update live, and there's no sideways scroll at 390.

Defects:
1. **No keyboard path.** The grip is a focusable `<button aria-label="Slide to confirm">` that Tab reaches (9th stop). Enter, Space, ArrowRight and End do nothing: I sampled the grip x position and the label for 800 ms after each key. A keyboard user can't confirm at all. `sc_focus.png`
2. **The threshold is stricter than the description.** The description reads "past the mark it takes over and finishes itself". With a pointer drag of 290 px the grip ends at 98 % of the track, and 305 px puts it 5 px from the end. Both snap back. Only a pointer drag of 320 px or more, which overshoots the track's end, confirms it. A mouse user who stops at the visible end gets bounced back.
3. The focus ring on the grip is the browser default (`outline:auto`, blue), unlike the rest of the block.

**To get it to 9:** Enter or Space confirms (or arrow keys walk the grip), and the threshold sits around 80–90 % of travel.

### 2b. bencho: toast stack (8.5)

What worked:
- Pointing at the stack, or Tab focus inside it, fans the toasts out into a list. While they're collapsed, the hidden toasts' close buttons are `tabindex=-1` and become 0 when expanded, which is well thought out. `tst_hover.png`, `tst_kbd_x.png`
- **Retry** changes "Payment declined" to "Payment complete" in the same spot, with no new toast and no jump.
- After a dismiss, the next toast slides in at the same position, so the close button stays under the pointer (front toast y = 525 after each of 4 dismissals). You can click repeatedly without chasing it.
- No sideways scroll at 390. `tst_390.png`

Defects:
1. **Focus is lost after a keyboard dismiss.** I tabbed to "Dismiss Payment declined" and pressed Enter, and `activeElement` became `<body>`. Focus should move to the next toast or back to the region.
2. **A duplicate toast.** After 4 dismissals the stack showed "Kai joined your bench" twice. `tst_empty.png`
3. The region has no `aria-live` and the toasts have no `role=status`, so nothing is announced.
4. Retry has a blue inset ring, a fourth focus style across bencho.

**To get it to 9:** focus lands on the next toast after a dismiss, and the duplicate is fixed.

### 3. BoardUI: data table (8.5)

What worked:
- **Sorting** cycles ascending → descending → unsorted on each header. Column widths stay put (within ±1 px) across 5 sorts, and rows don't jump.
- **Select-all cycles through three states.** Starting from 2 rows checked, it shows indeterminate. A click checks all 8, and another click clears all 8. Space on a row checkbox toggles it.
- **Grid keyboard model** (react-aria). The table is a single Tab stop, and the arrow keys move by cell and by row. The focused row gets a 2 px blue ring. Focusing an icon button shows a tooltip ("More actions", "Delete"). `bt_kbd_grid0.png`, `bt_kbd_grid1.png`
- **Status select.** Mouse or keyboard (Enter opens it, ↓ highlights, Enter picks), and focus returns to the trigger. In dark mode the selected option is highlighted and the chevron flips. Row heights don't change. `bt_dark_dd.png`
- **Empty state.** Searching "zzzz" shows "No customers match your filters." Searching "lubin" filters live to 2 rows.
- **Dark toggle** in the header: clean, and the toggle relabels itself "Use light mode".
- **At 390** the page doesn't scroll sideways. The filter chips become a strip that scrolls sideways, and pagination collapses to "1 2 3 … 6". `bt_390_dark.png`

Defects:
1. **Escape after the ⋮ menu puts focus on Delete.** I opened "More actions for Kianna Vaccaro" with the mouse and pressed Escape. Focus and a visible ring, plus the "Delete" tooltip, landed on that row's **Delete** button, not on ⋮. The next Enter would hit Delete. `bt_esc_focus.png`
2. **Delete and Edit are dead clicks.** Neither confirms, offers undo, shows a toast or changes the row (I compared tbody before and after). "Archive customer" does nothing visible either.
3. **Sideways scroll at desktop width.** At 1440 the table is 1000 px wide inside a 756 px container, so Price is cut off and Actions are out of view until you scroll the card sideways. The row focus ring is clipped at the right edge. `bt0.png`, `bt_kbd_grid0.png`
4. Inside the ⋮ popover (it's a `role=dialog` section), ArrowDown doesn't move between items; only Tab does. Headers have no `aria-sort`.
5. At 390 only Name and half of Purchase are visible. The site's floating palette and theme buttons sit over the bottom-right corner of the table card, next to the pagination's Next button.

**To get it to 9:** Escape returns focus to ⋮, Delete gives feedback (undo), and the Actions column fits or sticks at 1440.

### 4. Rainbrand: home (9)

What worked:
- **Mega-menu.** It opens on hover and on click, and a second click closes it. Moving from Features to Resources morphs the open panel across without closing it. Enter opens it, Tab goes into the panel, the arrow keys move between items (the focused item gets the same grey fill as hover), and Escape closes it and returns focus to "Features". `rb_features_hover.png`, `rb_kbd_menu.png`
- **FAQ "+" rows** (`<details>`). Several can be open at once. The height animates over about 250 ms (sampled 119 → 185 → 213 → 215). Rows above the clicked one keep their y position, so only the content below moves, which is expected for an accordion. The "+" becomes a filled black "−". Keyboard focus shows a clear 2 px rounded ring around the whole row, and Space and Enter toggle it. `rb_faq_1440_focus.png`
- **Agent tabs.** Arrow keys move between tabs and select them. Panel heights vary (184 to 312 px), but the FAQ below stays at y = 952 for every tab, so switching tabs moves nothing else.
- **390.** scrollWidth stays 390 everywhere. The hamburger opens a menu with collapsible Features and Resources sections, and Escape closes it and returns focus to "Open menu". FAQ rows wrap cleanly with the "+" aligned. `rb_390_menu_features.png`, `rb_390_faq.png`
- The CTA focus rings ("Get started", "Sign in") are a crisp double ring. `rb_focus_getstarted.png`

Defects:
1. **The top nav has no visible focus.** Features, Resources, Customers and Pricing compute to `outline: none` with a transparent box-shadow while `:focus-visible` is true. The screenshot of a focused Features shows nothing. `rb_focus_features.png`
2. At 390 the agent tablist scrolls sideways (505 px of tabs in 354 px) with Cursor and API hidden, and nothing shows that more tabs exist. `rb_390_tabs.png`
3. The mobile menu doesn't lock body scroll (minor, because it's a 220 px drop-down, not a sheet).

**To drop to 8.5:** another missing focus state, or a click that moves content (for example tab panels pushing the FAQ down).

---

### Anchors (reuse every round)

**10: nothing to change.** Every behaviour from the 9.5 time scrubber, plus none of its nitpicks:
- Pointer interaction is as good as the bencho ruler and sliders: live feedback during the drag, a snap or coast on release, values clamped at the ends, and a click on a track sets the value.
- Clicking any control moves nothing else, measured by bounding boxes before and after (bencho pills: identical boxes across 7 clicks; Rainbrand tabs: the FAQ stays at y = 952 across 4 tab switches).
- **One focus-ring style everywhere**, visible on every focusable control. No browser-default blue `outline:auto` mixed in, no control with `outline:none` and nothing else.
- Tab order follows the reading order, Escape closes any layer **and returns focus to its trigger** (Rainbrand Features, BoardUI status select), and focus is never dropped to `<body>`.
- Every drag control also works from the keyboard: the arrow keys step, and Home/End go to the ends.
- State feedback stays in place and resets itself, like bencho's "Share → ✓ Link copied". Every button does something visible.
- Empty states exist (BoardUI: "No customers match your filters."). At 390 there's no sideways scroll, and anything that scrolls sideways shows it continues.

**9: one or two nitpicks a keyboard or a11y tester would find; a mouse user notices nothing.** Rainbrand home (nav focus invisible, a 390 tab strip with no affordance) and the time scrubber minus half a point (focus styles are inconsistent across 3 styles, Home/End do nothing, tab order puts the panel first). Everything a pointer user does is smooth, and nothing shifts on click.

**8: clearly good, but a tester hits a visible rough edge.**
- One real keyboard or focus bug: the slide-confirm can't be confirmed from the keyboard; a toast dismiss drops focus to `<body>`; BoardUI's Escape sends focus to **Delete**.
- Or a dead click: BoardUI's Delete and Edit give no feedback.
- Or a threshold that fights the user: slide-confirm snaps back at 98 % of travel.
- Or sideways scroll at desktop width: BoardUI Actions are hidden at 1440.

One of these makes an 8.5. Two or three, or one of them in a main flow, makes an 8.

How to apply these to NAVI: a screen gets ≥ 9.5 only if every check in the 10 list passes when run, with at most one cosmetic focus-ring inconsistency. Any focus that goes to `<body>`, a missing Escape return, a dead button or a shift caused by a click caps the screen at 8.5. Two of them cap it at 8.

---

