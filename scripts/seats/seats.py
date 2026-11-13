"""NAVI seats: named saved logins per site, and which one each video uses.

A seat is one saved login on one site, with a name, for example "owner" (the user's own login, which opens their
businesses' dashboards). The user logs in to each seat once, in the one visible window NAVI ever opens; NAVI never
types a password. A buyer's view is filmed with the owner seat on the member-facing pages (the course, its modules
and lessons), never the dashboard (Andy, 11 Nov 2026: no second "student" login).

Files (outside the repo, readable only by the user):
  $NAVI_DATA/seats.json                 the seats and businesses per site (example: config/seats.example.json)
  $NAVI_DATA/logins/<site>/<seat>.json  each seat's saved session
  $NAVI_DATA/test-businesses.json       businesses the USER marked as tests (NAVI never marks one itself)

A business is "test" only when the user marked it in test-businesses.json. Any other business is treated as real:
the action guard (scripts/guard/guard.mjs) blocks every change there that the job didn't ask for.

The seat picker (pick) chooses, from the job's own words:
  owner, member view     anything a buyer sees: opening courses, modules, lessons; the member-facing pages of the
                         business the job names (or the test business), not the dashboard; no changes allowed
  owner in the test biz  "how to build X" demos (the default for an owner job)
  owner in a real biz    only when the job names that business AND needs the owner dashboard

  .venv/bin/python scripts/seats/seats.py list [--site whop.com]
  .venv/bin/python scripts/seats/seats.py pick whop.com "Open the Real Biz course and play the first lesson"
  .venv/bin/python scripts/seats/seats.py login whop.com owner
      (opens the one visible window, on the seat's home page, for the user to log in; saved when they close it)
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RULES = json.load(open(os.path.join(ROOT, 'config', 'seats.json')))


def data_dir():
    return os.path.expanduser(os.environ.get('NAVI_DATA') or '~/Library/Application Support/NAVI')


def site_of(url):
    m = re.match(r'^(?:[a-z]+://)?([^/:?#]+)', (url or '').strip().lower())
    if not m:
        raise ValueError('Not a web address.')
    return m.group(1).removeprefix('www.')


def _name(s, what):
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]*', s or ''):
        raise ValueError(f'Not a {what} name: {s!r}')
    return s


def _read(path, default):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default


def config():
    """$NAVI_DATA/seats.json: {site: {"seats": {name: {...}}, "businesses": {key: {...}}}}."""
    return _read(os.path.join(data_dir(), 'seats.json'), {})


def save_config(cfg):
    path = os.path.join(data_dir(), 'seats.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.part'
    with open(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f:
        json.dump(cfg, f, indent=1)
    os.replace(tmp, path)


def default_seat(site):
    seats = config().get(site, {}).get('seats', {})
    return 'owner' if 'owner' in seats or not seats else next(iter(seats))


def login_file(site, seat=None):
    """The seat's saved session. A login saved before seats existed (logins/<site>.json) becomes the site's
    default seat (owner) the first time it's asked for."""
    site = _name(site, 'site')
    seat = _name(seat or default_seat(site), 'seat')
    path = os.path.join(data_dir(), 'logins', site, seat + '.json')
    legacy = os.path.join(data_dir(), 'logins', site + '.json')
    if not os.path.exists(path) and seat == default_seat(site) and os.path.exists(legacy):
        os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
        shutil.move(legacy, path)
    return path


def test_marks():
    return _read(os.path.join(data_dir(), 'test-businesses.json'), [])


def _norm(u):
    return re.sub(r'^[a-z]+://(www\.)?', '', (u or '').lower()).rstrip('/')


def businesses(site):
    """Every business on the site with its key, name, id, seat, and test/real. Only the user's own marks make a
    business a test; everything else counts as real."""
    out = []
    marks = [m for m in test_marks() if m.get('site') == site]
    for key, b in config().get(site, {}).get('businesses', {}).items():
        mark = next((m for m in marks if b.get('id') and b['id'] in m.get('match', '')), None)
        out.append({'key': key, 'site': site, **b, 'test': bool(mark), 'real': not mark,
                    'match': (mark or {}).get('match') or b.get('match', ''), 'mark': mark})
    return out


def business(site, key):
    return next((b for b in businesses(site) if b['key'] == key), None)


def business_for_url(url):
    """The business a page belongs to (by the business id in its address), or None."""
    try:
        site = site_of(url)
    except ValueError:
        return None
    u = _norm(url)
    for b in businesses(site):
        if (b.get('id') and b['id'].lower() in u) or (b['match'] and u.startswith(_norm(b['match']))):
            return b
    return None


def seats(site=None):
    """Every seat, per site: name, label, account, whether a login is saved, and the businesses it opens."""
    cfg = config()
    out = []
    for s in sorted(cfg) if site is None else [site]:
        for name, seat in cfg.get(s, {}).get('seats', {}).items():
            path = login_file(s, name)
            biz = [b for b in businesses(s) if b.get('seat') == name]
            out.append({'site': s, 'seat': name, 'label': seat.get('label', name.title()), 'account': seat.get('account', ''),
                        'home': seat.get('home') or f'https://{s}/', 'saved': os.path.exists(path), 'file': path,
                        'businesses': [{'key': b['key'], 'name': b['name'], 'test': b['test']} for b in biz]})
    return out


# ---- the seat picker -----------------------------------------------------------------------------------------
def _hits(words, text):
    return [w for w in words if re.search(r'(?<![a-z])' + re.escape(w) + r'(?![a-z])', text)]


def pick(site, job):
    """Which seat (and business) a job runs in, from its own words. Returns {seat, business, label, why, allow}."""
    site = site_of(site)
    text = ' ' + re.sub(r'\s+', ' ', (job or '').lower()) + ' '
    cfg = config().get(site, {})
    seat_names = list(cfg.get('seats', {}))
    biz = businesses(site)
    named = [b for b in biz if any(_hits([n.lower()], text) for n in [b['name'], *b.get('aliases', [])])]
    named_real = [b for b in named if b['real']]
    test = next((b for b in biz if b['test'] and b.get('seat', 'owner') == 'owner'), None)
    p = RULES['picker']
    # business names never count as seat words ("Real Biz" is not about revenue)
    for b in biz:
        for n in [b['name'], *b.get('aliases', [])]:
            text = re.sub(r'(?<![a-z])' + re.escape(n.lower()) + r'(?![a-z])', ' ', text)
    explicit_member = _hits(p['member_phrases'], text)
    explicit_owner = _hits(p['owner_phrases'], text)
    buyer = _hits(p['buyer_words'], text)
    owner = _hits(p['owner_words'], text)
    build = _hits(p['builder_phrases'], text)
    owner_score = len(owner) + 3 * len(build) + 5 * len(explicit_owner)
    buyer_score = len(buyer) + 5 * len(explicit_member)

    def done(seat, b, why, view='dashboard'):
        allow = guard_allow(site, job) if b and b['real'] and view == 'dashboard' else []
        seat_label = cfg.get('seats', {}).get(seat, {}).get('label', (seat or '').title())
        label = f"{seat_label}, as a member of {b['name']}" if view == 'member' and b else \
            f"{seat_label}, as a member" if view == 'member' else f"{seat_label}{' in ' + b['name'] if b else ''}"
        return {'site': site, 'seat': seat, 'view': view, 'business': b['key'] if b else None,
                'business_name': b['name'] if b else None, 'real': bool(b and b['real']), 'label': label,
                'why': why, 'allow': allow, 'login_saved': os.path.exists(login_file(site, seat)) if seat in seat_names else False}

    # a buyer's view: the owner seat on the member-facing pages (the course, modules, lessons), never the dashboard;
    # no changes are allowed there (the guard treats pages outside a dashboard as the owner's real account)
    if seat_names and buyer_score > owner_score:
        b = named[0] if named else test
        return done(default_seat(site), b, 'a buyer\'s view, on the member pages, not the dashboard ('
                    + ', '.join((explicit_member + buyer)[:3]) + ')', view='member')
    # a how-to ("how to build X") is shown in the test business even when it names the real one; the real
    # business only when the job needs ITS dashboard (it says so, or it's about that business without a how-to)
    if named_real and (explicit_owner or (owner and not build)):
        return done('owner', named_real[0], f"names {named_real[0]['name']} and needs the owner dashboard ("
                    + ', '.join((explicit_owner + owner)[:3]) + ')')
    if test:
        why = 'a how-to demo, made in the test business' + (f" (the job names {named_real[0]['name']}, but nothing that needs its dashboard)" if named_real else '')
        return done('owner', test, why)
    if seat_names:
        return done(default_seat(site), None, 'the site\'s default login')
    return done(None, None, 'no saved seats for this site') | {'seat': None, 'label': 'Logged out'}


def describe(script):
    """The seat line a script preview shows: {seat, business, label, why, allow, login_saved}."""
    s = for_script(script)
    chosen = script.get('seat') if isinstance(script.get('seat'), dict) else {}
    seat_cfg = config().get(s['site'], {}).get('seats', {}).get(s['seat'], {})
    label = seat_cfg.get('label', (s['seat'] or 'logged out').title())
    kind = (' (real business)' if s['business']['real'] else ' (test business)') if s['business'] else ''
    if s['view'] == 'member':
        label += (f", as a member of {s['business']['name']}" if s['business'] else ', as a member') + kind + ': member pages, not the dashboard'
        if chosen.get('preview_as'):
            label += f" (previewing as a buyer of {chosen.get('preview_name') or chosen['preview_as']})"
    elif s['business']:
        label += f" in {s['business']['name']}" + kind
    return {'seat': s['seat'], 'view': s['view'], 'business': s['business']['key'] if s['business'] else None, 'label': label,
            'why': chosen.get('why') or ('' if script.get('seat') else 'no seat picked: the site\'s default login'),
            'allow': s['allow'], 'login_saved': bool(s['login']), 'site': s['site']}


def guard_allow(site, job):
    """The changes a job explicitly asks for (by the guard pack's own phrases), allowed in a real business."""
    pack_path = os.path.join(ROOT, 'config', 'guard', f'{site}.json')
    if not os.path.exists(pack_path):
        return []
    text = (job or '').lower()
    pack = json.load(open(pack_path))
    return [c['id'] for c in pack.get('changes', []) if c.get('asked_by') and re.search(c['asked_by'], text, re.I)]


def for_script(script):
    """The seat a script records in: its "seat" field, or the site's default seat. Returns
    {site, seat, business (dict or None), login (path or None), allow}."""
    start = next((a.get('target', '') for s in script.get('sections', []) for a in s.get('actions', []) if a.get('do') == 'goto'), '')
    site = site_of(script.get('site') or start)
    seat_cfg = script.get('seat') or {}
    if isinstance(seat_cfg, str):
        seat_cfg = {'seat': seat_cfg}
    seat = seat_cfg.get('seat') or default_seat(site)
    b = business(site, seat_cfg['business']) if seat_cfg.get('business') else None
    view = seat_cfg.get('view') or 'dashboard'
    if b is None:
        b = business_for_url(start)
    path = login_file(site, seat) if re.fullmatch(r'[a-z0-9.-]+', site) else None
    # a member view never carries an allowance: nothing may change on a buyer's pages
    return {'site': site, 'seat': seat, 'view': view, 'business': b, 'login': path if path and os.path.exists(path) else None,
            'allow': [] if view == 'member' else list(seat_cfg.get('allow', []))}


def guard_config(script, log, mode='enforce', allow_test_deletes=False):
    """The action guard's settings for a recording/explore of this script (scripts/guard/guard.mjs)."""
    s = for_script(script)
    return {'site': s['site'], 'seat': s['seat'], 'view': s['view'], 'business': s['business'], 'allow': s['allow'], 'mode': mode,
            'allowTestDeletes': allow_test_deletes, 'log': log,
            # 'pages': a business's own pages outside the dashboard (whop.com/navi-test/...: courses live there), so the
            # guard knows whose they are; without it the recorder took NAVI Test's course pages for the real account
            'businesses': [dict({k: b[k] for k in ('key', 'name', 'id', 'test', 'real')}, pages=b.get('pages') or []) for b in businesses(s['site'])]}


def main():
    a = sys.argv[1:]
    if a[:1] == ['list']:
        site = a[a.index('--site') + 1] if '--site' in a else None
        print(json.dumps(seats(site), indent=1))
    elif a[:1] == ['login'] and len(a) == 3:
        site, seat = site_of(a[1]), _name(a[2], 'seat')
        home = config().get(site, {}).get('seats', {}).get(seat, {}).get('home') or f'https://{site}/'
        path = login_file(site, seat)
        os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
        print(f'A browser window opens on {home}. Log in to the {seat} account, then close the window; NAVI saves it.')
        import subprocess
        subprocess.run(['node', os.path.join(ROOT, 'recorder', 'agent-screenplay', 'dist', 'cli.js'), 'login', home, '--out', path])
        print('saved' if os.path.exists(path) else 'not saved (closed before logging in?)')
    elif a[:1] == ['pick'] and len(a) >= 3:
        print(json.dumps(pick(a[1], ' '.join(a[2:])), indent=1))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
