"""NAVI app state, the engine side of the local app (Phase 7): settings, demos, saved logins, the ElevenLabs key's
status, and "Your data". Everything here is the user's own and stays on their Mac:

  NAVI_DATA (default ~/Library/Application Support/NAVI)   settings.json, logins/<site>.json (browser sessions)
  NAVI_WORK (default <repo>/output/demos)                  one folder per demo: demo.json, script.json, the voice,
                                                           the recording; batches/<id>/batch.json
  Keychain, service "navi-elevenlabs"                      the ElevenLabs key (never read into state, never logged)

Finished videos are exported to the folder the user names and are never touched from here.
"""
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CONFIG = json.load(open(os.path.join(ROOT, 'config', 'defaults.json')))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'script'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'seats'))
import seats  # noqa: E402


def data_dir():
    return os.path.expanduser(os.environ.get('NAVI_DATA') or '~/Library/Application Support/NAVI')


def work_dir():
    return os.path.expanduser(os.environ.get('NAVI_WORK') or os.path.join(ROOT, CONFIG.get('app', {}).get('work_dir', 'output/demos')))


def key_service():
    return os.environ.get('NAVI_KEY_SERVICE') or 'navi-elevenlabs'


def _read(path, default):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default


def _write(path, obj, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.part'
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    if mode:
        os.chmod(tmp, mode)
    os.replace(tmp, path)


# ---- settings ---------------------------------------------------------------------------------------------------
def defaults():
    on, ex, rc = CONFIG['on_screen'], CONFIG['export'], CONFIG['recording']
    return {'voice': CONFIG.get('app', {}).get('default_voice', 'alex'), 'kind': 'saas', 'privacy_preset': CONFIG['privacy']['preset'],
            'hide_words': [], 'video_style': rc['style'], 'captions': on['captions'], 'caption_look': on['caption_look'],
            'corner_label': on['corner_label'], 'corner_text': on['corner_text'], 'export_to': ex['folder'],
            'preview_720p': ex.get('preview_720p', False), 'speed_copy': ex['speed_copy']['speed'] if ex['speed_copy']['on'] else None,
            'voice_model': 'v4', 'sliders': {}, 'privacy_custom': {},
            # batches: the most one may spend without asking, and whether it starts without the Go click
            'credit_limit': CONFIG['app']['batch']['credit_limit'], 'auto_go': False}


CHOICES = {'kind': ['saas', 'course', 'tour'], 'privacy_preset': list(CONFIG['privacy']['presets']),
           'video_style': list(CONFIG['recording']['styles']), 'captions': CONFIG['on_screen']['captions_options'],
           'caption_look': CONFIG['on_screen']['caption_look_options'], 'corner_label': CONFIG['on_screen']['corner_options'],
           'voice_model': ['v4', 'v3']}
PRIVACY_ITEMS = ('email', 'phone', 'names', 'address', 'money', 'customers', 'counts', 'usage', 'prices', 'dates')


def settings():
    return {**defaults(), **_read(os.path.join(data_dir(), 'settings.json'), {})}


def check_setting(k, v):
    d = defaults()
    if k not in d:
        raise ValueError(f'Unknown setting "{k}".')
    if k in CHOICES and v not in CHOICES[k]:
        raise ValueError(f'{k} must be one of {CHOICES[k]}.')
    if k == 'hide_words' and not (isinstance(v, list) and all(isinstance(w, str) for w in v)):
        raise ValueError('hide_words must be a list of words.')
    if k == 'speed_copy' and v is not None:
        lo, hi = CONFIG['export']['speed_copy']['range']
        if not (isinstance(v, (int, float)) and lo <= v <= hi):
            raise ValueError(f'speed_copy must be off (null) or between {lo} and {hi}.')
    if k == 'export_to':
        p = os.path.abspath(os.path.expanduser(str(v)))
        if p == ROOT or p.startswith(ROOT + os.sep):
            raise ValueError("Exports can't go inside NAVI's own folder.")
    if k == 'credit_limit' and not (isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 10_000_000):
        raise ValueError('credit_limit must be a whole number of credits.')
    if k == 'auto_go' and not isinstance(v, bool):
        raise ValueError('auto_go must be true or false.')
    if k == 'voice' and v not in CONFIG['voices']:
        raise ValueError(f'Unknown voice "{v}".')
    if k == 'sliders':
        rng = {n: (d['min'], d['max']) for n, d in CONFIG['sliders'].items() if isinstance(d, dict) and 'min' in d}
        if not isinstance(v, dict) or any(not isinstance(x, (int, float)) for x in v.values()):
            raise ValueError('sliders must be numbers by name.')
        for n, x in v.items():
            if n in rng and not rng[n][0] <= x <= rng[n][1]:
                raise ValueError(f'{n} must be between {rng[n][0]} and {rng[n][1]}.')
    if k == 'privacy_custom' and not (isinstance(v, dict) and set(v) <= set(PRIVACY_ITEMS) and all(isinstance(x, bool) for x in v.values())):
        raise ValueError('privacy_custom must say true or false per category.')


def set_settings(patch):
    for k, v in patch.items():
        check_setting(k, v)
    cur = _read(os.path.join(data_dir(), 'settings.json'), {})
    cur.update(patch)
    _write(os.path.join(data_dir(), 'settings.json'), cur)
    return settings()


# ---- the ElevenLabs key: status only, never the key -------------------------------------------------------------
_key_cache = {'t': 0, 'v': None}


def _get_key():
    if os.environ.get('NAVI_ELEVENLABS_KEY') and key_service() == 'navi-elevenlabs':
        return os.environ['NAVI_ELEVENLABS_KEY'].strip(), 'environment'
    if sys.platform == 'darwin':
        r = subprocess.run(['security', 'find-generic-password', '-s', key_service(), '-w'], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip(), 'Keychain'
    return None, None


def _api(path, key):
    req = urllib.request.Request('https://api.elevenlabs.io' + path, headers={'xi-api-key': key})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {'error': type(e).__name__}


def key_status(fresh=False):
    """{'stored', 'where', 'works', 'credits_left', 'credits_limit', 'plan', 'resets', 'problem'}. Cached for a minute."""
    if not fresh and _key_cache['v'] and time.time() - _key_cache['t'] < 60:
        return _key_cache['v']
    key, where = _get_key()
    st = {'stored': bool(key), 'where': where, 'works': False, 'credits_left': None, 'credits_limit': None, 'plan': None,
          'resets': None, 'problem': None if key else 'No key stored yet.'}
    if key:
        code, sub = _api('/v1/user/subscription', key)
        if code == 200:
            st.update(works=True, credits_limit=sub.get('character_limit'), plan=sub.get('tier'),
                      credits_left=(sub.get('character_limit') or 0) - (sub.get('character_count') or 0),
                      resets=sub.get('next_character_count_reset_unix'))
        elif code == 401 and _api('/v2/voices?page_size=1', key)[0] == 200:
            st.update(works=True, problem="The key works but isn't allowed to read your credits (give it \"User: read\").")
        else:
            st['problem'] = "Couldn't reach ElevenLabs." if code == 0 else f'ElevenLabs refused the key (HTTP {code}).'
    _key_cache.update(t=time.time(), v=st)
    return st


def credits_left():
    """Credits left, or None if unknown. NAVI_FAKE_CREDITS simulates a balance (tests, the low-credit pause)."""
    fake = os.environ.get('NAVI_FAKE_CREDITS')
    if fake is not None:
        return int(fake)
    return key_status(fresh=True)['credits_left']


def test_key(key):
    """Check a key with ElevenLabs without storing it. Returns {'result': ok | bad | offline, credits_left, ...}.
    The app's Test key uses this, and the key is saved to the Keychain only when it works."""
    key = (key or '').strip()
    if not re.fullmatch(r'[A-Za-z0-9_\-]{20,200}', key):
        return {'result': 'bad'}
    code, sub = _api('/v1/user/subscription', key)
    if code == 200:
        return {'result': 'ok', 'credits_left': (sub.get('character_limit') or 0) - (sub.get('character_count') or 0),
                'credits_limit': sub.get('character_limit')}
    if code == 401 and _api('/v2/voices?page_size=1', key)[0] == 200:
        return {'result': 'ok', 'credits_left': None, 'problem': "The key works but can't read your credits (give it \"User: read\")."}
    return {'result': 'offline' if code == 0 else 'bad'}


def test_and_store_key(key):
    r = test_key(key)
    if r['result'] == 'ok':
        store_key(key, verify=False)
        r['key'] = key_status(fresh=True)
    return r


def store_key(key, verify=True):
    """Store the key in the Keychain. It goes to `security` on its stdin, never on a command line or into a log."""
    key = (key or '').strip()
    if not re.fullmatch(r'[A-Za-z0-9_\-]{20,200}', key):
        raise ValueError("That doesn't look like an ElevenLabs key (it starts with sk_ and has no spaces).")
    if sys.platform != 'darwin':
        raise ValueError('The Keychain is macOS only. On Linux, set NAVI_ELEVENLABS_KEY instead.')
    cmd = f'add-generic-password -U -a "{os.environ.get("USER", "navi")}" -s {key_service()} -l "NAVI ElevenLabs key" -w {key}\n'
    r = subprocess.run(['security', '-i'], input=cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError("The Keychain didn't accept the key.")
    _key_cache['v'] = None
    return key_status(fresh=True) if verify else {'stored': True}


def remove_key():
    r = subprocess.run(['security', 'delete-generic-password', '-s', key_service()], capture_output=True, text=True)
    _key_cache['v'] = None
    return r.returncode == 0


# ---- saved logins (browser sessions per site) ---------------------------------------------------------------
def site_of(url):
    m = re.match(r'^(?:[a-z]+://)?([^/:?#]+)', url.strip().lower())
    if not m:
        raise ValueError('Not a web address.')
    return m.group(1).removeprefix('www.')


def login_file(site, seat=None):
    """The seat's saved session ($NAVI_DATA/logins/<site>/<seat>.json; scripts/seats/seats.py)."""
    if not re.fullmatch(r'[a-z0-9.-]+', site or ''):
        raise ValueError('Not a site name.')
    return seats.login_file(site, seat)


def login_status():
    """The last live check of every login ($NAVI_DATA/login-status.json, written by scripts/seats/check_logins.mjs)."""
    return _read(os.path.join(data_dir(), 'login-status.json'), {})


_checking = {'proc': None, 'started': 0}


def logins_checking():
    p = _checking['proc']
    return bool(p and p.poll() is None)


def check_logins(site=None, seat=None, wait=False):
    """Check every login live, headless (scripts/seats/check_logins.mjs). In the background unless `wait`."""
    if logins_checking():
        return {'checking': True}
    cmd = ['node', os.path.join(ROOT, 'scripts', 'seats', 'check_logins.mjs')]
    if site:
        cmd += ['--site', site]
    if seat:
        cmd += ['--seat', seat]
    if wait:
        r = subprocess.run(cmd, capture_output=True, text=True)
        return {'checking': False, 'results': json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 and r.stdout.strip() else []}
    _checking.update(proc=subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), started=time.time())
    return {'checking': True}


def logins():
    """Every login: one per site and seat ({site, seat, label, account, businesses, home, saved, status, checked}),
    including seats not logged in yet. status: working / needs login / unreachable (checked live) / unchecked."""
    d = os.path.join(data_dir(), 'logins')
    out, seen = [], set()
    for s in seats.seats():
        seen.add((s['site'], s['seat']))
        out.append({'site': s['site'], 'seat': s['seat'], 'label': s['label'], 'account': s['account'],
                    'businesses': s['businesses'], 'home': s['home'], 'saved': _saved(s['file']) if s['saved'] else None})
    for entry in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, entry)
        if entry.endswith('.json'):                    # a login saved before seats: the site's default seat
            site, seat, f = entry[:-5], seats.default_seat(entry[:-5]), p
            if (site, seat) not in seen:
                out.append({'site': site, 'seat': seat, 'label': seat.title(), 'saved': _saved(f)})
                seen.add((site, seat))
        elif os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                if f.endswith('.json') and (entry, f[:-5]) not in seen:
                    out.append({'site': entry, 'seat': f[:-5], 'label': f[:-5].title(), 'saved': _saved(os.path.join(p, f))})
    st = login_status()
    for l in out:
        l.setdefault('businesses', [])
        l.setdefault('home', f"https://{l['site']}/")
        c = st.get(f"{l['site']}/{l['seat']}")
        if not l['saved']:
            l['status'], l['checked'] = 'needs login', None
        elif c and c.get('checked', 0) >= os.path.getmtime(login_file(l['site'], l['seat'])) - 1:
            l['status'], l['checked'] = c['status'], c['checked']   # a check older than the last login doesn't count
        else:
            l['status'], l['checked'] = 'unchecked', None
    return out


def _saved(path):
    return time.strftime('%d %b %Y', time.localtime(os.path.getmtime(path)))


def start_login(url, seat=None):
    """Open a visible browser on the site for the user to log in themselves (to the given seat). The session is saved
    when they close it."""
    site = site_of(url)
    path = login_file(site, seat)
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    proc = subprocess.Popen(['node', os.path.join(ROOT, 'recorder', 'agent-screenplay', 'dist', 'cli.js'), 'login',
                             url if '://' in url else 'https://' + url, '--out', path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {'site': site, 'seat': seat or seats.default_seat(site), 'pid': proc.pid}


def forget_login(site, seat=None):
    """Forget one seat's login, or every login for the site when no seat is given."""
    paths = [login_file(site, seat)] if seat else [os.path.join(data_dir(), 'logins', site + '.json')] + \
        [os.path.join(data_dir(), 'logins', site, f) for f in (os.listdir(os.path.join(data_dir(), 'logins', site))
                                                              if os.path.isdir(os.path.join(data_dir(), 'logins', site)) else [])]
    gone = False
    for p in paths:
        if os.path.exists(p):
            os.remove(p)
            gone = True
    return gone


# ---- demos ------------------------------------------------------------------------------------------------------
STEPS = ['Script', 'Voice', 'Privacy', 'Record', 'Review', 'Export']


def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:40] or 'demo'


def demo_dir(did):
    if not re.fullmatch(r'[a-z0-9-]+', did or ''):
        raise ValueError('Not a demo id.')
    return os.path.join(work_dir(), did)


def pick_seat(site, title, what):
    """The seat a new video records in, picked from the job's own words (scripts/seats/seats.py), or None for a
    site without seats."""
    try:
        site_name = seats.site_of(site)
    except ValueError:
        return None
    if not seats.config().get(site_name, {}).get('seats'):
        return None
    p = seats.pick(site_name, f'{title}. {what}')
    return {k: p[k] for k in ('seat', 'view', 'business', 'allow', 'why')}


def new_demo(title, site='', kind=None, length_min=None, audience=None, what='', batch=None, **extra):
    s = settings()
    if site and 'seat' not in extra:
        extra['seat'] = pick_seat(site, title, what)
    did = f'{slug(title)}-{secrets.token_hex(2)}'
    d = {'id': did, 'title': title, 'site': site, 'what': what, 'kind': kind or s['kind'], 'length_min': length_min,
         'audience': audience, 'voice': s['voice'], 'batch': batch, 'created': time.time(), 'updated': time.time(),
         'script_approved': False, 'review': None, 'marks': [], 'blur_decisions': {}, 'exports': [], 'progress': None,
         'settings': {}, **extra}
    _write(os.path.join(demo_dir(did), 'demo.json'), d)
    return demo(did)


DEMO_FIELDS = {'title', 'site', 'what', 'kind', 'length_min', 'audience', 'voice', 'script_approved', 'review', 'marks',
               'blur_decisions', 'exports', 'progress', 'settings', 'batch', 'hidden', 'request', 'seat', 'test'}
APP_EDITABLE = {'title', 'site', 'what', 'kind', 'length_min', 'audience', 'voice', 'settings', 'hidden'}


def update_demo(did, patch):
    bad = set(patch) - DEMO_FIELDS
    if bad:
        raise ValueError(f'Unknown demo fields: {sorted(bad)}')
    for k, v in (patch.get('settings') or {}).items():
        check_setting(k, v)
    p = os.path.join(demo_dir(did), 'demo.json')
    d = _read(p, None)
    if d is None:
        raise ValueError('No such demo.')
    d.update(patch)
    d['updated'] = time.time()
    _write(p, d)
    if patch.get('test'):                     # approved as a test, not for real use: never counts in the variety history
        _mark_real(did, False)
    elif (patch.get('review') == 'approved' or patch.get('exports')) and not d.get('test'):
        _mark_real(did)
    return demo(did)


def _mark_real(did, real=True):
    """An approved or exported video counts in the variety history from now on (scripts/script/variety.py mark_real);
    test and dev runs never get here, so they don't restrict real lessons. A demo marked test (approved only as a
    test) is taken out again: real=False."""
    sc = _read(os.path.join(demo_dir(did), 'script.json'), None)
    if not sc:
        return
    sd = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'script')
    if sd not in sys.path:
        sys.path.insert(0, sd)
    import variety
    variety.mark_real(sc, real=real)


def demo(did):
    """A demo with everything the app shows, worked out from the files that exist."""
    folder = demo_dir(did)
    d = _read(os.path.join(folder, 'demo.json'), None)
    if d is None:
        raise ValueError('No such demo.')
    f = lambda *p: os.path.join(folder, *p)
    script = _read(f('script.json'), None)
    rep = _read(f('recording', 'report.json'), None)
    priv = _read(f('recording', 'privacy.json'), None)
    check = None
    if script:
        from check_script import check as check_script
        issues = check_script(script, folder)
        check = {'errors': sum(i['level'] == 'error' for i in issues), 'warnings': sum(i['level'] == 'warning' for i in issues)}
    blurs = []
    for b in (priv or {}).get('blurs', []):
        dec = d['blur_decisions'].get(b['id'])
        blurs.append({**b, 's': dec or b.get('s', '')})
    voice = _read(f('voice.json'), None)
    win = {w['section']: w for w in (voice or {}).get('sections', [])}
    takes = CONFIG['app']['batch']['takes']
    have = lambda n, k: os.path.exists(f(f'{n}_take{k}.json')) or (os.path.exists(f(f'{n}_take{k}.mp3')) and os.path.exists(f(f'{n}_take{k}.words.json')))
    clean = lambda t: re.sub(r'\s+', ' ', re.sub(r'\[[^\]]*\]', '', t or '')).strip()
    secs = []
    for s in (script or {}).get('sections', []):
        w = win.get(s['name'])
        words = len(clean(s.get('talk')).split())
        secs.append({'name': s['name'], 'title': s.get('title') or s['name'].replace('-', ' ').capitalize(), 'talk': clean(s.get('talk')),
                     'caption': s.get('caption', ''), 'start': w['start'] if w else None,
                     'seconds': round(w['end'] - w['start'], 2) if w else round(max(3.0, words / 2.6), 1),
                     'cost': len(s.get('talk') or '') * takes})
    seat_src = dict(script) if script else {'site': d.get('site') or '', 'sections': [], 'seat': d.get('seat')}
    if not seat_src.get('seat') and d.get('seat'):
        seat_src['seat'] = d['seat']
    try:
        seat = seats.describe(seat_src) if seat_src.get('site') and (seat_src.get('seat') or seats.config().get(seats.site_of(seat_src['site']))) else None
    except ValueError:
        seat = None
    d.update({
        'seat': seat,
        'script_sections': secs,
        'voice_cost': sum(len(s.get('talk') or '') for s in (script or {}).get('sections', []) for k in range(1, takes + 1) if not have(s['name'], k)),
        'video': 'recording/recording.mp4' if os.path.exists(f('recording', 'recording.mp4')) else None,
        'settings': {**settings(), **d.get('settings', {})},
        'written': bool(script) and check['errors'] == 0,
        'script_check': check,
        'sections': len(script['sections']) if script else 0,
        'voiced': os.path.exists(f('voice.json')),
        'timed': os.path.exists(f('timing.json')),
        'recorded': bool(rep),
        'length_s': rep['duration_s'] if rep else None,
        'checks_pass': rep['checks']['pass'] if rep else None,
        'blurs': blurs,
        'privacy_reminder': (priv or {}).get('reminder'),
        'unsure_blurs': sum(1 for b in blurs if b.get('unsure') and not b['s']),
        'exported': bool(d.get('exports')),
    })
    step = 0 if not d['written'] or not d['script_approved'] else 1 if not d['voiced'] else 3 if not d['recorded'] \
        else 4 if d['review'] != 'approved' else 5
    d['step'], d['step_name'] = step, STEPS[step]
    d['status'] = d['progress'] or ('Exported' if d['exported'] else 'Ready to export' if d['review'] == 'approved'
                                     else 'Ready to watch' if d['recorded'] else 'Recording next' if d['voiced']
                                     else 'Script approved' if d['script_approved'] else 'Script ready to read' if d['written']
                                     else 'Script has problems' if script else 'Writing script')
    return d


def demos():
    w = work_dir()
    out = []
    for name in sorted(os.listdir(w)) if os.path.isdir(w) else []:
        if os.path.exists(os.path.join(w, name, 'demo.json')):
            try:
                d = demo(name)
            except ValueError:
                continue
            if not d.get('hidden'):
                out.append(d)
    return sorted(out, key=lambda d: -d['updated'])


def batches():
    d = os.path.join(work_dir(), 'batches')
    out = [_read(os.path.join(d, b, 'batch.json'), {}) for b in sorted(os.listdir(d))] if os.path.isdir(d) else []
    out = [b for b in out if b and not b.get('hidden')]
    sys.path.insert(0, os.path.join(ROOT, 'scripts', 'batch'))
    mac = None
    for b in out:
        if b.get('state') in ('writing', 'ready', 'needs you', 'approved') and not b.get('started'):   # the Go screen
            mac = mac or mac_load()
            b['mac'] = mac
        if os.path.exists(os.path.join(d, b['id'], 'runner.json')):   # its own background job: alive, what it is doing, where it paused
            import runner
            b['runner'] = runner.status(b['id'])
        if b.get('blind'):      # the blind A/B/C picks, by letter only: which model made which is never sent to the app
            sys.path.insert(0, os.path.join(ROOT, 'scripts', 'batch'))
            import blind
            b['blind_view'] = blind.view(b)
    return out


def live_frame(did):
    """The newest browser frame of a recording in progress (Watch live), or None. The frames are the recorder's own
    capture of the page, so the in-page privacy blur is already on them; the frame scan after recording still runs."""
    root = os.path.join(demo_dir(did), 'recording', '.screenplay')
    best, now = None, time.time()
    for dp, _, files in os.walk(root) if os.path.isdir(root) else []:
        jpgs = [x for x in files if x.endswith('.jpg')] if os.path.basename(dp) == 'frames' else []
        if not jpgs:
            continue
        f = os.path.join(dp, max(jpgs))            # frames are numbered in order: f000001.jpg, f000002.jpg ...
        t = os.path.getmtime(f)
        if now - t < 15 and (best is None or t > best[0]):
            best = (t, f)
    return best[1] if best else None


def tools_ready():
    """Recording tools are installed: NAVI's Python, ffmpeg and the patched recorder."""
    return all(os.path.exists(os.path.join(ROOT, p)) for p in ('.venv/bin/python', '.venv/bin/ffmpeg', 'recorder/agent-screenplay/dist/cli.js'))


# The apps that are NAVI's own tools or the system, never named as something to quit
NOT_HEAVY = {'T3 Code (Beta)', 'T3 Code', 'Claude', 'Terminal', 'iTerm', 'Ghostty', 'Finder', 'Activity Monitor'}


def mac_load():
    """How busy the Mac is right now, for the Go screen and the warning before a batch:
    {load, cores, busy, quiet_under, heavy: [{app, cpu}], line}. `heavy`: apps the user runs that a recording
    competes with: any app using more than heavy_cpu % of a core (plus any named in config heavy_apps, empty by
    default). NAVI's own browser and tools are never on it."""
    b = CONFIG['app']['batch']
    load1 = os.getloadavg()[0]
    try:
        cores = int(subprocess.run(['sysctl', '-n', 'hw.ncpu'], capture_output=True, text=True).stdout.strip() or 8)
    except (OSError, ValueError):
        cores = os.cpu_count() or 8
    cpu = {}
    try:
        out = subprocess.run(['ps', '-Ao', 'pcpu=,comm='], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.TimeoutExpired):
        out = ''
    sync = 0.0
    for line in out.splitlines():
        m = re.match(r'\s*([\d.]+)\s+(.*)$', line)
        if not m:
            continue
        if re.search(r'/(fileproviderd|bird|cloudd)$', m.group(2)):      # iCloud Drive syncing: can't be quit, only waited for
            sync += float(m.group(1))
            continue
        a = re.search(r'(?:^|/)Applications/(?:[^/]+/)*?([^/]+)\.app(?:/|$)', m.group(2))
        if a and a.group(1) not in NOT_HEAVY:
            cpu[a.group(1)] = cpu.get(a.group(1), 0.0) + float(m.group(1))
    named = [n for n in b.get('heavy_apps', []) if n in cpu]
    busy_apps = [n for n, v in cpu.items() if v >= b.get('heavy_cpu', 25) and n not in named]
    heavy = [{'app': n, 'cpu': round(cpu[n])} for n in sorted(named + busy_apps, key=lambda n: -cpu[n])]
    quiet = b['quiet_load']
    busy = load1 >= quiet
    names = [h['app'] for h in heavy]
    lst = (', '.join(names[:-1]) + ' and ' + names[-1]) if len(names) > 1 else (names[0] if names else '')
    syncing = sync >= b.get('heavy_cpu', 25)
    sync_line = ' iCloud Drive is busy syncing too: let it finish first.' if syncing else ''
    if busy:
        line = (f"Your Mac is busy (load {load1:.0f}; recordings come out best under {quiet:g})."
                + (f" Quit {lst} before Go." if lst else '' if syncing else ' Close what you can before Go.') + sync_line)
    else:
        line = f"Your Mac is quiet (load {load1:.1f})." + (f" Still, quit {lst} before Go: they slow a recording down when they wake up." if lst else '') + sync_line
    return {'load': round(load1, 1), 'cores': cores, 'busy': busy, 'quiet_under': quiet, 'heavy': heavy, 'icloud_syncing': syncing, 'line': line}


def jobs_state():
    """Each job's model and effort, for the read-only list in Settings (config/defaults.json "jobs")."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts', 'jobs'))
    import jobs
    try:
        cfg = jobs.config()
    except jobs.JobError as e:
        return {'jobs': [], 'job_warnings': [str(e)]}
    return {'jobs': [{'job': j, 'label': jobs.LABELS[j], 'model': cfg[j]['model'], 'effort': cfg[j]['effort'], 'fallback': cfg[j]['fallback']} for j in jobs.JOBS],
            'job_warnings': jobs.warnings(cfg)}


def state():
    return {'settings': settings(), 'choices': CHOICES, 'tools_ready': tools_ready(), 'voices': CONFIG['voices'], 'sliders': CONFIG['sliders'],
            'privacy': {'presets': CONFIG['privacy']['presets']}, 'key': key_status(), 'logins': logins(), 'logins_checking': logins_checking(), 'demos': demos(),
            'batches': batches(), 'steps': STEPS, **jobs_state()}


# ---- "Your data": look first, then delete with a token ------------------------------------------------------------
_pending = {}


def _size(p):
    if os.path.isfile(p):
        return os.path.getsize(p)
    return sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(p) for f in fs) if os.path.isdir(p) else 0


def plan_delete(what):
    """What would go, without deleting anything. Returns a token to confirm with. Finished videos are never on the list."""
    if what not in ('key', 'logins', 'settings', 'work', 'everything'):
        raise ValueError('Delete what? key, logins, settings, work or everything.')
    items = []
    if what in ('key', 'everything') and _get_key()[1] == 'Keychain':
        items.append({'what': 'key', 'label': 'Your ElevenLabs key, from the Keychain',
                      'note': 'Also revoke it at elevenlabs.io if you no longer want it to work.'})
    if what in ('logins', 'everything'):
        for l in logins():
            if l['saved']:
                items.append({'what': 'login', 'site': l['site'], 'seat': l['seat'],
                              'label': f"Saved login for {l['site']} ({l['label']})"})
        if os.path.exists(os.path.join(data_dir(), 'test-businesses.json')):
            items.append({'what': 'test_businesses', 'label': 'Which businesses are marked as test businesses'})
    if what in ('settings', 'everything') and os.path.exists(os.path.join(data_dir(), 'settings.json')):
        items.append({'what': 'settings', 'label': 'Your settings (back to the defaults)'})
    if what in ('settings', 'everything') and os.path.exists(os.path.join(data_dir(), 'jobs.json')):
        items.append({'what': 'jobs', 'label': 'Your own job settings (models, blind tests), back to the defaults'})
    if what in ('work', 'everything'):
        for d in demos():
            items.append({'what': 'demo', 'id': d['id'], 'label': f"Working files for \"{d['title']}\" (script, voice, recording)",
                          'bytes': _size(demo_dir(d['id']))})
        if os.path.isdir(os.path.join(work_dir(), 'batches')):
            items.append({'what': 'batches', 'label': 'Batch lists'})
    token = secrets.token_urlsafe(16)
    _pending[token] = {'t': time.time(), 'what': what, 'items': items}
    return {'token': token, 'items': items, 'never': 'Finished videos in your export folders are never deleted from here.'}


def confirm_delete(token):
    p = _pending.pop(token, None)
    if not p or time.time() - p['t'] > 300:
        raise ValueError('That confirmation has expired. Ask again.')
    done = []
    for it in p['items']:
        if it['what'] == 'key':
            remove_key() and done.append(it['label'])
        elif it['what'] == 'login':
            forget_login(it['site'], it.get('seat')) and done.append(it['label'])
        elif it['what'] == 'test_businesses':
            os.remove(os.path.join(data_dir(), 'test-businesses.json'))
            done.append(it['label'])
        elif it['what'] == 'settings':
            os.remove(os.path.join(data_dir(), 'settings.json'))
            done.append(it['label'])
        elif it['what'] == 'jobs':
            os.remove(os.path.join(data_dir(), 'jobs.json'))
            done.append(it['label'])
        elif it['what'] == 'demo':
            folder = demo_dir(it['id'])
            if os.path.exists(os.path.join(folder, 'demo.json')):    # only a NAVI demo folder, nothing else
                shutil.rmtree(folder)
                done.append(it['label'])
        elif it['what'] == 'batches':
            shutil.rmtree(os.path.join(work_dir(), 'batches'))
            done.append(it['label'])
    return {'deleted': done}
