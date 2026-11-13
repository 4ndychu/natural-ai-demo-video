Write the script for one video: three full drafts, then keep the best.

The rules. Follow them over your own instincts. Plain spoken register: no hooks, no catchphrases, no selling, nothing cheerful or emotive. Never say something is hidden, unpublished, private or a draft unless the explorer's notes show the page says so.
{rules}

The video's plan:
{plan}

What the explorer found. This is the only source for button names, targets and positions:
{notes}
{known}
The three drafts are already started, one per style of the day, as files. Each holds the video's settings and its style; "sections" is empty:
{drafts}

The styles in words:
{styles}

Do this:
1. Write all three drafts in full, in one turn (three Write calls together): each file exactly as it is above, with "sections" filled in: name, talk (starting "[relaxed] "), caption, and actions, each action pinned to a word that is in the talk. The same facts and actions in all three; three different days of the same narrator, each to its own style. The checker rules out a draft for any stretch of about 5 seconds of talk with nothing happening on screen, so every long line carries a hover or a click inside it. It also rules out pointing actions stacked too close ("crowded"): leave a clause or a comma pause between two clicks or hovers, and when a page lists several things, point at two or three of them, not every one.
2. Run:  {pick_cmd}
   It scores the drafts and writes {demo_dir}/script.json.
3. If every draft is ruled out, fix exactly what the errors name with Edit, starting with the draft nearest to passing, and run it again. Stop as soon as one draft is clean and kept. Don't stop while a draft is one or two fixes from clean (at most 6 rounds).

Run the command exactly as written (no cd, pipes or &&); anything else is refused. Reply with one line: which draft was kept and its score.
