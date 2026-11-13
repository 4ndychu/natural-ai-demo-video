"""Check every position a script gives ("top right", "at the bottom of the form") against the explored page.

Andy, 2026-11-10: the whop video said "Create product, bottom left" when the button was at the bottom right of the
form (the form fills the left of the screen). Every position must be checked against the explored page, or
described loosely ("at the bottom of the form").

How: each position phrase in a section's talk or caption is tied to the action it describes (the action whose cue
word is nearest in the same sentence of the talk; in a caption, the action whose target's name is in the same
sentence, else the one the talk tied). The target is looked up in the explore data (explore.json files written by
scripts/explore/explore.mjs: every visible control with its box and the panel it sits in). Then:
  - "of the form / panel / dialog / list ..." is checked against the panel the target sits in;
  - a bare position ("top right", "up top") is checked against the screen, and must also agree with the panel the
    target sits in, when it's in one: otherwise a viewer reads it the other way, so say which ("of the form").
Positions that can't be checked (no explore data, a target that isn't in it, a CSS target with no text) are errors
too: explore it, or describe it without a position.
"""
import glob
import json
import os
import re

CORNER = re.compile(r"\b(top|upper|bottom|lower)[ -](left|right)(?:[ -]hand)?(?: corner)?\b", re.I)
VERT = re.compile(r"\b(up top|at the top|on top|top of|along the top|across the top|at the bottom|bottom of|down at the bottom|"
                  r"down the bottom|along the bottom)\b", re.I)
HORIZ = re.compile(r"\b(on the (?:left|right)|to the (?:left|right)|(?:left|right)[ -]hand side|(?:left|right) side|"
                   r"in the (?:left|right) column|over on the (?:left|right))\b", re.I)
OF = re.compile(r"^\s*(?:of|in|on) (?:the|this|that) (form|panel|dialog|pop-?up|popup|window|menu|list|table|sidebar|side panel|"
                r"card|box|row|section|modal|page|screen)\b", re.I)
SCREENISH = {'page', 'screen', 'window'}


def phrases(text):
    """[(start, end, v, h, container)] for every position phrase. v: top/bottom/None, h: left/right/None."""
    out, taken = [], []
    for rx in (CORNER, VERT, HORIZ):
        for m in rx.finditer(text):
            if any(a < m.end() and m.start() < b for a, b in taken):
                continue
            g = m.group(0).lower()
            v = 'top' if re.search(r'top|upper', g) else 'bottom' if re.search(r'bottom|lower', g) else None
            h = 'left' if 'left' in g else 'right' if 'right' in g else None
            end = m.end()
            if g.endswith(' of'):              # "top of the form"
                end = m.end() - 3
            c = OF.match(text[end:])
            container = c.group(1).lower() if c else None
            out.append((m.start(), m.end() + (c.end() if c else 0), v, h, container))
            taken.append((m.start(), m.end()))
    return sorted(out)


def target_name(target):
    """(name, kind) from a recorder target, or (None, None) when it has no visible text to look up."""
    if not target:
        return None, None
    m = re.match(r"^role=(\w+)\[name=['\"](.+?)['\"]\]$", target)
    if m:
        return m.group(2), m.group(1)
    m = re.match(r'^(text|placeholder|label)=(.+)$', target)
    if m:
        return m.group(2).strip('\'"'), m.group(1)
    m = re.search(r":has-text\(['\"](.+?)['\"]\)", target)
    if m:
        return m.group(1), 'has-text'
    m = re.match(r'^(?:css=)?([a-z][a-z0-9]*)?((?:[.#][\w-]+)+)$', target.strip())
    if m:                                   # a plain CSS target: tag.class or #id, matched on what explore logged
        return target.strip().removeprefix('css='), 'css'
    return None, None


def load_explore(script, base):
    """Every element seen while exploring: [{text, label, tag, role, box, panel}]. The script's "explore" (a folder or
    a list of them, relative to the script) or <script folder>/explore."""
    want = script.get('explore') or 'explore'
    folders = want if isinstance(want, list) else [want]
    els = []
    for f in folders:
        root = os.path.join(base or '.', f)
        for path in glob.glob(os.path.join(root, '**', 'explore.json'), recursive=True) + glob.glob(os.path.join(root, 'explore.json')):
            data = json.load(open(path))
            vw, vh = (data.get('viewport') or [1440, 810])[:2]
            for sc in data.get('screens', []):
                for e in sc.get('elements', []):
                    els.append({**e, 'vw': vw, 'vh': vh, 'shot': os.path.relpath(os.path.join(os.path.dirname(path), sc.get('file', '')), base or '.')})
    return els


def norm(t):
    return re.sub(r'\s+', ' ', (t or '').strip().lower())


def css_match(e, sel):
    m = re.match(r'^([a-z][a-z0-9]*)?((?:[.#][\w-]+)+)$', sel)
    tag, rest = m.group(1), m.group(2)
    if tag and e.get('tag') != tag:
        return False
    cls = set((e.get('cls') or '').split())
    for kind, val in re.findall(r'([.#])([\w-]+)', rest):
        if (kind == '.' and val not in cls) or (kind == '#' and e.get('id') != val):
            return False
    return True


def matches(els, name, kind):
    if kind == 'css':
        return [e for e in els if css_match(e, name)]
    n = norm(name)
    out = []
    for e in els:
        texts = {norm(e.get('text')), norm(e.get('label'))}
        hit = n in texts if kind in ('role', 'button', 'link', 'tab', 'menuitem', 'textbox', 'placeholder', 'label') or kind is None \
            else any(n and n in t for t in texts)
        if kind == 'placeholder' or kind == 'label':
            hit = n == norm(e.get('label'))
        if not hit:
            continue
        if kind == 'button' and not (e.get('tag') == 'button' or e.get('role') == 'button'):
            continue
        if kind == 'link' and not (e.get('tag') == 'a' or e.get('role') == 'link'):
            continue
        if kind == 'menuitem' and e.get('role') != 'menuitem':
            continue
        out.append(e)
    return out


def region(box, frame):
    """('top'|'middle'|'bottom', 'left'|'centre'|'right') of a box's centre inside frame [x, y, w, h]."""
    cx = (box[0] + box[2] / 2 - frame[0]) / max(frame[2], 1)
    cy = (box[1] + box[3] / 2 - frame[1]) / max(frame[3], 1)
    v = 'top' if cy < 0.4 else 'bottom' if cy > 0.6 else 'middle'
    h = 'left' if cx < 0.4 else 'right' if cx > 0.6 else 'centre'
    return v, h


def says(v, h):
    return ' '.join(x for x in (v, h) if x)


def agrees(v, h, reg):
    return (v is None or v == reg[0]) and (h is None or h == reg[1])


def check(script, base):
    """[(level, section, message)] for every position phrase that is wrong, ambiguous or can't be checked."""
    els = load_explore(script, base)
    out = []
    for sec in script.get('sections', []):
        name = sec.get('name', '?')
        acts = [a for a in sec.get('actions', []) if a.get('do') in ('click', 'hover', 'highlight', 'type') and (a.get('target') or a.get('into'))]
        talk = re.sub(r'\[[^\]]+\]', '', sec.get('talk', ''))
        # where each action's cue sits in the talk (in order, like the timing does)
        pos, cur = [], 0
        for a in acts:
            i = talk.lower().find(str(a.get('on', '')).lower(), cur)
            pos.append(i if i >= 0 else None)
            if i >= 0:
                cur = i + 1
        talk_ties = {}
        for field in ('talk', 'caption'):
            text = talk if field == 'talk' else sec.get('caption', '')
            for start, end, v, h, container in phrases(text):
                quote = text[start:end]
                sent = (text.rfind('.', 0, start) + 1, (text.find('.', end) + 1) or len(text))
                act = None
                if field == 'talk':
                    near = [(abs(p - start), a) for a, p in zip(acts, pos) if p is not None and sent[0] <= p <= sent[1]]
                    act = min(near, key=lambda x: x[0])[1] if near else None
                    talk_ties[(v, h, container)] = act
                else:
                    for a in acts:
                        n, _ = target_name(a.get('target') or a.get('into'))
                        if n and norm(n) in norm(text[sent[0]:sent[1]]):
                            act = a
                    act = act or talk_ties.get((v, h, container))
                where = f'{field} "{quote}"'
                if not act:
                    out.append(('error', name, f'{where}: no click or hover near it to check the position against. '
                                               'Describe it without a position, or tie it to the action it names.'))
                    continue
                tname, kind = target_name(act.get('target') or act.get('into'))
                if not els:
                    out.append(('error', name, f'{where}: positions are checked against the explored page, and this script has '
                                               'no explore data (explore.json). Explore it first, or describe it without a position.'))
                    continue
                found = matches(els, tname, kind) if tname else []
                if not found:
                    out.append(('error', name, f'{where}: "{act.get("target") or act.get("into")}" isn\'t in the explored pages, so the '
                                               'position can\'t be checked. Explore that screen, or describe it without a position.'))
                    continue
                # explore data from before panels were logged can't show a panel: use the newer data when there is some
                if any('panel' in e for e in found):
                    found = [e for e in found if 'panel' in e]
                problems = []
                for e in found:
                    screen = [0, 0, e['vw'], e['vh']]
                    sreg = region(e['box'], screen)
                    preg = region(e['box'], e['panel']['box']) if e.get('panel') else None
                    if container and container not in SCREENISH:
                        ref = preg or sreg
                        if not agrees(v, h, ref):
                            problems.append(f'it\'s the {says(*ref)} of its {e["panel"]["kind"] if preg else "screen"}, not the {says(v, h)} ({e["shot"]})')
                    else:
                        if not agrees(v, h, sreg):
                            if preg and agrees(v, h, preg):
                                problems.append(f'on screen it\'s {says(*sreg)}; it\'s the {says(v, h)} of the panel it sits in, so say '
                                                f'that ("at the {v or h} of the list / form") ({e["shot"]})')
                            else:
                                problems.append(f'on screen it\'s {says(*sreg)}, not {says(v, h)} ({e["shot"]})')
                        elif preg and not agrees(v, h, preg) and not container:
                            problems.append(f'on screen it\'s {says(*sreg)}, but in the panel it sits in it\'s the {says(*preg)}, so a viewer '
                                            f'can read it either way: say which, for example "at the {preg[0] if v else ""} of the form" '
                                            f'({e["shot"]})'.replace('the  of', 'the side of'))
                if problems and len(problems) == len(found):
                    out.append(('error', name, f'{where} ("{tname}"): {problems[0]}.'))
    return out
