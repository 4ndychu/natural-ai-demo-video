# Swearing: how often, where, and what it costs

Research pass 2, 5 November 2026. **Findings and proposals only: nothing here has been applied to `voice-rules.md` or `config/defaults.json`.** Citations in [sources.md](sources.md).

## How often

| Source | Swearing |
|---|---|
| Casual conversation, review (Jay 2009) | 0.3 to 0.7% of words; individuals 0 to 3.4% |
| Spoken British English (Love 2021) | 0.23% (1990s), 0.14% (2010s), counting a narrower word list |
| Map Task instruction dialogues (measured here) | 29 in 152,705 words: **0.019%** (0.19 per 1,000 words), counting mild words like "oh god" |
| DisfluencySpeech, US phone chat (measured here) | 12 in 113,367 words: 0.011% |
| **Real casual screen demos (measured here)** | **1 in about 48 minutes** of single-narrator demos (about 8,000 words): "it would suck to record a twenty-minute video and not have the proper audio" (Kris Occhipinti) |
| Real scripted walkthroughs (measured here) | 0 in 53 minutes |

At 160 words a minute, even everyday conversation (0.14 to 0.7%) is about one swear every 1 to 4 minutes. **Public screen demos are far below that:** one in 48 minutes, and that one was "suck".

## Where it falls

- **At a slip or a surprise.** In Map Task, 22 of 29 swears sit right next to a correction or a "sorry", and 17 come straight after "oh" or "oh my": "oh god, what am I saying, south southwest", "oh shit, down near the bottom", "what the hell am I meant to do". The speaker has just noticed their own mistake, or something unexpected on the map.
- **As a short outburst.** Two-thirds of swearing expresses frustration, anger or surprise, usually as a one-word or short reaction (Jay 2009); Goffman's "response cries" (a reaction to a stumble or a spill).
- **For emphasis aimed at the content.** The one demo swear backs up advice ("it would suck to…"). In class, swearing aimed at the course content, for emphasis or humour, was judged most acceptable (Generous et al. 2014).
- Never inside an instruction, in any source.

## What listeners make of it

- More intense, more informal, sometimes more persuasive or credible (Scherer & Sagarin 2006, Rassin & van der Heijden 2005, Cavazza & Guidetti 2014).
- But also less intelligent and less trustworthy (DeFrank & Kahlbaugh 2019, secondary).
- A lecture with two swears: no effect on learning; students rated it neutral on credibility (3.1 out of 5) and slightly unprofessional (Washmuth et al. 2025).
- **In how-to videos, each swear cut engagement, by up to 6.5%,** and more in sponsored videos and with mixed audiences (Mahajan & Niknejad Moghadam 2026, secondary, from a press release).

## Proposed rules (not applied)

1. **Default 0 in every preset.** The current Quick SaaS demo preset has `swear: 1`. Real demo narrators almost never swear (1 in 48 minutes), and in how-to videos it costs engagement.
2. **The slider stays, but scales with length:** "One" means one per video; "A few" means at most one per 2 minutes and never more than 2 in a video. Two in a one-minute demo would be about five times everyday conversation.
3. **Where:** only at a slip or a surprise on screen ("oh, damn, it's moved"), or for emphasis aimed at the product or the step ("it would suck to lose all that"). Never inside an instruction, a number or a warning. Never at the viewer. Quick SaaS demos only; course walkthroughs and product tours always 0. Sponsored or brand videos: 0.
4. **Words:** mild only (damn, hell, sucks, "oh my god"), as the slider already says.
5. Captions stay clean (already the default).
