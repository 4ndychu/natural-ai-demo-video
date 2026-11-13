# Variety spec: making every NAVI video sound like the same person on a different day

Answer to Andy's complaint of 11 Nov 2026 (`reference/listening/2026-11-11-everything-sounds-the-same.md`).
Nothing here has been applied yet: this is the design, the replacement wording for the rules, and the checker spec.
The four scripts rewritten under it are in `docs/variety-examples.md`.

Where a number comes from `reference/research/`, the file is named. Where it is a guess, it says **guess**. Nothing
in this spec has been judged by ear yet; section 8 lists the listening round that should decide it.

---

## 1. Diagnosis: how "one good option" became the template

Eleven sections have been written across the four scripts. What they share:

| Slot | What the scripts did | Count |
|---|---|---|
| First words of the video | "(Okay,) so this is [a / the / what]…" | 4 of 4 |
| First word of the video is "Okay" | | 3 of 4 |
| Section 2 starts "Right, so" | | 4 of 4 |
| Section 3 starts "Okay. So now" | | 2 of 2 |
| A section starts with a marker at all | | 10 of 11 |
| Filler sits between "the / is / can't" and the thing named | "the, uh, little circle", "the, uh, three dots", "is, um, Real Course" | 5 of 5 fillers are mid-phrase, none at a clause start |
| Kind of restart | word, filler, same word: "book the, uh, book the", "it can't, um, it can't" | 2 of 2 |
| Hunt | "there's, where is it," | 1 of 1 |

### 1.1 The rules that did it (quoted)

1. **Step openers.** `voice-rules.md`: *"Start a new step with "Okay. So now," or "Right, so,". Both beat a bare
   "So now,"."* Experiment E3 compared three wordings of one line. The rule turned the two winners into the way
   every step starts. Real result: 10 of 11 sections open on a marker, and two markers cover 9 of them.
2. **Filler position.** `voice-rules.md`: *"A filler just before the name of the thing on screen… beat every other
   wording of that line. About a third of real casual narrators' fillers sit there."* and `script-writing.md` step 3:
   *"A filler sits inside a sentence, just before the name of the thing on screen."* The rule's own evidence says a
   third; the instruction makes it all of them. Clark & Fox Tree put more fillers at the start of a unit than anywhere
   else (43 per 1000 words at a boundary, 27 after the first word, 13 later: `research/disfluency.md`), and NAVI
   writes none there.
3. **Restarts.** `voice-rules.md`: *"One small restart or repeated word per section, not more. Repeat a small word
   with the stall between the two copies: "book the, uh, book the train tickets", "I'm, uh, I'm gonna", "the, the
   menu", "it's, it's in the left column"."* and `config/defaults.json` (hesitations slider): *"fillers and restarts
   per section written into the talking script"*. Two faults:
   - A cap ("not more") written as a count per section reads as a quota, so every section gets one. At 15 to 35 s a
     section, one per section is 2 to 4 a minute. Real casual narrators repeat about **1.0 a minute**, so a real rate
     is one every two or three sections (`research/casual-vs-scripted.md`).
   - Only one kind of repair is described. In the Map Task instruction givers, repeats are 1.32 per 100 words,
     restarts 1.77 and substitutions 0.62 (`research/disfluency.md`): repeats are about a third of repairs, and NAVI
     writes them 100% of the time.
4. **Hunts.** `voice-rules.md` gives two literal phrases ("there's, where is it," / "there's, where's the, um,"), and
   `config/defaults.json` `audio_edit.hunt_words` protects the pause only next to those phrases (`"where is it",
   "where's the", "where's it", "hang on", "let's see", "um"`). A hunt worded any other way gets its pause cut by
   `shape()` in `scripts/voice/generate.py`, so the pipeline rewards the template.
5. **Closers.** `voice-rules.md` lists four ("so that's one", "so yeah", "okay.", "all right.") and
   `check_script.py`'s `CLOSERS` knows only those four. The rule already says they can't repeat inside a video;
   nothing looks across videos.
6. **The example in `script-writing.md`.** The one sample script starts *"[relaxed] So this is a pretty basic to-do
   list."* All four videos then opened "…so this is…", even though the rule above it says the open "starts on the
   app doing something".
7. **The checker's own error messages hand out the template.** `check_script.py`: *"Write the hesitation into the
   sentence ("the, uh, little circle")"*, *"repeat a small word instead ("I'm, uh, I'm")"*, *"Put it inside the flow
   ("because, uh, it's a demo")"*. Every fix it suggests is the same three phrases.
8. **Take picking pulls every section to one take.** `voice-rules.md` section 2: *"2 per section; keep the one
   closest to the approved reference in pace and tone"*, and in `generate.py`:
   `score = (abs(wps - ref), fin) if ref else (fin,)` with `reference_pace_wps: 3.16` from one approved to-do take.
   Between two takes, the one that sounds most like that single take always wins, in every section of every video.
   The research's main finding was that Alex already varies less than even scripted narrators (pace variation 0.15
   against 0.25 casual: `research/casual-vs-scripted.md`). This picker reduces it further.
9. **The quality bar only ever adds recipes.** `voice-rules.md` section 8: *"Every new complaint from a review
   becomes a rule in this file… so the same mistake can't come back."* Each listening round judged one video. No
   round ever played two videos back to back, and the checker reads one script with no memory, so repetition was
   never a thing that could fail.

### 1.2 The breath at every start (found in the audio and the code)

Measured on the raw takes of the three recent videos (20 ms frames, level against each take's peak):

| Take | First word (alignment) | What the audio does |
|---|---|---|
| `buyer/home_take1` "Okay, so…" | 0.08 to 0.64 s | "Okay" loud for about 0.1 s (0 dB), then about 0.4 s of soft noise at −17 to −24 dB, then "so" at −12 dB |
| `real-biz-tour/balance_take1` "Okay, so…" | 0.08 to 0.72 s | same: about 0.1 s of word, about 0.45 s at −16 to −25 dB |
| `whop/price_take1` "Okay. So now…" | 0.08 to 0.76 s | same, longer (0.5 s falling to −40 dB) |
| `whop/name_take1`, `buyer/modules_take1`, `real-biz-tour/keys_take1` "Right, so…" | 0.16 to 0.64–0.72 s | "Right" about 0.25 s, then 0.2 to 0.3 s at −26 to −48 dB, then "so" |
| `whop/hide_take1` "It gives you a link…" (the only section with no marker) | 0.14 s on | speech straight through, no soft stretch |

The coordinator's separate measurement on the finished tracks agrees (marker about 0.25 s, then 0.4 to 0.6 s of
breathy noise at about −25 dB with rising zero-crossings, then the "s" of "so").

So the cause is three things together:

1. **The wording.** Every section is its own request, and nearly every one starts `[relaxed] Marker, so`. The model
   says the marker, then fills the comma with an in-breath, every time. It is the same sound in the same place because
   it is the same two words in the same place. (`research/mouth-and-breath.md` even proposed it on purpose: *"Start a
   new step on a fresh sentence after a full stop ("Okay. So now…"), the spot where a click and an in-breath
   naturally go."*)
2. **The edit can't see it.** ElevenLabs' alignment stretches the first word over the breath ("Okay," runs 0.08 to
   0.72 s), so to `shape()` there is no gap. And `shape()` only shortens a gap over `MAX_PAUSE = 0.8` after
   punctuation anyway. The raw takes have no silence before speech (onset 0.08 to 0.16 s), and `shape()` starts each
   section 40 ms before the first word, so there is no breath *before* the marker: what Andy hears as "a breath, then
   okay" is the previous section's tail, the fixed gap, "Okay", then the comma-breath.
3. **The gap is a constant.** `SECTION_GAP = 0.40` in `generate.py`. Every boundary has the same length of quiet
   before the same marker and the same breath.

The breath itself is good (Andy's best-rated moments were the model's own breaths). The fault is that it is the
same breath in the same slot of every section.

---

## 2. The principles

1. **A winning wording is one member of a family, never the family.** An A/B result adds an option and can ban the
   loser. It never fixes a slot.
2. **Caps are not quotas.** "At most one restart in a section" does not mean one in each. Rates are set per video
   (per minute, per 100 words), and many sections carry no disfluency at all.
3. **Proportions come from the research, per video kind.** Where real narrators spread a thing across several
   positions or kinds, NAVI's output across recent videos has to show roughly the same spread.
4. **Each video gets a style of the day,** drawn before writing: the same person, in a slightly different mood.
5. **Repetition is a defect that is measured:** inside a script, across a batch, and against a history of recent
   scripts. A script that repeats recent ones fails the checker like any other tell.
6. **The evidence-backed bans all stay:** cheerful one-word lines, a filler as its own sentence, "…", a filler as the
   last word, cut-off words, "If I click…", "and yeah, it's X" as the last words, announcing results, bright rising
   endings, tacked-on clauses, tags other than `[relaxed]`, invented personal history, more than one repair in a
   section.

---

## 3. The families

Each family lists options. They are examples of a kind, not a closed list: a new wording of the same kind is fine
and is better than reusing one from here. Lines in the families obey the bans in principle 6.

### 3.1 How a video opens

The open is still 10 to 12 s and still starts on the app doing something. What changes is that there are many
ways in. Each has a code the checker and the history use.

| Code | Kind | Example |
|---|---|---|
| `action` | Mid-action, no lead-in | "I'm clicking into the box up top here, and I'll put call the dentist." |
| `reason` | Why it's done this way | "Quickest way to show you this is to just use it, so…" |
| `question` | A real question the video answers | "What does NAVI do when the whole page is money?" |
| `probably` | "You've probably…" | "You've probably had the Products tab open and never touched it." |
| `opinion` | A view first | "Honestly the best thing about this one is how little there is to it." |
| `cond` | If / when / once / the first time | "If you're selling anything on Whop it starts on the Products page." |
| `scene` | Where the viewer has just arrived | "The first time you join, this is where it drops you." |
| `goal` | What will get done | "I want a product listed and hidden again in under a minute." |
| `stuck` | The bit people get wrong | "The bit that catches people is the price, not the name." |
| `wrong` | A common wrong guess, corrected from what was checked | "You'd think the course opens on a video. It, well, it doesn't." |
| `count` | A number or a time | "Three clicks gets you from the home page to the first lesson." |
| `two-ways` | A choice, and which one | "There's two ways to make a product and I only ever use the second." |
| `screen` | A remark on what's showing | "Nothing on the list yet, which is fine, that's the first job." |
| `noun` | The thing itself as subject | "The balance report is the page with the most money on it." |
| `lets` | "Let's" or "let me" | "Let me get a couple of things onto this list first." |
| `instr` | Straight instruction | "Go to Products on the left, and it's Create product." |
| `this-is` | "So this is…" (run-in marker, no comma) | "So this is the balance report." |
| `marker` | Marker, comma, then the line | "Okay, so…", "Right, so…", "All right, so…" |

Limits (**guess**; the research has no count of how demo videos open): `this-is` and `marker` together open at most
1 video in 6; "Okay" is the first word of at most 1 video in 8; no family opens two videos in a row or more than 2 of
any 6. Personal claims ("I use this every day") only when the brief gives them.

### 3.2 How a step starts

Four classes, by what the first words do to the voice:

| Class | What it is | Examples |
|---|---|---|
| `M0` no marker | The step starts on its content | noun first: "The price is the only other bit…"; action: "I'll add a couple…"; you: "You get a link for it…"; condition: "Once that's saved…", "When one's done…", "While it's still half set up…"; reason: "It needs a few more on it before…"; question: "And if you've finished one?"; opinion: "Honestly I'd skip the description."; what just appeared: "That's the link it gives you." |
| `M1` run-in marker | A marker with **no comma**, running straight into the line | "Then the filters are…", "And you get…", "So the price…", "Now the price…", "Next it wants…", "After that…", "From here…", "Back on the list…", "Over on the right…", "Same thing for…", "The other thing is…", "Last thing…", "That leaves…", "Inside it's just…" |
| `M2` marker, comma | The marker, a comma (the model breathes here), the line | "Okay, so…", "Right, so,…", "All right, so…", "Now, …", "So, …", "Anyway, …" (only after an aside) |
| `M3` marker, full stop | The marker as its own beat | "Okay. So now, …", "Right. …", "All right. …" |

Targets per video (**guess**, except where noted):
- At least half the sections are `M0`.
- `M2` and `M3` together: at most one section in a video of up to 4 sections, at most a quarter in a longer one, and
  never two in a row. These are the starts that carry the comma-breath (1.2), so this is also the breath budget.
- No marker word starts two sections of the same video, and no two sections of a video start with the same word.
- E3 stands as evidence that "Okay. So now," and "Right, so," sound good. They stay in the family. They are used
  about once every other video each, not once per video each.

Markers real narrators use at a step: so, and, now, then, okay, all right, right, well, anyway (verbatim examples in
`research/casual-vs-scripted.md` start "So from here, um,", "And it's gonna show me,", "So, uh, first things first").
"But", "so" and "anyway" are how casual narrators come back from an aside (`research/asides-and-examples.md`).

### 3.3 Fillers: which, and where

**How many** (from `research/disfluency.md` and `casual-vs-scripted.md`): quick SaaS demo 1.5 to 2.8 per 100 words
is the real range, and NAVI starts at the low end because a written filler is over-pronounced; course walkthrough
0 to 1; product tour 0 to 0.5. Two of ten real casual narrators used none at all, so **a video with no uh or um is
a normal day**, and so is a section with none in any video.

**Which.** Casual demos: about 58% uh, 42% um. Um goes where a real pause should follow (median pause after um
342 ms, after uh 0 ms), so um sits at boundaries and uh inside a phrase.

**Where.** Slots, with the share to aim for across recent videos:

| Slot code | Position | Example | Target share |
|---|---|---|---|
| `unit` | First thing in a clause, or straight after "and / but / so / then / because" | "and then, um, book the train tickets", "So, uh, first things first", "because, uh, it's a test" | **40 to 50%** (Clark & Fox Tree 43 : 27 : 13 gives 52% at a boundary; Map Task: 53% of um and 39% of uh open a move) |
| `pre-noun` | After "the / a / this / to / into / about", before the thing named | "the, uh, three dots", "go to, uh, Settings", "into, uh, say the home page" | **25 to 35%** (casual demos: about a third) |
| `pre-verb` | Between subject and verb | "you, uh, drag it across" | the rest, about 20 to 30% between these four (**guess** for the split) |
| `topic` | After naming the topic, before the sentence about it | "API keys, uh, those are under Developer" | |
| `value` | Before a value being chosen or typed | "I'll call it, um, test product" | |
| `tail` | After a clause, before "but / so" carries on | "you could keep going, um, but none of it's needed yet" | |
| `repeat` | Between the two copies of a repeated word | "the, uh, the" | counts as a repair (3.4), not here |

Rules that stay: a filler is never its own sentence, never before "…", never the last word, and attaches to the
word before it.

**Hedges and small words** are a separate budget from uh and um, and real narrators lean on them more:
"actually" (36 times in 63 minutes, the most common by far), "I think" (15), "probably" (6), "maybe" (3)
(`research/unsureness.md`); also "kind of", "sort of", "basically", "pretty much", "I mean", "honestly", "to be fair",
"go ahead and", "say". About 0.9 a minute in casual demos, none in scripted. "I think" and "you know" go inside the
phrase without commas. Each video has one or two favourites of the day (section 4) and no single hedge appears more
than twice in a video under two minutes (**guess**).

### 3.4 Repairs: restarts, repeats, corrections

**How many.** Real casual narrators: about 1 repeat a minute. Proposed total repairs: quick SaaS demo 1 to 2 a
minute, course about 1 a minute, product tour under 0.5 (`research/casual-vs-scripted.md`, proposed table). In NAVI
terms: **a repair in about one section in two or three, never more than one in a section, and at least one section
with none in any video of three sections or more.**

**Which kind.** Targets across recent videos:

| Code | Kind | Example | Target share |
|---|---|---|---|
| `rep` | Bare repeat of a small word | "I'll, I'll just call it a test", "the, the menu" | repeats together **35 to 45%** (Map Task 36%, Bortfeld 43%, phone chat 55%); of repeats, about two-thirds one word, a fifth two words (Map Task 68% / 21%) |
| `rep-f` | Repeat with the filler between | "book the, uh, book the", "I'm, uh, I'm gonna" | |
| `rep-2` | Two-word repeat | "it's in, it's in the left column" | |
| `fresh` | Abandoned start: begin, drop it, start the clause again another way | "And NAVI can, so it'll open this page fine…", "You could, actually just use the quick amounts." | **30 to 40%** (Map Task restarts 48% of repairs; lower here because cut-off words are banned and written fresh starts are the hardest to voice: **guess**) |
| `sub` | Swap one word for the right one | "the second, sorry, third tab", "click, well, tap the row" | **10 to 20%** (Map Task substitutions 17%) |
| `reph` | Say it, then say it better | "it's in order, or, I mean, you do them in order" | about 10% (**guess**) |
| `ins` | Go back to add a word | "the button, the blue button, top right" | about 5% (**guess**) |

Rules that stay: repeat small words, never nouns; never cut a word off ("You- you") – an abandoned start drops a
whole word or phrase instead; a `sub` must land on the true name (the corrected word is the one on screen);
repairs go at the start of a clause and at hard moments (naming something, a negative), not in easy joining phrases.

Editing words to rotate: uh, um, I mean, well, sorry, or rather, no, actually, wait.

### 3.5 Hunts

Real rate: about once every 20 to 30 minutes of casual narration (`research/unsureness.md`). So **most NAVI videos
have no hunt.** One at most per video, only where the explore step flagged the thing as hard to find, in SaaS demos
(and mumbling only there). Never the same hunt wording as any of the last 12 videos.

Options (self-talk, then land the target cleanly): "where is it", "where's the, um,", "where did they put it",
"where's it gone", "which one is it", "what's it called", "let's see", "hang on", "one sec", "it's somewhere down
here", "not that one", "it's under, no, it's on", "should be next to", "I always lose this one", "it's usually by
the", "bear with me", "it was here a second ago". A hunt can also be silent: write the line so it pauses before the
target ("and to clear them it's this one, Clear completed") and let the cursor travel.

`audio_edit.hunt_words` must protect the pause for all of them: section 6.

### 3.6 Reactions

Short, flat, said as the thing appears; real narrators narrate a result about once in nine minutes, so 0 to 2 a
video (**guess** for the upper end). Never cheerful, never one word with "!". Options: "yeah, that's it", "that's
the one", "fifty, fine", "took a second", "bit slow today", "and it asks again", "nothing yet", "same as before",
"oh, it's moved", "huh, it kept the name", "three of them now", "that's new", "so it remembered", "there's the
link", "not much to it". No reaction wording repeats inside the last 12 videos.

### 3.7 How a section ends

All endings still land low and plain. Classes:

| Code | Kind | Examples | Target |
|---|---|---|---|
| `act` | Stops on the action | "…and hit Enter.", "…so Hide." | **most sections** (at least half) |
| `place` | Trails on where it is | "…over on the right.", "…from here.", "…down here.", "…in the list." | |
| `reason` | Ends on the reason or opinion | "…you don't really need to see what's done.", "…none of it's needed yet." | |
| `under` | Understates | "…so that's one.", "…that'll do.", "…which is fine.", "…more or less.", "…for now." | at most 1 or 2 a video, as now |
| `word` | A falling closing word | "…, okay.", "…, all right.", "…, so yeah.", "…, anyway." | at most 1 or 2 a video, as now; real speakers close 61% of steps this way face to face (Bangerter & Clark), far fewer talking to a recorder (**guess**) |
| `count` | Ends on what's left | "…down to the two I haven't done." | |

No ending class finishes two sections in a row except `act`. The last sentence of a video is never the same class
as the last sentence of the previous video, and its last three words never repeat inside the last 12 videos.

### 3.8 Asides

Rates stay as in `voice-rules.md` (provisional). What varies is how one opens and how the talk comes back:

- In: "which", "honestly", "I think" (no commas), "to be fair", "for what it's worth", "annoyingly", "weirdly",
  "funnily enough", "again", "actually", "by the way", "quick side note" (course), "so".
- Back: "but" (15 of the casual returns), "so", "and", "anyway", "all right", "now", or nothing.
- No opener repeats inside a video; the same opener and return pair doesn't repeat in consecutive videos.

### 3.9 Who does the action

Real casual narrators, per minute: "you can / you just" 0.75, "I'm gonna / I'll / let me" 0.33, "let's" 0.32,
"if / when I click" 0.32 (banned as "If I click…", allowed as "when you click"), bare imperative 0.11, "we" 0.11
(`research/casual-vs-scripted.md`). So across recent videos: about 40% you, 20% I, 20% let's / let me, 10% when-you,
10% imperative and we. Each video leans one way (section 4), with no one form over 60% of its action sentences.

### 3.10 Sentence shape

- Sentence length varies inside a video: the spread (standard deviation over mean) of words per sentence is at
  least 0.35 (**guess**; the nearest measured figures are pace variation 0.25 and pause unevenness 0.93 for casual
  narrators). Long run-on sentences stay the default; three or more sentences of under 8 words in a row is the
  "clipped" pattern E2 rated weakest.
- No more than two sentences in a video start with the same two words. "So" starts at most a quarter of sentences,
  "And" at most a third (**guess**).
- Sections differ in build: not every section is "marker, statement, action, action".

---

## 4. Picking: the style of the day

Before writing, NAVI draws a **style** for the video and saves it in the script (`"style": {…}`), so the writer,
the checker, `show_script.py` and the voice step all read the same thing.

**Seed.** `seed = sha256(title + site + ISO date + a random 32-bit nonce)`. The nonce is what makes two videos
made the same day differ; it is stored so the draw can be reproduced. In a batch, seeds are drawn one after another
and a draw is thrown back if it lands too close to a profile already in the batch (below).

**What is drawn** (ranges narrow with the kind of demo and the sliders; the hesitations slider sets the ceiling,
not the amount):

| Field | Values | Notes |
|---|---|---|
| `opening` | one family from 3.1 | never one used by the previous video, or by more than 2 of the last 6, or by another video in the batch until all families have been used |
| `markers_on` | 2 or 3 markers this video may use to start a step | from: so, and, then, now, okay, right, all right, next, after that, from here |
| `markers_resting` | 2 markers this video may not use at a start | always includes whichever started the most sections in the last 3 videos |
| `marker_share` | 0.2 to 0.5 of sections start `M1`–`M3` | |
| `breath_starts` | 0 or 1 section allowed to start `M2` / `M3` (2 in a video of 8 or more) | which section is drawn too; never section 1 if the previous video's section 1 had one |
| `filler_rate` per 100 words | SaaS: 0 (15%), 0.7 (25%), 1.2 (30%), 1.8 (20%), 2.4 (10%). Course: 0 (40%), 0.5 (40%), 1.0 (20%). Tour: 0 (70%), 0.4 (30%) | range from the research; weights are a **guess** that starts low |
| `uh_share` | 0.45 to 0.75 | casual demos 58%, median speaker 52%, talking to a recorder 76% |
| `filler_slots` | two slots favoured, one resting | the resting one is whichever slot the last 6 videos used most |
| `hedges` | 1 or 2 favourites, 1 resting | from 3.3 |
| `repair_rate` per minute | SaaS 0 to 2, course 0 to 1, tour 0 to 0.5 | |
| `repair_kinds` | 2 of the kinds in 3.4 | weighted by the target shares, minus what the last 6 videos over-used |
| `sentences` | "long" (mean 22 to 30 words), "mixed" (14 to 22), "long-and-short" (mostly long with one short line a section) | never "clipped" |
| `person` | a lead and a second from 3.9 | weighted by the real rates |
| `asides` | count from the provisional rates, with an opener and a way back | |
| `closing_words` | 0, 1 or 2 sections may end `under` or `word` | |
| `hunt` | 0, or 1 if explore flagged a hard-to-find target (then a wording not in the last 12 videos) | |
| `gaps` | one gap per section boundary, 0.25 to 0.70 s | section 6 |

**Far enough apart.** Two profiles are "too close" if they match on more than 4 of these 8: `opening`, lead marker,
`filler_rate` band (none / low / mid / high), favoured filler slot, first repair kind, `sentences`, `person` lead,
first hedge. No two videos in a batch, and no video and the one before it, may be too close (**guess** at 4 of 8).

**Within the video.** The profile sets leanings, and then the spread rules in section 3 apply: no two sections
start with the same word, at least half start `M0`, at least one section has no disfluency, no slot or repair kind
is used twice in a video under two minutes, no ending class twice in a row.

**The profile is a lean, not a script.** The writer still writes what the screen earns. If the page gives no real
moment for a repair, the video has none, whatever was drawn.

---

## 5. Memory across videos

**File:** `$NAVI_DATA/script-history.jsonl` (`~/Library/Application Support/NAVI/` when `NAVI_DATA` isn't set), one
JSON line per finished script. Written when the voice for a script is generated (`generate.py --yes` succeeds), or
by `check_script.py --record`. A script's line is replaced, not added again, when the same script id is recorded
twice (id = sha1 of title + site), so a retake never counts against itself.

**What a line holds:**

```json
{"id": "…", "title": "…", "date": "2026-11-12", "kind": "saas", "voice_id": "…", "batch": "…",
 "style": {…the drawn profile…},
 "words": 167, "fillers_per_100": 0.6, "uh_share": 0.0, "repairs_per_min": 1.1,
 "opening": {"family": "cond", "first": "if", "first2": "if you're", "first4": "if you're selling anything"},
 "sections": [
   {"name": "open", "first": "if", "first2": "if you're", "start": "M0", "start_kind": "cond", "marker": null,
    "fillers": [{"w": "um", "slot": "tail", "prev": "it", "next": "but"}],
    "repairs": [{"kind": "rep", "words": "i'll"}],
    "hunts": [], "hedges": ["actually"], "reactions": [], "aside_in": ["which"], "aside_back": ["so"],
    "end": "place", "last3": "button top right", "closer": null,
    "person": {"you": 2, "i": 1}, "sentence_lengths": [24],
    "start_breath_s": 0.0}
 ],
 "sentence_mean": 21.4, "sentence_cv": 0.41,
 "ngrams4": ["…every 4-word run with no on-screen name in it…"]}
```

`start_breath_s` is filled in after the voice is made (section 6).

**How far back:** the last **12** scripts for the same voice, plus every script in the current batch whatever its
age. Twelve because a viewer looking at a channel sees about that many recent uploads, and a course module is
about that long (**guess**). Narrower windows are used where noted.

**What counts as a repeat** (levels and thresholds in section 7.3):

| Kind of repeat | Definition |
|---|---|
| Exact phrase | the same run of 6 or more words, or of 4 to 5 words, outside on-screen names and position phrases |
| Same opening | the same first two words of the video; the same opening family |
| Same marker in the same slot | section *k* starts with the same word as section *k* of a recent video (so "Right" in section 2 again) |
| Same start sequence | the first words of sections 1 and 2 together match a recent video |
| Same filler pattern | the same filler, in the same slot, after the same word ("uh" + `pre-noun` + "the") |
| Same repair shape | the same repair kind; for repeats, the same repeated word |
| Same hunt | the same hunt wording |
| Same ending | the same last three words of a section; the same ending class on the last section |
| Same shape | filler rate, mean sentence length and spread all close to both of the last two videos |
| Same start breath | an audible breath after the first word of section 1 in each of the last two videos |

Beyond single repeats, the history is also checked as a **distribution**: across the window plus the new script,
the share of fillers in each slot and of repairs of each kind has to sit near the targets in 3.3 and 3.4. That is
what stops the next recipe from forming.

---

## 6. Breath: varying the start of each section

The model's breaths stay; nothing is added with tags. Four changes, in order of how much they matter.

**1. Wording (the main fix).** The identical breath comes from "marker, comma, so" at the start of every request.
Under 3.2 at most one section in a short video starts `M2` / `M3`; the rest start on content or on a run-in marker
with no comma. Measured on `whop/hide_take1`, the one existing section that starts on content, the voice goes
straight into speech. So most sections will start clean, one may start with the marker and its breath, and which
one changes from video to video (`breath_starts` in the profile).

**2. Take picking (`scripts/voice/generate.py`).** Replace `score = (abs(wps - ref), fin)`:
- Pace becomes a gate, not the ranking: a take is eligible if its pace is within 15% of `reference_pace_wps`
  (2.7 to 3.6 words a second). If neither is, fall back to the closer one.
- Among eligible takes, rank by finality as now.
- New measurement per take, `start_breath_s`: from the audio, not the alignment. Take 20 ms frames from the first
  word's start; find the first word's voiced end (the first frame more than 12 dB under that word's peak that stays
  there for 60 ms); count the time from there until the level comes back within 14 dB of the take's peak (the next
  word). If that stretch is 0.2 s or more and sits between 14 and 45 dB under the peak, it is a start breath of
  that length; otherwise 0.
- Tie-break on it: if the two takes' finality scores are within 1.5, prefer the take whose start (breath or no
  breath) matches the plan for this section, and failing that the one that differs from the section before.
- Write `start_breath_s` for the chosen take into `voice.json` and the history line.

**3. The edit (`shape()` in `generate.py`).** One new, narrow edit: **the start breath of a section may be
shortened when the plan says this section starts clean and the wording still produced one.**
- Only the stretch found above: after the first word of a section, where that word ends in a comma (not a full
  stop: a full stop makes it the end of a sentence, and nothing is trimmed after a sentence).
- Keep 60 ms after the first word's voiced end and 60 ms before the next word's onset, cut the middle, and join
  with the existing 30 ms equal-power crossfade. A 0.45 s breath becomes about 0.12 s: a catch, not a breath.
- Never applied to more than half the sections of a video, never to a hunt, never anywhere but the first word.
- Mid-section breaths, tongue clicks and sentence ends are untouched, exactly as now.
- The breaths slider gates it: "Kept" turns this edit off; "Natural" and "Trimmed" allow it.
This is a fallback for takes already paid for. Change 1 is what removes the pattern.

**4. The gap between sections.** `SECTION_GAP = 0.40` becomes one value per boundary, drawn with the style
(`gaps`): 0.25 to 0.70 s, weighted to the middle (most between 0.3 and 0.5), with no two neighbouring boundaries
within 0.08 s of each other. Real casual narrators pause a median 0.41 s after a sentence but unevenly (spread
0.93), and a quarter of sentences run straight on (`research/casual-vs-scripted.md`); the fixed 0.40 is the tidy
scripted pattern. Long waits still fall at section boundaries and play at real length, as now; this only replaces
the constant. The recording follows `voice.json`, so nothing else moves.

**Also:** add the rest of the hunt wordings to `audio_edit.hunt_words` ("where did", "where's it gone", "which one
is it", "what's it called", "one sec", "somewhere down here", "not that one", "bear with me", "it was here"), or
better, have `shape()` skip the pause cap inside any action tagged `"kind": "hunt"` by word index instead of by
phrase, so new wordings are protected without a list.

**Not proposed:** changing or dropping `[relaxed]` per section. It might change how sections start, but it's
untested and the tag rule came from listening rounds; it belongs in the listening round (section 8), not in a rule.

---

## 7. Checker spec (`scripts/script/check_script.py`)

Plain Python, standard library only. All new checks sit beside the existing ones; nothing existing is removed
except the template phrases in two error messages (7.5).

### 7.1 Command line

```
check_script.py script.json [--history PATH] [--no-history] [--batch other1.json other2.json …] [--record] [--json]
```
- History defaults to `$NAVI_DATA/script-history.jsonl`; a missing file is an empty history.
- `--batch` checks this script against the others as if they were its history, with the tighter batch thresholds.
  `scripts/batch/batch.py` runs every script in a batch this way before any credits are spent.
- `--record` appends (or replaces) this script's line. `generate.py --yes` calls the same function after a
  successful run.
- `check(script, base, history=None, batch=None)` keeps its current first two arguments.

### 7.2 Getting the features out of a talking line

```python
plain   = TAG.sub('', talk).strip()
sents   = sentences(plain)                      # existing splitter
toks    = [w.lower() for w in words(plain)]     # existing tokeniser
raw     = re.findall(r"[\w'’-]+|[.,?!]", plain) # tokens with punctuation kept, for slot tests

MARKERS = {'okay','ok','right','so','now','then','and','well','anyway','next','alright'}   # plus the pairs
MARKER2 = {('all','right'),('after','that'),('from','here'),('next','up')}
FILLER  = {'uh','um','er','erm'}
CONJ    = {'and','but','so','then','because','cause','or','which','though'}
DET     = {'the','a','an','this','that','these','those','your','my','its','to','into','in','on','under','about',
           'for','from','with','at','of'}
SUBJ    = {'i','you','we','it','they','he','she',"i'm","i'll","i'd","you're","you'll","it's","we'll",'can',
           "can't",'just','gonna','will',"won't",'could','should'}
```

**Start of a section**
- `first`, `first2`, `first4`: first one, two and four tokens.
- `start` class:
  - `M3` if the first sentence has 1 or 2 words and all are markers ("Okay.", "All right.");
  - else `M2` if the first token (or pair) is a marker and a comma comes within the first 3 raw tokens
    (`^(okay|ok|right|all right|alright|now|so|well|anyway)\s*,` or `^(okay|right|all right)\s+so\s*,?` followed by
    a comma before token 4) – "Okay, so", "Right, so,", "Now,";
  - else `M1` if the first token (or pair) is in `MARKERS` / `MARKER2`;
  - else `M0`.
- `start_kind` for `M0` and for the video's opening family: first match of
  `question` (first sentence ends "?"), `cond` (`^(if|when|once|while|before|after|the first time|as soon as)\b`),
  `probably` (`^you('ve| have)? probably\b`), `reason` (`^(because|since|quickest|easiest|simplest|the reason)\b`
  or `\bso (i'll|i'm|you|we)\b` in the first sentence with no "this is" before it),
  `opinion` (`^(honestly|personally|i think|i'd|to be fair|the best|the nicest|the only)\b`),
  `lets` (`^(let's|let me)\b`), `action` (`^(i'm|i'll|i've|i)\b`), `you` (`^(you|your)\b`),
  `instr` (`^(go|click|open|head|hit|type|pick|scroll|press)\b`), `count` (`^(\d+|one|two|three|four|five)\b`),
  `this-is` (`^(?:\w+,?\s+){0,2}(this|here)('s| is)\b`), else `noun`.
  The writer may set `"opening"` in the script's `style` to override a wrong guess; the checker then only confirms
  that an `M2` / `M3` / `this-is` start isn't being declared as something else.

**Fillers**: for each token in `FILLER` at index *i*, with `prev` = the token before (skipping commas) and `next`
the token after:
- `repeat` if `prev == next` (it belongs to a repair, not counted as a filler slot);
- `unit` if *i* is the first token of a sentence, or `prev` in `CONJ`, or the raw token before `prev` is a sentence
  end and `prev` in `MARKERS`;
- `pre-noun` if `prev` in `DET`;
- `pre-verb` if `prev` in `SUBJ`;
- `tail` if `next` in `CONJ`;
- `value` if `prev` in `{'it','call','name','type','pick','say','like'}` and `next` is capitalised in `plain` or is
  inside the text of the section's next `type` action;
- `topic` if the raw token before the filler's comma is not in `DET | SUBJ | CONJ` and `next` in
  `{'those','that','it','they','this','these','which'} | SUBJ`;
- else `other`.
(Order matters: test in the order `repeat`, `unit`, `value`, `pre-noun`, `pre-verb`, `tail`, `topic`.)
Signature = `(filler, slot, prev)`.

**Hedges**: counts of `actually|i think|probably|maybe|kind of|sort of|basically|pretty much|i mean|honestly|
to be fair|you know|go ahead and` (word-boundary regex; "I mean" between commas after a clause counts as a repair
editing word instead, below).

**Repairs**
- Repeats: the existing `RESTART` regex, with the filler group captured:
  `\b((?:\w+'\w+|\w+)(?: (?:\w+'\w+|\w+))?),?\s+(?:((?:uh|um|er),?)\s+)?\1\b` →
  `rep-f` if the filler group matched, `rep-2` if group 1 has two words, else `rep`. Keep the existing exclusions
  (very, really, so, no, bye, okay) and add number words and "Hide"-style on-screen names (any capitalised group 1).
  Record the repeated word(s).
- `sub`: `\b(\w+),\s+(sorry|or rather|no|wait|well),\s+(\w+)` where group 1 and group 3 are both in the same small
  class (both number words or ordinals, both in `{click,tap,press,hit}`, both capitalised, or both in `DET`).
- `reph`: `,\s+(?:or,?\s+)?(i mean|or rather),\s+` where the 6 tokens after share at least one non-stopword with
  the 6 tokens before.
- `fresh`: a clause fragment that ends on a word that can't end a clause, then starts again:
  `(?:^|[.?!]\s+|,\s+)((?:and|but|so)\s+)?((?:[\w']+\s+){0,3}(?:can|can't|could|will|would|is|it's|that's|there's|
  i'm|i'll|you|to|the|a))\s*,\s+(so|actually|well|no|anyway|or)\s+` – and not already matched as a repeat, a filler
  slot or a hunt.
- `ins`: `\b(the|a|this) (\w+), \1 (\w+) \2\b` ("the button, the blue button").
- A section's repairs = all of the above. More than one is the existing `restarts` error (now counting every kind).
- Because `fresh` and `sub` are heuristics, a section may declare what it meant: optional
  `"repairs": ["fresh"]` on the section is added to what the regexes find (never subtracted).

**Hunts**: `where (is|did|was|has)\b|where's|which one is it|what's it called|let's see|hang on|one sec|
somewhere (down|up|over) here|not that one|bear with me|it was here|i always lose` – plus any action with
`"kind": "hunt"`; the hunt wording is the 2 to 5 tokens between the commas around the match.

**Ending**: `last3` = last three tokens; class by first match on the last sentence:
`word` (`,?\s*(okay|all right|alright|so yeah|anyway)\.$`), `under` (`so that's \w+\.$|that'll do\.$|which is fine\.$|
more or less\.$|for now\.$`), `place` (ends within 4 tokens of `here|there|top|bottom|left|right|list|row|page|form|
corner|side`), `count` (a number word in the last 6 tokens), `reason` (last clause starts `you don't|it's not|
none of|no need|because|since|i'd`), else `act`.

**Person**: per sentence, first match of `\byou (can|just|could|'ll|want|get|have)\b|\byou\b` → you;
`\b(i'm gonna|i'm going to|i'll|let me|i'd|i)\b` → i; `\blet's\b` → lets; `\bwe('ll| can)?\b` → we;
sentence starts with a bare verb from the `instr` list → imp.

**Shape**: `sentence_lengths` (words per sentence), mean and spread (population SD over mean) over the script.

**4-grams**: every run of 4 tokens that contains no token of any action's `target` / `text`, no capitalised
mid-sentence word, and no part of a position phrase found by `positions.py` ("at the bottom of the form"). On-screen
names and positions are fixed by the page, so they never count as repeats.

### 7.3 New checks

Level E = error (blocks `generate.py`), W = warning. "Window" = the last 12 history lines for this voice.
Thresholds marked * are guesses to tune after the first batch.

**Inside one script**

| Code | Level | Rule |
|---|---|---|
| `start-repeat` | E | Two sections start with the same first word. (W instead, when the script has 6 or more sections and the two aren't neighbours and it happens once.) |
| `start-marker` | E | More than one section starts `M2` / `M3` in a script of 4 sections or fewer; more than a quarter in a longer one; or two in a row. |
| `start-marker` | W | Fewer than half the sections start `M0`.* |
| `start-first` | W | Section 1 starts `M2` / `M3`, or is `this-is`. (E when the history rules below also hit.) |
| `filler-everywhere` | E | 3 or more sections and every one has a filler (uh / um) or a repair. |
| `filler-rate` | E | uh + um over 2.8 per 100 words (SaaS), 1.0 (course), 0.5 (tour). |
| `filler-rate` | W | More than 0.5 per 100 words above the style's `filler_rate`. |
| `filler-slot` | E | The same filler signature `(filler, slot, prev)` twice in the script. |
| `filler-slot` | W | The same slot twice in a script under 300 words; or every filler in the script is `pre-noun` when there are 2 or more. |
| `repair-rate` | W | Repairs in more than half the sections (SaaS), a third (course), or more than one in a tour.* |
| `repair-shape` | E | The same repair kind twice in a script under 450 words (about 2.5 minutes); the same repeated word twice in any script. |
| `restarts` | E | (existing) more than one repair in a section, now counting every kind. |
| `hunt` | E | More than one hunt in a script; any hunt in a course or tour; a hunt with no action tagged `hunt`. |
| `hedge-repeat` | W | One hedge more than twice in a script under 300 words.* |
| `closer` | W | (existing, widened) the same ending class twice in a row other than `act`; `under` + `word` endings more than twice in a video; fewer than half the sections end `act` / `place` / `reason`. |
| `end-repeat` | E | Two sections with the same `last3`. |
| `sentence-start` | W | More than two sentences start with the same two words; "so" starts over 25% of sentences or "and" over 33% (scripts of 8 or more sentences).* |
| `sentence-shape` | W | Spread of sentence length under 0.35 (scripts of 6 or more sentences); or three sentences under 8 words in a row.* |
| `person` | W | One form over 60% of action sentences (scripts with 6 or more).* |
| `style` | W | The script has no `style` block, or its features contradict it (a resting marker used at a start, a resting slot used, a repair kind not drawn). |

**Against the history** (skipped with a note when the history has fewer than 2 lines)

| Code | Level | Rule |
|---|---|---|
| `open-repeat` | E | The video's first two words match the opening of any of the last 8 videos; or its first word matches 2 or more of the last 5. |
| `open-repeat` | W | First word matches the previous video's. |
| `open-family` | E | Same opening family as the previous video, or as 3 or more of the last 6. `marker` + `this-is` openings: more than 1 in the last 6 including this one. "Okay" first: more than 1 in the last 8. |
| `slot-marker` | E | Section *k* starts with the same word as section *k* in 2 or more of the last 4 videos. |
| `slot-marker` | W | …as section *k* of the previous video. |
| `start-sequence` | E | The first words of sections 1 and 2 together match any of the last 5 videos. |
| `phrase-repeat` | E | A run of 6 or more words shared with any video in the window (outside on-screen names). |
| `phrase-repeat` | W | A shared 4-gram found in 2 or more window videos, or any shared 5-gram.* |
| `filler-pattern` | E | A filler signature that appears in 3 or more of the last 6 videos. |
| `filler-pattern` | W | A filler signature that appears in the previous video. |
| `filler-spread` | E | Window + this script has 6 or more fillers and over 50% are in one slot. |
| `filler-spread` | W | …over 40% `pre-noun` (target about a third) or under 25% `unit` (target 40 to 50%), with 8 or more fillers. |
| `repair-pattern` | W | The same repair kind as both of the last two videos that had a repair. |
| `repair-spread` | E | Window + this script has 5 or more repairs and repeats (`rep`, `rep-f`, `rep-2`) are over 60%, or `rep-f` alone is over 40%. |
| `hunt-repeat` | E | The same hunt wording anywhere in the window. |
| `hunt-repeat` | W | A hunt in this script and in 2 or more of the last 3 videos (real rate: once in 20 to 30 minutes). |
| `end-repeat` | E | The video's last sentence matches the last sentence of any window video. |
| `end-repeat` | W | Any section's `last3` matches one in the window; or the last section's ending class matches the previous video's (other than `act`). |
| `reaction-repeat` | W | A reaction or aside opener + way-back pair that appears in the previous video; a reaction wording anywhere in the window. |
| `same-shape` | W | Filler rate within 0.3 per 100 words (and not 0), mean sentence length within 10% and spread within 10% of **both** of the last two videos. |
| `same-profile` | E | The style profile is "too close" (section 4: more than 4 of 8 matching) to the previous video's. |

**Across a batch** (`--batch`): every history rule above is applied with the other batch scripts as the window, plus:

| Code | Level | Rule |
|---|---|---|
| `batch-open` | E | Two videos in the batch share a first word, or an opening family (until the batch is larger than the 18 families). |
| `batch-slot` | E | Section *k* starts with the same word in more than a quarter of the batch's videos (minimum 2). |
| `batch-phrase` | E | Any shared 5-gram between two batch scripts (outside on-screen names). |
| `batch-profile` | E | Two batch profiles are too close. |
| `batch-spread` | W | Over the whole batch: every video has a filler; or every video has a repair; or no video starts a section `M2` / `M3` and none starts `M0` only (the batch should hold both a clean video and a messier one).* |

**After the voice is made** (`generate.py`, reported with the take report, not by the checker):
- `start-breath` W: a start breath of 0.2 s or more on the chosen take of more than one section in a video of 4 or
  fewer (more than a third in a longer one), or on two sections in a row, or on section 1 when the last two videos'
  section 1 had one. The fix order: the other take, then the edit in section 6, then a reword.

### 7.4 What the checker prints

Each repeat names what it repeats and where: `open-repeat: "okay so" also opens "Opening the course" (2026-11-10)
and "A look at the money pages" (2026-11-10)`. For a spread error it prints the tally: `filler-spread: 5 of 6
recent fillers are pre-noun (target about a third). Move this one to a clause start, or drop it.`

### 7.5 Messages to change in the existing checks

The fixes the checker suggests must not be a phrase to copy:
- `ellipsis`: replace *'Write the hesitation into the sentence ("the, uh, little circle").'* with
  *'Write the hesitation into the sentence, in a slot this video hasn't used (voice-rules.md, Fillers).'*
- `cut-off`: replace *'repeat a small word instead ("I\'m, uh, I\'m").'* with
  *'drop the whole word and start the clause again, or use another kind of repair (voice-rules.md, Repairs).'*
- `filler-sentence`: replace *'Put it inside the flow ("because, uh, it\'s a demo").'* with
  *'Attach it to the word before, inside a sentence.'*
- `restarts`: replace *'one per section at most. Two slips sound nervous.'* with
  *'one per section at most, and most sections have none.'*

---

## 8. Rule rewrites (replacement text)

### 8.1 `reference/voice-rules.md`

**Top of the file, after "The short version", add:**

> **And no two videos alike.** Every wording in this file that won a test is one good option. None of them is the
> way to write a line. A script that reuses the openings, markers, fillers, restarts or endings of recent videos
> fails, the same as a script with a cheerful line in it. See "Variety" below and `docs/variety-spec.md`.

**Replace the bullet "One small restart or repeated word per section, not more. …" with:**

> - **Repairs: about one section in two or three has one, never more than one in a section, and the kind changes.**
>   Real casual narrators slip about once a minute, so most sections have none. Kinds, with the share to keep
>   across recent videos: a repeated small word, with or without a filler between the copies ("I'll, I'll just",
>   "book the, uh, book the", "it's in, it's in the") about 4 in 10; an abandoned start, where a clause begins, is
>   dropped whole and starts again another way ("And it can, so it'll open the page fine") about 3 or 4 in 10; a
>   swapped word that lands on the right one ("the second, sorry, third tab") 1 or 2 in 10; saying it again better
>   ("it's in order, or, I mean, you do them in order") or going back to add a word ("the button, the blue button")
>   the rest. Repeat small words, never nouns. Never cut a word off ("You- you just drag"): it sounded fake. Two
>   slips in a 40-second stretch already sounds nervous. A video never uses the same kind twice in under two and a
>   half minutes, or the same kind as both of the last two videos. *(Script v2; experiments E4 and A/B, 2026-11-05;
>   shares from reference/research/disfluency.md; variety rule 2026-11-11.)*

**Replace the bullet "A filler just before the name of the thing on screen. …" with:**

> - **Fillers move around.** Just before the name of the thing on screen ("the, uh, little circle") is one good
>   place and won its test, but only about a third of real fillers sit there. More sit at the start of a clause or
>   straight after "and", "but", "so", "then" ("and then, um, book the train tickets"): aim for 4 or 5 in 10 there.
>   The rest go between subject and verb ("you, uh, drag it"), after naming a topic ("API keys, uh, those are under
>   Developer"), before a value being chosen ("call it, um, test product"), or after a clause before it carries on
>   ("you could keep going, um, but none of it's needed"). Um where a pause should follow, uh where the talk runs
>   straight on. Many sections have no filler, and a whole video with none is a normal day (two of ten real
>   narrators used none). The same filler in the same place after the same word never appears twice in a video, or
>   in two videos running. *(Experiment E1; reference/research/disfluency.md; variety rule 2026-11-11.)*

**Replace the bullet "Start a new step with "Okay. So now," or "Right, so,". …" with:**

> - **Most steps start on their content, with no marker.** "The price is the only other bit…", "You get a link…",
>   "Once that's saved…", "It needs a few more on it…". Some start on a marker that runs straight in with no comma
>   ("Then the filters are…", "And you get…", "So the price…"). At most one section in a short video (a quarter in
>   a long one, never two in a row) starts with a marker and a comma or full stop ("Okay. So now,", "Right, so,",
>   "All right, so"): both of those beat a bare "So now," in their test, and they are also where the voice takes
>   the same audible breath every time, so they are rationed. No two sections of a video start with the same word,
>   and section *k* doesn't start with the word that started section *k* of a recent video. *(Experiment E3;
>   breath measurements and variety rule 2026-11-11.)*

**Replace the bullet "Write a hunt as self-talk, then land the target cleanly: …" with:**

> - **A hunt is self-talk, then the target landed cleanly, and it is rare.** "there's, where is it, Clear completed"
>   and "there's, where's the, um, Clear completed" were both rated amazing; so the kind works, and the wording
>   changes every time ("where did they put it", "which one is it", "what's it called", "hang on", "it's somewhere
>   down here", "not that one"…). Real narrators do this about once every 20 to 30 minutes, so most videos have
>   none: one at most, only where exploring showed the thing is hard to find, and never a wording used in the last
>   12 videos. *(Experiment E5; reference/research/unsureness.md; variety rule 2026-11-11.)*

**In "The opening", add a third bullet:**

> - **No two videos open the same way.** Open mid-action, on a reason, a question, an opinion, a "you've
>   probably…", an "if you're…", where the viewer has just landed, the bit people get wrong, a number, a choice.
>   "So this is the…" and "Okay, so…" are allowed about one video in six between them, and "Okay" as the first word
>   about one in eight. The first two words of a video never match any of the last eight.

**Replace the bullet "Closers can't repeat, and most sections don't need one. …" with:**

> - **Endings vary, and most sections just stop on the action.** Others trail on a place ("…over on the right"),
>   end on the reason ("…none of it's needed yet") or on what's left ("…down to the two I haven't done"). An
>   understatement ("so that's one", "that'll do", "which is fine") or a falling closing word ("okay.", "all
>   right.", "so yeah.") ends at most one or two sections a video, never two in a row, and no section's last three
>   words repeat inside a video or match a recent one. *(Andy, 2026-11-05; variety rule 2026-11-11.)*

**New subsection at the end of section 1, "Variety":**

> ### Variety (no two videos alike)
> - **Each video gets a style of the day,** drawn before writing and saved in the script: how it opens, which
>   markers it may and may not use, how many fillers (none is allowed) and where they lean, which kinds of repair,
>   long or mixed sentences, "you" or "I" led, how many asides and closing words, and which section, if any, starts
>   with a marker and its breath. Same person, different day. *(docs/variety-spec.md, section 4.)*
> - **Inside a video:** no two sections start with the same word; at least half start with no marker; at least one
>   section has no filler and no repair; no filler place and no kind of repair is used twice in a short video.
> - **Across videos:** NAVI keeps a record of every finished script (`script-history.jsonl`) and the checker
>   compares each new script with the last 12 and with everything in the same batch: openings, the first word of
>   each section, fillers and where they sit, kinds of repair, hunts, endings, shared phrases, and the overall
>   amount of hesitation and sentence length.
> - **The spread is checked too.** Across recent videos, fillers and repairs have to be spread over places and kinds
>   roughly as real narrators spread them. If a third of recent fillers should be before a noun and five of the
>   last six were, the next one goes somewhere else.
> - **A test winner is one option.** When a listening round finds a wording that works, it's added to a family here
>   with what it beat. It is never written as "do this".

**Section 2 table, replace the "Takes" row:**

> | Takes | 2 per section. A take must be within 15% of the reference pace; among those, keep the one whose last sentence sounds most finished. When the two are close, prefer the one whose start (breath after the first word, or none) differs from the section before and fits the video's plan | The model varies a lot between takes, and that variation is wanted. Picking the take nearest one reference take made every section of every video sound alike (2026-11-11). |

**Section 3, add:**

> - **The same breath in the same place every time is a tell.** A marker and a comma at the start of a section
>   ("Okay, so") makes the voice breathe in after the marker, every time. Breaths stay; that pattern doesn't. It's
>   varied by the wording first, then by which take is kept, and last by the edit (section 4).

**Section 4, replace the bullet "Only shorten silences longer than 0.8 s, …" with:**

> - Only shorten silences longer than 0.8 s, cutting from the middle and leaving at least 250 ms after the last
>   word. **One exception:** the breath straight after the first word of a section, when that word ends in a comma
>   and the video's plan has this section starting clean, may be shortened to about 0.12 s (60 ms kept either side,
>   crossfaded). Never after a full stop, never on more than half the sections, never when the breaths slider is
>   on Kept.

**Section 4, replace the bullet "Gap between sections: about 0.35 to 0.45 s, …" with:**

> - Gap between sections: 0.25 to 0.70 s, different at each boundary (most between 0.3 and 0.5, no two neighbours
>   within 0.08 s), placed where the screen changes step. A fixed gap is the tidy scripted pattern; real casual
>   pauses between sentences are uneven.

**Section 8, add a paragraph:**

> A video is also judged next to the ones before it. Play its opening and one step start back to back with the
> last three videos': if they could be swapped without anyone noticing, it isn't done. A complaint about one line
> becomes a ban or an option in a family, never a recipe for every script.

### 8.2 `reference/script-writing.md`

**New step between 2 and 3:**

> 2b. **Draw the style of the day** (`docs/variety-spec.md`, section 4) and save it in the script as `"style"`.
> Look at the history first (`check_script.py --history` prints the last few videos' openings, section starts,
> fillers and repairs): the style rests whatever recent videos leaned on.

**Replace step 3 with:**

> 3. **Write the talking version** of each section (`voice-rules.md` section 1): talk, don't read, with opinions
> and reasons where the screen earns them. Write to the style: open the way it says; start most sections on their
> content with no marker, and no two with the same word; put a filler or a repair only where the screen earns one,
> in the places and kinds the style leans to, and leave most sections without either. Never more than one repair
> in a section. The last line ends low and plainly, often just on the action. Start each section with `[relaxed]`
> and no other tag.

**Replace step 6 with:**

> 6. **Run the checker** and fix every error: `.venv/bin/python scripts/script/check_script.py script.json`. It
> checks the script by itself, against the record of recent scripts, and, in a batch, against the other scripts in
> the batch (`--batch`). A repeat of a recent video is an error like any other. Read the warnings too.

**In "The file", replace the sample section's talk and add the style block:**

> ```json
> "style": {"seed": "5f1c…", "opening": "reason", "markers_on": ["then", "and"], "markers_resting": ["okay", "right"],
>           "breath_starts": 0, "filler_rate": 0.7, "uh_share": 0.5, "filler_slots": ["unit", "tail"],
>           "repair_kinds": ["fresh", "reph"], "sentences": "long", "person": ["i", "you"], "hunt": 1,
>           "gaps": [0.34, 0.52]},
> …
> "talk": "[relaxed] Quickest way to show you this is to just use it, so I'll click in the box up top, call the dentist, and hit Enter.",
> ```
> with a note under it: *"This is one script, not the pattern. The next one must not open this way."*

### 8.3 `config/defaults.json`

- `sliders.hes.drives`: *"the ceiling on fillers and repairs for the video (per 100 words and per minute); the
  style of the day picks the amount under it, which can be none. Never more than one repair in a section"*.
- `voice.rank_takes_by`: *"pace within 15% of reference_pace_wps as a gate, then finality of the last sentence;
  ties broken by a start that differs from the section before; then the ear"*.
- `audio_edit.section_gap_s`: `[0.25, 0.70]`, with `"section_gap_varies": true`.
- `audio_edit.hunt_words`: add the wordings in section 6, or switch to protecting by the `hunt` action.
- `audio_edit.start_breath`: `{"shorten_to_s": 0.12, "only_after_comma": true, "max_share_of_sections": 0.5}`.
- New `script.variety`: `{"history": "script-history.jsonl", "window": 12, "max_marker_comma_starts": 1,
  "min_m0_share": 0.5, "filler_slot_targets": {"unit": [0.4, 0.5], "pre-noun": [0.25, 0.35]},
  "repair_targets": {"repeat": [0.35, 0.45], "fresh": [0.3, 0.4], "sub": [0.1, 0.2]}}` so every threshold in
  section 7 is a value here, not a constant in the checker.

### 8.4 `reference/research/mouth-and-breath.md`

Proposal 2 (*"Start a new step on a fresh sentence after a full stop ("Okay. So now…")"*) gets a note: applied to
every section it produced the same breath at every start (2026-11-11); use it for at most one section a video.

---

## 9. What has to be heard before this is settled

None of the new wordings have been voiced. Suggested round (about 2,500 credits at 2 takes):

1. **The four rewritten scripts** in `docs/variety-examples.md`, 2 takes each, and then the test this whole spec
   exists for: play the four openings back to back, then the four second sections back to back, old then new.
2. **Run-in markers:** E3 found a bare "So now," meh. That was one line. Check that `M1` starts ("Then the
   filters…", "And you get…") and `M0` starts don't sound flat as a class; if one does, it leaves the family.
3. **Written abandoned starts** ("And NAVI can, so it'll…"): the riskiest new kind, since E4's cut-off word
   failed. If the voice reads it as a mistake in the script rather than a person changing course, `fresh` drops to
   a small share and the repair targets shift to repeats and `reph`.
4. **Clause-start fillers** ("and then, um, book…"; "…, um, but…"): only pre-noun fillers have been judged by ear.
5. **The shortened start breath** against the same take unedited, blind.
6. **Whether `[relaxed]` is part of the start pattern:** one section, with and without it. Listening only; no rule
   changes unless Andy hears a difference he likes.

Every threshold marked as a guess in this file should be looked at again after the first real batch has run
through the checker: too many errors on scripts that sound different by ear means the threshold is wrong, not the
script.

---

## 10. The narrator card: one person, different days (added 11 Nov 2026)

Andy, after reading sections 1 to 9: "one recognisable person on different days, not a different person each video."
Rotating everything makes a different person every time. So each voice can have a card (`config/narrators/<name>.json`)
with a few habits that stay:

| Habit | Kind | Rate | Rules |
|---|---|---|---|
| "uh" is his filler; "um" rarer | filler | every video with fillers: "uh" 65 to 85% of them | "um" only where a real pause follows |
| "pretty much" | hedge | about 4 videos in 10 | once a video at most |
| "there we go" | reaction | about 1 in 10 (was 3) | only inside a sentence, words before and after it |
| "where've they put it" / "hang on" | hunt | whenever there's a hunt (rare anyway) | the words may repeat; the hunt itself stays rare |

The style draw brings out each phrase habit at about its rate and never in three videos running. (12 Nov 2026: a
run of videos with no habit no longer forces one in, "which is handy" is gone, and "there we go" is rarer and
inside a sentence only; see section 13.) The checker allows a habit's words across videos (they're masked out of the
repeated-phrase check, and his hunt words out of the repeated-hunt check), and fails: a habit twice in one video, a
section ending on a habit (that turns it into a catchphrase), a habit in four videos running. It warns when a
habit runs well over its rate, . Everything else (openings, step starts, phrases, endings, slips) still has to change.

## 11. Draft three, keep the best (added 11 Nov 2026)

The checker refusing a repeat is the floor, not the method. `scripts/script/drafts.py`:
- `styles` draws three styles for the video, each with a different opening and no two profiles close, away from the
  recent videos and from the videos already picked in the batch, and writes `draft1.json` to `draft3.json`.
- The writer writes all three: the same facts and actions, three different days.
- `pick` scores them. **Quality:** any checker error rules a draft out; then 100, less 6 a single-video warning.
  **Difference** (0 to 100), against the last 12 videos and the batch neighbours: the opening (same first two words
  0, same first word 0.4, same family 0.6, else 1; weight 0.25), the step starts (same start in the same slot 0,
  used anywhere recently 0.5; 0.25), shared 4-word runs (0.2), the same filler in the same place (0.1), the same
  section endings (0.1), the style profile (0.1). The narrator's habits never count. **Total** 0.6 x quality + 0.4 x
  difference. When the top two are within 3 points, the writer reads both aloud and keeps the one that sounds more
  like a person talking: the score can't hear.

## 12. Scale: a 30-video batch (added 11 Nov 2026)

`scripts/script/scale_test.py` writes a 30-lesson course (`examples/variety/course-30.json`) through the whole loop,
lesson by lesson, scripts only. What it changed:
- **Batch rules are by neighbourhood, not the whole batch.** The old rules failed any opening first word used
  anywhere in the batch, and any family once 18 videos were in, so a long batch would run out. Now: no shared opening
  first word (first two words when the first is "the", "you", "I'm"…) within 8 videos either side, no shared opening
  family within 5, no marker or "So this is" opening within 6 of another; across the whole batch only shares are
  watched (a family on more than about 12% of the videos is a warning). Section starts in the same slot: an error when
  3 or more of 9 neighbours share it. A shared 5-word run with a neighbour is a warning (a course goes back to the
  same pages, and "back on the product" will recur); 6 words or more is an error anywhere.
- **Openings cycle.** In a batch, every family is used before any comes round again (families used more than the
  least-used one are weighted down), and a family is never drawn within 4 videos of its last use. Over 200 simulated
  30-video batches all 18 families come up, the closest repeat is 5 videos apart, and marker or "So this is" openings
  stay well under 1 in 6.
- **The card is a lean, not a quota** (the first writer's notes): repairs, filler slots and habits come out only where a
  moment earns them; one filler is always allowed whatever the length (a 100-word lesson can't hold "0.5 per 100");
  the markers a card offers are ones the last two videos didn't use, named in full ("from here" rests "from here").
- **Where the draw and the checker disagreed** (found by the writers of lessons 11 to 30, fixed): a card could offer
  an opening family or first word a neighbour had just used (the draw now rests a family for 5 videos, the checker's
  neighbourhood, and each card lists the first words the last 8 videos opened with); a "marker" opening drew a second
  breath start (a marker opening is now that video's only one); "So this is…" was offered with "so" as a step marker
  (it now rests "so"); the rare openings were rested for 5 videos but checked over 6; a rare opening the style drew,
  and a plain "This is what…", were still marked down as worn; a "long" style on a short lesson tripped the
  sentence-spread warning; "let's see what…" read as a hunt; "and it's in the sidebar" read as announcing a result.
- **Result** (`output/variety-dev/course-sim/report.md`; picture: `output/variety-dev/visual/navi-variety-30-lessons.png`):
  30 lessons, 90 drafts, 9 ruled out, every lesson had a clean draft first time. 17 of 18 opening families used,
  none more than twice, never closer than 6 lessons; 27 of 30 different first two words (14 of 15 in the first half,
  15 of 15 in the second); 47 different step starts out of 60. Alex's habits came out in 12 lessons (under their
  rates: the writers took "none is fine" literally). Re-scoring a written sequence after a rule change is not a fair
  test (each lesson's styles were drawn against the picks made at the time), so the picks stay as written.
- **An independent read** of the 30 kept lessons (a reviewer who saw only the lines, not the scores): one person
  throughout ("the same relaxed, slightly hedging guy who likes 'I'd' advice"); naturalness 7, 7, 6 and variety 6, 5, 6
  out of 10 for lessons 1-10, 11-20, 21-30 ("slightly worse toward the end, but not much"). What it heard that the
  checks didn't measure, and what changed: the myth-busting openers ("You'd think", "What people miss", "You've
  probably") sound like one move (the draw now rests them as a group for 3 videos, and "question"/"two ways" too);
  "Okay, so" / "All right, so" step starts every few lessons (breath starts now drawn in 35% of videos, not 50%, and
  a third neighbour with the same one is refused); slips and hedges at an even rate, "so the variety itself starts
  to sound like a recipe" (40% of styles now draw no repairs, 30% no hedge). Still to watch, not yet checked: "X is
  where" / "X is the one" frames, the blur notice on every money page, hedges in odd places ("Payments is I think
  the most honest page"). These changes are in the draw; the 30 lessons were written before them.


## 13. Variety without catchphrases (added 12 Nov 2026)

Andy played the voiced rewrites against the old to-do and Whop videos: "before was okay, after is actually slightly
worse… just because variety is different doesn't mean we drop off quality", "he's sounding way too emotive", and of
the Whop rewrite: "cringy AI catchphrases, absolutely terrible".

What went wrong: the opening families gave the writer hooks as examples ("You'd think…", "You've probably…",
"Honestly the best thing about this one…", "There's two ways…"), and the writer reached for knowing asides to sound
different ("I'd sooner fill it in myself", "not that I'm sharing it yet", "while it's half built", "that's sort of
all it needs to exist") and a performed slip ("Completed, sorry, Active"). Same voice, same model, same settings
(eleven_v4, stability 0.7) as the old videos; both takes of each rewritten opening moved their pitch about 20 to 30%
more than the old openings (0.44 and 0.50 semitones a frame against 0.37 and 0.39), so the text, not the take
picker, made it emotive.

Changes:
- Opening families cut to the plain ones: mid-action, why you're here, if/when, where you've landed, what will get
  done, a remark on what's showing, the thing itself, "Let's", an instruction, and the rare "So this is" and marker.
  The hook families (question, probably, opinion, stuck, wrong, count, two-ways) are no longer drawn.
- `catchphrase` (error, check_script.py): hooks, teasers, myth-busting, selling lines, knowing asides and the
  "X, sorry, Y" slip. `there-we-go` (error): the phrase anywhere but inside a sentence.
- The "sub" repair (wrong word, then the right one) is no longer drawn.
- Narrator card: "which is handy" removed; "there we go" 1 video in 10; no habit forced in after a quiet run; the
  "identity" warning removed.

## 14. Moves, not strings; words, not labels (added 12 Nov 2026, round 3)

Andy on the plain rewrites: they still shared shapes ("what's on screen, so action" in both openings; ", so" as the
hinge of nearly every section; one "uh" right before a typed value in each; "I'm gonna" and "on the right" in both),
two lines were the banned asides reworded ("nobody's seeing this yet", "while it's not finished"), and "pretty much"
was pushed in. "Your checker bans strings, not moves."

- **Moves (moves.py).** Pattern families by word class are the offline floor; on text written by a separate writer
  who never saw them they caught 11 of 38 and 14 of 40. So drafts.py pick also runs a model review
  (move_review.md, the local claude CLI) that judges what each line does. Measured on the same unseen lines: 38/38
  and 39/40 caught, 0 of 85 plain lines refused, the same on repeat runs (set 2 was scored before anyone read it).
  Anything it finds is an error. test_moves.py --model re-measures it.
- **Words across videos (variety.py).** Per section: the hinges joining clauses (", so", ", but", ", then"; ", and"
  is left out as too common, and a sentence-start marker is not a hinge), repeated softeners ("just" twice),
  "it offers X, but I…" twice, fillers right before an action's word. Across the last videos or batch neighbours:
  the turn in the first line (", so" in both is an error), the first three words of the skeleton, the first word,
  shared tics ("i'm gonna", "i'll just", ", so it's"; three or more shared is an error), shared position phrases, the
  same main hinge, every filler before a typed or clicked value in both.
- **Tried and dropped:** a whole-sentence skeleton similarity (content words blanked). It scored the pair Andy heard
  as alike at 0.38 and unrelated openings up to 0.8: noise.
- **By ear (moves.alike, alike_review.md).** On 10 openings in a row the word checks flagged nothing, while a reviewer
  heard two strong pairs (a reason, then the place, then ", and I'll…"; two "this is a page with X, and it's empty"
  back to back). A model check of each new opening against the recent ones caught both of those and the round-1
  pair, but missed the round-2 pair on two runs, which the word rule catches. Both run in pick; strong is an error.
- **Habits are never offered to the writer.** The style card used to list today's habit ("pretty much"), and it got
  written in. Now the writer is told who Alex is, his filler, his hunt words, and which phrases are resting; the
  checker still caps any that come anyway.
