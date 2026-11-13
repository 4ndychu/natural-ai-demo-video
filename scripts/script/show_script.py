"""Show a NAVI script for approval: talking and caption versions side by side, with the actions and what the
checker found. Nothing is generated and nothing costs credits.

Usage: .venv/bin/python scripts/script/show_script.py script.json [--out script.md]
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_script import WPS, check, words  # noqa: E402
sys.path.insert(0, os.path.join(HERE, '..', 'seats'))
import seats  # noqa: E402


def cell(t):
    return t.replace('|', '\\|').replace('\n', ' ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('--out')
    a = ap.parse_args()
    sc = json.load(open(a.script))
    issues = check(sc, os.path.dirname(os.path.abspath(a.script)))
    total = 0.0
    lines = [f"# {sc.get('title', 'Script')}", '']
    try:
        st = seats.describe(sc)
        lines += [f"**Seat:** {st['label']}" + (f" ({st['why']})" if st['why'] else '')
                  + ('' if st['login_saved'] else ' **Not logged in yet: log this seat in from Settings > Logins.**')
                  + (f" Changes the job asked for: {', '.join(st['allow'])}." if st['allow'] else ''), '']
    except ValueError:
        pass
    if sc.get('style'):
        import style as style_mod
        lines += ['**Style of the day** (scripts/script/style.py):', '', *('- ' + l for l in style_mod.describe(sc['style']).split('\n')), '']
    lines += ['| # | Talking version (what the voice says) | Caption (what\'s shown) | Actions | About |', '|---|---|---|---|---|']
    for i, s in enumerate(sc['sections'], 1):
        talk = re.sub(r'^\[relaxed\]\s*', '', s['talk'])
        secs = len(words(talk)) / WPS
        total += secs
        acts = '<br>'.join(f"on \"{x['on']}\": {x['do']} {x.get('text') or x.get('key') or x.get('target', '')}" for x in s.get('actions', []))
        lines.append(f"| {i} | {cell(talk)} | {cell(s.get('caption', ''))} | {cell(acts)} | {secs:.0f} s |")
    lines += ['', f'About {total:.0f} s of talk in {len(sc["sections"])} sections (at {WPS:.2f} words a second), '
              f'about {sum(len(s["talk"]) for s in sc["sections"]):,} characters a take.', '']
    errors = [x for x in issues if x['level'] == 'error']
    lines += [f"**Checker:** {len(errors)} errors, {len(issues) - len(errors)} warnings." if issues else '**Checker:** no problems found.']
    lines += [f"- {'Error' if x['level'] == 'error' else 'Warning'} ({x['section'] or 'script'}): {x['message']}" for x in issues]
    text = '\n'.join(lines) + '\n'
    if a.out:
        open(a.out, 'w').write(text)
    print(text)


if __name__ == '__main__':
    main()
