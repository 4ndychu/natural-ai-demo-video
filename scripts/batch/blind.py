"""Blind A/B/C tests inside real production (Andy, 12 Nov 2026): no separate test rounds.

Writing (config jobs.writing.blind_test): for the first `lessons` videos of a real batch, each arm (a model and an
effort) writes one draft of the video, to the same style of the day and the same explored facts. Each draft is voiced
once. The user hears them as A, B and C, shuffled, with the arm hidden, and picks one; the pick is recorded and the
picked take is the one that ships (its script and its voice take; nothing is generated again).

Planning (jobs.planning.blind_test): the same outline is planned once per arm; the plans are shown unlabelled and the
user picks one before anything is explored or written.

Which letter is which arm lives only in <batch>/blind/key.json, which nothing serves to the app. It is revealed in
the batch report once every pick of the batch is made, so one answer can't colour the next. Every pick is appended to
$NAVI_DATA/blind-picks.jsonl; `batch.py blind-results` adds them up.

An arm whose model is unavailable is left out (with a warning), never swapped for another model: a fallback would be
testing something else. With fewer than two drafts left there is nothing to compare, and the one draft just ships.

NAVI_NO_BLIND=1 switches all of it off (the tests).
"""
import json
import os
import random
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
for p in ('app', 'jobs', 'script'):
    sys.path.insert(0, os.path.join(ROOT, 'scripts', p))
import store  # noqa: E402
import jobs  # noqa: E402

LETTERS = 'ABCDE'


def cfg(kind):
    return jobs.config()[kind].get('blind_test') or {}


def on(kind, b):
    return bool(cfg(kind).get('enabled')) and len(cfg(kind).get('arms', [])) >= 2 and not os.environ.get('NAVI_NO_BLIND') and not b.get('no_blind')


def lessons_for(b):
    """The videos of this batch that get the writing test: the first `lessons` of them."""
    return b['items'][:int(cfg('writing').get('lessons', 0))] if on('writing', b) else []


def bdir(b):
    return os.path.join(store.work_dir(), 'batches', b['id'], 'blind')


def _key(b):
    return store._read(os.path.join(bdir(b), 'key.json'), {'plan': {}, 'lessons': {}})


def _save_key(b, key):
    store._write(os.path.join(bdir(b), 'key.json'), key, 0o600)


def _shuffle(arm_indexes):
    order = list(arm_indexes)
    random.SystemRandom().shuffle(order)
    return {LETTERS[i]: k for i, k in enumerate(order)}


def arm_dir(did, k):
    return os.path.join(store.demo_dir(did), 'blind', f'arm{k + 1}')


def lesson(b, did):
    return (b.get('blind') or {}).get('lessons', {}).get(did)


# ---- planning --------------------------------------------------------------------------------------------------------
def plan(bm, b):
    """Plan the batch once per arm. Returns True when plans are waiting for the user's pick (the batch stops there),
    False when there was nothing to compare (the caller plans the normal way)."""
    arms, made = cfg('planning')['arms'], []
    os.makedirs(os.path.join(bdir(b), 'plan'), exist_ok=True)
    bm.log(b, f"Planning {len(b['items'])} videos {len(arms)} ways, for you to pick from")
    for k, arm in enumerate(arms):
        try:
            e = bm.job(b, 'planning', arm=arm, videos=bm.videos_block(b), known=bm.known_block(b))
            if not e.get('data') or not isinstance(e['data'].get('videos'), list):
                raise jobs.JobError('it gave no plan that could be read')
            store._write(os.path.join(bdir(b), 'plan', f'arm{k + 1}.json'), e['data'])
            made.append(k)
        except jobs.JobError as err:
            bm.log(b, f"  WARNING: one plan is missing from the comparison ({arm['model']} / {arm['effort']}: {err})")
    if len(made) < 2:
        if made:
            shutil.copy(os.path.join(bdir(b), 'plan', f'arm{made[0] + 1}.json'), os.path.join(os.path.dirname(bdir(b)), 'plan.json'))
        return False
    key = _key(b)
    key['plan'] = _shuffle(made)
    _save_key(b, key)
    b.setdefault('blind', {})['plan'] = {'status': 'waiting', 'letters': sorted(key['plan'])}
    b['state'], b['reason'] = 'needs you', f"pick a plan: {', '.join(sorted(key['plan'])[:-1])} or {sorted(key['plan'])[-1]}"
    bm.log(b, f"{len(made)} plans are ready, unlabelled: pick one (the app's review queue, or batch.py pick-plan). Nothing is explored or written until then.")
    bm.save(b)
    return True


def pick_plan(bm, bid, letter):
    b = bm.load(bid)
    st, key = (b.get('blind') or {}).get('plan'), _key(b)
    letter = (letter or '').upper()
    if not st or st['status'] != 'waiting':
        raise ValueError('No plan is waiting for a pick in this batch.')
    if letter not in key['plan']:
        raise ValueError(f"Pick one of {', '.join(sorted(key['plan']))}.")
    arms = cfg('planning')['arms']
    shutil.copy(os.path.join(bdir(b), 'plan', f"arm{key['plan'][letter] + 1}.json"), os.path.join(os.path.dirname(bdir(b)), 'plan.json'))
    st.update(status='picked', picked=letter, t=time.time())
    _record(b, 'planning', None, letter, key['plan'], arms)
    b['state'], b['reason'] = 'writing', None
    bm.log(b, f'Plan {letter} picked.')
    _reveal_if_done(bm, b)
    bm.save(b)
    return {'picked': letter}


# ---- writing ---------------------------------------------------------------------------------------------------------
def write(bm, b, did, plan_txt, notes):
    """One draft per arm for this video, each checked. Returns True when two or more passed (the lesson then waits to
    be voiced and picked); False when the caller should write it the normal way (nothing usable came back)."""
    folder, arms, fr = store.demo_dir(did), cfg('writing')['arms'], bm.rel(store.demo_dir(did))
    code, styles = bm.step([bm.PY, os.path.join(ROOT, 'scripts', 'script', 'drafts.py'), 'styles', os.path.join(folder, 'script.template.json'), '--n', '1'])
    if code != 0 or not os.path.exists(os.path.join(folder, 'draft1.json')):
        raise jobs.JobError('the style of the day could not be drawn: ' + styles.strip()[-200:])
    base = dict(store._read(os.path.join(folder, 'draft1.json'), {}), explore='../../explore')
    passed = []
    for k, arm in enumerate(arms):
        ad = arm_dir(did, k)
        shutil.rmtree(ad, ignore_errors=True)
        store._write(os.path.join(ad, 'draft1.json'), base)
        ar, sp = bm.rel(ad), os.path.join(ad, 'script.json')
        try:
            bm.job(b, 'writing', did, arm=arm, prompt='writing_one', rules=bm.writer_rules(), plan=plan_txt, known=bm.known_block(b, did),
                   notes=jobs.attach(notes, bm.rel(notes)), styles=styles.strip(), drafts=jobs.attach(os.path.join(ad, 'draft1.json'), ar + '/draft1.json'),
                   pick_cmd=f'.venv/bin/python scripts/script/drafts.py pick {ar}/draft1.json --base {ar}', demo_dir=ar)
            if not os.path.exists(sp):
                raise jobs.JobError('its draft never passed the checker')
            if bm.check_one(b, did, sp, notes)[0]:
                raise jobs.JobError('its draft still had checker errors')
            why = bm.rehearse(b, did, sp, notes)
            if why:
                raise jobs.JobError(why)
            passed.append(k)
        except jobs.JobError as err:
            bm.log(b, f"  WARNING: one draft is missing from the comparison ({arm['model']} / {arm['effort']}: {err})")
    if not passed:
        return False
    ship = dict(store._read(os.path.join(arm_dir(did, passed[0]), 'script.json'), {}))
    ship.pop('explore', None)
    store._write(os.path.join(folder, 'script.json'), ship)   # stands in (seat, start page, cost) until the pick
    if len(passed) < 2:
        bm.log(b, '  only one draft passed, so there is nothing to compare: it ships as it is')
        return True
    key = _key(b)
    key['lessons'][did] = _shuffle(passed)
    _save_key(b, key)
    b.setdefault('blind', {}).setdefault('lessons', {})[did] = {'status': 'written', 'letters': sorted(key['lessons'][did])}
    bm.save(b)
    return True


def cost(b, did):
    """Credits still needed to voice this lesson's drafts, one take each (None: not a blind lesson any more)."""
    st = lesson(b, did)
    if not st or st['status'] not in ('written', 'waiting'):
        return None
    total = 0
    for k in _key(b)['lessons'].get(did, {}).values():
        ad = arm_dir(did, k)
        sc = store._read(os.path.join(ad, 'script.json'), None) or {}
        total += sum(len(s['talk']) for s in sc.get('sections', []) if not (
            os.path.exists(os.path.join(ad, f"{s['name']}_take1.json")) or os.path.exists(os.path.join(ad, f"{s['name']}_take1.words.json"))))
    return total


def voice(bm, b, did):
    """Each draft voiced once. Returns the letters ready to hear."""
    key, st, ready = _key(b), lesson(b, did), []
    for letter, k in sorted(key['lessons'][did].items()):
        ad = arm_dir(did, k)
        code, out = bm.step([bm.PY, os.path.join(ROOT, 'scripts', 'voice', 'generate.py'), os.path.join(ad, 'script.json'), '--out', ad, '--takes', '1', '--yes'])
        mp3 = os.path.join(store.demo_dir(did), 'blind', f'{letter}.mp3')
        if code == 0:
            code, out = bm.step([os.path.join(ROOT, '.venv', 'bin', 'ffmpeg'), '-v', 'error', '-y', '-i', os.path.join(ad, 'voice.wav'), '-q:a', '3', mp3])
        if code != 0 or not os.path.exists(mp3):
            bm.log(b, f"  WARNING: version {letter} could not be voiced ({(out.strip().splitlines() or [''])[-1][:160]}); it is left out")
            continue
        ready.append(letter)
    for letter in [x for x in key['lessons'][did] if x not in ready]:
        key['lessons'][did].pop(letter)
    _save_key(b, key)
    st.update(status='waiting', letters=ready)
    bm.save(b)
    return ready


def _req(b, did):
    return os.path.join(bdir(b), 'requests', did + '.json')


def pick(bm, bid, did, letter, auto=False):
    """The user's pick. While the batch's own runner is busy with other videos it holds the batch file, so the pick
    is left as a request (blind/requests/<video>.json) that the runner applies between two videos; with no runner
    busy it is applied at once. Either way it is the user's answer from this moment: the app shows it as picked."""
    b = bm.load(bid)
    st, key = lesson(b, did), _key(b)
    letter = (letter or '').upper()
    if not st or st['status'] != 'waiting' or os.path.exists(_req(b, did)):
        raise ValueError('That video is not waiting for a pick.')
    if letter not in key['lessons'].get(did, {}):
        raise ValueError(f"Pick one of {', '.join(sorted(key['lessons'][did]))}.")
    import runner
    rs = runner.status(bid)
    if not auto and rs['alive'] and not rs['waiting_for']:
        store._write(_req(b, did), {'letter': letter, 't': time.time()})
        return {'picked': letter, 'queued': True, 'waiting': [x for x in waiting(b) if x != did]}
    return apply(bm, bid, did, letter, auto)


def apply_requests(bm, bid):
    """Picks made while the runner was busy. Called by the runner between videos, when nothing else holds the batch."""
    b, n = bm.load(bid), 0
    for did in list((b.get('blind') or {}).get('lessons', {})):
        r = store._read(_req(b, did), None)
        if r:
            os.remove(_req(b, did))
            try:
                apply(bm, bid, did, r['letter'])
                n += 1
            except ValueError:
                pass
    return n


def apply(bm, bid, did, letter, auto=False):
    """That draft's script and its one voice take become the video's. Nothing is generated again."""
    b = bm.load(bid)
    st, key = lesson(b, did), _key(b)
    letter = (letter or '').upper()
    if not st or st['status'] != 'waiting':
        raise ValueError('That video is not waiting for a pick.')
    if letter not in key['lessons'].get(did, {}):
        raise ValueError(f"Pick one of {', '.join(sorted(key['lessons'][did]))}.")
    folder, ad = store.demo_dir(did), arm_dir(did, key['lessons'][did][letter])
    sc = dict(store._read(os.path.join(ad, 'script.json'), {}))
    sc.pop('explore', None)
    store._write(os.path.join(folder, 'script.json'), sc)
    for f in os.listdir(ad):
        if '_take1.' in f or f in ('voice.wav', 'voice_dry.wav', 'voice.json'):
            shutil.copy2(os.path.join(ad, f), os.path.join(folder, f))
    st.update(status='picked', picked=letter, t=time.time(), takes=1)
    if not auto:
        _record(b, 'writing', did, letter, key['lessons'][did], cfg('writing')['arms'])
    b.get('results', {}).pop(did, None)
    store.update_demo(did, {'progress': None})
    bm.log(b, f"\"{store.demo(did)['title']}\": version {letter} picked" + (' (the only one that could be voiced)' if auto else '') + '; it records next.')
    _reveal_if_done(bm, b)
    bm.save(b)
    return {'picked': letter, 'waiting': waiting(b)}


def waiting(b):
    """Videos still waiting for the user (a pick left as a request is an answer already)."""
    return [did for did, st in (b.get('blind') or {}).get('lessons', {}).items() if st['status'] == 'waiting' and not os.path.exists(_req(b, did))]


# ---- what the user sees (never which arm) ----------------------------------------------------------------------------
def view(b):
    """For the app's pick screen and `batch.py blind`: the plans and the lessons waiting, by letter only."""
    bl, key, out = b.get('blind') or {}, _key(b), {'plan': None, 'lessons': [], 'revealed': (b.get('blind') or {}).get('revealed')}
    if bl.get('plan'):
        out['plan'] = {'status': bl['plan']['status'], 'picked': bl['plan'].get('picked'), 'options': [
            {'letter': x, 'plan': store._read(os.path.join(bdir(b), 'plan', f"arm{key['plan'][x] + 1}.json"), {})} for x in sorted(key.get('plan', {}))]}
    for did in b['items']:
        st = bl.get('lessons', {}).get(did)
        if not st:
            continue
        opts = []
        for x in sorted(key['lessons'].get(did, {})):
            ad = arm_dir(did, key['lessons'][did][x])
            sc, vj = store._read(os.path.join(ad, 'script.json'), {}) or {}, store._read(os.path.join(ad, 'voice.json'), {}) or {}
            opts.append({'letter': x, 'audio': f'blind/{x}.mp3' if os.path.exists(os.path.join(store.demo_dir(did), 'blind', f'{x}.mp3')) else None,
                         'seconds': vj.get('duration'),
                         'sections': [{'name': s.get('name'), 'talk': s.get('talk', '').replace('[relaxed] ', ''), 'caption': s.get('caption', '')} for s in sc.get('sections', [])]})
        req = store._read(_req(b, did), None)
        out['lessons'].append({'demo': did, 'title': store.demo(did)['title'], 'status': 'picked' if req else st['status'],
                               'picked': req['letter'] if req else st.get('picked'), 'options': opts})
    return out


# ---- the record ------------------------------------------------------------------------------------------------------
def picks_path():
    return os.path.join(store.data_dir(), 'blind-picks.jsonl')


def _record(b, kind, did, letter, letters, arms):
    row = {'t': time.time(), 'date': time.strftime('%Y-%m-%d'), 'kind': kind, 'batch': b['id'], 'demo': did,
           'title': store.demo(did)['title'] if did else b['name'], 'picked_letter': letter, 'picked': arms[letters[letter]],
           'shown': [{'letter': x, **arms[k]} for x, k in sorted(letters.items())]}
    os.makedirs(os.path.dirname(picks_path()), exist_ok=True)
    with open(picks_path(), 'a') as f:
        f.write(json.dumps(row) + '\n')


def _reveal_if_done(bm, b):
    """Once every pick of the batch is made, say which arm each letter was (in the report and for the app)."""
    bl = b.get('blind') or {}
    states = [st['status'] for st in bl.get('lessons', {}).values()] + ([bl['plan']['status']] if bl.get('plan') else [])
    writing_pending = [d for d in lessons_for(b) if d not in bl.get('lessons', {}) and not (b.get('written', {}).get(d))]
    if not states or any(s != 'picked' for s in states) or writing_pending:
        return
    rows = [r for r in read_picks() if r['batch'] == b['id']]
    name = lambda a: f"{a['model']} / {a['effort']}"
    bl['revealed'] = {'picks': [{'kind': r['kind'], 'title': r['title'], 'picked_letter': r['picked_letter'], 'picked': name(r['picked']),
                                 'shown': {s['letter']: name(s) for s in r['shown']}} for r in rows], 'tally': tally(rows)}


def read_picks():
    out = []
    try:
        for line in open(picks_path()):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    except OSError:
        pass
    return out


def tally(rows=None):
    """{kind: [{arm, picked, shown}]}: how often each arm was picked out of the times it was on offer."""
    out = {}
    for r in (read_picks() if rows is None else rows):
        t = out.setdefault(r['kind'], {})
        for s in r['shown']:
            a = t.setdefault(f"{s['model']} / {s['effort']}", {'picked': 0, 'shown': 0})
            a['shown'] += 1
        t[f"{r['picked']['model']} / {r['picked']['effort']}"]['picked'] += 1
    return {k: [{'arm': a, **v} for a, v in sorted(t.items(), key=lambda x: -x[1]['picked'])] for k, t in out.items()}


def report_lines(b):
    bl = b.get('blind') or {}
    if not bl:
        return []
    lines = ['## Blind tests', '']
    if bl.get('revealed'):
        for p in bl['revealed']['picks']:
            lines.append(f"- {'Plan' if p['kind'] == 'planning' else p['title']}: you picked **{p['picked_letter']}** = {p['picked']} "
                         f"({'; '.join(f'{x} was {a}' for x, a in p['shown'].items())})")
        for kind, rows in bl['revealed']['tally'].items():
            lines += ['', f"{'Plans' if kind == 'planning' else 'Scripts'} in this batch: " + '; '.join(f"{r['arm']} picked {r['picked']} of {r['shown']}" for r in rows) + '.']
    else:
        n = len(waiting(b)) + (1 if (bl.get('plan') or {}).get('status') == 'waiting' else 0)
        made = sum(1 for st in bl.get('lessons', {}).values() if st['status'] == 'picked')
        lines.append(f"{made} pick(s) made, {n} waiting. Which model wrote which version is shown here once every pick in the batch is made.")
    return lines + ['']
