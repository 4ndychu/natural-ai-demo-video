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
            'credit_limit': CONFIG['app']['batch']['credit_limit'], 'auto_go': False,
            # apps the busy-Mac check never asks the user to quit (Andy, 14 Nov 2026: Google Chrome and Wispr Flow)
            'keep_apps': list(CONFIG['app']['batch'].get('keep_apps', []))}


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
    if k == 'keep_apps' and not (isinstance(v, list) and len(v) <= 50 and all(isinstance(x, str) and 0 < len(x.strip()) <= 80 for x in v)):
        raise ValueError('keep_apps must be a list of app names.')
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
    if logins_checking() and not wait:
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
        if entry.startswith('_'):                      # _joined: sessions joined for two-login videos, not a site
            continue
        p = os.path.join(d, entry)
        if entry.endswith('.json'):                    # a login saved before seats: the site's default seat
            site, seat, f = entry[:-5], seats.default_seat(entry[:-5]), p
            if (site, seat) not in seen:
                out.append({'site': site, 'seat': seat, 'label': seat.title(), 'saved': _saved(f)})
                seen.add((site, seat))
        elif os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                # a file saved under the logged-out seat's name is never a login (it is never loaded either)
                if f.endswith('.json') and f[:-5] != seats.LOGGED_OUT and (entry, f[:-5]) not in seen:
                    out.append({'site': entry, 'seat': f[:-5], 'label': f[:-5].title(), 'saved': _saved(os.path.join(p, f))})
    st = login_status()
    windows = login_windows()
    for l in out:
        l.setdefault('businesses', [])
        l.setdefault('home', f"https://{l['site']}/")
        c = st.get(f"{l['site']}/{l['seat']}")
        if f"{l['site']}/{l['seat']}" in windows:     # its login window is still open: it's checked when it closes
            l['status'], l['checked'] = 'window open', None
        elif not l['saved']:
            l['status'], l['checked'] = 'needs login', None
        elif c and c.get('checked', 0) >= os.path.getmtime(login_file(l['site'], l['seat'])) - 1:
            l['status'], l['checked'] = c['status'], c['checked']   # a check older than the last login doesn't count
        else:
            l['status'], l['checked'] = 'unchecked', None
    return out


def _saved(path):
    return time.strftime('%d %b %Y', time.localtime(os.path.getmtime(path)))


def _windows_file():
    return os.path.join(data_dir(), 'login-windows.json')


def _alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except (OSError, TypeError):
        return False


def login_windows():
    """The login windows still open: {"<site>/<seat>": pid}, only those whose process is alive."""
    w = _read(_windows_file(), {}) or {}
    return {k: v for k, v in w.items() if _alive(v.get('pid') if isinstance(v, dict) else v)}


def start_login(url, seat=None):
    """Open a visible browser on the site for the user to log in themselves (to the given seat). It opens with the
    session already saved (so it shows them logged in), saves whenever the session changes, and when they close it
    the login is checked at once (Andy, 13 Nov 2026: logins looked unsaved because the windows were still open
    behind other windows, kept rewriting the file, and a second click opened a second, logged-out window).
    Only one window per login: a second click while it is open opens nothing and says so."""
    site = seats.login_site(site_of(url))
    seat = seat or seats.default_seat(site)
    if seat == seats.LOGGED_OUT:      # FG08, 14 Nov 2026: a real X login got saved under this name
        raise ValueError('The logged-out seat never holds a login: videos in it show the pages as a visitor sees them.')
    key = f'{site}/{seat}'
    open_now = login_windows()
    if key in open_now:
        return {'site': site, 'seat': seat, 'already_open': True,
                'message': f'The login window for {site} is already open (it may be behind other windows). Finish there and close it.'}
    path = login_file(site, seat)
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    url = url if '://' in url else 'https://' + url
    # a site added from Settings > Logins ("Add a site") gets its seat in seats.json, with the page it was logged in
    # on as its home, so "Check now" and the check after the window closes check it like every other login (before,
    # only seats.json sites were checked: an added site stayed "Not checked yet" for good)
    cfg = seats.config()
    if site not in cfg:
        cfg[site] = {'seats': {seat: {'label': seat.title(), 'home': url}}}
        seats.save_config(cfg)
    proc = subprocess.Popen(['node', os.path.join(ROOT, 'recorder', 'agent-screenplay', 'dist', 'cli.js'), 'login',
                             url, '--out', path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    open_now[key] = {'pid': proc.pid, 'started': time.time()}
    _write(_windows_file(), open_now)

    def after_close():
        proc.wait()
        w = login_windows()
        w.pop(key, None)
        _write(_windows_file(), w)
        if os.path.exists(path):          # checked straight away: no need to press "Check now"
            check_logins(site, seat, wait=True)
    import threading
    threading.Thread(target=after_close, daemon=True).start()
    return {'site': site, 'seat': seat, 'pid': proc.pid}


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


# ---- how busy the Mac is -----------------------------------------------------------------------------------------
# Apps that are the user's tools or the system: never named as something to quit (their CPU still counts)
NOT_HEAVY = {'T3 Code (Beta)', 'T3 Code', 'Claude', 'Terminal', 'iTerm', 'iTerm2', 'Ghostty', 'Finder', 'Activity Monitor'}
# NAVI's own processes, never counted as load: anything run from NAVI's folder, its recording browser (Chrome for
# Testing, from Playwright's cache) and renderer, ffmpeg from NAVI's .venv, NAVI's scripts started with a relative path,
# and everything any of them started (the app server, batch runners, the jobs they run)
NAVI_CMD = re.compile(r'/ms-playwright/|(?:^|/)\.venv/bin/\S+\s+(?:\S*/)?scripts/[a-z]+/\w+\.(?:py|mjs)|'
                      r'(?:^|/)node\s+(?:\S*/)?(?:scripts/[a-z]+/\w+\.mjs|recorder/)')
APP_OF = re.compile(r'^(?:/System)?(?:/Users/[^/]+)?/Applications/(?:[^/]+/)*?([^/]+)\.app/')
ICLOUD = re.compile(r'^/\S*/(?:fileproviderd|bird|cloudd)(?:\s|$)')


def _cpu_secs(t):
    """ps's cumulative CPU time ("9:43.04", "1:02:03.45", "2-03:04:05") in seconds."""
    days, _, t = t.rpartition('-')
    secs = 0.0
    for part in t.split(':'):
        secs = secs * 60 + float(part)
    return (int(days) if days else 0) * 86400 + secs


def _processes():
    """{pid: (ppid, CPU seconds used so far, command line)} for every process."""
    try:
        out = subprocess.run(['ps', '-Ao', 'pid=,ppid=,time=,command='], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {}
    procs = {}
    for line in out.splitlines():
        m = re.match(r'\s*(\d+)\s+(\d+)\s+(\S+)\s+(.*)$', line)
        if m:
            try:
                procs[int(m.group(1))] = (int(m.group(2)), _cpu_secs(m.group(3)), m.group(4))
            except ValueError:
                continue
    return procs


def _navi_pids(procs):
    """NAVI's own processes (NAVI_CMD, this process) and every process they started."""
    kids = {}
    for pid, (ppid, _, _) in procs.items():
        kids.setdefault(ppid, []).append(pid)
    todo = [os.getpid()] + [pid for pid, (_, _, cmd) in procs.items() if ROOT + os.sep in cmd or NAVI_CMD.search(cmd)]
    navi = set()
    while todo:
        pid = todo.pop()
        if pid not in navi and pid > 1:
            navi.add(pid)
            todo += kids.get(pid, [])
    return navi


def _mac_file():
    return os.path.join(data_dir(), 'mac-cpu.json')


def mac_sample(procs=None):
    """One reading of every process's CPU time so far, kept for a few windows in $NAVI_DATA/mac-cpu.json, so the app
    and a batch average over the same readings. The app server takes one every few seconds; mac_load takes one too.
    Returns (readings, the processes just read)."""
    win = CONFIG['app']['batch'].get('load_seconds', 30)
    procs = procs if procs is not None else _processes()
    now = time.time()
    st = _read(_mac_file(), {}) or {}
    readings = [r for r in st.get('readings', []) if isinstance(r, dict) and 0 <= now - r.get('t', 0) < win * 3]
    if procs and (not readings or now - readings[-1]['t'] >= 2):
        readings.append({'t': now, 'cpu': {str(pid): round(p[1], 2) for pid, p in procs.items()}})
        st['readings'] = readings
        try:
            _write(_mac_file(), st)
        except OSError:
            pass
    return st, readings, procs


def _keeps(name, keep):
    n = name.lower()
    return any(k == n or (len(k) >= 3 and k in n) for k in keep)


def mac_load():
    """How busy the Mac is, for the Go screen, the warning before a batch and the wait before each take:
    {others, navi, seconds, load, cores, busy, quiet_under, heavy: [{app, cpu}], kept: [{app, cpu}], icloud_syncing,
    line}. Averaged over the last load_seconds (30 s), not one moment, so it doesn't change with every refresh.
    `others`: cores' worth of CPU used by everything except NAVI's own processes and the apps the user keeps open
    (Settings: keep_apps, Google Chrome and Wispr Flow by default). `heavy`: apps to quit, only those averaging at
    least heavy_cpu % of a core, never a kept app or one of the user's tools. Busy from quiet_cores up, and it stays
    busy until a quarter under, so it doesn't flicker at the line."""
    b = CONFIG['app']['batch']
    win = b.get('load_seconds', 30)
    heavy_at = b.get('heavy_cpu', 50)
    quiet = b.get('quiet_cores', 2.0)
    keep = [k.strip().lower() for k in settings().get('keep_apps', []) if isinstance(k, str) and k.strip()]
    try:
        cores = int(subprocess.run(['sysctl', '-n', 'hw.ncpu'], capture_output=True, text=True).stdout.strip() or 8)
    except (OSError, ValueError):
        cores = os.cpu_count() or 8
    st, readings, procs = mac_sample()
    now = readings[-1]['t'] if readings else time.time()
    older = [r for r in readings if r['t'] <= now - win]
    base = older[-1] if older else (readings[0] if readings else None)
    if base is None or now - base['t'] < 1.5:      # the first reading NAVI has: a short one now, the full window after
        time.sleep(2.2)
        st, readings, procs = mac_sample(_processes())
        now = readings[-1]['t'] if readings else time.time()
        base = base or (readings[0] if readings else None)
    span = max(now - base['t'], 0.5) if base else 0.5
    cur = readings[-1]['cpu'] if readings else {}
    navi_pids = _navi_pids(procs)
    others = navi = sync = 0.0
    apps, kept = {}, {}
    for pid, (_, _, cmd) in procs.items():
        used = cur.get(str(pid))
        if used is None or base is None:
            continue
        before = base['cpu'].get(str(pid), 0.0)
        cpu = max(used - before if used >= before else used, 0.0) / span * 100      # % of one core, on average
        if pid in navi_pids:
            navi += cpu
            continue
        if ICLOUD.search(cmd):                      # iCloud Drive syncing: can't be quit, only waited for
            sync += cpu
            continue
        a = APP_OF.search(cmd)
        if a and _keeps(a.group(1), keep):
            kept[a.group(1)] = kept.get(a.group(1), 0.0) + cpu
            continue
        others += cpu
        if a and a.group(1) not in NOT_HEAVY:
            apps[a.group(1)] = apps.get(a.group(1), 0.0) + cpu
    others /= 100
    was_busy, was_named = bool(st.get('busy')), set(st.get('named') or [])
    busy = others >= (quiet * 0.75 if was_busy else quiet)
    names = sorted((n for n, v in apps.items() if v >= heavy_at or (n in was_named and v >= heavy_at * 0.6)), key=lambda n: -apps[n])
    if (busy, names) != (was_busy, sorted(was_named)) and readings:
        st.update(busy=busy, named=names)
        try:
            _write(_mac_file(), st)
        except OSError:
            pass
    heavy = [{'app': n, 'cpu': round(apps[n])} for n in names]
    lst = (', '.join(names[:-1]) + ' and ' + names[-1]) if len(names) > 1 else (names[0] if names else '')
    syncing = sync >= heavy_at
    sync_line = ' iCloud Drive is busy syncing too: let it finish first.' if syncing else ''
    over = f'the last {round(win)} seconds' if span >= win - 5 else f'the last {max(int(span), 1)} seconds'
    if busy:
        line = (f"Your Mac is busy: other apps used about {max(round(others), 1)} of its {cores} cores over {over} "
                f"(recordings come out best under {quiet:g})." + (f" Quit {lst} before Go." if lst else '') + sync_line)
    else:
        line = "Your Mac is quiet." + (f" Still, quit {lst} before Go: {'they slow' if len(names) > 1 else 'it slows'} a recording down." if lst else '') + sync_line
    return {'others': round(others, 1), 'navi': round(navi / 100, 1), 'seconds': round(span), 'load': round(os.getloadavg()[0], 1),
            'cores': cores, 'busy': busy, 'quiet_under': quiet, 'heavy': heavy,
            'kept': [{'app': n, 'cpu': round(v)} for n, v in sorted(kept.items(), key=lambda x: -x[1]) if v >= 1],
            'icloud_syncing': syncing, 'line': line}


def mac_sampler(every=5):
    """The app server's background reading of the Mac's CPU (mac_sample), so mac_load always has a full window."""
    while True:
        try:
            mac_sample()
        except Exception:      # never take the server down over a reading
            pass
        time.sleep(every)


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
