"""Rehearse a script before any credits are spent (recording-rules.md 14): play every action once, quickly, in the
recorder's own browser, with the script's login, the action guard and the privacy blur, and say which steps the
recorder could not do. Nothing is filmed and no voice is needed.

A script can pass every check on paper and still name a button in a way the recorder can't find ("role=link
[name='Products']" where the link's name is drawn by an icon): that used to show up only after the voice was
paid for, as a failed take (12 Nov 2026). Now it shows up here, with what the page does offer.

In a business the user marked as a test, NAVI's own "NAVI test" products are cleared before and after, as for a
take. In a real business the action guard blocks changes exactly as it would in the take, and the rehearsal says so.

  .venv/bin/python scripts/record/rehearse.py <script.json> [--json] [--realtime]

--realtime (Andy, 14 Nov 2026: "rehearse at real-time speed before voicing"): the recorder's own take mode, on the
take's clock: each action starts at its word (the video's real word timings from timing.json when it has been
voiced, else estimated at the approved voice's measured pace), the cursor travels and waits as it does on camera,
so hover cards, pop-ups and slow loads behave as they will in the take. Filmed at 1x and thrown away. It takes as
long as the video. A take failed only this way before (FG01, 13 Nov 2026: a hover card covered the next target).
Exit code 0: every step can be done. 1: at least one can't (they are listed, with the section and cue word).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import record  # noqa: E402


def rehearse(script_path):
    script = json.load(open(script_path))
    actions, t = [], 0.0
    for sec in script.get('sections', []):
        for a in sec.get('actions', []):
            actions.append({'section': sec['name'], 'on': a.get('on'), 'do': a['do'], 'target': a.get('target'), 'text': a.get('text'),
                            'key': a.get('key'), 'into': a.get('into'), 'then': a.get('then'), 't': round(t, 2)})
            t += 0.1
    out = tempfile.mkdtemp(prefix='navi-rehearse-')
    try:
        private = record.privacy.settings(script)
        guard, member = record.guard_for(script, out), record.member_view(script, out)
        scenario, plan = record.build(script, {'actions': actions, 'words': []}, {}, None, None, private, guard, member)
        for k in ('startAt', 'landAt', 'realtime'):      # as fast as the pages allow
            scenario.pop(k, None)
        first = next((i for i, x in enumerate(actions) if x['do'] == 'goto'), None)   # the start page; later gotos are steps
        by_step = {p['step']: a for p, a in zip(plan, [x for i, x in enumerate(actions) if i != first])}
        path = os.path.join(out, 'scenario.json')
        json.dump(scenario, open(path, 'w'))
        record.cleanup(script)
        try:
            record.prepare(script, os.path.dirname(os.path.abspath(script_path)))   # the ready state the takes start from
        except record.RecorderFailed as e:
            record.cleanup(script)
            return {'ok': False, 'problems': [{'section': None, 'on': None, 'why': str(e)}], 'steps': 0}
        r = subprocess.run(['node', os.path.join(record.REC, 'dist', 'cli.js'), 'check', '--json', path], cwd=out, capture_output=True, text=True)
        record.cleanup(script)
        blocks = record.guard_blocks(out)
        try:
            rep = json.loads(r.stdout[r.stdout.index('{'):])
        except ValueError:
            return {'ok': False, 'problems': [{'section': None, 'on': None, 'why': 'the rehearsal did not run: ' + (r.stdout + r.stderr).strip()[-300:]}], 'steps': 0}
        problems = []
        for s in rep.get('steps', []):
            if s.get('ok') or s.get('error') == 'not reached':
                continue
            a = by_step.get(s['index'], {})
            problems.append({'section': a.get('section'), 'on': a.get('on'), 'do': a.get('do'), 'target': a.get('target') or a.get('into') or a.get('text'),
                             'why': s.get('error', ''), 'page_offers': (s.get('candidates') or [])[:12], 'page': rep.get('url')})
        if blocks:
            problems.append({'section': None, 'on': None, 'why': 'the action guard blocked it: ' + record.blocked_reason(blocks[0])})
        done = sum(1 for s in rep.get('steps', []) if s.get('ok'))
        return {'ok': bool(rep.get('ok')) and not problems, 'problems': problems, 'steps': len(rep.get('steps', [])), 'done': done}
    finally:
        shutil.rmtree(out, ignore_errors=True)


def words_for(script, folder):
    """Word timings for the take's clock: the voiced video's own (timing.json, when its talk hasn't changed since),
    else estimated per section at the approved voice's measured pace (check_script.spoken_at), with a short gap
    between sections. Returns ([{w, start, end, sec}], 'real' | 'estimated')."""
    import re
    tj = os.path.join(folder, 'timing.json')
    talks = [s.get('talk', '') for s in script.get('sections', [])]
    if os.path.exists(tj):
        t = json.load(open(tj))
        vj = os.path.join(folder, 'voice.json')
        voiced = [s.get('talk', '') for s in json.load(open(vj)).get('sections', [])] if os.path.exists(vj) else None
        if t.get('words') and (voiced is None or voiced == talks or len(t.get('sections', [])) == len(talks)):
            return t['words'], 'real'
    sys.path.insert(0, os.path.join(record.ROOT, 'scripts', 'script'))
    from check_script import spoken_at
    words, t0 = [], 0.0
    for k, talk in enumerate(talks):
        raw = re.sub(r'\[[^\]]*\]', ' ', talk).split()
        for i, w in enumerate(raw):
            st = t0 + spoken_at(raw, i)
            words.append({'w': re.sub(r'^[^\w]+|[^\w]+$', '', w), 'start': round(st, 3), 'end': round(st + 0.24, 3), 'sec': k})
        t0 += (spoken_at(raw, len(raw)) if raw else 0) + 0.45
    return words, 'estimated'


def actions_on_clock(script, words):
    """Every action at its word, as timing.py pins them (cue matched in order inside its section)."""
    sys.path.insert(0, os.path.join(record.ROOT, 'scripts', 'timing'))
    from timing import match
    out, problems = [], []
    for k, sec in enumerate(script.get('sections', [])):
        sw = [w for w in words if w.get('sec') == k]
        if not sw:
            continue
        cursor = 0
        for a in sec.get('actions', []):
            row = {'section': sec['name'], 'on': a.get('on'), 'do': a['do'], 'target': a.get('target'), 'text': a.get('text'),
                   'key': a.get('key'), 'into': a.get('into'), 'then': a.get('then')}
            if a.get('on') in ('start', 'end'):
                row['t'] = sw[0]['start'] if a['on'] == 'start' else sw[-1]['end']
            else:
                i, n = match(a['on'], sw, cursor)
                if i is None:
                    problems.append({'section': sec['name'], 'on': a.get('on'), 'do': a['do'], 'target': a.get('target'),
                                     'why': f"the cue word \"{a.get('on')}\" isn't in this section's talk"})
                    continue
                row['t'], cursor = sw[i]['start'], i + n
            out.append(row)
    return out, problems


def rehearse_realtime(script_path):
    """The take, on its own clock, without the voice or the footage (see the top of this file)."""
    import re
    script = json.load(open(script_path))
    folder = os.path.dirname(os.path.abspath(script_path))
    words, source = words_for(script, folder)
    actions, problems = actions_on_clock(script, words)
    if problems:
        return {'ok': False, 'problems': problems, 'steps': 0, 'done': 0, 'clock': source}
    out = tempfile.mkdtemp(prefix='navi-rehearse-rt-')
    try:
        private = record.privacy.settings(script)
        guard, member = record.guard_for(script, out), record.member_view(script, out)
        leads_file = os.path.join(folder, 'record-leads.json')      # what an earlier take of this video learned
        leads = {}
        if os.path.exists(leads_file):
            saved = json.load(open(leads_file))
            if saved.get('key') == record.leads_key({'actions': actions}):
                leads = {int(k): v for k, v in saved['leads'].items()}
        scenario, plan = record.build(script, {'actions': actions, 'words': words}, leads, None, None, private, guard, member)
        scenario['scale'] = 1                                         # same timing and behaviour, a quarter of the pixels
        scenario['output'] = dict(scenario['output'], path='rehearsal.mp4')
        first = next((i for i, x in enumerate(actions) if x['do'] == 'goto'), None)
        by_step = {p['step']: a for p, a in zip(plan, [x for i, x in enumerate(actions) if i != first])}
        path = os.path.join(out, 'scenario.json')
        json.dump(scenario, open(path, 'w'))
        record.cleanup(script)
        try:
            record.prepare(script, folder)
        except record.RecorderFailed as e:
            record.cleanup(script)
            return {'ok': False, 'problems': [{'section': None, 'on': None, 'why': str(e)}], 'steps': 0, 'done': 0, 'clock': source}
        r = subprocess.run(['node', os.path.join(record.REC, 'dist', 'cli.js'), 'record', '--take-only', path], cwd=out,
                           capture_output=True, text=True)
        record.cleanup(script)
        log = (r.stdout or '') + (r.stderr or '')
        problems = []
        blocks = record.guard_blocks(out)
        if blocks:
            problems.append({'section': None, 'on': None, 'why': 'the action guard blocked it: ' + record.blocked_reason(blocks[0])})
        for m in re.finditer(r'Step (\d+) \(([^)]*)\) failed: ([^\n]+)', log):
            a = by_step.get(int(m.group(1)) - 1, {})
            problems.append({'section': a.get('section'), 'on': a.get('on'), 'do': a.get('do'), 'target': a.get('target') or a.get('into') or a.get('text'),
                             'why': f"in real time, step {m.group(1)} ({m.group(2)}) failed: {m.group(3)[:400]}"})
        if r.returncode != 0 and not problems:
            problems.append({'section': None, 'on': None, 'why': 'the real-time rehearsal did not finish: ' + log.strip()[-400:]})
        # late landings: the join check's rule (an action more than 0.5 s from its word) on the rehearsal's own step times
        steps_done = len(re.findall(r'^▶ \d+/', log, re.M))
        return {'ok': not problems, 'problems': problems, 'steps': len(scenario['steps']), 'done': steps_done, 'clock': source}
    finally:
        shutil.rmtree(out, ignore_errors=True)


if __name__ == '__main__':
    res = rehearse_realtime(sys.argv[1]) if '--realtime' in sys.argv else rehearse(sys.argv[1])
    if '--json' in sys.argv:
        print(json.dumps(res, indent=1))
    elif res['ok']:
        print(f"Rehearsal passed{' in real time (' + res['clock'] + ' word timings)' if res.get('clock') else ''}: all {res['steps']} steps can be done.")
    else:
        print(f"Rehearsal stopped: {res.get('done', 0)} of {res['steps']} steps done, then:")
        for p in res['problems']:
            print(f"- section \"{p.get('section')}\", the action on \"{p.get('on')}\" ({p.get('do')} {p.get('target')}): {p['why']}")
            if p.get('page_offers'):
                print('  the page offers: ' + '; '.join(str(c) for c in p['page_offers']))
    sys.exit(0 if res['ok'] else 1)
