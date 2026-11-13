"""The narrator card, draft-and-pick and the batch rules at scale (Andy, 11 Nov 2026: "one recognisable person on
different days, not a different person each video"; "draft several, pick one"; "check it scales").

Runs on a throwaway $NAVI_DATA; touches nothing of the user's.
  .venv/bin/python scripts/script/test_drafts.py     (exit 1 on any failure)
"""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
os.environ['NAVI_DATA'] = tempfile.mkdtemp(prefix='navi-drafts-')
sys.path.insert(0, HERE)
import drafts  # noqa: E402
import style  # noqa: E402
import variety  # noqa: E402

EX = os.path.join(ROOT, 'examples', 'variety')
ALEX = 'hLygPNd2gK6Azddorc5W'
rows, ok = [], True


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")


def codes(issues, level='error'):
    return sorted({i['code'] for i in issues if i['level'] == level})


def video(title, talks, kind='saas'):
    return {'title': title, 'site': 'example.com', 'kind': kind, 'voice_id': ALEX,
            'sections': [{'name': f's{i}', 'talk': '[relaxed] ' + t, 'caption': 'x', 'actions': []} for i, t in enumerate(talks)]}


# 1. the narrator card
card = variety.narrator(ALEX)
check('Alex has a narrator card', card.get('name') == 'Alex' and len(card['habits']) >= 4,
      ', '.join(h['id'] for h in card.get('habits', [])))
check('a voice with no card has no habits', variety.narrator('someone-else') == {})

# a habit phrase is not a repeated phrase; the same words without it are
a = video('A', ['Pick the plan you want, and that is pretty much the form, then save.', 'Save it.'])
b = video('B', ['Type the name in, and that is pretty much the form, then on we go.', 'Done.'])
c = video('C', ['Type the name in, and that is just about all of the form, nothing else.', 'Done.'])
d = video('D', ['Pick a colour, and that is just about all of the form for now.', 'Done.'])
e = variety.check_history(variety.features(b), [variety.features(a), variety.features(a)])
check('"pretty much" (a habit) in two videos is not a repeated phrase', 'phrase-repeat' not in codes(e), ', '.join(codes(e)) or 'no errors')
e = variety.check_history(variety.features(d), [variety.features(c), variety.features(c)])
check('the same six words without a habit are', 'phrase-repeat' in codes(e), ', '.join(codes(e)))

# habits: once a video, mid-sentence, never three videos running
twice = video('T', ['It is pretty much done, and the rest is pretty much the same.', 'Then save.'])
check('a habit twice in one video is an error', 'habit' in codes(variety.check(twice, history=[])))
ending = video('E', ['Click save and there we go.', 'Then the list.'])
check('a section ending on a habit is an error', 'habit-place' in codes(variety.check(ending, history=[])))
uses = [variety.features(video(f'H{i}', [f'Number {i} is pretty much ready to go out today.', f'Thing {i}.'])) for i in range(3)]
e = variety.check_history(variety.features(video('H3', ['The fourth is pretty much ready as well.', 'Then save.'])), uses)
check('a habit in four videos running is an error', 'habit-rate' in codes(e), ', '.join(codes(e)))
e = variety.check_history(variety.features(video('H4', ['The fourth is pretty much ready as well.', 'Then save.'])), uses[:1] + [variety.features(a)] * 0 + uses[1:2])
check('a habit in two videos running is fine', 'habit-rate' not in codes(e), ', '.join(codes(e)) or 'no errors')

# his hunt words may repeat; any other hunt wording may not
h1 = video('Hu1', ['The export is, hang on, under the menu.', 'Then save.'])
h2 = video('Hu2', ['The invite is, hang on, on the team page.', 'Then save.'])
h3 = video('Hu3', ['The export is, where is it, under the menu.', 'Then save.'])
h4 = video('Hu4', ['The invite is, where is it, on the team page.', 'Then save.'])
e = variety.check_history(variety.features(h2), [variety.features(h1), variety.features(a)])
check('Alex\'s own hunt words ("hang on") can come back', 'hunt-repeat' not in codes(e), ', '.join(codes(e)) or 'no errors')
e = variety.check_history(variety.features(h4), [variety.features(h3), variety.features(a)])
check('another hunt wording can\'t', 'hunt-repeat' in codes(e), ', '.join(codes(e)))

# the style brings out habits at about their rate, never three running
hist, seen, runs = [], [], 0
for i in range(120):
    st = style.draw({'title': f'V{i}', 'site': 'x', 'kind': 'saas', 'voice_id': ALEX, 'sections': [{}, {}, {}]}, hist, [])
    hist.append({'opening': {'family': st['opening'], 'first': '', 'first2': ''}, 'sections': [], 'style': st,
                 'habits': {h: 1 for h in st['habits']}})
    seen.append(set(st['habits']))
runs = sum(1 for i in range(len(seen) - 2) for h in seen[i] if h in seen[i + 1] and h in seen[i + 2])
share = {h['id']: round(sum(1 for s in seen if h['id'] in s) / len(seen), 2) for h in card['habits'] if h.get('rate')}
check('120 style draws: habits near their rate', all(abs(share[h['id']] - h['rate']) < 0.15 for h in card['habits'] if h.get('rate')),
      ', '.join(f'{k} {v}' for k, v in share.items()))
check('120 style draws: no habit three videos running', runs == 0, f'{runs} runs')
fams = [h['opening']['family'] for h in hist]
gap = min(j - i for i in range(len(fams)) for j in range(i + 1, len(fams)) if fams[i] == fams[j])
check('120 style draws: an opening family never comes back within 5 videos', gap >= 5, f'closest {gap} apart; {len(set(fams))} families used')

check('120 style draws: no hook openings (question, "You\'d think", "You\'ve probably", an opinion first, two ways)',
      not set(fams) & {'question', 'probably', 'opinion', 'stuck', 'wrong', 'count', 'two-ways'}, ', '.join(sorted(set(fams))))
check('120 style draws: no performed wrong-word slip ("Completed, sorry, Active")', not any('sub' in h['style']['repair_kinds'] for h in hist))
br = video('Br', ['The list is empty.', 'Okay, so the filter is on the right.'])
others = [dict(variety.features(video(f'B{i}', ['The page is new.', 'Okay, so the menu is up top.'])), pos=i) for i in range(2)]
e = codes(variety.check_history(dict(variety.features(br), pos=2), others, batch=True))
check('batch: "Okay, so" with its breath in two neighbours already: refused', 'batch-breath' in e, ', '.join(e))

# "there we go" only inside a sentence; the catchphrases of the first rewrites are refused (Andy, 12 Nov 2026)
from check_script import check as check1  # noqa: E402
def one(talk):
    return codes(check1(video('X', [talk, 'The list is next, at the bottom of the page.']), variety_checks=False))
check('"There we go." on its own is refused', 'cheerful-line' in one('Click save. There we go.'))
check('"There we go, it\'s on the list." (a sentence start) is refused', 'there-we-go' in one("I click save. There we go, it's on the list now."))
check('"…and there we go." (a sentence end) is refused', 'there-we-go' in one('I click save and there we go.'))
check('"I hit save and there we go, it\'s on the list" is fine', not {'there-we-go', 'cheerful-line'} & set(one("I hit save and there we go, it's on the list with the others.")))
for line in ["You'd think making a product would be buried in settings somewhere, but it's right there.",
             'Honestly the nicest thing about this one is there\'s nothing to set up.',
             "Let's skip the bit where it offers to draft it, I'd sooner fill it in myself.",
             "There's a link for it straight away, not that I'm sharing it yet.",
             "The box stays put after each one, which is handy, you just keep typing.",
             "I'd click Completed, sorry, Active, because that's the list you work from."]:
    check(f'catchphrase refused: "{line[:48]}…"', 'catchphrase' in one(line))
check('a plain line passes ("So this is a pretty basic to-do list…")',
      'catchphrase' not in one("So this is a pretty basic to-do list. I'm gonna type in the box up top, call the dentist, and hit Enter."))

# round 3 (12 Nov 2026): words, not labels; no habit offered to the writer
r2a = dict(variety.features(video('A', ["Nothing on this list yet, so I'm gonna click in the box up top, type call the dentist, and hit Enter.", 'Then the list.'])), pos=0)
r2b = dict(variety.features(video('B', ["Products is the page with everything you're selling on it, and I want a new one, so it's Create product, top right.", 'Then the form.'])), pos=1)
check('the round-2 pair Andy heard as alike is refused (first line turns on ", so")', 'batch-open-hinge' in codes(variety.check_history(r2b, [r2a], batch=True)))
ok_a = dict(variety.features(video('A', ['Okay, so this is a pretty basic to-do list.', 'Then the list.'])), pos=0)
check('"Okay, so this is…" is a marker, not a ", so" turn', not variety.features(video('A', ['Okay, so this is a pretty basic to-do list.', 'x']))['open_hinges'])
hv = video('H', ['The list is empty, so I type a task.', 'The filter is down there, so I click Active.', 'Clear completed is on the right, so it goes.'])
check('", so" in every section is an error (the hinge of the whole video)', 'hinge' in codes(variety.check(hv, history=[])))
tw = dict(variety.features(video('T', ["I'm gonna open the menu and I'll just pick one.", 'Then save.'])), pos=1)
tw0 = dict(variety.features(video('T0', ["I'm gonna type a name and I'll just press save.", 'Then save.'])), pos=0)
check('the same little phrases as the video before ("I\'m gonna", "I\'ll just") are flagged', any(c.endswith('tic-repeat') for c in codes(variety.check_history(tw, [tw0], batch=True), 'warning') + codes(variety.check_history(tw, [tw0], batch=True))))
st0 = style.draw({'title': 'P', 'site': 'x', 'kind': 'saas', 'voice_id': ALEX, 'sections': [{}, {}]}, [], [], seed=1)
st0['habits'] = ['pretty-much']
check('the writer is never offered a habit phrase ("pretty much" was pushed in)', 'pretty much' not in style.habits_line(st0))

# the draw and the checker agree (the scale test's writers found where they didn't)
neigh = []
for i in range(40):
    st = style.draw({'title': f'M{i}', 'site': 'x', 'kind': 'course', 'voice_id': ALEX, 'sections': [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]}, neigh, [])
    if st['opening'] == 'marker' and st['breath_sections'] != ['a']:
        break
    neigh.append({'opening': {'family': st['opening'], 'first': f'w{i}', 'first2': f'w{i} x'}, 'sections': [], 'style': st, 'habits': {}})
check('a marker opening is the video\'s only breath start', not (st['opening'] == 'marker' and st['breath_sections'] != ['a']))
check('a style lists the first words the recent videos opened with', neigh and 'opened_with' in neigh[-1]['style'] and len(neigh[-1]['style']['opened_with']) == 8,
      ', '.join(neigh[-1]['style'].get('opened_with', [])))
m = video('Mk', ['Okay, so the member list is the next page along.', 'The filter is on the right.'])
m['style'] = {'opening': 'marker', 'breath_sections': ['s0']}
check('a marker opening the style drew is not marked down', 'start-first' not in codes(variety.check(m, history=[]), 'warning'))
m['style'] = {'opening': 'cond', 'breath_sections': []}
check('one it didn\'t draw still is', 'start-first' in codes(variety.check(m, history=[]), 'warning'))
sys.path.insert(0, HERE)
from check_script import RESULT  # noqa: E402
check('"and it\'s in the dashboard sidebar" is a place, not a result', not RESULT.search("and it's in the dashboard sidebar"))
check('"and it\'s in." still announces one', bool(RESULT.search("and it's in.")))
check('"let\'s see what a buyer gets" is not a hunt', not variety.HUNT.search("let's see what a buyer gets"))

# 2. draft several, keep the best
old = json.load(open(os.path.join(EX, 'old-todo.json')))
new = json.load(open(os.path.join(EX, 'new-todo.json')))
hist = [variety.features(json.load(open(os.path.join(EX, f'old-{k}.json')))) for k in ('whop', 'buyer', 'real-biz')]
best, ranked, tie = drafts.pick([('old', old), ('new', new)], hist, [], skip=('position', 'still-screen'))
sc = dict(ranked)
check('drafts: the rewrite beats the old script', best == 'new',
      f"new {sc['new']['total']} (Q {sc['new']['quality']} / D {sc['new']['difference']}), old {sc['old']['total']} "
      f"(Q {sc['old']['quality']} / D {sc['old']['difference']}{', ruled out' if not sc['old']['eligible'] else ''})")
copied = copy.deepcopy(json.load(open(os.path.join(EX, 'old-whop.json'))))
copied['title'] = 'Another product'
best, ranked, _ = drafts.pick([('copy of a recent video', copied), ('new', new)], hist + [variety.features(json.load(open(os.path.join(EX, 'old-whop.json'))))], [],
                              skip=('position', 'still-screen'))
check('drafts: a copy of a recent video is ruled out', not dict(ranked)['copy of a recent video']['eligible'] and best == 'new',
      ', '.join(e['code'] for e in dict(ranked)['copy of a recent video']['errors'][:4]))
s3 = style.draw_options(new, hist, [], 3)
check('drafts: three styles, three different openings', len({s['opening'] for s in s3}) == 3, ', '.join(s['opening'] for s in s3))

# 3. batch rules scale: neighbours are strict, far apart is fine
nf = variety.features(new)
far = dict(variety.features(new), pos=20, title='lesson 21')
near = dict(variety.features(new), pos=2, title='lesson 3')
mine = dict(nf, pos=0)
others = [dict(variety.features(json.load(open(os.path.join(EX, f'new-{k}.json')))), pos=10 + i) for i, k in enumerate(('whop', 'buyer', 'real-biz'))]
e_near = codes(variety.check_history(mine, others + [near], batch=True))
e_far = codes(variety.check_history(mine, others + [far] + [dict(o, pos=30 + i) for i, o in enumerate(others * 3)], batch=True))
check('batch: the same opening two videos apart is an error', 'batch-open' in e_near, ', '.join(e_near))
check('batch: the same opening twenty videos apart is not', 'batch-open' not in e_far and 'phrase-repeat' in e_far,
      ', '.join(e_far) + ' (the copied lines still count as repeated phrases)')

# 4. the history lives outside the repo
try:
    variety.record(new, path=os.path.join(ROOT, 'script-history.jsonl'))
    refused = False
except ValueError:
    refused = True
check('history: refuses to write inside the repo', refused and not os.path.exists(os.path.join(ROOT, 'script-history.jsonl')))
check('history: default path is outside the repo', not os.path.realpath(variety.history_path()).startswith(ROOT + os.sep), variety.history_path())

print('\n'.join(['| Check | Result | Detail |', '|---|---|---|'] + rows + ['', f"**{'PASS' if ok else 'FAIL'}**"]))
sys.exit(0 if ok else 1)
