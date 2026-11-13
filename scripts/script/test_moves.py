"""The move check against lines written by a separate writer who never saw the patterns (examples/variety/
moves-unseen-1.json, -2.json). Set 1 was read before the model brief was written; set 2 was scored before anyone read it.

  .venv/bin/python scripts/script/test_moves.py           the patterns (offline) and the lines that started it
  .venv/bin/python scripts/script/test_moves.py --model   also the model review (runs the local claude CLI, ~30 s)
Measured 12 Nov 2026: patterns 11/38 and 14/40 caught; model review 38/38 (1 of 40 plain lines refused) and 39/40
(0 of 45 refused), the same on two runs.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from moves import find_moves, review  # noqa: E402

EX = os.path.join(HERE, '..', '..', 'examples', 'variety')
ok = True
rows = []


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")


started = ["You'd think making a product would be buried in settings somewhere, but it's right there on the Products page.",
           'Honestly the nicest thing about this one is there\'s nothing to set up.',
           "Let's skip the bit where it offers to describe it, I'd sooner fill it in myself.",
           "There's a link for it straight away, not that I'm sharing it yet, so Done.",
           "I'd hide it while it's half built, that's the three dots.",
           "It gives you a link to share, but nobody's seeing this yet, so Done.",
           "I'll hide it while it's not finished, it's the three dots at the end of its row.",
           'The box stays put after each one, which is handy, you just keep typing.',
           "I'd click Completed, sorry, Active, because that's the list you actually work from."]
plain = ["So this is a pretty basic to-do list.", "I'll put a couple more on, uh, pay the gas bill and book the train tickets.",
         "Then the price, on the right, and I'll take fifty and press Done.", "I'd rather just fill it in myself.",
         "Book the, book the train tickets.", "Three dots at the end of the row, then Hide, and Hide again to confirm."]
missed = [l for l in started if not find_moves(l)]
check('patterns: every line that started it is refused', not missed, '; '.join(missed))
wrong = [l for l in plain if find_moves(l)]
check('patterns: plain lines pass', not wrong, '; '.join(wrong))
if '--model' in sys.argv:
    for k in (1, 2):
        d = json.load(open(os.path.join(EX, f'moves-unseen-{k}.json')))
        items = [(l, m) for m, ls in d['refuse'].items() for l in ls] + [(l, None) for l in d['pass']]
        random.Random(k).shuffle(items)
        res = review([l for l, _ in items])
        if res is None:
            check(f'model review, unseen set {k}', False, 'did not run')
            continue
        flag = {r['n'] for r in res}
        R = sum(1 for _, m in items if m)
        caught = sum(1 for i, (_, m) in enumerate(items) if m and i in flag)
        fp = sum(1 for i, (_, m) in enumerate(items) if not m and i in flag)
        check(f'model review, unseen set {k}: catches at least 90%, refuses at most 5% of plain lines',
              caught >= 0.9 * R and fp <= 0.05 * (len(items) - R), f'caught {caught}/{R}, refused {fp}/{len(items) - R} plain')
    res = review(started + plain)
    check('model review: the lines that started it, and the plain ones', res is not None and {r['n'] for r in res} == set(range(len(started))),
          f"flagged {sorted(r['n'] for r in res or [])}")
print('\n'.join(['| Check | Result | Detail |', '|---|---|---|'] + rows + ['', f"**{'PASS' if ok else 'FAIL'}**"]))
sys.exit(0 if ok else 1)
