"""NAVI style of the day: before a script is written, draw how this video leans, so two videos made the same day
are still two different days of the same person (docs/variety-spec.md section 4; Andy, 11 Nov 2026: "they sound
the exact same").

The style is saved in the script ("style": {...}) and read by the writer (Claude), the checker
(scripts/script/variety.py), show_script.py and the voice step (gaps between sections, which section may start with
a breath). It is a lean, not a script: the writer still writes what the screen earns.

  .venv/bin/python scripts/script/style.py script.json [--write] [--batch other.json ...] [--seed N]
      prints the style (and writes it into the script with --write). It avoids what the recent videos in
      $NAVI_DATA/script-history.jsonl leaned on, and, with --batch, what the other scripts in the batch drew.

The narrator card (config/narrators/*.json) is the one thing that does not rotate: the style brings out a few of
the narrator's habits each day ("habits"), at about each habit's rate, and never the same one three videos running.
For the draft-and-pick step (scripts/script/drafts.py), draw_options() draws several far-apart styles at once.
"""
import argparse
import hashlib
import json
import os
import random
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import variety  # noqa: E402

OPENINGS = ['action', 'reason', 'cond', 'scene', 'goal', 'screen', 'noun', 'lets', 'instr', 'this-is', 'marker']
# Gone (Andy, 12 Nov 2026, "cringy AI catchphrases"): the hook openings (question, "You've probably", an opinion first,
# "the bit that catches people", "You'd think", a number, "two ways"). They are a YouTuber's intro, not someone showing
# a friend how they do it. Every opening below starts from what's on screen or what's about to be done, said plainly.
OPENING_HINT = {
    'action': 'start mid-action, no lead-in ("I\'m clicking into the box up top here…")',
    'reason': 'why you\'re here, plainly ("I need a product set up for the course, so it\'s Products on the left.")',
    'cond': 'if / when / once ("When you\'re selling something on Whop it starts on the Products page.")',
    'scene': 'where the viewer has just landed ("This is the page you get when you first log in.")',
    'goal': 'what will get done ("I\'m gonna make a product, give it a price, and hide it for now.")',
    'screen': 'a plain remark on what\'s showing ("Nothing on the list yet, so I\'ll start with the box up top.")',
    'noun': 'the thing itself as the subject ("The balance report is the page with the money on it.")',
    'lets': '"Let\'s" or "let me" ("Let me get a couple of things onto this list first.")',
    'instr': 'a straight instruction ("Go to Products on the left, and it\'s Create product.")',
    'this-is': '"So this is…" (rare: at most one video in six)',
    'marker': 'a marker, a comma, then the line ("Right, so…") (rare: at most one video in six)',
}
GROUPS = {}
MARKERS = ['so', 'and', 'then', 'now', 'okay', 'right', 'all right', 'next', 'after that', 'from here']
SLOTS = ['unit', 'pre-noun', 'pre-verb', 'topic', 'value', 'tail']
SLOT_WEIGHT = {'unit': 45, 'pre-noun': 30, 'pre-verb': 8, 'topic': 6, 'value': 6, 'tail': 5}
# no 'sub' (a wrong word, then "sorry", then the right one): it sounds performed (Andy, 12 Nov 2026)
REPAIRS = {'rep': 30, 'rep-f': 12, 'rep-2': 5, 'fresh': 33, 'reph': 12, 'ins': 8}
HEDGES = ['actually', 'I think', 'kind of', 'basically', 'pretty much', 'honestly', 'probably', 'to be fair', 'sort of', 'I mean']
FILLER_RATES = {'saas': [(0, 15), (0.7, 25), (1.2, 30), (1.8, 20), (2.4, 10)],
                'course': [(0, 40), (0.5, 40), (1.0, 20)], 'tour': [(0, 70), (0.4, 30)]}
# led by the person doing it: "you"/instruction-led drafts read like written help text (Andy, 12 Nov 2026: "too stiff")
PERSON = {'i': 45, 'you': 25, 'lets': 15, 'we': 10, 'imp': 5}


def pick(rnd, weights):
    keys = list(weights)
    return rnd.choices(keys, weights=[weights[k] for k in keys])[0]


def band(rate):
    return 'none' if rate == 0 else 'low' if rate < 1 else 'mid' if rate < 2 else 'high'


def draw(script, history=(), batch=(), seed=None, avoid=(), _tries=0):
    """history: feature dicts of the recent videos, oldest first, including the ones already picked in this batch;
    batch: styles of the videos already in this batch (in order); avoid: styles drawn as other options for this
    same video (draw_options), which this one must not be close to."""
    kind = script.get('kind', 'saas') if script.get('kind') in FILLER_RATES else 'saas'
    n = max(1, len(script.get('sections', [])) or 3)
    nonce = seed if seed is not None else random.getrandbits(32)
    seed_s = hashlib.sha256(f"{script.get('title')}|{script.get('site')}|{time.strftime('%Y-%m-%d')}|{nonce}".encode()).hexdigest()
    rnd = random.Random(seed_s)
    recent = list(history)[-6:]
    used_open = Counter(h['opening']['family'] for h in recent)
    last_open = recent[-1]['opening']['family'] if recent else None
    worn = sum(1 for h in list(history)[-6:] if h['opening']['family'] in ('this-is', 'marker'))   # the checker's 1 in 6
    # in a batch every family gets used before any comes round again (a 30-video course cycles, it doesn't run out)
    in_batch = Counter(b.get('opening') for b in batch)
    floor = min(in_batch.get(o, 0) for o in OPENINGS)
    taken = {a.get('opening') for a in avoid}
    last4 = {h['opening']['family'] for h in list(history)[-5:]}     # the checker's batch neighbourhood (5)
    grouped = {o for g in GROUPS.values() if g & {h['opening']['family'] for h in list(history)[-3:]} for o in g}
    opts = {o: (1 if o in ('this-is', 'marker') else 6) * (0.15 ** (in_batch.get(o, 0) - floor)) for o in OPENINGS
            if o not in last4 and o not in grouped and used_open[o] < 2 and o not in taken and not (o in ('this-is', 'marker') and worn)}
    opening = pick(rnd, opts or {o: 1 for o in OPENINGS if o != last_open and o not in ('this-is', 'marker')})
    # markers: rest every marker that started a section in the last two videos and the most used of the last three
    # (by the marker's full name, so "from here" rests "from here", not "from"), and offer only the others
    mk = lambda s: s.get('marker') or s['first']
    starts = Counter(mk(s) for h in list(history)[-3:] for s in h['sections'] if s['start'] != 'M0')
    last2 = {mk(s) for h in list(history)[-2:] for s in h['sections'] if s['start'] != 'M0'}
    resting = [m for m in MARKERS if m in last2] + [m for m, _ in starts.most_common(1) if m in MARKERS and m not in last2]
    if not resting:
        resting = rnd.sample(['okay', 'right'], 2)
    while len(resting) < 2:
        resting.append(rnd.choice([m for m in MARKERS if m not in resting]))
    if opening == 'this-is':              # "So this is…" uses up "so" for this video
        resting.append('so')
    free = [m for m in MARKERS if m not in resting]
    on = rnd.sample(free, min(len(free), rnd.choice([2, 3])))
    breath_n = 0 if rnd.random() < 0.65 else (2 if n >= 8 else 1)
    prev_first_breath = recent and recent[-1]['sections'] and recent[-1]['sections'][0]['start'] in ('M2', 'M3')
    names = [s.get('name') for s in script.get('sections', [])]
    # section 1 starts with a breath only when the video opens on a marker, and not twice in a row across videos
    choices = [x for i, x in enumerate(names) if not (i == 0 and (prev_first_breath or opening != 'marker'))]
    breath_sections = sorted(rnd.sample(choices, min(breath_n, len(choices)))) if choices else []
    if opening == 'marker' and names:      # it opens on "marker, comma": that is this video's breath start, the only one
        breath_sections = [names[0]]
    rate = pick(rnd, dict(FILLER_RATES[kind]))
    slots_used = Counter(f['slot'] for h in recent for s in h['sections'] for f in s['fillers'] if f['slot'] != 'repeat')
    slot_rest = slots_used.most_common(1)[0][0] if slots_used else None
    favoured = []
    w = {k: v for k, v in SLOT_WEIGHT.items() if k != slot_rest}
    while len(favoured) < 2:
        x = pick(rnd, w)
        if x not in favoured:
            favoured.append(x)
    # the narrator's habits brought out today: each at about its rate, never three videos running
    card = variety.narrator(script.get('voice_id'))
    habits = []
    for hid, texts, h in variety.phrase_habits(card):
        if h['kind'] == 'hunt':
            continue
        run = list(history)[-2:]
        if len(run) == 2 and all(r.get('habits', {}).get(hid) for r in run):
            continue
        if rnd.random() < h.get('rate', 0.3):
            habits.append(hid)
    # no habit is ever forced in to keep him recognisable: a forced phrase is a catchphrase (Andy, 12 Nov 2026)
    filler_habit = next((h for h in card.get('habits', []) if h.get('kind') == 'filler'), None)
    uh_range = filler_habit.get('uh_share', [0.45, 0.75]) if filler_habit else [0.45, 0.75]
    rep_used = Counter(r['kind'] for h in recent for s in h['sections'] for r in s['repairs'])
    rw = {k: max(1, v - 8 * rep_used[k]) for k, v in REPAIRS.items()}
    kinds = []
    while len(kinds) < 2:
        x = pick(rnd, rw)
        if x not in kinds:
            kinds.append(x)
    repair_max = {'saas': 2.0, 'course': 1.0, 'tour': 0.5}[kind]
    hedges = [] if rnd.random() < 0.3 else rnd.sample([x for x in HEDGES if x != 'pretty much' or 'pretty-much' in habits], rnd.choice([1, 2]))
    sentences = pick(rnd, {'long': 4, 'mixed': 3, 'long-and-short': 3})
    person = pick(rnd, PERSON)
    second = pick(rnd, {k: v for k, v in PERSON.items() if k != person})
    gaps = []
    while len(gaps) < max(0, n - 1):
        g = round(min(0.70, max(0.25, rnd.triangular(0.25, 0.70, 0.40))), 2)
        if not gaps or abs(g - gaps[-1]) >= 0.08:
            gaps.append(g)
    style = {
        'drawn': time.strftime('%Y-%m-%d'), 'seed': nonce, 'opening': opening,
        'markers_on': on, 'markers_resting': resting, 'breath_sections': breath_sections,
        'filler_rate': rate, 'uh_share': round(rnd.uniform(*uh_range), 2), 'filler_slots': favoured,
        'filler_slot_resting': slot_rest, 'hedges': hedges,
        'repair_rate_per_min': 0.0 if rnd.random() < 0.4 else round(rnd.uniform(0.3, repair_max), 1), 'repair_kinds': kinds,
        'sentences': sentences, 'person': [person, second],
        'closing_words': rnd.choice([0, 0, 1, 1, 2]),
        'gaps': gaps, 'narrator': card.get('name'), 'habits': habits,
        'opened_with': sorted({variety.open_key(h['opening']) for h in list(history)[-8:] if h['opening'].get('first')}),
        # the whole sentences, not only their first words: the by-ear check (drafts.alike_issues) compares shapes, and a
        # writer shown only first words kept the shape and failed it three rewrites running (13 Nov 2026)
        'opened_sentences': [x for x in dict.fromkeys(h.get('open_sentence') for h in list(history)[-8:]) if x][-6:],
    }
    style['profile'] = {'opening': opening, 'lead_marker': on[0], 'filler_band': band(rate), 'filler_slot': favoured[0],
                        'repair_kind': kinds[0] if style['repair_rate_per_min'] else 'none', 'sentences': sentences, 'person': person, 'hedge': hedges[0] if hedges else 'none'}
    # too close to the last video, to a neighbour in this batch or to another option for this video: draw again
    others = [h.get('style', {}).get('profile') for h in recent[-1:]] + [b.get('profile') for b in list(batch)[-variety.BATCH_NEAR:]] + \
             [a.get('profile') for a in avoid]
    if any(variety._close_profiles(style['profile'], o) for o in others if o) and seed is None and _tries < 40:
        return draw(script, history, batch, avoid=avoid, _tries=_tries + 1)
    return style


def draw_options(script, history=(), batch=(), n=3):
    """n styles for the same video, each far from the others (a different opening, profiles not close), for
    writing n drafts from different days and keeping the best (scripts/script/drafts.py)."""
    out = []
    for _ in range(n):
        out.append(draw(script, history, batch, avoid=out))
    return out


def habits_line(s):
    """What the writer is told about the narrator. His phrases are never offered: offering one got it written in
    (Andy, 12 Nov 2026: "Was 'pretty much' pushed in?" It was). The checker still caps them if they come anyway."""
    card = variety.narrator_by_name(s.get('narrator'))
    if not card:
        return 'Narrator: no card for this voice'
    hunt = next((t for _, t, h in variety.phrase_habits(card) if h['kind'] == 'hunt'), [])
    filler = next((h['text'] for h in card.get('habits', []) if h.get('kind') == 'filler'), None)
    resting = [t[0] for hid, t, h in variety.phrase_habits(card) if h['kind'] != 'hunt' and hid not in s.get('habits', [])]
    return (f"{card['name']}: {card.get('who', '')}" + (f' His filler is "{filler}" (about {round(100 * s.get("uh_share", 0.6))}% of fillers).' if filler else '')
            + (f' If there\'s a real hunt: {" or ".join(chr(34) + t + chr(34) for t in hunt)}.' if hunt else '')
            + (f' Not today: {", ".join(chr(34) + t + chr(34) for t in resting)}.' if resting else ''))


def describe(style):
    s = style
    lines = [f"Opening: {s['opening']}: {OPENING_HINT.get(s['opening'], '')}"
             + (f"; recent videos opened with: {', '.join(chr(34) + w + chr(34) for w in s['opened_with'])} (don't)" if s.get('opened_with') else ''),
             *([f"Recent openings, whole (yours must not share their shape: the same build of clauses, turn of phrase or rhythm, "
                f"e.g. a purpose, then \", and that starts here on X, with Y\". Naming the same page or doing the same task is fine): "
                + ' | '.join(chr(34) + x + chr(34) for x in s['opened_sentences'])] if s.get('opened_sentences') else []),
             f"Step starts: mostly on the content itself; markers this video may use: {', '.join(s['markers_on'])}; "
             f"resting (don't start a step with): {', '.join(s['markers_resting'])}",
             f"Breath starts (marker + comma, the model breathes there): {', '.join(s['breath_sections']) or 'none this video'}",
             f"Fillers: at most about {s['filler_rate']} per 100 words (one is always allowed)" + (' (none today: a clean day is normal)' if not s['filler_rate'] else
                                                                   f"; if one comes, lean to {' or '.join(s['filler_slots'])}" + (f", not {s['filler_slot_resting']}" if s['filler_slot_resting'] else '')),
             ("Repairs: none today, a clean read" if not s['repair_rate_per_min'] else f"Repairs: none needed. Only where the screen earns one (naming something awkward, a wrong guess): up to {s['repair_rate_per_min']} a minute, "
             f"and then a {' or a '.join(s['repair_kinds'])} (never one per section)"),
             f"Hedges of the day: {', '.join(s['hedges']) or 'none today'}",
             f"Sentences: {s['sentences']}; who acts: {s['person'][0]}, then {s['person'][1]}",
             f"Closing words (\"okay.\", \"so that's one\"): at most {s['closing_words']}",
             habits_line(s),
             f"Gaps between sections: {', '.join(f'{g:.2f}' for g in s['gaps']) or '-'} s"]
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--batch', nargs='*', default=[])
    ap.add_argument('--seed', type=int)
    a = ap.parse_args()
    sc = json.load(open(a.script))
    hist = variety.load_history(voice_id=sc.get('voice_id'), exclude=variety.script_id(sc))
    batch = [json.load(open(p)).get('style') or {} for p in a.batch]
    st = draw(sc, hist, [b for b in batch if b], a.seed)
    print(describe(st))
    if a.write:
        sc['style'] = st
        json.dump(sc, open(a.script, 'w'), indent=1)
        print(f'written into {a.script}')


if __name__ == '__main__':
    main()
