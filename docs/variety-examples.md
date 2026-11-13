# Variety examples: the four scripts, rewritten

Proof for `docs/variety-spec.md`: the same four videos, written so that read together they sound like one person
on four different days. Talking versions only. **None of this has been voiced or heard yet** (spec section 9).

What was checked: every rewritten talking version was run through the current `scripts/script/check_script.py`
against the real script files (cue words in order, still-screen, restarts, positions, bans). All four pass with no
errors on the talking versions. Two errors remain and both are in the existing **captions**, not the talk; they
are noted under the scripts they belong to.

## The four side by side

| | To-do list | Whop product | Buyer view | Real Biz tour |
|---|---|---|---|---|
| Kind | SaaS | SaaS | Course | SaaS |
| Opens with | a reason ("Quickest way to show you this…") | a condition ("If you're selling anything…") | where the viewer lands ("The first time you join…") | a question ("What does NAVI do when…?") |
| First word of each section | Quickest / It / Then | If / First / Price / And | The / Inside | What / API |
| Starts with marker + comma (the breath start) | none | none | none | none |
| Run-in marker starts | "Then" | "And" | none | none |
| uh / um | 1 um, at a clause start ("and then, um, book") | 1 um, after a clause ("the rest of it, um, but") | none | 1 uh, after the topic ("API keys, uh, those") |
| Per 100 words | 0.8 | 0.6 | 0 | 1.7 |
| Repair | none | bare repeat ("I'll, I'll just") | said again better ("or, I mean, you do them in order") | abandoned start ("And NAVI can, so it'll…") |
| Hunt | "where did they put it" | none | none | none |
| Hedge of the day | honestly | actually | none | none |
| Who acts | I, then you | you, then I | you | NAVI / it |
| Endings | action / action / what's left | place / "for now" / place / action | place / place | list / place |

Old versions, for comparison: all four opened "(Okay,) so this is…", every second section started "Right, so", the
fillers were "the, uh, [thing]" or "is, um, [thing]", and both restarts were word, filler, same word.

No section here starts with a marker and a comma, because the last three videos used that start in every section
and the history rules rest it. In normal running about one video in two would have one such section.

---

## 1. A simple to-do list (`examples/test-todo-b.json`)

Style of the day: opens on a reason; I-led; markers on: then; resting: okay, right, so; one um at a clause start;
no repair; one hunt (the explore step flagged Clear completed); long sentences.

**open** — cues: start, this, box, call, Enter
> [relaxed] Quickest way to show you this is to just use it, so I'll click in the box up top, call the dentist, and hit Enter.

**add-and-tick** — cues: couple, gas, book, circle (the file's own cues add, Pay, "book the train", circle also still match, in order)
> [relaxed] It needs a few more on it before there's anything to show, so I'll add a couple, pay the gas bill, and then, um, book the train tickets, that'll do. And once you've actually done one, the little circle next to it is the tick, you just click that.

**filter-and-clear** — cues: bottom, Active, Clear, two (the file's leave, finished, where also still match)
> [relaxed] Then the filters are at the bottom of the list, All, Active, Completed, and honestly I'd leave it on Active, the done ones aren't much to look at. To get the finished ones off there completely there's a, where did they put it, Clear completed, over on the right. So it's down to the two I haven't done.

Notes:
- "down at the bottom" in the old script fails today's position check (with three items the filter bar sits
  mid-screen, not at the bottom). "at the bottom of the list" passes.
- Caption to fix (existing error, not from this rewrite): "At the bottom, switch between…" → "Under the list,
  switch between active and completed tasks. Clear completed removes the finished ones."
- The hunt is worded "where did they put it", which `audio_edit.hunt_words` doesn't protect yet (spec section 6).

---

## 2. Create a product on Whop (`output/demos/create-a-product-in-your-whop-e1b1/script.json`)

Style of the day: opens on a condition; you-led with I for the choices; markers on: and; resting: okay, right;
one um after a clause; one bare repeat; no hunt; "actually" as the hedge; mixed sentence lengths.

**open** — cues: start, Products, Create
> [relaxed] If you're selling anything on Whop it starts on the Products page, and a new one is Create product, the blue button top right.

**name** — cues: describe, myself, box, just
> [relaxed] First thing it offers is to describe it and the AI drafts the lot, which is fine, I'd just rather fill it in myself. Name goes in this box, and I'll, I'll just call it a test for now.

**price** — cues: price, right, take, Done, Create
> [relaxed] Price is the only other bit I'd bother with at this point, it's this bit on the right, there's a few quick amounts so I'll take fifty, and Done. You could keep going with the rest of it, um, but none of it's needed yet, so Create product, at the bottom of the form.

**hide** — cues: link, Done, dots, Hide, Hide
> [relaxed] And you get a link for it right away, which I'm not sharing with anyone yet, so Done. Actually while it's still half set up I'd hide it as well, that's under the three dots on the end of the row, Hide, and then it asks you again, so Hide.

Notes:
- "bottom left" (the mistake from the 10 Nov review) is now "at the bottom of the form".
- Caption to fix (existing error): "…click Create product at the bottom left." → "…click Create product at the
  bottom of the form."
- In **name**, the typing cue is the second "just" ("I'll just call it"), as in the original, where the first
  "just" also came before "box". The first "just" sits before "myself", so the cue order still resolves.

---

## 3. Opening the course, buyer view (`output/seats-dev/videos/buyer/script.json`)

Style of the day (course: calm, few fillers, no mumbling): opens on where the viewer lands; you-led; no markers at
a start; no uh or um; one repair, said again better; long sentences.

**home** — cues: start, join, System
> [relaxed] The first time you join Real Biz this is where it drops you, and the course you're after is Real Course, right here in the list.

**modules** — cues: modules, 01, down
> [relaxed] Inside it's just the modules, nothing else to click through. Start Here comes first, then Module 01, and after that it's in order, or, I mean, you do them in order, all the way down.

---

## 4. A look at the money pages, Real Biz tour (`output/seats-dev/videos/real-biz-tour/script.json`)

Style of the day: opens on a question; NAVI is the one acting; no markers at a start; one uh after the topic;
one abandoned start; short question then a long line.

**balance** — cues: start, report, number, in, out
> [relaxed] What does NAVI do when the whole page is money? This is the balance report, in the real business, and every number on it stays blurred, cash flow, money in, money out.

**keys** — cues: Developer, film, key
> [relaxed] API keys, uh, those are under Developer. And NAVI can, so it'll open this page and film it no problem, it just can't make a key from here.

Notes:
- The cue "in" still resolves to "money in": the earlier "in the real business" comes before "number", so the
  in-order search skips it.
- "And NAVI can, so it'll…" is an abandoned start with no cut-off word. It's the least tested kind of repair
  (spec section 9, item 3): if it reads as a slip in the script, the fallback is
  "NAVI will open this page and film it no problem, it just, it just can't make a key from here."

---

## How these score on the proposed checks

- **Starts:** 11 sections, 11 different first words; 9 start with no marker, 2 with a run-in marker, none with a
  marker and a comma.
- **Fillers:** 3 across four videos, in three different places, none before a noun (the last five were all
  mid-phrase before the thing named, so that place is resting). One video has none.
- **Repairs:** 3 across four videos, three different kinds, in 3 of 11 sections (the old scripts: the same kind
  every time).
- **Hunts:** one, reworded.
- **Endings:** 4 stop on the action or the last item, 5 trail on a place, 1 on what's left, 1 "for now"; no two
  share their last three words.
- **Shared phrases between the four:** the only shared run of three or more words is the position phrase "at the
  bottom of the" (list / form) in the to-do and Whop scripts, which the spec leaves out of the phrase check
  because positions are fixed by the page.
