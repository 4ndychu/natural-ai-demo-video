# NAVI references: what we borrow, and for which screen

Studied 5 Nov 2026 with Playwright at 1440×900 in light mode, plus BoardUI in dark. Screenshots are kept outside the repo. The rule is vibe and components only, never a layout.

## What was looked at

| Site | Pages opened |
|---|---|
| bencho.dev | Home; the block pages Time scrubber, Label input, Step player, Slide to confirm, Toast stack, Picker (assignees), Checklist, Liquid toggle, Search (seek), Voice note, Context meter, Upload dropzone, Stacked bars |
| spaceui.one | Home, Components, Interactions, Primitives, Timeline |
| boardui.com | Home (light and dark); the components Sidebar, Agent Progress, Data Table, Composer Attachments; the templates AI Chat and Project Board |
| inspora.design | Home grid, the Product category, the "Interactive folder cards" post |
| rainbrand.com | The whole home page (7 scroll positions), Brand guidelines |
| macroscope.com | The whole home page (8 scroll positions) |
| hermes-agent.nousresearch.com | The whole home page (8 scroll positions) |
| Mobbin | **Not used:** the connector needs a paid plan. Figma isn't authorized in this session. |

## What each one teaches (the vibe, in one line each)

- **bencho.dev:** quiet, light type (about 14px, weight 400–500). Settings are rows with a label on the left and a compact pill control on the right. Bar sliders have the label and value inside. One full-width black button sits at the bottom of a panel, with an outline pill above it. Everything sits on a pale grey card with generous empty space. Micro-interactions are precise but small.
- **spaceui.one:** soft grey hero tray with very large rounded corners. Small "pill with a dot" status chips. A vertical timeline with hollow and filled nodes.
- **boardui.com:**
  - Agent Progress: one list per task, with a "4 steps left" header, finished rows greyed with a tick, the current row in an outlined pill with a spinner, and future rows behind dashed circles.
  - Data Table: status chips with a dot, a small dropdown per row, filter pills.
  - Dark mode keeps the same structure with lifted surfaces.
- **inspora.design:** a calm detail panel of label/value rows (Industries, Colors, Styles) with one black button at the bottom. Folder cards whose covers fan out, with liquid gradient images.
- **rainbrand.com:** a grey ground with white sheets in big rounded trays, joined by thin connector lines. Extra-wide caps headings, and key words set as grey pills inside running text. Liquid colour only in the imagery. Numbered FAQ rows, each with a "+" button. *Not borrowed:* its mono "[NOTICE] //" eyebrows (Andy dislikes eyebrow labels).
- **macroscope.com:** grainy halftone illustration behind quiet type. Feature cards with one thin line icon, a title and two lines of text. A soft lilac palette, with dark sections for contrast.
- **hermes-agent:** electric-blue engraved statues, condensed caps. It confirms NAVI's statue colour language: one bold colour per voice, the UI chrome stays neutral.

## What NAVI borrows, per screen

| NAVI screen | Borrowed pattern | From | Why |
|---|---|---|---|
| All step screens | Settings as label-left / control-right rows with compact pills, not full-width segment bars | bencho settings panel, inspora detail panel | Less visual weight; reads as a calm list |
| All step screens | Body type at weight 400–500, 14–15px secondary text, bold only for one thing per area | bencho, spaceui | Andy: "bold everywhere" is a dislike |
| Header / credits | Context-meter pattern: "26,400 of 30,000" with a thin stacked bar (used / this video / left) and legend dots, shown in a small popover from the credits pill | bencho Context meter | One tidy place for cost; the header stays a single number |
| Home | Batch card as a "folder" whose three covers fan slightly (static, no hover motion) | inspora folder cards | Tells a batch from a single demo at a glance |
| Home, New demo | Grey pills inside running text for the key choices in the summary line ("Using **Beginners** · **5 min** · **Alex**") | rainbrand | Makes the defaults line scannable without bold or labels |
| Script | Section list as a quiet list with the active item in a white pill; the line big on the right | bencho picker list, boardui sidebar | Calmer than the current tray highlight |
| Voice | Bar sliders keep the bencho look exactly: mid-grey fill, label left, value right, 12px radius. The "recommended" mark is a small notch | bencho slider | Andy loves these; match the source more closely |
| Voice | Statue cards stay; the colour lives only in the statue | hermes, macroscope | Colour from imagery, not chrome |
| Privacy | Preset cards as quiet tiles with one line each; the selected tile gets a dark ring | spaceui cards, bencho | Already close; keep it simple |
| Record | Progress as a single step list: done greyed with a tick, now in an outlined pill with a spinner, next behind dashed circles, and a "6 sections left" header | boardui Agent Progress | Replaces the separate Done / Now / Next labels |
| Review | Ruler-style timeline: fine tick marks, a red playhead line, and section names as small labels under the ruler | bencho Time scrubber | Makes "sections as ticks" literal and precise |
| Review | Marks as a toast-style list: a white pill with a red dot, the time, the reason, and an ×; and "Mark this moment" as one quiet pill | bencho Toast stack | Familiar, compact |
| Record, Stop | Slide to confirm, instead of an inline "Stop?" confirm | bencho Slide to confirm | Fits "confirm only destructive or costly"; no layout change |
| New batch | The file drop as a white dropzone card ("Drop a course outline here · .txt .md .csv") | bencho Upload dropzone | One clear target; the textarea stays for pasting |
| Batch | Rows like a data table: a status chip with a dot, fixed columns, one action | boardui Data Table | Less dead space, scannable |
| Settings | FAQ-like rows: a number-free list, a "+" or chevron to open, hairlines | rainbrand FAQ | Calm and consistent |
| Toasts | A stacked white toast with an icon, a short message and one action pill | bencho Toast stack | Matches the rest |

## Not borrowed (on purpose)

- Marketing-page hero layouts, big centered headlines, and sponsor or nav chrome from any site.
- Eyebrow labels in mono caps (rainbrand, macroscope), which are on Andy's dislike list.
- Glassmorphism, gradients in the chrome, and glow buttons (spaceui "aurora" buttons, boardui's blue CTA). These are AI-slop tells.
- Hover lifts and spring motion that move layout (bencho's playful blocks). NAVI keeps "nothing moves when you click".
