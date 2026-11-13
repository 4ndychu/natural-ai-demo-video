"""Draft several, keep the best: each video is written three times, from three different "days" (three far-apart
styles), and the drafts are scored on quality AND on how different they are from the recent videos and the rest
of the batch. The best one becomes script.json. The checker refusing a repeat is the floor, not the method
(Andy, 11 Nov 2026).

  .venv/bin/python scripts/script/drafts.py styles TEMPLATE [--n 3] [--batch picked.json ...]
      draws n styles far apart from each other, from the recent videos ($NAVI_DATA/script-history.jsonl) and from
      the videos already picked in the batch, and writes TEMPLATE's folder/draft1.json … draftN.json, each the
      template plus one style. Prints each style for the writer. In a batch made by batch.py the picked scripts of
      the earlier videos are found by themselves.
  .venv/bin/python scripts/script/drafts.py pick DRAFT.json ... [--batch picked.json ...] [--base EXPLORE_DIR]
                                                  [--out script.json] [--record] [--json]
      scores every draft and writes the best to --out (default: script.json next to the drafts).

Score (0 to 100), quality first:
  quality     any checker error rules a draft out (the single-video tells, the variety rules, the narrator's
              habits, and the model move review: hooks, selling, framing, reveals, knowing asides, written English,
              performed slips; --no-moves skips it); then 100, less 6 for each single-video warning.
  difference  how far it sits from the last 12 videos and its batch neighbours: the opening (same first two words,
              same first word, same family), how each step starts (same start in the same slot), shared 4-word
              runs, the same filler in the same place, the same section endings, and the style profile. The
              narrator's habits never count as a repeat.
  total       0.6 x quality + 0.4 x difference. When the top two are within 3 points, the writer reads both aloud and
              keeps the one that sounds more like a person talking; the table says so.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import style as style_mod  # noqa: E402
import variety  # noqa: E402

W_QUALITY, W_DIFF = 0.6, 0.4
WARN_COST = 6
HISTORY_CODES = ('open-', 'slot-', 'start-sequence', 'phrase-', 'filler-pattern', 'filler-spread', 'repair-pattern',
                 'repair-spread', 'hunt-repeat', 'same-', 'batch', 'habit-rate', 'identity', 'history', 'end-repeat')


def batch_siblings(template):
    """The picked scripts of the videos before this one in its batch (batch.py), in batch order."""
    bid = template.get('batch')
    if not bid:
        return []
    sys.path.insert(0, os.path.join(HERE, '..', 'batch'))
    sys.path.insert(0, os.path.join(HERE, '..', 'app'))
    import batch as batch_mod
    import store
    b = batch_mod.load(bid)
    out = []
    for i, did in enumerate(b['items']):
        if i >= template.get('batch_pos', len(b['items'])):
            break
        p = os.path.join(store.demo_dir(did), 'script.json')
        if os.path.exists(p):
            sc = json.load(open(p))
            sc.setdefault('batch_pos', i)
            out.append(sc)
    return out


def feats_of(scripts):
    out = []
    for i, sc in enumerate(scripts):
        f = variety.features(sc)
        f['pos'] = sc.get('batch_pos', i)
        out.append(f)
    return out


def difference(f, window, near):
    """0 to 1: how far this draft is from the recent videos (window, oldest first) and its batch neighbours."""
    pool = list(window[-variety.WINDOW:]) + list(near)
    if not pool:
        return 1.0, {}
    op = f['opening']
    if any(w['opening']['first2'] == op['first2'] for w in pool):
        a = 0.0
    elif any(w['opening']['first'] == op['first'] for w in pool[-6:]):
        a = 0.4
    elif any(w['opening']['family'] == op['family'] for w in pool[-6:]):
        a = 0.6
    else:
        a = 1.0
    steps = []
    for k, s in enumerate(f['sections'][1:], 1):
        key = variety.start_key(s)
        same = [w for w in pool if len(w['sections']) > k and variety.start_key(w['sections'][k]) == key]
        anywhere = [w for w in pool[-6:] if any(variety.start_key(x) == key for x in w['sections'])]
        steps.append(0.0 if same else 0.5 if anywhere else 1.0)
    b = sum(steps) / len(steps) if steps else 1.0
    mine4 = set(f['ngrams4'])
    seen4 = set().union(*[set(w.get('ngrams4', [])) for w in pool])
    c = 1 - min(1.0, 3 * len(mine4 & seen4) / max(1, len(mine4)))
    sigs = [variety.filler_sig(x) for s in f['sections'] for x in s['fillers'] if x['slot'] != 'repeat']
    seen_sigs = {variety.filler_sig(x) for w in pool for s in w['sections'] for x in s['fillers']}
    d = sum(1 for x in sigs if x not in seen_sigs) / len(sigs) if sigs else 1.0
    ends = [s['last3'] for s in f['sections']]
    seen_ends = {s['last3'] for w in pool for s in w['sections']}
    e = sum(1 for x in ends if x not in seen_ends) / len(ends) if ends else 1.0
    keys = ['opening', 'lead_marker', 'filler_band', 'filler_slot', 'repair_kind', 'sentences', 'person', 'hedge']
    prof = (f.get('style') or {}).get('profile') or {}
    dists = [1 - sum(1 for k in keys if prof.get(k) is not None and prof.get(k) == (w.get('style') or {}).get('profile', {}).get(k)) / len(keys)
             for w in pool[-6:] if (w.get('style') or {}).get('profile')]
    g = min(dists) if dists and prof else 1.0
    parts = {'opening': a, 'step starts': b, 'phrases': c, 'fillers': d, 'endings': e, 'profile': g}
    weights = {'opening': .25, 'step starts': .25, 'phrases': .2, 'fillers': .1, 'endings': .1, 'profile': .1}
    return sum(parts[k] * weights[k] for k in parts), parts


def move_issues(script):
    """The model move review (moves.py): every line that hooks, sells, frames, reveals, makes a knowing aside about
    the thing's state, sounds written, or performs a slip, as errors. A warning if the review couldn't run."""
    import moves
    found = moves.review_script(script)
    if found is None:
        return [{'level': 'warning', 'code': 'move-review', 'section': None, 'message': 'The move review did not run (no claude CLI or no answer): read every line for hooks and asides yourself.'}]
    return [{'level': 'error', 'code': 'move', 'section': x['section'], 'message': f'"{x["words"]}" ({x["move"]}) in: {x["line"]}'} for x in found]


def alike_issues(script, history, batch_scripts):
    """By ear: does this opening sound like the recent ones (moves.alike)? Strong is an error, mild a warning. The word
    checks (variety.py) and this miss different things, so both run (12 Nov 2026)."""
    import moves
    f = variety.features(script)
    earlier = [h.get('open_sentence') for h in list(history)[-8:]] + [variety.features(b).get('open_sentence') for b in batch_scripts[-variety.BATCH_NEAR:]]
    earlier = [e for e in earlier if e]
    if not f.get('open_sentence') or not earlier:
        return []
    found = moves.alike(f['open_sentence'], earlier)
    if found is None:
        return [{'level': 'warning', 'code': 'alike-review', 'section': None, 'message': 'The by-ear opening check did not run.'}]
    return [{'level': 'error' if x['strength'] == 'strong' else 'warning', 'code': 'open-alike', 'section': None,
             'message': f'Sounds like a recent opening ({x["strength"]}): "{x["line"][:70]}". Shared: {x["shared"]}'} for x in found]


def score(script, history, batch_scripts, base=None, skip=(), review_moves=False):
    """One draft: {'eligible', 'quality', 'difference', 'total', 'errors', 'warnings', 'parts'}."""
    from check_script import check
    sc = dict(script)
    batch_feats = feats_of(batch_scripts)
    sc.setdefault('batch_pos', len(batch_scripts) if batch_scripts else None)
    issues = [i for i in check(sc, base, history=history, batch=batch_feats or None) if i['code'] not in skip]
    if review_moves:
        issues += move_issues(sc)
        issues += alike_issues(sc, history, batch_scripts)
    errors = [i for i in issues if i['level'] == 'error']
    warns = [i for i in issues if i['level'] == 'warning' and not i['code'].startswith(HISTORY_CODES)]
    quality = max(0, 100 - WARN_COST * len(warns))
    f = variety.features(sc)
    f['pos'] = sc.get('batch_pos')
    near = variety._near(f, batch_feats) if batch_feats else []
    diff, parts = difference(f, history, near)
    total = round(W_QUALITY * quality + W_DIFF * 100 * diff, 1)
    return {'eligible': not errors, 'quality': quality, 'difference': round(100 * diff), 'total': total,
            'errors': errors, 'warnings': warns, 'parts': {k: round(v, 2) for k, v in parts.items()}}


def pick(drafts, history, batch_scripts, base=None, skip=(), review_moves=False):
    """drafts: [(name, script)]. Returns (best name or None, [(name, score)] ranked, near_tie)."""
    scored = [(n, score(sc, history, batch_scripts, base, skip, review_moves)) for n, sc in drafts]
    ranked = sorted(scored, key=lambda x: (not x[1]['eligible'], -x[1]['total']))
    ok = [r for r in ranked if r[1]['eligible']]
    tie = len(ok) >= 2 and ok[0][1]['total'] - ok[1][1]['total'] < 3
    return (ok[0][0] if ok else None), ranked, tie


def table(ranked, best, tie):
    rows = ['| Draft | Opening | Quality | Difference | Total | |', '|---|---|---|---|---|---|']
    for n, s in ranked:
        why = 'kept' if n == best else ('ruled out: ' + '; '.join(f"[{e['code']}] {e['message'][:70]}" for e in s['errors'][:2])
                                        if not s['eligible'] else '')
        rows.append(f"| {n} | {s.get('opening', '')} | {s['quality']} | {s['difference']} | {s['total']} | {why} |")
    if tie:
        rows.append('\nThe top two are within 3 points: read both aloud and keep the one that sounds more like a person talking.')
    return '\n'.join(rows)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    a1 = sub.add_parser('styles')
    a1.add_argument('template')
    a1.add_argument('--n', type=int, default=3)
    a1.add_argument('--batch', nargs='*', default=[])
    a1.add_argument('--out-dir')
    a2 = sub.add_parser('pick')
    a2.add_argument('drafts', nargs='+')
    a2.add_argument('--batch', nargs='*', default=[])
    a2.add_argument('--base')
    a2.add_argument('--out')
    a2.add_argument('--record', action='store_true', help='add the kept script to the history now (normally the voice step does)')
    a2.add_argument('--json', action='store_true')
    a2.add_argument('--no-moves', action='store_true', help='skip the model move review (it runs the local claude CLI)')
    a2.add_argument('--no-screen', action='store_true', help='scripts with no explored page or actions (the scale test): skip the position and still-screen checks')
    a = ap.parse_args()
    if a.cmd == 'styles':
        tmpl = json.load(open(a.template))
        batch_scripts = [json.load(open(p)) for p in a.batch] or batch_siblings(tmpl)
        hist = variety.load_history(voice_id=tmpl.get('voice_id'), exclude=variety.script_id(tmpl))
        recent = hist + feats_of(batch_scripts)
        styles = style_mod.draw_options(tmpl, recent, [s.get('style') or {} for s in batch_scripts], a.n)
        out_dir = a.out_dir or os.path.dirname(os.path.abspath(a.template))
        for i, st in enumerate(styles, 1):
            d = dict(tmpl, style=st, draft=i)
            if batch_scripts and 'batch_pos' not in d:
                d['batch_pos'] = len(batch_scripts)
            p = os.path.join(out_dir, f'draft{i}.json')
            json.dump(d, open(p, 'w'), indent=1)
            print(f'--- draft {i}: {p}\n{style_mod.describe(st)}\n')
        print(f'Write all {a.n} drafts (the same video, the same facts and actions), then: drafts.py pick {out_dir}/draft*.json')
        return
    drafts = [(os.path.basename(p), json.load(open(p))) for p in a.drafts]
    batch_scripts = [json.load(open(p)) for p in a.batch] or batch_siblings(drafts[0][1])
    hist = variety.load_history(voice_id=drafts[0][1].get('voice_id'), exclude=variety.script_id(drafts[0][1]))
    best, ranked, tie = pick(drafts, hist, batch_scripts, a.base, ('position', 'still-screen') if a.no_screen else (), not a.no_moves)
    for n, s in ranked:
        s['opening'] = dict(drafts)[n].get('style', {}).get('opening', '')
    if a.json:
        print(json.dumps({'best': best, 'tie': tie, 'ranked': [{'draft': n, **{k: v for k, v in s.items()}} for n, s in ranked]}))
    else:
        print(table(ranked, best, tie))
    if not best:
        print('\nNo draft is clean: fix the errors above (or write another draft) before going on.')
        sys.exit(1)
    sc = dict(drafts)[best]
    sc.pop('draft', None)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.drafts[0])), 'script.json')
    json.dump(sc, open(out, 'w'), indent=1)
    print(f'\nKept {best} -> {out}')
    if a.record:
        variety.record(sc)


if __name__ == '__main__':
    main()
