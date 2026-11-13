"""A short, readable version of explore.json for the model jobs: one line per button, link and field, with where it
sits on the page. The full file (every box in pixels) is what the position checker reads; a model only needs this.

  .venv/bin/python scripts/explore/digest.py <explore folder or explore.json> [--screen N]
"""
import json
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'script'))
from positions import region, says  # noqa: E402  (the same words the position checker will hold the script to)


def where(box, vw, vh):
    return 'on screen ' + says(*region(box, [0, 0, vw, vh])) + (' (below the first screen)' if box[1] >= vh else '')


def line(e, vw, vh):
    name = e.get('text') or e.get('label') or e.get('placeholder') or e.get('aria') or ''
    bits = [e.get('tag', '?') + (f"[{e['type']}]" if e.get('type') else ''), json.dumps(name[:70], ensure_ascii=False)]
    if e.get('label') and e.get('label') != name:
        bits.append(f"label {json.dumps(e['label'][:50], ensure_ascii=False)}")
    if e.get('href'):
        bits.append('-> ' + e['href'][:80])
    if e.get('cls'):
        bits.append('.' + str(e['cls']).split()[0])
    if e.get('box'):
        b = [round(v) for v in e['box']]
        bits.append(f"{where(e['box'], vw, vh)}, at {b[0]},{b[1]} size {b[2]}x{b[3]}")
    p = e.get('panel')
    if isinstance(p, dict) and p.get('box') and e.get('box'):
        bits.append(f"in its panel ({p.get('kind', 'panel')}): {says(*region(e['box'], p['box']))}")
    return '  ' + ' | '.join(bits)


def digest(path, only=None):
    if os.path.isdir(path):
        path = os.path.join(path, 'explore.json')
    ex = json.load(open(path))
    vw, vh = (ex.get('viewport') or [1440, 810])[:2] if isinstance(ex.get('viewport'), list) else (
        (ex.get('viewport') or {}).get('width', 1440), (ex.get('viewport') or {}).get('height', 810))
    out = [f"Explored {ex.get('url')} (site {ex.get('site')}, seat {ex.get('seat')}); page {vw}x{vh}."]
    if ex.get('blocked'):
        out.append('BLOCKED by the action guard: ' + json.dumps(ex['blocked'], ensure_ascii=False)[:400])
    prev = None
    for s in ex.get('screens', []):
        if only is not None and s.get('n') != only:
            continue
        out.append(f"\nScreen {s.get('n')}: after \"{s.get('step')}\" | {s.get('url')} | title \"{s.get('title')}\" | settled in "
                   f"{s.get('settle_ms')} ms | screenshot {s.get('file')}" + (f" | ERROR {s['error']}" if s.get('error') else ''))
        lines = [line(e, vw, vh) for e in s.get('elements', [])]
        if prev is not None and only is None:      # after the first screen, only what changed
            new = [x for x in lines if x not in prev]
            gone = len([x for x in prev if x not in lines])
            out += new or ['  (nothing new)']
            out.append(f'  ({len(lines) - len(new)} as before' + (f', {gone} gone' if gone else '') + ')')
        else:
            out += lines
        prev = lines
    return '\n'.join(out)


if __name__ == '__main__':
    a = sys.argv[1:]
    only = int(a[a.index('--screen') + 1]) if '--screen' in a else None
    print(digest(a[0], only))
