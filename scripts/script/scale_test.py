"""Does variety hold up over a long batch? A 30-lesson course (examples/variety/course-30.json), written lesson by
lesson the way a real batch is: three drafts from three styles, scored, the best kept, each lesson checked against
the ones before it. Scripts only: nothing is voiced or recorded, no credits.

  .venv/bin/python scripts/script/scale_test.py styles N     lesson N's three styles (draft1-3.json in its folder)
  .venv/bin/python scripts/script/scale_test.py pick N       score lesson N's drafts, keep the best (script.json)
  .venv/bin/python scripts/script/scale_test.py report       the whole course: openings, step starts, habits,
                                                             scores, what was ruled out (report.md)
  .venv/bin/python scripts/script/scale_test.py draws [N] [--runs 200]
                                                             the style draw alone, many times over: do openings
                                                             and markers keep rotating, or run out?
Writes to output/variety-dev/course-sim (or --out). Its $NAVI_DATA is a folder inside that, so the user's own
history is never read or touched.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
COURSE = json.load(open(os.path.join(ROOT, 'examples', 'variety', 'course-30.json')))
ALEX = 'hLygPNd2gK6Azddorc5W'


def lesson_dir(out, n):
    return os.path.join(out, f'lesson-{n:02d}')


def picked(out, upto):
    return [p for p in (os.path.join(lesson_dir(out, i), 'script.json') for i in range(1, upto)) if os.path.exists(p)]


def run(args, out):
    env = dict(os.environ, NAVI_DATA=os.path.join(out, 'navi-data'))
    return subprocess.run([sys.executable, os.path.join(HERE, 'drafts.py')] + args, env=env, capture_output=True, text=True)


def styles(out, n):
    les = COURSE['lessons'][n - 1]
    d = lesson_dir(out, n)
    os.makedirs(d, exist_ok=True)
    tmpl = {'title': les['title'], 'site': COURSE['site'], 'kind': COURSE['kind'], 'voice_id': ALEX,
            'course': COURSE['course'], 'lesson': n, 'batch_pos': n - 1,
            'sections': [{'name': f's{i + 1}', 'beat': b, 'talk': '', 'caption': '', 'actions': []} for i, b in enumerate(les['beats'])]}
    json.dump(tmpl, open(os.path.join(d, 'template.json'), 'w'), indent=1)
    prev = picked(out, n)
    r = run(['styles', os.path.join(d, 'template.json'), '--batch'] + prev, out)
    print(f'Lesson {n} of {len(COURSE["lessons"])}: "{les["title"]}" ({len(prev)} lessons before it)')
    for i, b in enumerate(les['beats'], 1):
        print(f'  s{i}: {b}')
    print(r.stdout + r.stderr)


def pick(out, n):
    d = lesson_dir(out, n)
    r = run(['pick'] + sorted(glob.glob(os.path.join(d, 'draft*.json'))) + ['--batch'] + picked(out, n) +
            ['--no-screen', '--out', os.path.join(d, 'script.json')], out)
    open(os.path.join(d, 'pick.md'), 'w').write(r.stdout + r.stderr)
    print(r.stdout + r.stderr)
    return r.returncode


def report(out):
    sys.path.insert(0, HERE)
    import variety
    rows, feats = [], []
    for n in range(1, len(COURSE['lessons']) + 1):
        p = os.path.join(lesson_dir(out, n), 'script.json')
        if not os.path.exists(p):
            continue
        sc = json.load(open(p))
        f = variety.features(sc)
        pk = open(os.path.join(lesson_dir(out, n), 'pick.md')).read() if os.path.exists(os.path.join(lesson_dir(out, n), 'pick.md')) else ''
        ruled = pk.count('ruled out')
        kept = next((l for l in pk.splitlines() if '| kept |' in l), '')
        cells = [c.strip() for c in kept.split('|')[1:-1]]
        feats.append(f)
        rows.append({'n': n, 'title': sc['title'], 'opening': f['opening']['family'], 'first2': f['opening']['first2'],
                     'starts': [variety.start_key(s) + ('' if s['start'] == 'M0' else f' ({s["start"]})') for s in f['sections']],
                     'habits': ', '.join(f['habits']) or '-', 'fillers': f['fillers_per_100'],
                     'repairs': sum(len(s['repairs']) for s in f['sections']), 'ruled_out': ruled,
                     'kept': cells[0] if cells else '?', 'quality': cells[2] if len(cells) > 2 else '', 'diff': cells[3] if len(cells) > 3 else '',
                     'text': ' / '.join(variety.plain_of(s['talk']) for s in sc['sections'])})
    if not rows:
        sys.exit('No lessons picked yet.')
    fam = Counter(r['opening'] for r in rows)
    first = Counter(r['first2'].split(' ')[0] for r in rows)
    keys = Counter(k.split(' (')[0] for r in rows for k in r['starts'][1:])
    markers = Counter(k.split(' (')[0] for r in rows for k in r['starts'] if '(M' in k)
    breath = sum(1 for r in rows for k in r['starts'] if '(M2)' in k or '(M3)' in k)
    habit_n = Counter(h for f in feats for h in f['habits'])
    half = len(rows) // 2
    distinct = lambda rs: len({r['first2'] for r in rs})
    lines = [f'# Scale test: {len(rows)} lessons of "{COURSE["course"]}"', '',
             '| # | Lesson | Opens (family) | First words | Step starts (sections 2+) | Habits | Fillers /100 | Repairs | Drafts ruled out | Kept (Q / D) |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['n']} | {r['title']} | {r['opening']} | {r['first2']} | {' · '.join(r['starts'][1:])} | {r['habits']} | "
                     f"{r['fillers']} | {r['repairs']} | {r['ruled_out']} | {r['kept']} ({r['quality']} / {r['diff']}) |")
    lines += ['', '## Totals', '',
              f'- Opening families used: {len(fam)} of 18; most used: {", ".join(f"{k} {v}" for k, v in fam.most_common(4))}',
              f'- Different first two words: {distinct(rows)} of {len(rows)} (first half {distinct(rows[:half])} of {half}, second half {distinct(rows[half:])} of {len(rows) - half})',
              f'- First words of the videos: {", ".join(f"{k} {v}" for k, v in first.most_common(6))}',
              f'- Step starts (sections 2 and later): {sum(keys.values())} starts, {len(keys)} different; most used: {", ".join(f"{k} {v}" for k, v in keys.most_common(6))}',
              f'- Marker starts: {sum(markers.values())} ({", ".join(f"{k} {v}" for k, v in markers.most_common())}); breath starts (marker + comma or full stop): {breath}',
              f'- Alex\'s habits: {", ".join(f"{k} in {v} lessons" for k, v in habit_n.items()) or "none"}; lessons with none: {sum(1 for f in feats if not f["habits"])}',
              f'- Drafts ruled out by the checker: {sum(r["ruled_out"] for r in rows)} of {3 * len(rows)}',
              '', '## The lines', ''] + [f"{r['n']}. **{r['title']}**: {r['text']}" for r in rows]
    open(os.path.join(out, 'report.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:len(rows) + 14]))
    print(f'\n(full report with every line: {os.path.join(out, "report.md")})')


def draws(n, runs):
    """The style draw alone, run as if writing an n-video batch, runs times: openings and habits over the batch."""
    sys.path.insert(0, HERE)
    import style as style_mod
    fams, gaps_left, habit_runs, longest = Counter(), [], 0, []
    for r in range(runs):
        hist, styles, seq = [], [], []
        for i in range(n):
            st = style_mod.draw({'title': f'L{i}', 'site': 'x', 'kind': 'course', 'voice_id': ALEX, 'sections': [{}, {}, {}]}, hist, styles)
            styles.append(st)
            seq.append(st['opening'])
            hist.append({'opening': {'family': st['opening'], 'first': '', 'first2': ''}, 'sections': [], 'style': st,
                         'habits': {h: 1 for h in st['habits']}})
        fams.update(seq)
        gaps_left.append(min((j - i for i in range(n) for j in range(i + 1, n) if seq[i] == seq[j]), default=n))
        run_len = max((sum(1 for _ in g) for h in ('pretty-much', 'there-we-go')
                       for g in [[k for k in range(n - 2) if all(h in styles[k + d]['habits'] for d in range(3))]]), default=0)
        habit_runs += run_len > 0
        longest.append(max(sum(1 for s in styles if h in s['habits']) for h in ('pretty-much', 'there-we-go')))
    print(f'{runs} simulated batches of {n} videos (style draw only):')
    print(f'  openings drawn: {len(fams)} families; per batch of {n}: ' +
          ', '.join(f'{k} {v / runs:.1f}' for k, v in fams.most_common()))
    print(f'  closest repeat of an opening family within a batch: at least {min(gaps_left)} videos apart (median {sorted(gaps_left)[len(gaps_left) // 2]})')
    print(f'  "marker" + "this-is" openings per batch: {(fams["marker"] + fams["this-is"]) / runs:.1f} (limit: 1 in 6 = {n / 6:.1f})')
    print(f'  a habit in three videos running: {habit_runs} of {runs} batches')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['styles', 'pick', 'report', 'draws'])
    ap.add_argument('n', nargs='?', type=int)
    ap.add_argument('--out', default=os.path.join(ROOT, 'output', 'variety-dev', 'course-sim'))
    ap.add_argument('--runs', type=int, default=200)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, 'navi-data'), exist_ok=True)
    if a.cmd == 'styles':
        styles(a.out, a.n)
    elif a.cmd == 'pick':
        sys.exit(pick(a.out, a.n))
    elif a.cmd == 'report':
        report(a.out)
    else:
        draws(a.n or 30, a.runs)


if __name__ == '__main__':
    main()
