"""NAVI privacy (reference/privacy.md): settings, the in-page blur, the live page check and the frame scan.

Layer 2, before recording: blur.js runs inside every page (the recorder's initScript) and blurs matches before
they are painted. check_page() opens the start page with it and saves a screenshot and the list, so the blur can be
checked on the live page before the first take.

Layer 3, after recording: scan_take() reads every distinct browser frame with Apple's built-in text recognition
(scripts/privacy/ocr.swift, compiled to .venv/bin/navi-ocr). Anything still readable that matches (text inside
images or canvases, or anything the page blur missed) is blurred over its time range: the boxes go in
take/post-blur.json and the polish step blurs them in the raw frames, before Recordly's renderer zooms anything.

Layer 4: review() writes privacy.json and privacy.md: every blur with its time, and the unsure ones first.
No private text is ever written down: every preview is masked.
"""
import concurrent.futures
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
P = json.load(open(os.path.join(HERE, 'patterns.json')))
CONFIG = json.load(open(os.path.join(ROOT, 'config', 'defaults.json')))['privacy']
OCR = os.path.join(ROOT, '.venv', 'bin', 'navi-ocr')
REC = os.path.join(ROOT, 'recorder', 'agent-screenplay')
CATS = P['categories']


def label(cat):
    return 'hide words' if cat == 'hide' else CATS[cat]['label']


def cap(t):
    return t[:1].upper() + t[1:]


# ---- settings ----------------------------------------------------------------------------------------------
def data_dir():
    return os.path.expanduser(os.environ.get('NAVI_DATA') or '~/Library/Application Support/NAVI')


def start_url(script):
    return next((a.get('target', '') for s in script.get('sections', []) for a in s.get('actions', []) if a.get('do') == 'goto'), '')


def test_business(script):
    """The user's test business this demo opens in, if they marked it as one ($NAVI_DATA/test-businesses.json:
    [{"site": "whop.com", "match": "whop.com/dashboard/biz_...", "name": "NAVI Test"}]), else None.
    Only the user marks a business as a test; NAVI never guesses it from a name."""
    path = os.path.join(data_dir(), 'test-businesses.json')
    url = re.sub(r'^[a-z]+://(www\.)?', '', start_url(script).lower())
    if not url or not os.path.exists(path):
        return None
    for b in json.load(open(path)):
        m = re.sub(r'^[a-z]+://(www\.)?', '', b.get('match', '').lower())
        if m and url.startswith(m):
            return b
    return None


def settings(script):
    """The demo's privacy settings: which categories are blurred, hide words, and the warnings to show."""
    p = script.get('privacy', {})
    name = p.get('preset', CONFIG['preset'])
    preset = CONFIG['presets'][name]
    blur = {c for c, v in CATS.items() if v['tier'] in preset['blur_tiers']}
    warnings = []
    for c in list(preset.get('show', [])) + list(p.get('show', [])):
        if c not in CATS:
            warnings.append(f'Unknown privacy item "{c}" (ignored).')
        elif CATS[c]['tier'] == 1:
            warnings.append(f'{cap(label(c))} are always blurred, so "show" is ignored.')
        else:
            blur.discard(c)
            if CATS[c].get('warn'):
                warnings.append(f'Showing {label(c)}: {CATS[c]["warn"]}')
            if CATS[c].get('other_people'):
                warnings.append(f"Showing {label(c)}: if they're real, that's other people's data. Only show it if it's fake.")
    # In a business the user marked as a test, prices and money amounts show (Andy, 2026-11-10): it's fake data, and
    # a demo about setting a price needs to show it. A real business keeps money blurred unless the demo says "show".
    biz = test_business(script)
    if biz and 'money' not in p.get('blur', []) and 'money' in blur:
        blur.discard('money')
        warnings.append(f'Test business "{biz.get("name", biz["match"])}": prices and money amounts are shown (fake data).')
    for c in p.get('blur', []):
        if c in CATS:
            blur.add(c)
    hide = [w.strip() for w in p.get('hide_words', []) if w.strip()]
    return {'preset': name, 'blur': sorted(blur), 'hide_words': hide, 'warnings': warnings,
            'test_business': biz.get('name', biz['match']) if biz else None}


def init_script(s):
    """JavaScript for the recorder's initScript: the settings, then blur.js, then the page parts hidden before recording."""
    cfg = {'typed': s.get('typed', []), 'patterns': P['patterns'], 'categories': CATS, 'blur': s['blur'], 'hideWords': s['hide_words'],
           'blurPx': CONFIG['blur_px'], 'elementHints': P['element_hints'], 'typingPrefixes': P['typing_prefixes'],
           'ignore': P['ignore'], 'sensitivePages': P.get('sensitive_pages'), 'sensitiveCats': P.get('sensitive_categories', [])}
    return ('window.__NAVI_PRIVACY__ = ' + json.dumps(cfg) + ';\n' + open(os.path.join(HERE, 'blur.js')).read() + '\n' + hide_script())


def hide_script():
    """JavaScript that takes a site's nag banners off the page before recording (config recording.hide_on_page;
    page_hide.js). Hidden, not blurred."""
    rules = json.load(open(os.path.join(ROOT, 'config', 'defaults.json')))['recording'].get('hide_on_page') or []
    return 'window.__NAVI_HIDE__ = ' + json.dumps(rules) + ';\n' + open(os.path.join(HERE, 'page_hide.js')).read()


# ---- matching (the same rules as blur.js) ------------------------------------------------------------------
def _compile(s):
    pats = []
    for p in P['patterns']:
        pats.append({**p, 'rx': re.compile(p['re'], re.I if 'i' in p.get('flags', '') else 0),
                     'near_rx': re.compile(p['near'], re.I) if p.get('near') else None,
                     'suffix_rx': re.compile(p['price_suffix'], re.I) if p.get('price_suffix') else None})
    if s['hide_words']:
        pats.append({'cat': 'hide', 'rx': re.compile(r'\b(?:' + '|'.join(map(re.escape, s['hide_words'])) + r')\b', re.I),
                     'near_rx': None, 'suffix_rx': None})
    return pats


def _luhn(t):
    d = re.sub(r'\D', '', t)
    total = 0
    for i, ch in enumerate(reversed(d)):
        n = int(ch)
        if i % 2:
            n = n * 2 - 9 if n * 2 > 9 else n * 2
        total += n
    return len(d) >= 13 and total % 10 == 0


def find(text, s, ctx=None, _cache={}):
    """Matches to blur in `text`: [(start, end, cat)]. `ctx` is nearby text for the context-only categories."""
    key = json.dumps([s['blur'], s['hide_words']])
    pats = _cache.get(key) or _cache.setdefault(key, _compile(s))
    active = set(s['blur'])
    ignore = {k: re.compile(v, re.I) for k, v in P['ignore'].items()}
    out = []
    for p in pats:
        if p['cat'] != 'hide' and p['cat'] not in active and not (p['suffix_rx'] and 'price' in active):
            continue
        # "control" rules look only at the text's own line (a button or row), never at the whole frame
        near = text if p.get('near_scope') == 'control' else (ctx or text)
        if p['near_rx'] and not p['near_rx'].search(near):
            continue
        for m in p['rx'].finditer(text):
            if not m.group(0):
                continue
            a, b = m.span(p['group']) if p.get('group') else m.span()
            if a < 0:
                continue
            if p.get('min_digits') and len(re.sub(r'\D', '', m.group(0))) < p['min_digits']:
                continue
            if p.get('luhn') and not _luhn(m.group(0)):
                continue
            cat = p['cat']
            if p['suffix_rx'] and p['suffix_rx'].search(text[b:b + 24]):
                cat = 'price'
            if cat in ignore and ignore[cat].search(text[a:b]):
                continue
            if cat != 'hide' and cat not in active:
                continue
            out.append((a, b, cat))
    out.sort(key=lambda x: (x[0], -x[1]))
    kept = []
    for a, b, c in out:
        if not kept or a >= kept[-1][1]:
            kept.append((a, b, c))
    return kept


def mask(text, cat):
    text = text.strip()
    if cat == 'hide' or CATS.get(cat, {}).get('tier') == 1:
        return f'•••• ({len(text)} characters)'
    return '•••' if len(text) <= 3 else f'{text[0]}•••{text[-1]} ({len(text)} characters)'


def typed(texts, s):
    """Text NAVI will type that has something private in it (blur.js blurs the field from the first letter),
    and a warning for each."""
    found, warnings = [], []
    for where, text in texts:
        cats = [c for _, _, c in find(text or '', s)]
        if cats:
            found.append({'text': text, 'cat': cats[0]})
            warnings.append(f'{where}: the typed text has {label(cats[0])} in it, so the field is blurred from the first letter.')
    return found, warnings


# ---- layer 2: check the blur on the live page ------------------------------------------------------------------
def check_page(url, s, out_png, viewport, storage_state=None, guard=None, extra_js=''):
    """Open the start page with the blur, wait for it to settle, save a 2x screenshot and return what was blurred.
    guard: the action guard ({module, config}), so even this check can't change anything."""
    cfg = {'url': url, 'out': out_png, 'width': viewport[0], 'height': viewport[1], 'script': init_script(s) + ('\n' + extra_js if extra_js else ''),
           'storageState': storage_state, 'guard': guard}
    r = subprocess.run(['node', os.path.join(HERE, 'check_page.mjs')], input=json.dumps(cfg), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('The privacy page check failed: ' + (r.stdout + r.stderr)[-1500:])
    return json.loads(r.stdout.strip().splitlines()[-1])


# ---- layer 3: read the frames ------------------------------------------------------------------------------
def ensure_ocr():
    src = os.path.join(HERE, 'ocr.swift')
    if not os.path.exists(OCR) or os.path.getmtime(OCR) < os.path.getmtime(src):
        r = subprocess.run(['swiftc', '-O', src, '-o', OCR], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("Couldn't build the text reader (needs Swift from Xcode or the Command Line Tools):\n" + r.stderr[-1500:])


def ocr(paths, workers=4, batch=8):
    ensure_ocr()
    chunks = [paths[i:i + batch] for i in range(0, len(paths), batch)]
    results = {}

    def run(chunk):
        r = subprocess.run([OCR] + chunk, capture_output=True, text=True, check=True)
        return [json.loads(line) for line in r.stdout.splitlines() if line.strip()]

    with concurrent.futures.ThreadPoolExecutor(workers) as ex:
        for res in ex.map(run, chunks):
            for d in res:
                results[d['image']] = d
    return results


def _box(line, a, b, pad):
    words = [w for w in line['words'] if w['start'] < b and w['start'] + len(w['text']) > a] or [line]
    x0 = min(w['box'][0] for w in words)
    y0 = min(w['box'][1] for w in words)
    x1 = max(w['box'][0] + w['box'][2] for w in words)
    y1 = max(w['box'][1] + w['box'][3] for w in words)
    return [x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad]


REMINDER = ("Watch every video all the way through before you publish it. NAVI lowers the risk of showing something "
            "private, but it can't remove it. Record with a test account and fake data where you can, and add any names or "
            "words that must never show (a client, a surname) to the hide-words box.")

UNSURE = [  # readable things that look private but match no rule: blurred, and listed first for the user to decide
    ('a long code that might be a key or token', re.compile(r'\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[A-Za-z])[A-Za-z0-9_-]{20,}\b')),
    ('what might be an email', re.compile(r'\S@\S')),
    ('a long number', re.compile(r'\b\d{8,}\b')),
]


def _allowed(text, m, s):
    """An unsure match that is really something the rules allow: an example address, or a category the user shows."""
    a, b = m.start(), m.end()
    while a > 0 and not text[a - 1].isspace():
        a -= 1
    while b < len(text) and not text[b].isspace():
        b += 1
    token = text[a:b].strip('.,;:()<>"\'')
    if any(re.search(rx, token, re.I) for rx in P['ignore'].values()):
        return True
    email = next(p['re'] for p in P['patterns'] if p['cat'] == 'email')
    return '@' in token and 'email' not in s['blur'] and re.fullmatch(email, token) is not None


# A menu item read off the picture: its icon misread as one or two characters, then a short label ("8 Customers",
# "& Payments"). Navigation labels are never blurred (Andy, 2026-11-10: the people icon next to "Customers" read as
# "8" and the menu item was blurred as a customer count). A real count has a longer number ("1,204 Customers") or
# sits in a sentence, so it still matches.
NAV_LABEL = re.compile(r"^\s*(\S{1,2})\s+([A-Z][A-Za-z&'-]*(?:\s+[A-Za-z&'-]+){0,2})\s*$")


def nav_label(text, a, box=None, size=None):
    """True when the match starting at a is only a menu item's icon misread as a number. With the line's box and the
    frame size, only where menus sit (the left quarter, or the top eighth), so a "2 Members" tile mid-page still blurs."""
    m = NAV_LABEL.match(text)
    if not m or a > m.end(1):
        return False
    if box and size:
        return box[0] + box[2] <= size[0] * 0.25 or box[1] + box[3] <= size[1] * 0.125
    return True


def _png_size(path):
    with open(path, 'rb') as f:
        head = f.read(24)
    return int.from_bytes(head[16:20], 'big'), int.from_bytes(head[20:24], 'big')


def scan_take(take_dir, s):
    """Read every distinct frame of the take. Returns the hits, and writes the blur boxes to take/post-blur.json."""
    take = json.load(open(os.path.join(take_dir, 'take.json')))
    frames = take['source']['frames']
    paths = [os.path.join(take_dir, take['source']['dir'], f) for _, f in frames]
    res = ocr(paths)
    pad = 6 * take.get('scale', 2) // 2
    size = _png_size(paths[0]) if paths else None
    hits = []
    for i, (t, f) in enumerate(frames):
        t1 = frames[i + 1][0] if i + 1 < len(frames) else take['duration']
        r = res.get(paths[i], {'lines': []})
        whole = ' '.join(l['text'] for l in r['lines'])
        for line in r['lines']:
            found = [(a, b, cat) for a, b, cat in find(line['text'], s, whole)
                     if cat == 'hide' or not nav_label(line['text'], a, _box(line, a, b, 0), size)]
            for a, b, cat in found:
                hits.append({'t0': t, 't1': t1, 'cat': cat, 'box': _box(line, a, b, pad),
                             'preview': mask(line['text'][a:b], cat), 'unsure': line['conf'] < CONFIG['unsure_below_confidence']})
            taken = [(a, b) for a, b, _ in found]
            for what, rx in UNSURE:
                for m in rx.finditer(line['text']):
                    if any(a < m.end() and m.start() < b for a, b in taken):
                        continue
                    if _allowed(line['text'], m, s):
                        continue
                    hits.append({'t0': t, 't1': t1, 'cat': 'unsure', 'what': what, 'box': _box(line, m.start(), m.end(), pad),
                                 'preview': mask(m.group(0), 'secret'), 'unsure': True})
    spans = _merge(hits)
    json.dump([{'t0': h['t0'], 't1': h['t1'], 'box': h['box']} for h in spans],
              open(os.path.join(take_dir, 'post-blur.json'), 'w'), indent=1)
    return {'frames_read': len(paths), 'hits': spans}


def _iou(a, b):
    ax1, ay1, bx1, by1 = a[0] + a[2], a[1] + a[3], b[0] + b[2], b[1] + b[3]
    iw, ih = max(0, min(ax1, bx1) - max(a[0], b[0])), max(0, min(ay1, by1) - max(a[1], b[1]))
    inter = iw * ih
    return inter / max(1, a[2] * a[3] + b[2] * b[3] - inter)


def _merge(hits):
    """One entry per thing on screen: the same category in about the same place in back-to-back frames."""
    out = []
    for h in sorted(hits, key=lambda h: h['t0']):
        for o in reversed(out):
            if o['cat'] == h['cat'] and abs(o['t1'] - h['t0']) < 1e-3 and _iou(o['box'], h['box']) > 0.4:
                o['t1'] = h['t1']
                o['box'] = [min(o['box'][0], h['box'][0]), min(o['box'][1], h['box'][1]),
                            max(o['box'][0] + o['box'][2], h['box'][0] + h['box'][2]) - min(o['box'][0], h['box'][0]),
                            max(o['box'][1] + o['box'][3], h['box'][1] + h['box'][3]) - min(o['box'][1], h['box'][1])]
                o['unsure'] = o['unsure'] and h['unsure']
                break
        else:
            out.append(dict(h))
    return out


# ---- layer 4: the list for Review --------------------------------------------------------------------------
def fmt(t):
    return f'{int(t // 60)}:{int(t % 60):02d}'


def in_page(take):
    """The page blurs, from what blur.js reported during the take: each with the times it was on screen."""
    hits, spans = {}, {}
    for r in take.get('reports', []):
        if r.get('kind') != 'privacy':
            continue
        if r['event'] == 'blur':
            hits[r['id']] = {k: r[k] for k in ('id', 'cat', 'tier', 'how', 'preview', 'where', 'page')}
        elif r['event'] == 'show':
            spans.setdefault(r['id'], []).append([r['t'], None])
        elif r['event'] == 'hide' and spans.get(r['id']) and spans[r['id']][-1][1] is None:
            spans[r['id']][-1][1] = r['t']
    out = []
    for i, h in hits.items():
        sp = [[a, b if b is not None else take['duration']] for a, b in spans.get(i, [])]
        if sp:
            out.append({**h, 'on_screen': [[round(a, 2), round(b, 2)] for a, b in sp]})
    return sorted(out, key=lambda h: h['on_screen'][0][0])


def review(out_dir, take, scan, s, page_check=None):
    """privacy.json (for the app's Review list) and privacy.md."""
    page = in_page(take)
    items = []
    groups = []  # the same thing seen in back-to-back frames (it moves while the page scrolls): one entry
    for h in sorted(scan['hits'], key=lambda h: h['t0']):
        key = (h['cat'], h.get('what'), h['preview'])
        g = next((g for g in groups if g['key'] == key and h['t0'] - g['t1'] < 1.0), None)
        if g:
            g['t1'] = max(g['t1'], h['t1'])
            g['unsure'] = g['unsure'] and h['unsure']
        else:
            groups.append({**h, 'key': key})
    for h in groups:
        what = h.get('what') or (('what might be ' if h['unsure'] else '') + label(h['cat']) + ' in the video frame')
        items.append({'id': f"f{len(items) + 1}", 't': fmt(h['t0']), 'at': round(h['t0'], 2), 'until': round(h['t1'], 2),
                      'what': (what[0].upper() + what[1:]) + ' (read from the picture, not the page text)',
                      'preview': h['preview'], 'unsure': h['unsure'], 'layer': 'frame scan', 's': ''})
    for h in page:
        items.append({'id': h['id'], 't': fmt(h['on_screen'][0][0]), 'at': h['on_screen'][0][0], 'until': h['on_screen'][-1][1],
                      'what': f"{cap(label(h['cat']))} ({h['how']}, {h['where'] or 'page'})", 'preview': h['preview'],
                      'unsure': False, 'layer': 'page', 's': 'keep'})
    items.sort(key=lambda x: (not x['unsure'], x['at']))
    doc = {'reminder': REMINDER, 'preset': s['preset'], 'blurred': s['blur'], 'shown': sorted(set(CATS) - set(s['blur'])), 'hide_words': len(s['hide_words']),
           'warnings': s['warnings'], 'frames_read': scan['frames_read'], 'blurs': items, 'page_check': page_check}
    json.dump(doc, open(os.path.join(out_dir, 'privacy.json'), 'w'), indent=1, ensure_ascii=False)
    lines = ['# Privacy', '', f'**{REMINDER}**', '',
             f"Preset: {CONFIG['presets'][s['preset']]['label']}. Blurred: {', '.join(label(c) for c in s['blur'])}."
             + (f" Hide words: {len(s['hide_words'])}." if s['hide_words'] else ''), '']
    lines += [f'- **Warning:** {w}' for w in s['warnings']]
    unsure = [i for i in items if i['unsure']]
    lines += ['', f"## Not sure ({len(unsure)}): blurred for now, keep or show each one", '']
    lines += [f"- {i['t']}  {i['what']}: {i['preview']}" for i in unsure] or ['- Nothing.']
    lines += ['', f"## Blurred ({len(items) - len(unsure)})", '']
    lines += [f"- {i['t']}  {i['what']}: {i['preview']}" for i in items if not i['unsure']] or ['- Nothing.']
    lines += ['', f"Frames read after recording: {scan['frames_read']}. Anything readable that matched is blurred over the time it was on screen."]
    open(os.path.join(out_dir, 'privacy.md'), 'w').write('\n'.join(lines) + '\n')
    return doc
