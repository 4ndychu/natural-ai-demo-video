A rehearsal played this script's actions in the real browser, and at least one could not be done. Fix the script so every action can be done, changing as little as possible.

The script ({script_path}):
{script}

What the rehearsal said:
{report}

What the explorer found:
{notes}

Rules:
- Fix the action's "target" (or "into"): use a name the page offers (the rehearsal lists them), or one from the explorer's notes, or look one up with:  {digest_cmd}
  Targets are written as role=button[name='...'], role=link[name='...'], text=..., placeholder=..., label=..., or css=... (a link's address is the steadiest: css=a[href='/path']).
- {talk_rule}
- Never add, remove or reorder steps that change something on the site, and never point a step at a different thing than the voice names.

After each fix, rehearse again:  {rehearse_cmd}
It stops at the first step that can't be done, so fix that one and run it again, until it says the rehearsal passed (at most 10 runs). Then run:  {check_cmd}
and fix any ERROR it shows the same careful way.

Run the commands exactly as written (no cd, pipes or &&); anything else is refused. Reply with PASS or FAIL on the first line, then one line per action you changed.
