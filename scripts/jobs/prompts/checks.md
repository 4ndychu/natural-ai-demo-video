Make one script pass every check without making it worse, then read it once as the viewer.

The script ({script_path}):
{script}

What the checker says now:
{check_out}

What the explorer found (the truth for names and positions):
{notes}

Lines that sound fake:
{rules}

Do this:
1. Fix every ERROR with the smallest change (Edit) that keeps the line sounding like a person talking: change the words, never the facts, the actions' targets or the order of steps. A cue word ("on") must still be in its talk line. Leave warnings unless the fix is clearly better.
2. Read the script once as the viewer: does it say anything is hidden, unpublished, private or a draft that the explorer's notes don't show? Take that out. does every name and position match the explorer's notes? Does anything sound written, cheerful, or like a hook? Fix only what is clearly wrong.
3. If you changed anything, run:  {check_cmd}
   and repeat until it shows no errors (at most 5 rounds). If you changed nothing, run nothing.

Run the command exactly as written (no cd, pipes or &&); anything else is refused. Reply with PASS or FAIL on the first line (FAIL only if errors remain), then one line on what you changed.
