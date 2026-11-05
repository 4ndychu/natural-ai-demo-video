# Asides, tangents, over-explaining and real-world examples

Research pass 2, 5 November 2026. **Findings and proposals only: nothing here has been applied to `voice-rules.md` or `config/defaults.json`.** Citations in [sources.md](sources.md). Swearing is in [swearing.md](swearing.md).

## What was measured

The same 20 CC BY demos as [casual-vs-scripted.md](casual-vs-scripted.md), from their verbatim transcripts. Each transcript was hand-coded against one codebook:

- **Aside:** a short remark that steps out of the step and comes straight back (an opinion, a joke, a comment on the app or the recording). One clause or sentence.
- **Tangent:** two or more sentences away from the task (background, other tools, a story) before coming back.
- **Over-explaining:** more than the step needs (restating what was just shown, explaining the obvious, the same thing twice, edge cases nobody asked about).
- **Example:** a concrete real-world case, either personal ("in my case, I…") or hypothetical or customer ("say you're a teacher…").

Each instance got a length (from the timestamps) and a position: right after an action, during a wait, while hunting, at the start of a section, mid-explanation, or at the wrap-up.

**Correction to the first pass:** two of the ten "casual" videos are not one person narrating a screen. Canvas Mobile Annotations Quick Demo is a webinar Q&A with several speakers; Totally Unscripted episode 4 is a two-host show. The numbers below use the **8 single-narrator videos** (48 minutes). Re-checked without those two, the first pass's pace and pitch findings barely change (see casual-vs-scripted.md).

## The numbers

| Per minute | Casual (8 videos, 48 min) | Scripted (10 videos, 53 min) |
|---|---|---|
| **Asides** | **0.68** (median 4.4 s, about 12 words) | 0.19 (median 5.0 s) |
| **Over-explaining** | 0.48 (median 8.5 s) | 0.21 (median 5.9 s) |
| **Real-world examples** | 0.25 (median 12.6 s; 9 of 12 personal) | 0.36 (median 8.1 s; 13 of 19 hypothetical or about a customer) |
| **Tangents** | 0.08 (median 28 s) | 0.04 (12 s and 27 s) |
| All of these together | about 1.5 per minute | about 0.8 per minute (about 11% of the running time) |

### Where they fall

- **Casual asides come right after an action** (13 of 33), then mid-explanation (9), at the start of a section (5) and while hunting (2). They're the narrator reacting to what just happened: "hopefully this is recording okay" (Kris Occhipinti), "Google automatically randomized for me. Thank you Google." (Dasheroo), "which I don't think is that practical, but you can do it" (Bryce Vandegrift).
- **Scripted asides are mid-explanation** (6 of 10) and never during a wait or a hunt: the voiceover is laid over edited footage, so the narrator never waits on screen. Typical: "As a side note, this is just one of the possible WordPress dashboard configurations." (WordPress)
- **Over-explaining is mid-explanation** in both styles: mostly restating what was just shown, and edge cases ("if you ever run out of space…").
- **Examples sit mid-explanation** in both. Casual ones are personal ("In my case, what I'm doing is I have a main backlog", Sebastien Dubois) and long. Scripted ones are about a user or customer ("For instance, if you give ten days upfront on January first…", PurelyHR).
- **Tangents** (casual, median 28 s, about 100 words) cluster at section starts and wrap-ups.

### How they're marked

- **Into an aside or example:** mostly "so", then "actually", "and", "in my case", "again". Scripted: "for example", "for instance", "as a side note", "for reference".
- **Out:** casual narrators come back with **"but"** (15 times: "but I'm just gonna be showing you…", "but let's just get on it"), then "so", "and", "all right", "now moving on". Scripted narrators almost never mark the way back.
- This matches the research: "anyway", "so" and "but" close your own digression; "by the way" opens one (Bangerter & Clark 2003, Ferrara 1997).

## What the research says

**Asides sound different.** Parenthetical remarks are lower in pitch than the sentence around them, with their own flatter contour and a narrower range, and tend to be faster and quieter; the pitch steps back up when the main line resumes (Kutik et al. 1983; Döring 2007, secondary; Dehé 2009). In direction-giving monologues, a new step starts higher, louder and after a longer pause; a step ends lower, quieter and faster (Hirschberg & Nakatani 1996).

**But short comment clauses aren't set apart.** "I think", "you know": 74.5% are said inside the phrase, not as a separate bit (Dehé 2009, 102 of 139). Longer parentheticals get their own phrase about 90% of the time.

**Over-describing is normal.** Speakers add an unneeded detail about 30% of the time, and listeners don't rate them worse (Engelhardt et al. 2006). Experts talking to novices add a description to a name 42% of the time (13% to fellow experts), starting at 73% and dropping as the task goes on; words per item fall from about 16 to 6 (Isaacs & Clark 1987) and from 41 to 8 (Clark & Wilkes-Gibbs 1986).

**A demo is the no-feedback case, where instructions fail.** Instructions recorded for a later listener led to 39% of models built wrong, against 5% when the pair could talk (Clark & Krych 2004). The cause was instructions that didn't say enough.

**Conversational wording helps learning** (d = 0.30 for retention, 0.54 for transfer; Ginns et al. 2013), and faster, informal explainers held viewers better (Guo et al. 2014: engagement rose with speaking rate).

**Personal stories cut both ways.** A personal story raised attention and liking of the instructor (Kromka & Goodboy 2019), but interesting details that don't serve the point hurt learning (g = −0.33; Sundararajan & Adesope 2020, secondary), more so when the viewer can't control the pace. Lecturers use about one or two stories or "imagine…" scenarios per lecture (Nesi & Alsop 2021).

**No study counts asides per minute in spoken explanations;** the rates above from the 20 demos are the only figures we have.

## Proposed rules by demo style (not applied)

| | Quick SaaS demo | Course walkthrough | Product tour |
|---|---|---|---|
| **Asides** | About one per minute (casual narrators 0.7), at most one per section. One clause, about 4 s. **Right after an action**, reacting to it. | About one every 2 to 3 minutes, flagged ("quick side note,"). | About one per video (scripted 0.2 per minute), mid-explanation. |
| **What an aside says** | An opinion, a reason, a warning or a shortcut about what's on screen. Never filler. | A reason or a warning. | A reason or a benefit, plainly. |
| **Way back** | "but", "so" or "anyway", then straight to the next action. | "so" or "anyway". | No marker needed. |
| **Real-world examples** | At most one per video under 5 minutes, one sentence, personal ("I use this for…") **only if the user's brief gives it**. | One per module: a user or customer case ("say you're a teacher…"), or a personal one from the brief. | User-centred ("say you run a small shop…"), never first person. |
| **Over-explaining** | First mention: the name plus where it is ("Export, the little arrow top right"); after that, the bare name. One check on tricky steps ("you should see a green tick"). | Same, and keep the fuller descriptions longer (aimed at a novice). One recap per module. | One clear description per feature, no repeats. |
| **Tangents** | None in a video under 5 minutes (real ones run about 28 s, far past the 4 to 5 s screen-change rule). | None. | None. |

Notes on these proposals:

1. **Never invent personal history.** Personal examples come only from the user's brief. A first-person story the user didn't give is a fabricated claim in their voice.
2. **Asides are a recording question too.** A casual aside lands right after an action, which is when the screen is changing, so it never leaves the screen still. A tangent does, which is why none are proposed.
3. **To test before making it a rule:** whether eleven_v4 drops pitch and speeds up for an aside written between commas ("you click Export, which honestly took me ages to find, and pick MP4"), or whether it has to be its own short sentence. That's one small experiment, about 300 credits.
4. Don't write commas around "I think" or "you know"; say them inside the phrase ("it's I think the second tab").
