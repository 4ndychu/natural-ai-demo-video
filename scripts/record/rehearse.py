"""Rehearse a script before any credits are spent (recording-rules.md 14): play every action once, quickly, in the
recorder's own browser, with the script's login, the action guard and the privacy blur, and say which steps the
recorder could not do. Nothing is filmed and no voice is needed.

A script can pass every check on paper and still name a button in a way the recorder can't find ("role=link
[name='Products']" where the link's name is drawn by an icon): that used to show up only after the voice was
paid for, as a failed take (12 Nov 2026). Now it shows up here, with what the page does offer.

In a business the user marked as a test, NAVI's own "NAVI test" products are cleared before and after, as for a
take. In a real business the action guard blocks changes exactly as it would in the take, and the rehearsal says so.

  .venv/bin/python scripts/record/rehearse.py <script.json> [--json]
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
        by_step = {p['step']: a for p, a in zip(plan, [x for x in actions if x['do'] != 'goto'])}
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


if __name__ == '__main__':
    res = rehearse(sys.argv[1])
    if '--json' in sys.argv:
        print(json.dumps(res, indent=1))
    elif res['ok']:
        print(f"Rehearsal passed: all {res['steps']} steps can be done.")
    else:
        print(f"Rehearsal stopped: {res.get('done', 0)} of {res['steps']} steps done, then:")
        for p in res['problems']:
            print(f"- section \"{p.get('section')}\", the action on \"{p.get('on')}\" ({p.get('do')} {p.get('target')}): {p['why']}")
            if p.get('page_offers'):
                print('  the page offers: ' + '; '.join(str(c) for c in p['page_offers']))
    sys.exit(0 if res['ok'] else 1)
