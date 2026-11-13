Explore the real pages for one video and write down exactly what is there, so the writer never guesses.

The video: "{title}" on {site}. Saved login: {seat}
Its plan:
{plan}
{known}
How the explorer works:
{explore_help}

Do this:
1. Write the steps file {demo_dir}/explore/steps.json: walk the plan's sections in order, one step per click or field. With earlier notes (above), only the steps that reach what they don't cover, or no run at all (go to step 5).
2. Run:  {explore_cmd}
   It is always headless. Exit code 3 means the action guard blocked a step: never try to get round it; note what was blocked.
3. Run:  .venv/bin/python scripts/explore/digest.py {demo_dir}/explore
   It lists every screen: each button, link and field with its exact name, where it sits on screen and inside its panel. Use this, not explore.json. Look at a screenshot (Read the .png in {demo_dir}/explore) only where the list leaves a doubt, for example what a control looks like.
4. If a step failed or a page wasn't what the plan expected, fix steps.json and run again (at most 5 runs in all). A control that failed in two runs is written down as not found (with what the page offered instead): never try it a third time. Every run starts from the start page again, so a later run repeats the earlier steps that worked and then goes further.
5. Write {demo_dir}/explore/notes.md: for each section of the plan, the exact visible name of what is clicked or typed; where it sits, in the digest's own words (on screen, and in its panel); a stable target for it (text=..., placeholder=..., role=button[name='...'], or a CSS selector from the digest); what appears afterwards (pop-ups, renamed items, counts); anything that loads slowly. Say plainly what you could not find.

{account}

Never type a password, code or key. Run the commands exactly as written (no cd, pipes, && or sed); anything else is refused, and a refused command is no reason to stop. To change a file, Write it again.

Reply with one short paragraph: what you found, and anything the plan got wrong.
