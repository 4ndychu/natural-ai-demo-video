"""The variety check (scripts/script/variety.py): the four scripts that made Andy say "they sound the exact same"
(11 Nov 2026) must fail it, and the same four videos rewritten to sound like one person on four different days
(docs/variety-examples.md) must pass it, within each script, as a batch and against the old ones as history.

Runs on a throwaway $NAVI_DATA; touches nothing of the user's.
  .venv/bin/python scripts/script/test_variety.py     (exit 1 on any failure)
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
os.environ['NAVI_DATA'] = tempfile.mkdtemp(prefix='navi-variety-')
sys.path.insert(0, HERE)
import variety  # noqa: E402

EX = os.path.join(ROOT, 'examples', 'variety')
KEYS = ['todo', 'whop', 'buyer', 'real-biz']
old = [json.load(open(os.path.join(EX, f'old-{k}.json'))) for k in KEYS]
new = [json.load(open(os.path.join(EX, f'new-{k}.json'))) for k in KEYS]
rows, ok = [], True


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")


def errors(issues, ignore=()):
    return sorted({i['code'] for i in issues if i['level'] == 'error' and i['code'] not in ignore})


# 1. what the old scripts did, measured
of = [variety.features(s) for s in old]
check('old: all four open on a marker or "So this is"', all(f['opening']['family'] in ('this-is', 'marker') for f in of),
      ', '.join(f'"{f["opening"]["first2"]}"' for f in of))
check('old: every second section starts "Right, so"', all(f['sections'][1]['first2'] == 'right so' for f in of))

# 2. the old scripts fail: inside themselves, and each against the ones before it
for i, s in enumerate(old):
    e = errors(variety.check(s, history=of[:i]))
    want = {'start-marker'} if i == 0 else {'start-marker', 'open-repeat', 'open-family'}
    if i >= 2:
        want |= {'slot-marker', 'start-sequence'}
    if i == 1:
        want = {'start-marker', 'start-repeat'}      # "Okay, so" and "Okay. So now" in one script; only one video before it
    check(f'old "{s["title"]}" fails', want <= set(e), ', '.join(e))

# 3. the rewrites pass: each on its own, as a batch, and after the old ones
nf = [variety.features(s) for s in new]
for i, s in enumerate(new):
    e = errors(variety.check(s, history=[]))
    check(f'new "{s["title"]}" passes on its own', not e, ', '.join(e) or 'no errors')
for i, s in enumerate(new):
    others = [f for j, f in enumerate(nf) if j != i]
    e = errors(variety.check(s, history=[], batch=others))
    check(f'new "{s["title"]}" passes as one of the batch', not e, ', '.join(e) or 'no errors')
# against the old videos as recent history (not its own old version: the same video replaces its line)
for i, s in enumerate(new):
    hist = [f for j, f in enumerate(of) if j != i] + nf[:i]
    e = errors(variety.check(s, history=hist), ignore=('repair-spread', 'filler-spread'))
    check(f'new "{s["title"]}" repeats nothing from the recent videos', not e, ', '.join(e) or 'no errors')
starts = [x['first'] for f in nf for x in f['sections']]
check('new: 11 sections, 11 different first words', len(starts) == 11 and len(set(starts)) == 11, ' / '.join(starts))
check('new: no section starts with a marker and a comma (the breath start)',
      all(x['start'] not in ('M2', 'M3') for f in nf for x in f['sections']))

# 4. the history file: record, replace (a retake doesn't count against itself), load
for s in old:
    variety.record(s)
check('history: a voiced video that was never approved does not count (13 Nov 2026: tests restricted real lessons)', variety.load_history() == [])
for s in old:
    variety.mark_real(s)
variety.record(old[0])
h = variety.load_history()
check('history: one line per script, a re-record replaces it and an approved video stays real', len(h) == 4, f'{len(h)} lines')
e = errors(variety.check(old[2]))            # read from the history file, without its own line
check('history: a recorded opening is caught on the next video', 'open-repeat' in e, ', '.join(e))
variety.mark_real(old[0], real=False)
check('history: a video approved only as a test stops counting', len(variety.load_history()) == 3 and len(variety.load_history(real_only=False)) == 4)
variety.mark_real({'sections': [{'name': 'x', 'talk': 'Never recorded before.'}]}, real=False)
check('history: taking out a test that was never recorded adds nothing', len(variety.load_history(real_only=False)) == 4)

print('\n'.join(['| Check | Result | Detail |', '|---|---|---|'] + rows + ['', f"**{'PASS' if ok else 'FAIL'}**"]))
sys.exit(0 if ok else 1)
