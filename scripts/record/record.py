"""NAVI Phase 3: record the browser live to the voice.

The voice leads (reference/recording-rules.md). From Phase 2's timing.json, every action gets a wall-clock start
time so that its click (or the first typed key) lands on its cue word. The recorder (agent-screenplay with NAVI's
patch) waits live for each step; the footage plays at normal speed ("realtime"), and nothing is retimed afterwards.
The recorder never gets the voice: if it did, it would hold frames to fit the audio. NAVI lays the voice track
over the finished recording at the moment the browser was told it started.

One take (Andy, 12 Nov 2026). The drawn cursor travels 0.42 to 1.05 s before a click, depending on distance, which
is only known once the target is on screen. So each click and hover is given the moment it should land ("landAt",
its word), and the recorder's cursor waits where it is and sets off exactly its travel time before that. The first
take is therefore on its words, and it is the only take: a second one is recorded only when the first would fail
the join check (an action more than 0.5 s from its word, for example a page that hung), up to --passes times, and
the better of the two is kept. (Before, every step started a fixed 0.75 s before its word, the first take was
measured, and a second take was always recorded with the measured times.)

Capture and render apart: --capture-only stops after the take(s); --finish then reads the frames for privacy, has
Recordly draw the video and runs the join checks. The batch uses this to draw one video while the next one is
being voiced and recorded.

Polish: the best take's raw browser frames and cursor log go through Recordly's own export renderer
(recorder/polish, Recordly pinned and unedited) in the chosen style: Casual (no zoom) or Recordly (Recordly's own
auto-zooms). The recorder's own drawn video is only a draft and is thrown away.

Privacy (reference/privacy.md): the demo's privacy settings blur matches inside every page before they are painted
(scripts/privacy/blur.js). The start page is checked with the blur before the first take (privacy-check.png).
After recording, every distinct frame is read with Apple's text recognition and anything still readable that matches
is blurred over its time. privacy.md / privacy.json list every blur with its time, the unsure ones first.

Seats and the action guard: the take uses the script's seat (its "seat" field, picked from the job by
scripts/seats/seats.py; else the site's default seat) and its saved login. The action guard (scripts/guard/guard.mjs,
Chrome's own request interception, set by the recorder on the whole browser) runs on every page: a blocked action ends the take and fails the
video with the reason (exit code 4, reason in report.md and guard.json). Nothing asks the user mid-run.

Join checks (recording-rules.md 7): no still screen over max_still_s (5 s); no frozen frame over 1.5 s while the
voice is silent; no cut within 1.5 s of a click (a live take has no cuts); every action within 0.5 s of its word.

Usage: .venv/bin/python scripts/record/record.py examples/test-todo-b.json output/test-todo-v4 [--passes 3]
       [--viewport 1440x810] [--name recording] [--style casual|recordly]
       .venv/bin/python scripts/record/record.py examples/test-todo-b.json output/test-todo-v4 --finish
         (finishes from the passes already recorded, for example after a later pass failed; no new recording)
       .venv/bin/python scripts/record/record.py examples/test-todo-b.json output/test-todo-v4 --restyle recordly
         (re-renders the existing take in the other style as recording-<style>.mp4; no new recording)
Output (in <voice_dir>/<name>/): scenario.json, take/ (raw frames + take.json), silent.mp4 (polished, no sound),
recording.mp4 (with the voice and room tone), report.md.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CONFIG = json.load(open(os.path.join(ROOT, 'config', 'defaults.json')))
REC = os.path.join(ROOT, 'recorder', 'agent-screenplay')
POLISH = os.path.join(ROOT, 'recorder', 'polish')
FF = os.path.join(ROOT, '.venv', 'bin', 'ffmpeg')
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'audio'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'privacy'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'seats'))
import privacy  # noqa: E402
import seats  # noqa: E402

GUARD = os.path.join(ROOT, 'scripts', 'guard', 'guard.mjs')

OPENING_DRIFT_S = 0.2  # the cursor starts moving this soon when the first action is later than the first second
VOICE_START = 0.6      # seconds after the first step before the voice starts (the page has already loaded and settled)
LEAD = {'click': 0.75, 'hover': 0.75, 'type_into': 0.75, 'type': 0.05, 'press': 0.05}
FIND_LEAD = 1.6        # a click or hover starts this long before its word to find its target; the cursor itself sets
                       # off later, its own travel time (0.42 to 1.05 s) before the word (the recorder's landAt)
LATE = 0.25            # a step that still landed later than this needed longer to find its target (a hidden checkbox
                       # the recorder waits 2 s for, a slow page): if a second take is recorded, and whenever this
                       # video is recorded again, that step starts earlier by what the first take measured
LANDS = ('click', 'hover', 'type_into')
END_AFTER_VOICE = -0.55  # a last, empty step this long after the last word (before it, here): with the recorder's
                         # own 0.2 s hold and 1 s tail after its last step, the video ends about 0.7 s after the voice,
                         # as a quiet page always did (the to-do clip: 44.5 s before and after)
MAX_DRIFT = 0.5        # recording-rules.md: every action within 0.5 s of its word
STYLE = {'cursor': 'macos', 'accent': '#1d1d1f', 'click': 'none',  # never a ring (Andy, Phase 3)
         'captions': False, 'padding': 0, 'radius': 0,
         'shadow': False, 'cards': False, 'background': '#ffffff'}
# zoom_on_click "none": the frame stays the same size the whole video (Andy, 2026-11-08: zooms in a casual demo look tacky)
ZOOM = {'none': 1.0, 'gentle': 1.6}


def target(t):
    """NAVI targets to the recorder's: placeholder=/text=/role=/label= pass through, anything else is CSS."""
    if re.match(r'^(placeholder|text|role|label|testid|css|at)=', t):
        return t
    return 'css=' + t.replace(' >> ', ' ').replace("'", '"')


def session_for(url, script=None):
    """The saved login of the script's seat ($NAVI_DATA/logins/<site>/<seat>.json, made from Settings > Logins),
    or None. Read only: NAVI never logs in itself (the user does, in the one visible window)."""
    s = dict(script or {})
    if not s.get('site'):
        s['site'] = url
    return seats.for_script(s)['login']


def guard_for(script, out):
    """The action guard's settings for this take (written to guard.json next to it). On every site: one without a
    guard pack still gets the payment rules (config/guard/_payments.json), and on a video with two or more logins
    its changes are blocked (guard.mjs). Blocked actions are logged to guard-log.jsonl."""
    cfg = seats.guard_config(script, os.path.join(out, 'guard-log.jsonl'))
    path = os.path.join(out, 'guard.json')
    json.dump(cfg, open(path, 'w'), indent=1)
    return {'module': GUARD, 'config': path}


class GuardBlocked(Exception):
    pass


def member_view(script, out):
    """A buyer's view filmed with the owner's login (recording-rules.md 13e), or None. From the site's pack
    ("member_view"): the site's own preview-as-a-buyer is set before the first frame (a cookie, on a copy of the
    login kept only for this take), owner-only controls are blurred (scripts/privacy/member_view.js), and pages the
    owner only sees as an editor fail the video."""
    s = seats.for_script(script)
    if s['view'] != 'member':
        return None
    pack_path = os.path.join(ROOT, 'config', 'guard', f"{s['site']}.json")
    mv = json.load(open(pack_path)).get('member_view') if os.path.exists(pack_path) else None
    if not mv:
        return None
    preview = (script.get('seat') or {}).get('preview_as')
    if not s['business'] or not preview or not s['login']:
        sys.exit(f"A member view on {s['site']} needs the business, a saved login and \"preview_as\" (the product whose "
                 'buyers the video shows) in the script\'s "seat".')
    state = json.load(open(s['login']))
    name = mv['preview_cookie'].format(business_id=s['business']['id'])
    state['cookies'] = [c for c in state.get('cookies', []) if c.get('name') != name] + [
        {'name': name, 'value': preview, 'domain': s['site'], 'path': '/', 'expires': -1, 'httpOnly': False,
         'secure': True, 'sameSite': 'Lax'}]
    session = os.path.join(out, 'member-session.json')
    with open(os.open(session, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f:
        json.dump(state, f)
    import atexit
    atexit.register(lambda: os.path.exists(session) and os.remove(session))  # a copy of the login: never kept
    start = next((a.get('target', '') for x in script.get('sections', []) for a in x.get('actions', []) if a.get('do') == 'goto'), '')
    m = re.match(r'^(?:[a-z]+://)?[^/]+(/[^/?#]+/)', start)
    cfg = {'ownerOnly': mv.get('owner_only', []), 'avoid': mv.get('avoid'), 'current': m.group(1) if m else None}
    js = 'window.__NAVI_MEMBER__ = ' + json.dumps(cfg) + ';\n' + open(os.path.join(ROOT, 'scripts', 'privacy', 'member_view.js')).read()
    return {'session': session, 'js': js, 'preview': preview}


def member_avoided(take):
    """The reason, when a member-view take opened a page the owner only sees as an editor."""
    hit = next((r for r in take.get('reports', []) if r.get('kind') == 'member-view' and r.get('event') == 'avoid'), None)
    return f"the video opens {hit['page']}, and {hit['reason']}" if hit else None


def guard_blocks(out):
    """Every action the guard blocked in this folder's takes."""
    path = os.path.join(out, 'guard-log.jsonl')
    if not os.path.exists(path):
        return []
    return [e for e in (json.loads(l) for l in open(path) if l.strip()) if e.get('kind') == 'blocked']


def blocked_reason(b):
    return f"NAVI's action guard blocked {b['why']} ({b['method']} {b['host']}{b['path'][:80]}, on {b.get('page', '')[:80]})"


def build(script, timing, leads, viewport=None, style_name=None, private=None, guard=None, member=None):
    url = next((a['target'] for a in timing['actions'] if a['do'] == 'goto'), None)
    if not url:
        sys.exit('The script needs a goto action at the start of the first section (the page the video opens on).')
    rc = CONFIG['recording']
    style = rc['styles'][style_name or rc.get('style', 'casual')]
    if not style.get('built'):
        sys.exit(f"The {style['label']} isn't wired up yet. Use the Casual style for now.")
    vw, vh = viewport or rc['viewport']
    steps, start_at, plan = [{'pause': 0.05}], [0.0], []  # the patch starts its clock only when step 1 has a time
    land_at = [None]
    # The opening is never still (Andy, 2026-11-10): when the first action's cursor would set off after the first
    # second, the cursor starts drifting toward the middle of the page at OPENING_DRIFT_S.
    first = next((a for a in timing['actions'] if a['do'] != 'goto'), None)
    if first is not None:
        # decided from the default lead only, so every pass has the same steps (leads are keyed by step number)
        first_kind = {'type': 'type_into' if first.get('into') else 'type', 'press': 'press', 'hover': 'hover',
                      'highlight': 'hover'}.get(first['do'], 'click')
        if VOICE_START + first['t'] - LEAD[first_kind] > 1.0 - OPENING_DRIFT_S:
            steps.append({'hover': f'at={round(vw * 0.5)},{round(vh * 0.42)}'})
            start_at.append(OPENING_DRIFT_S)
            land_at.append(None)
    opened = False
    for a in timing['actions']:
        if a['do'] == 'goto' and not opened:      # the page the video opens on (the scenario's url)
            opened = True
            continue
        if a['do'] == 'goto':
            # a later page, for example the second site of a video on two logins (X, then Google Sheets): opened at
            # its word, in the same tab, with the same browser and every login it holds
            st, kind = {'goto': a['target']}, 'goto'
        elif a['do'] == 'click':
            st, kind = {'click': target(a['target'])}, 'click'
        elif a['do'] == 'type':
            st = {'type': a['text']}
            kind = 'type'
            if a.get('into'):
                st['into'], kind = target(a['into']), 'type_into'
            if a.get('then') == 'Enter':
                st['submit'] = True
        elif a['do'] == 'press':
            st, kind = {'press': a['key']}, 'press'
        elif a['do'] in ('hover', 'highlight'):
            # NAVI never adds a spotlight overlay (recording-rules.md 9): "highlight" means the cursor goes there
            st, kind = {'hover': target(a['target'])}, 'hover'
        else:
            sys.exit(f"Don't know how to record '{a['do']}'.")
        lead = max(FIND_LEAD, leads.get(len(steps), 0)) if kind in LANDS else LEAD.get(kind, 0.0)
        steps.append(st)
        start_at.append(round(max(VOICE_START + a['t'] - lead, 0.0), 3))
        land_at.append(round(VOICE_START + a['t'], 3) if kind in LANDS else None)
        plan.append({'step': len(steps) - 1, 'cue': a['on'], 'cue_t': a['t'], 'kind': kind, 'lead': lead, 'do': a['do']})
    # The take ends on the voice's schedule (Andy, 11 Nov 2026: the whop clip sat still for 5 s at the end). Without
    # a step after it, the last action waits up to 4 s for the page to go quiet, which busy apps never do, then 1 s
    # more; a last empty step just after the last word cuts that wait short (the recorder's waits end when the next
    # step is due), so the video ends about 0.7 s after the voice, on any site (longer left the to-do clip still for over 1.5 s).
    voice_end = max((w['end'] for w in timing.get('words', [])), default=None)
    if voice_end is not None and VOICE_START + voice_end + END_AFTER_VOICE > start_at[-1]:
        steps.append({'pause': 0.05})
        start_at.append(round(VOICE_START + voice_end + END_AFTER_VOICE, 3))
        land_at.append(None)
    scenario = {'name': script.get('title', 'demo'), 'url': url, 'viewport': {'width': vw, 'height': vh},
                # a video filmed on a phone ("device": "iPhone 15"): Playwright's phone profile, which sets the size
                **({'device': script['device']} if script.get('device') else {}),
                'realtime': True, 'startAt': start_at, 'landAt': land_at, 'typingSpeed': 1.3, 'scale': rc.get('capture_scale', 2),
                'style': {**STYLE, 'maxZoom': ZOOM[style.get('zoom_on_click', 'none')]},
                'initScript': privacy.init_script(private or privacy.settings(script)) + ('\n' + member['js'] if member else ''),
                'output': {'width': 1920, 'height': 1080, 'fps': rc.get('fps', 60), 'path': 'silent.mp4'}, 'steps': steps}
    session = member['session'] if member else session_for(url, script)
    if session:
        scenario['auth'] = {'storageState': session}
    if guard:
        scenario['guard'] = guard
    return scenario, plan


def cleanup(script):
    """In a business the user marked as a test, delete the products NAVI created ("NAVI test ..."), so every take
    starts clean (recording-rules.md 13c). Does nothing anywhere else: never in a real business."""
    biz = privacy.test_business(script)
    if not biz or not biz.get('cleanup'):
        return
    r = subprocess.run(['node', os.path.join(ROOT, 'scripts', 'cleanup', 'test_products.mjs'), '--business', biz['match']],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"cleanup in {biz.get('name')}: failed: {(r.stdout + r.stderr).strip()[-300:]}", flush=True)
        return
    res = json.loads(r.stdout.strip().splitlines()[-1])
    print(f"cleanup in {res['business']}: deleted {len(res['deleted'])} test product(s)", flush=True)


def seat_args(s):
    """The explorer's login arguments for a seat (seats.for_script): every login of a two-login video, --logged-out
    for a video shown logged out, the seat's own login otherwise. Without one of these the explorer falls back to the
    site's default (owner) login, so a logged-out video must always say so."""
    if len(s['seats']) > 1:
        return ['--seat', s['seat'], '--seats', ','.join(f"{x['site']}:{x['seat']}" for x in s['seats'])]
    if s['seat'] == seats.LOGGED_OUT or not s['login']:
        return ['--logged-out']
    return ['--seat', s['seat']]


def prepare(script, folder):
    """The video's ready state, made off camera (<folder>/prepare.json: a start page and explore-style steps), after
    the cleanup and before every take, so a video that needs something to exist starts from it without depending on
    another video (Andy, 13 Nov 2026). Headless, the seat's login, the action guard on. Stops the take if a step fails."""
    path = os.path.join(folder, 'prepare.json')
    if not os.path.exists(path):
        return
    p = json.load(open(path))
    s = seats.for_script(script)
    out = os.path.join(folder, 'prepare-run')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    json.dump(p['steps'], open(os.path.join(out, 'steps.json'), 'w'))
    cmd = ['node', os.path.join(ROOT, 'scripts', 'explore', 'explore.mjs'), '--url', p['url'], '--site', s['site'], '--out', out,
           '--steps', os.path.join(out, 'steps.json')] + seat_args(s)
    r = subprocess.run(cmd, capture_output=True, text=True)
    ex = json.load(open(os.path.join(out, 'explore.json'))) if os.path.exists(os.path.join(out, 'explore.json')) else {}
    bad = [x for x in ex.get('screens', []) if x.get('error')]
    if r.returncode != 0 or bad or ex.get('blocked'):
        why = (bad[0]['step'] + ': ' + bad[0]['error'][:160]) if bad else (r.stdout + r.stderr).strip()[-200:]
        raise RecorderFailed(f"The ready state for this video couldn't be made off camera ({why}).")
    print(f"ready state made off camera ({len(p['steps'])} steps)", flush=True)


class RecorderFailed(Exception):
    pass


def record(scenario, out):
    path = os.path.join(out, 'scenario.json')
    json.dump(scenario, open(path, 'w'), indent=1)
    # --take-only: the recorder's own draft video was thrown away anyway (Recordly's renderer draws the real one from
    # the take), and making it took as long again as the recording itself (12 Nov 2026: 170 to 210 s on a 167 s video)
    r = subprocess.run(['node', os.path.join(REC, 'dist', 'cli.js'), 'record', '--take-only', path], cwd=out, capture_output=True, text=True)
    log = r.stdout + r.stderr
    open(os.path.join(out, 'recorder.log'), 'a').write(log + '\n----\n')
    blocks = guard_blocks(out)
    if blocks:                     # a blocked action fails the video, whatever the recorder made of it
        raise GuardBlocked(blocked_reason(blocks[0]))
    if r.returncode != 0:
        raise RecorderFailed('The recorder failed:\n' + log[-2000:])
    takes = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(out, '.screenplay')) for f in fs if f == 'take.json']
    newest = max(takes, key=os.path.getmtime)
    take = json.load(open(newest))
    if member_avoided(take):
        raise MemberAvoided(member_avoided(take))
    return take, os.path.dirname(newest), log


class MemberAvoided(Exception):
    pass


def polish(take_dir, style_name, silent):
    """Recordly's own export renderer, on the take's raw frames and cursor log (recorder/polish)."""
    if not os.path.isdir(os.path.join(POLISH, 'node_modules', 'pixi.js')):
        sys.exit('The polish step needs pixi.js: run "npm install" in recorder/polish (about 81 MB, inside the repo).')
    b = subprocess.run(['node', os.path.join(POLISH, 'build.mjs')], capture_output=True, text=True)
    if b.returncode != 0:
        sys.exit('The polish step would not build:\n' + (b.stdout + b.stderr)[-2000:])
    r = subprocess.run(['node', os.path.join(POLISH, 'render.mjs'), take_dir, silent, '--style', style_name,
                        '--fps', str(CONFIG['recording'].get('fps', 60))], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('The polish step failed:\n' + (r.stdout + r.stderr)[-2000:])
    info = json.loads(r.stdout.strip().splitlines()[-1])
    if info['page_errors']:
        sys.exit('The polish step reported errors: ' + '; '.join(info['page_errors']))
    return info


def leads_key(timing):
    """The same actions on the same targets (whatever their times): what a learned lead belongs to."""
    import hashlib
    return hashlib.sha1(json.dumps([[x['do'], x.get('target'), x.get('into'), x.get('text')] for x in timing['actions']]).encode()).hexdigest()[:16]


def drift(take, plan):
    steps = {s['index']: s for s in take['steps']}
    zero = steps[0]['start']
    rows = []
    for p in plan:
        s = steps[p['step']]
        at = s.get('actionAt', s['start'])
        landed = at - zero - VOICE_START          # on the voice track's clock
        rows.append({**p, 'landed': round(landed, 3), 'off': round(landed - p['cue_t'], 3),
                     'measured_lead': round(at - s['start'], 3), 'late_start': round(s['start'] - zero - (VOICE_START + p['cue_t'] - p['lead']), 3)})
    return zero, rows


def room_tone_track(seconds, sr=44100):
    import dsp
    from treat import add_room_tone, synth_room_tone
    tone = synth_room_tone(sr)
    return add_room_tone([0.0] * int(seconds * sr), tone, sr, tone_lufs=CONFIG['audio_edit']['room_tone_lufs'], fade_in=0.0)


def duration(video):
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', subprocess.run([FF, '-i', video], capture_output=True, text=True).stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def mux(out, silent, voice_wav, offset, name='recording.mp4'):
    import dsp
    dur = duration(silent)
    tone = os.path.join(out, 'roomtone.wav')
    dsp.write_wav(tone, room_tone_track(dur + 1), 44100)
    final = os.path.join(out, name)
    ms = int(round(offset * 1000))
    subprocess.run([FF, '-loglevel', 'error', '-y', '-i', silent, '-i', voice_wav, '-i', tone, '-filter_complex',
                    f'[1:a]adelay={ms}|{ms}[v];[v][2:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:{dur:.3f}[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', final], check=True)
    return final, dur


def activity(take):
    """Moments something visibly moves, on the recording's clock (the same as the take's). Pixel-difference detectors can't see a 44 px cursor or a few typed letters in an
    unzoomed 1080p frame, so this uses what the recorder logged: cursor travel, typing, clicks and page repaints."""
    spans = [(t, t) for t, _ in take['source']['frames']]               # the page repainted
    for s in take['steps']:
        if 'travelStart' in s:
            spans.append((s['travelStart'], s.get('actionAt', s['end'])))  # cursor moving
        if 'actionAt' in s:
            spans.append((s['actionAt'], s.get('actionEnd', s['actionAt']) + 0.4))  # click ripple / typing
    return sorted(spans)


def stills(spans, dur, longer_than):
    out, last = [], 0.0
    for a, b in spans + [(dur, dur)]:
        if a - last > longer_than:
            out.append((round(last, 2), round(a, 2)))
        last = max(last, b)
    return out


def checks(take, dur, offset, timing, rows):
    words = [(w['start'] + offset, w['end'] + offset) for w in timing['words']]
    def voiced(a, b):
        return sum(max(0, min(b, e) - max(a, s)) for s, e in words) / max(b - a, 1e-6)
    spans = activity(take)
    still = stills(spans, dur, CONFIG['recording']['max_still_s'])
    frozen_silent = [(a, b) for a, b in stills(spans, dur, CONFIG['recording']['max_frozen_frame_s']) if voiced(a, b) < 0.5]
    late = [r for r in rows if abs(r['off']) > MAX_DRIFT]
    return {'still_over_5s': still, 'frozen_while_silent': frozen_silent, 'cuts': [], 'actions_off_by_over_0.5s': late,
            'pass': not still and not frozen_silent and not late}


def restyle(a, out):
    """Re-render the kept take in another style (no new recording, no credits)."""
    rep = json.load(open(os.path.join(out, 'report.json')))
    take_dir = os.path.join(out, 'take')
    silent = os.path.join(out, f'silent-{a.restyle}.mp4')
    info = polish(take_dir, a.restyle, silent)
    final, dur = mux(out, silent, os.path.join(a.voice_dir, 'voice.wav'), rep['voice_offset_s'], f'recording-{a.restyle}.mp4')
    os.remove(silent)
    zooms = len(info['zoomRegions'])
    print(f"{CONFIG['recording']['styles'][a.restyle]['label']}: {final} ({dur:.1f} s, {zooms} zoom{'s' * (zooms != 1)})")


def fail_reason(out, reason):
    """A member-view take that opened an owner-only page fails this video, with the reason."""
    json.dump({'reason': reason}, open(os.path.join(out, 'blocked.json'), 'w'), indent=1)
    open(os.path.join(out, 'report.md'), 'w').write(f"# Recording report\n\n**Failed: {reason}.**\n\n"
        "A buyer's view stays on pages a buyer sees the same way; change the script to stop before this page.\n")
    print(f"FAILED: {reason}", flush=True)
    sys.exit(4)


def fail_blocked(out, block, script):
    """A blocked action fails this video, with the reason (never a question to the user mid-run)."""
    reason = blocked_reason(block)
    json.dump({'blocked': block, 'reason': reason}, open(os.path.join(out, 'blocked.json'), 'w'), indent=1)
    open(os.path.join(out, 'report.md'), 'w').write(f"# Recording report\n\n**Failed: {reason}.**\n\n"
        "Nothing was changed: the request was stopped before it left the browser. Change the script, or the job if "
        "this change is really wanted (in a real business a change is only allowed when the job asks for it).\n")
    print(f"FAILED: {reason}", flush=True)
    sys.exit(4)


STAGES = []      # [(what, seconds)]: where the recording step's time goes (report.json "stages"; Andy, 12 Nov 2026)
_T = [time.time()]


def lap(what):
    now = time.time()
    STAGES.append([what, round(now - _T[0], 1)])
    _T[0] = now


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('voice_dir')
    ap.add_argument('--passes', type=int, default=2, help='the most takes: a second one only when the first fails the join check')
    ap.add_argument('--capture-only', action='store_true', help='stop after the take(s); --finish draws the video later')
    ap.add_argument('--viewport', help='browser size, e.g. 1440x810 (default from config/defaults.json)')
    ap.add_argument('--name', default='recording', help='folder name inside voice_dir (default "recording")')
    ap.add_argument('--style', choices=sorted(CONFIG['recording']['styles']), help='video style (default from config/defaults.json)')
    ap.add_argument('--restyle', choices=sorted(CONFIG['recording']['styles']), help='re-render the existing take in this style')
    ap.add_argument('--finish', action='store_true', help='finish from the passes already recorded in the folder (no new recording)')
    a = ap.parse_args()
    out = os.path.abspath(os.path.join(a.voice_dir, a.name))
    if a.restyle:
        return restyle(a, out)
    style_name = a.style or CONFIG['recording'].get('style', 'casual')
    script = json.load(open(a.script))
    timing = json.load(open(os.path.join(a.voice_dir, 'timing.json')))
    if timing['problems']:
        sys.exit('Fix the timing problems first (scripts/timing/timing.py).')
    viewport = [int(x) for x in a.viewport.split('x')] if a.viewport else None
    if not a.finish:
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
    private = privacy.settings(script)
    private['typed'], warn = privacy.typed([(f'"{x["on"]}"', x['text']) for x in timing['actions'] if x['do'] == 'type'], private)
    private['warnings'] += warn
    for w in private['warnings']:
        print('privacy:', w, flush=True)
    start = next(x['target'] for x in timing['actions'] if x['do'] == 'goto')
    seat = seats.for_script(script)
    session = seat['login']
    where = f" in {seat['business']['name']}" if seat['business'] else ''
    print(f"seat: {seat['seat']}{where}; login: {'saved' if session else 'none (logged out)'}", flush=True)
    if len(seat['seats']) > 1:
        # a site the video shows logged out on purpose (seat "logged-out") needs no login
        missing = [x['site'] for x in seat['seats'] if not x['login'] and x['seat'] != seats.LOGGED_OUT]
        print('logins: ' + ' + '.join(f"{x['site']} ({x['seat']})" for x in seat['seats']) + ', in one browser', flush=True)
        if missing:
            sys.exit('Not logged in: ' + ', '.join(missing) + '. Log in from Settings > Logins first.')
    guard = None if a.finish else guard_for(script, out)
    member = None if a.finish else member_view(script, out)
    if member:
        print(f"member view: previewing as a buyer of {member['preview']}; owner-only controls blurred", flush=True)
    if guard:
        packs = [x['site'] for x in seat['seats'] if os.path.exists(os.path.join(ROOT, 'config', 'guard', f"{x['site']}.json"))]
        print(f"action guard: on ({', '.join(packs) or 'payments only: no guard pack for ' + seat['site']})", flush=True)
    cap = os.path.join(out, 'capture.json')
    if a.finish and os.path.exists(cap):      # the start page was checked when the take was captured
        check = {'hits': [None] * json.load(open(cap)).get('check_hits', 0)}
        _T[0] = time.time()
    else:
        check = privacy.check_page(start, private, os.path.join(out, 'privacy-check.png'), viewport or CONFIG['recording']['viewport'],
                                   member['session'] if member else session, guard=guard, extra_js=member['js'] if member else '',
                                   device=script.get('device'))
        if guard_blocks(out):
            fail_blocked(out, guard_blocks(out)[0], script)
        print(f"privacy: start page checked, {len(check['hits'])} blurred (privacy-check.png)", flush=True)
        lap('privacy check of the start page')
    leads, history = {}, []
    leads_file = os.path.join(a.voice_dir, 'record-leads.json')      # learned on an earlier take of this same video
    if os.path.exists(leads_file):
        saved = json.load(open(leads_file))
        if saved.get('key') == leads_key(timing):
            leads = {int(k): v for k, v in saved['leads'].items()}
    if a.finish:
        # finish from passes already recorded (take-pass<n>/, kept with their plan): no new recording
        for n in range(1, 10):
            kept = os.path.join(out, f'take-pass{n}')
            if not os.path.exists(os.path.join(kept, 'take.json')):
                continue
            pf = os.path.join(kept, 'plan.json')
            if os.path.exists(pf):
                plan = json.load(open(pf))
            elif n == 1:
                plan = build(script, timing, {}, viewport, style_name, private)[1]
            else:
                continue
            take = json.load(open(os.path.join(kept, 'take.json')))
            zero, rows = drift(take, plan)
            history.append({'pass': n, 'worst_off_s': max(abs(r['off']) for r in rows), 'rows': rows, 'zero': zero, 'take': take, 'dir': kept})
            print(f"pass {n} (kept): worst action {history[-1]['worst_off_s']:.2f} s from its word", flush=True)
        if not history:
            sys.exit('No finished passes to use (take-pass<n>/ with take.json) in ' + out)
    if not a.finish:
        cleanup(script)                                   # a test business starts every take clean
        lap('clean test business')
    for n in range(1, 0 if a.finish else a.passes + 1):
        try:
            prepare(script, a.voice_dir)                  # the ready state, off camera, on the clean business
        except RecorderFailed as e:
            cleanup(script)
            if not history:
                sys.exit(str(e))
            print(f'pass {n}: {e}; keeping the best earlier pass.', flush=True)
            break
        lap('ready state, off camera') if os.path.exists(os.path.join(a.voice_dir, 'prepare.json')) else None
        scenario, plan = build(script, timing, leads, viewport, style_name, private, guard, member)
        try:
            take, take_dir, log = record(scenario, out)
        except GuardBlocked:
            cleanup(script)
            fail_blocked(out, guard_blocks(out)[0], script)
        except MemberAvoided as e:
            fail_reason(out, str(e))
        except RecorderFailed as e:
            cleanup(script)
            if not history:
                sys.exit(str(e))
            # a retake failed (an app that changed between takes, a pop-up): keep the best pass already recorded
            print(f'pass {n} failed; keeping the best earlier pass. {str(e).splitlines()[-1][:300]}', flush=True)
            break
        zero, rows = drift(take, plan)
        worst = max(abs(r['off']) for r in rows)
        kept = os.path.join(out, f'take-pass{n}')
        shutil.move(take_dir, kept)                       # the next pass would overwrite the frames
        json.dump(plan, open(os.path.join(kept, 'plan.json'), 'w'))
        if os.path.exists(os.path.join(out, 'silent.mp4')):   # a draft from an older recorder build
            os.remove(os.path.join(out, 'silent.mp4'))
        history.append({'pass': n, 'worst_off_s': worst, 'rows': rows, 'zero': zero, 'take': take, 'dir': kept})
        print(f'pass {n}: worst action {worst:.2f} s from its word', flush=True)
        lap(f'take {n} (live, real time)')
        cleanup(script)
        lap('clean test business')
        for r in rows:              # what this take measured about slow-to-find targets, for the next take of this video
            if r['off'] > LATE and r['late_start'] < 0.05 and r['kind'] in LANDS:
                leads[r['step']] = round(r['measured_lead'] + 0.35, 3)
        json.dump({'key': leads_key(timing), 'leads': leads}, open(leads_file, 'w'))
        if worst <= MAX_DRIFT:      # within the join check's limit: this take is the video
            break
        print(f'pass {n}: an action is over {MAX_DRIFT} s from its word, which fails the join check' + ('; recording once more' if n < a.passes else ''), flush=True)
    if a.capture_only:
        json.dump({'stages': STAGES, 'check_hits': len(check['hits'])}, open(os.path.join(out, 'capture.json'), 'w'))
        print(f"captured: {len(history)} take(s); best is {min(h['worst_off_s'] for h in history):.2f} s from its words at worst. Finish with --finish.", flush=True)
        sys.exit(0)
    if a.finish:      # the capture's own timings come first in the report
        STAGES[:0] = (json.load(open(os.path.join(out, 'capture.json'))).get('stages', []) if os.path.exists(os.path.join(out, 'capture.json')) else [])
    best = min(history, key=lambda h: h['worst_off_s'])
    zero, rows, take = best['zero'], best['rows'], best['take']
    take_dir = os.path.join(out, 'take')
    shutil.move(best['dir'], take_dir)
    for h in history:
        shutil.rmtree(h['dir'], ignore_errors=True)
    shutil.rmtree(os.path.join(out, '.screenplay'), ignore_errors=True)
    lap('keep the best take')
    scan = privacy.scan_take(take_dir, private)          # writes take/post-blur.json, used by the polish step
    lap('privacy scan of the frames')
    silent = os.path.join(out, 'silent.mp4')
    info = polish(take_dir, style_name, silent)
    lap('draw the video (Recordly renderer)')
    priv = privacy.review(out, take, scan, private, {'blurred': len(check['hits']), 'screenshot': 'privacy-check.png'})
    offset = zero + VOICE_START
    final, dur = mux(out, silent, os.path.join(a.voice_dir, 'voice.wav'), offset)
    # the polished video runs on the take's own clock (the voice goes in at zero + VOICE_START on that clock)
    res = checks(take, dur, offset, timing, rows)
    lap('add the voice, join checks')
    history = [{k: v for k, v in h.items() if k not in ('take', 'dir')} for h in history]
    style = CONFIG['recording']['styles'][style_name]
    report = {'passes': history, 'voice_offset_s': round(offset, 3), 'duration_s': round(dur, 2), 'checks': res, 'video': final,
              'privacy': {'blurred': sum(not b['unsure'] for b in priv['blurs']), 'unsure': sum(b['unsure'] for b in priv['blurs']), 'file': 'privacy.json'},
              'style': style_name, 'polish': {k: info[k] for k in ('settings', 'zoomRegions', 'source', 'cursor_shapes', 'render_s')},
              'stages': [[w, t] for w, t in STAGES]}
    json.dump(report, open(os.path.join(out, 'report.json'), 'w'), indent=1)
    zooms = len(info['zoomRegions'])
    lines = [f"# Recording report", '', f"Video: `{final}` ({dur:.1f} s). Voice starts at {offset:.2f} s. Passes: {len(history)} (used pass {best['pass']}).", '',
             f"Style: {style['label']} (Recordly's renderer; {zooms} zoom{'s' * (zooms != 1)}; browser frames {info['source'][0]}x{info['source'][1]}; cursor shapes {info['cursor_shapes']}).", '',
             '| Cue | Word at | Action landed | Off by | Kind |', '|---|---|---|---|---|']
    lines += [f"| {r['cue']} | {r['cue_t']:.2f} s | {r['landed']:.2f} s | {r['off']:+.2f} s | {r['do']} |" for r in rows]
    lines += ['', f"Still screen over 5 s: {res['still_over_5s'] or 'none'}",
              f"Frozen over 1.5 s while the voice is silent: {res['frozen_while_silent'] or 'none'}",
              f"Cuts: none (one continuous live take)",
              f"Actions more than 0.5 s from their word: {[r['cue'] for r in res['actions_off_by_over_0.5s']] or 'none'}",
              '', f"Privacy ({privacy.CONFIG['presets'][private['preset']]['label']}): {sum(not b['unsure'] for b in priv['blurs'])} blurred, "
              f"{sum(b['unsure'] for b in priv['blurs'])} unsure, {scan['frames_read']} frames read after recording. See privacy.md."
              + ''.join(f"\n- Warning: {w}" for w in private['warnings']),
              '', '**Join checks: ' + ('PASS' if res['pass'] else 'FAIL') + '**']
    open(os.path.join(out, 'report.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    sys.exit(0 if res['pass'] else 1)


if __name__ == '__main__':
    main()
