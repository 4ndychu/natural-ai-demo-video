"""What NAVI already knows about a site, so the next video there doesn't explore the same pages again
(Andy, 12 Nov 2026).

Every time a video's pages are explored, the explorer's notes and the page data (explore.json) are kept in
$NAVI_DATA/sites/<site>/<login and view>/<time>-<video>/, with the addresses that were seen. The next video on the
same site, with the same login and the same view (a dashboard and a buyer's view are kept apart), gets those notes in
its explorer's prompt and the page data next to its own (explore/known/), so the position checker can use it too.
The explorer then only walks what the new video needs and the notes don't cover.

Pages change, so a memory is only used for `explore.remember_days` days (config/defaults.json; default 14), and the
explorer always opens the start page once to see that it still looks as the notes say.

  memory.py list [site]        what is remembered
  memory.py forget <site>      forget a site (it is explored afresh next time)
"""
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
for p in ('app', 'seats'):
    sys.path.insert(0, os.path.join(ROOT, 'scripts', p))
import store  # noqa: E402
import seats  # noqa: E402

CFG = json.load(open(os.path.join(ROOT, 'config', 'defaults.json'))).get('explore', {})
DAYS = CFG.get('remember_days', 14)
MOST = CFG.get('remember_most', 3)          # how many earlier explorations a new one is given
BUDGET = CFG.get('remember_chars', 14000)   # and how much of their notes, in characters


def root():
    return os.path.join(store.data_dir(), 'sites')


def key_for(template):
    """(site, key): which memory a video's script template reads and writes. Same site, login, business and view."""
    start = template.get('site') or ''
    s = seats.for_script(dict(template, sections=[{'actions': [{'do': 'goto', 'target': start}]}]))
    biz = s['business']['key'] if s.get('business') and s['business'].get('key') else 'any'
    seat = template.get('seat') or {}
    key = '-'.join(x for x in (s['seat'] or 'logged-out', biz, s['view'], str(seat.get('preview_as') or '')) if x)
    return s['site'], re.sub(r'[^a-zA-Z0-9._-]+', '_', key)


def folder(template):
    site, key = key_for(template)
    return os.path.join(root(), re.sub(r'[^a-zA-Z0-9._-]+', '_', site), key)


def remember(template, demo_dir, title):
    """Keep this video's exploration. Returns the folder, or None when there is nothing worth keeping."""
    ex = os.path.join(demo_dir, 'explore')
    notes, data = os.path.join(ex, 'notes.md'), os.path.join(ex, 'explore.json')
    if not (os.path.exists(notes) and os.path.exists(data)):
        return None
    d = json.load(open(data))
    if d.get('blocked'):
        return None                                   # a run the action guard stopped isn't a picture of the site
    out = os.path.join(folder(template), f"{int(time.time())}-{os.path.basename(demo_dir)}")
    os.makedirs(out, exist_ok=True)
    shutil.copy2(notes, out)
    shutil.copy2(data, out)
    urls = sorted({re.sub(r'[?#].*$', '', s.get('url', '')) for s in d.get('screens', []) if s.get('url')})
    store._write(os.path.join(out, 'meta.json'), {'t': time.time(), 'date': time.strftime('%Y-%m-%d'), 'title': title, 'urls': urls,
                                                  'screens': len(d.get('screens', []))}, 0o600)
    return out


def recall(template):
    """Earlier explorations for this site, login and view, newest first, still fresh: [{dir, meta, notes}]."""
    base, out = folder(template), []
    if not os.path.isdir(base):
        return out
    for name in sorted(os.listdir(base), reverse=True):
        d = os.path.join(base, name)
        meta = store._read(os.path.join(d, 'meta.json'), None)
        if not meta or time.time() - meta.get('t', 0) > DAYS * 86400:
            continue
        try:
            out.append({'dir': d, 'meta': meta, 'notes': open(os.path.join(d, 'notes.md')).read()})
        except OSError:
            continue
    return out[:MOST]


def _names(screen):
    return {(e.get('text') or e.get('label') or e.get('aria') or '').strip().lower()[:60]
            for e in screen.get('elements', []) if not e.get('area')} - {''}


def _path(u):
    return re.sub(r'[?#].*$', '', u or '').rstrip('/')


def fresh(template, demo_dir, cmd):
    """Does the site still look as remembered? Opens only the start page (no model, no steps: about 20 s) with `cmd`
    (explore.mjs with the video's login and the output folder <demo>/explore/fresh) and compares its buttons, links and
    fields with the remembered screen of the same address. Returns None when nothing is remembered or the page didn't
    open; else {'same', 'kept', 'of', 'new', 'gone', 'url', 'seconds'}. 13 Nov 2026: a remembered site still took 15
    minutes to explore, because the explorer re-walked everything to see if it had changed."""
    found = recall(template)
    if not found:
        return None
    out = os.path.join(demo_dir, 'explore', 'fresh')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    import subprocess
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
    try:
        now = json.load(open(os.path.join(out, 'explore.json')))['screens'][0]
    except (OSError, ValueError, KeyError, IndexError):
        return None
    then = None
    for f in found:      # newest first: the latest picture of this address
        try:
            then = next((s for s in json.load(open(os.path.join(f['dir'], 'explore.json'))).get('screens', [])
                         if _path(s.get('url')) == _path(now.get('url'))), None)
        except (OSError, ValueError):
            continue
        if then:
            break
    if not then:
        return {'same': False, 'kept': 0, 'of': 0, 'new': [], 'gone': [], 'url': now.get('url'), 'seconds': round(time.time() - t0),
                'why': 'the start page opened at an address the notes have no picture of' + (' (' + r.stderr.strip()[-120:] + ')' if r.returncode else '')}
    a, b = _names(then), _names(now)
    kept = len(a & b)
    # lists of the user's own items (products, courses) come and go between visits: most of the page staying is "same"
    return {'same': kept >= 0.7 * max(len(a), 1), 'kept': kept, 'of': len(a), 'new': sorted(b - a)[:10], 'gone': sorted(a - b)[:10],
            'url': now.get('url'), 'seconds': round(time.time() - t0)}


def known(template, demo_dir, check=None):
    """The text for the explorer's and the writer's prompts ('' when nothing is remembered), after putting the
    remembered page data in <demo>/explore/known/ for the position checker. `check`: what fresh() found."""
    found = recall(template)
    if not found:
        return ''
    kd = os.path.join(demo_dir, 'explore', 'known')
    shutil.rmtree(kd, ignore_errors=True)
    parts, left = [], BUDGET
    for i, f in enumerate(found, 1):
        os.makedirs(os.path.join(kd, str(i)), exist_ok=True)
        shutil.copy2(os.path.join(f['dir'], 'explore.json'), os.path.join(kd, str(i), 'explore.json'))
        text = f['notes'][:left]
        left -= len(text)
        parts.append(f"<explored date=\"{f['meta']['date']}\" for=\"{f['meta']['title']}\" pages=\"{', '.join(f['meta']['urls'][:8])}\">\n{text.strip()}\n</explored>")
        if left <= 0:
            break
    if check and check.get('same'):
        seen = (f"The start page was opened a moment ago and still looks as the notes say ({check['kept']} of {check['of']} of its buttons, links and fields are the same"
                + (f"; new: {', '.join(check['new'][:6])}" if check['new'] else '') + '). ')
    elif check:
        what = check.get('why') or f"only {check['kept']} of {check['of']} of its controls are the same"
        seen = (f'The start page was opened a moment ago and it has CHANGED since the notes: {what}'
                + (f"; new: {', '.join(check['new'][:8])}" if check.get('new') else '') + (f"; gone: {', '.join(check['gone'][:8])}" if check.get('gone') else '')
                + '. Explore what the change touches again. ')
    else:
        seen = ''
    return ('\nAlready explored on this site, with this login (what an earlier video\'s explorer wrote down):\n' + '\n'.join(parts) + '\n'
            + seen + 'Use the notes instead of the pages wherever they cover this plan: a section they describe (its names, places and targets, what '
            'appears after) needs no run. If they cover the whole plan, make NO run at all: write notes.md straight away. Otherwise run only for what '
            'they do not cover, the fewest steps that reach it, with no "wait" steps (the explorer waits for every page by itself). Then write '
            'notes.md for this video in full, section by section, from the earlier notes wherever they apply and from your runs for the rest, and '
            'say at the top which sections came from the notes. If a run shows a page that differs from the notes, trust the page.\n')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['forget'] and len(a) == 2:
        shutil.rmtree(os.path.join(root(), re.sub(r'[^a-zA-Z0-9._-]+', '_', a[1])), ignore_errors=True)
        print(f'Forgot what was explored on {a[1]}.')
    else:
        for site in sorted(os.listdir(root())) if os.path.isdir(root()) else []:
            if len(a) > 1 and a[1] != site:
                continue
            for key in sorted(os.listdir(os.path.join(root(), site))):
                for name in sorted(os.listdir(os.path.join(root(), site, key))):
                    m = store._read(os.path.join(root(), site, key, name, 'meta.json'), {}) or {}
                    age = (time.time() - m.get('t', 0)) / 86400
                    print(f"{site} / {key}: \"{m.get('title')}\", {m.get('date')}, {m.get('screens')} screens" + ('' if age <= DAYS else ' (too old to use)'))
