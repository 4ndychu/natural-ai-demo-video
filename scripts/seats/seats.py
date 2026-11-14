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
  logged-out             "no login", "logged out", "public pages" (config/seats.json logged_out_phrases): no saved
                         login at all, on every site, even one with a saved login. It never holds a login:
                         Settings > Logins never offers it, and a file saved under that name is never loaded

  .venv/bin/python scripts/seats/seats.py list [--site whop.com]
  .venv/bin/python scripts/seats/seats.py pick whop.com "Open the Real Biz course and play the first lesson"
  .venv/bin/python scripts/seats/seats.py login whop.com owner
      (opens the one visible window, on the seat's home page, for the user to log in; saved when they close it)

Two or more logins in one video (X and Google Sheets, Claude and Grok): the script lists them in "seats"
([{"site": "x.com", "seat": "owner"}, {"site": "google.com", "seat": "owner"}]) and each section names the site whose
login its steps use ("seat": "google.com"). The take runs in one browser holding every one of those logins (their
saved sessions joined into one file, kept only for the run: cookies belong to their own sites, so neither login can
act on the other's site), the action guard uses each site's own pack, and the batch preflight checks every login.
A site in seats.json can cover others that share its login: "google.com": {"covers": ["docs.google.com", ...]}.
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# the seat of a video that shows the public pages as a visitor sees them: no login, whatever is saved for the site
LOGGED_OUT = 'logged-out'
LOGGED_OUT_LABEL = 'Logged out (public pages, no login)'
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


def login_site(site):
    """The site whose saved login a page uses: itself, or the seats.json site that covers it (docs.google.com and
    mail.google.com use the google.com login)."""
    cfg = config()
    if site in cfg:
        return site
    for name, c in cfg.items():
        if not name.startswith('_') and isinstance(c, dict) and site in (c.get('covers') or []):
            return name
    return site


def default_seat(site):
    seats = config().get(login_site(site), {}).get('seats', {})
    return 'owner' if 'owner' in seats or not seats else next(iter(seats))


def login_file(site, seat=None):
    """The seat's saved session. A login saved before seats existed (logins/<site>.json) becomes the site's
    default seat (owner) the first time it's asked for."""
    site = login_site(_name(site, 'site'))
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
    for s in sorted(k for k in cfg if not k.startswith('_')) if site is None else [login_site(site)]:
        for name, seat in cfg.get(s, {}).get('seats', {}).items():
            path = login_file(s, name)
            biz = [b for b in businesses(s) if b.get('seat') == name]
            out.append({'site': s, 'seat': name, 'label': seat.get('label', name.title()), 'account': seat.get('account', ''),
                        'home': seat.get('home') or f'https://{s}/', 'saved': os.path.exists(path), 'file': path,
                        'covers': cfg[s].get('covers') or [], 'note': seat.get('note', ''),
                        'businesses': [{'key': b['key'], 'name': b['name'], 'test': b['test']} for b in biz]})
    return out


# ---- the seat picker -----------------------------------------------------------------------------------------
def _hits(words, text):
    return [w for w in words if re.search(r'(?<![a-z])' + re.escape(w) + r'(?![a-z])', text)]


def pick(site, job):
    """Which seat (and business) a job runs in, from its own words. Returns {seat, business, label, why, allow}."""
    site = login_site(site_of(site))
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
    logged_out = _hits(p.get('logged_out_phrases', []), text)
    buyer = _hits(p['buyer_words'], text)
    owner = _hits(p['owner_words'], text)
    build = _hits(p['builder_phrases'], text)
    owner_score = len(owner) + 3 * len(build) + 5 * len(explicit_owner)
    buyer_score = len(buyer) + 5 * len(explicit_member)

    def done(seat, b, why, view='dashboard'):
        # a real business, or the owner's own account on a site with no businesses (X, Claude): only the changes the
        # job asks for, by the site pack's own phrases
        allow = guard_allow(site, job) if seat != LOGGED_OUT and view == 'dashboard' and ((b and b['real']) or (not b and not biz)) else []
        seat_label = LOGGED_OUT_LABEL if seat == LOGGED_OUT else cfg.get('seats', {}).get(seat, {}).get('label', (seat or '').title())
        label = f"{seat_label}, as a member of {b['name']}" if view == 'member' and b else \
            f"{seat_label}, as a member" if view == 'member' else f"{seat_label}{' in ' + b['name'] if b else ''}"
        return {'site': site, 'seat': seat, 'view': view, 'business': b['key'] if b else None,
                'business_name': b['name'] if b else None, 'real': bool(b and b['real']), 'label': label,
                'why': why, 'allow': allow,
                'login_saved': True if seat == LOGGED_OUT else os.path.exists(login_file(site, seat)) if seat in seat_names else False}

    # "no login / public pages": the logged-out seat, on any site (FG08, 14 Nov 2026: a public-pages video on a phone
    # was given the owner's X login), unless the job also says it needs the owner
    if logged_out and not explicit_owner:
        return done(LOGGED_OUT, None, 'the job says ' + ', '.join(f'"{w}"' for w in logged_out[:2]) + ': no login, the pages as a visitor sees them')

    # a site with no businesses (X, Claude, Google): the owner's own account; buyer and member words ("lesson",
    # "course") are about the video's subject there, not about whose view it is
    if seat_names and not biz:
        return done(default_seat(site), None, "the owner's own account (this site has no businesses)")
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
    label = LOGGED_OUT_LABEL if s['seat'] == LOGGED_OUT else seat_cfg.get('label', (s['seat'] or 'logged out').title())
    kind = (' (real business)' if s['business']['real'] else ' (test business)') if s['business'] else ''
    if s['view'] == 'member':
        label += (f", as a member of {s['business']['name']}" if s['business'] else ', as a member') + kind + ': member pages, not the dashboard'
        if chosen.get('preview_as'):
            label += f" (previewing as a buyer of {chosen.get('preview_name') or chosen['preview_as']})"
    elif s['business']:
        label += f" in {s['business']['name']}" + kind
    if len(s['seats']) > 1:     # a video on two or more logins: each one, and whether it is saved
        label = ' + '.join(f"{x['site']} (" + ('logged out, no login' if x['seat'] == LOGGED_OUT else x['seat'] + ('' if x['login'] else ', not logged in')) + ')'
                           for x in s['seats'])
    return {'seat': s['seat'], 'view': s['view'], 'business': s['business']['key'] if s['business'] else None, 'label': label,
            'why': chosen.get('why') or ('' if script.get('seat') else 'no seat picked: the site\'s default login'),
            # a logged-out seat needs no login, so it never reads "not logged in yet"
            'allow': s['allow'], 'login_saved': all(x['login'] or x['seat'] == LOGGED_OUT for x in s['seats']),
            'site': s['site'], 'seats': [{k: x[k] for k in ('site', 'seat')} | {'saved': bool(x['login']) or x['seat'] == LOGGED_OUT} for x in s['seats']]}


def guard_allow(site, job):
    """The changes a job explicitly asks for (by the guard pack's own phrases), allowed in a real business."""
    site = login_site(site)
    pack_path = os.path.join(ROOT, 'config', 'guard', f'{site}.json')
    if not os.path.exists(pack_path):
        return []
    text = (job or '').lower()
    pack = json.load(open(pack_path))
    return [c['id'] for c in pack.get('changes', []) if c.get('asked_by') and re.search(c['asked_by'], text, re.I)]


def for_script(script):
    """The seat a script records in: its "seat" field, or the site's default seat. Returns
    {site, seat, business (dict or None), login (path or None), allow, seats}. With more than one login ("seats"),
    `login` is the joined session holding every one of them (merged_login) and `seats` lists each with its own."""
    start = next((a.get('target', '') for s in script.get('sections', []) for a in s.get('actions', []) if a.get('do') == 'goto'), '')
    site = login_site(site_of(script.get('site') or start))
    seat_cfg = script.get('seat') or {}
    if isinstance(seat_cfg, str):
        seat_cfg = {'seat': seat_cfg}
    seat = seat_cfg.get('seat') or default_seat(site)
    b = business(site, seat_cfg['business']) if seat_cfg.get('business') else None
    view = seat_cfg.get('view') or 'dashboard'
    if b is None:
        b = business_for_url(start)
    # "logged-out": a video that must show the public pages as a visitor sees them, even on a site with a saved login
    path = login_file(site, seat) if re.fullmatch(r'[a-z0-9.-]+', site) and seat != LOGGED_OUT else None
    login = path if path and os.path.exists(path) else None
    # a member view never carries an allowance: nothing may change on a buyer's pages
    allow = [] if view == 'member' else list(seat_cfg.get('allow', []))
    all_seats = script_seats(script, site, seat, login, allow)
    if len(all_seats) > 1:
        for x in all_seats[1:]:
            allow += [a for a in x['allow'] if a not in allow]
        joined = [x['login'] for x in all_seats if x['login']]
        login = merged_login(joined) if len(joined) > 1 else (joined[0] if joined else None)
    return {'site': site, 'seat': seat, 'view': view, 'business': b, 'login': login, 'allow': allow, 'seats': all_seats}



def script_seats(script, site=None, seat=None, login=None, allow=None):
    """Every login a script uses: the main one first, then each one in its "seats" list (and any a section names),
    once each: [{site, seat, login (path or None), allow}]."""
    out = []
    if site:
        out.append({'site': site, 'seat': seat, 'login': login, 'allow': list(allow or [])})
    extra = [x if isinstance(x, dict) else {'site': x} for x in (script.get('seats') or [])]
    extra += [sec['seat'] if isinstance(sec.get('seat'), dict) else {'site': sec['seat']}
              for sec in script.get('sections') or [] if sec.get('seat')]
    for x in extra:
        try:
            s = login_site(site_of(x.get('site') or ''))
        except ValueError:
            continue
        if not re.fullmatch(r'[a-z0-9][a-z0-9.-]*', s) or any(o['site'] == s for o in out):
            continue
        st = x.get('seat') or default_seat(s)
        p = None if st == LOGGED_OUT else login_file(s, st)
        out.append({'site': s, 'seat': st, 'login': p if p and os.path.exists(p) else None, 'allow': list(x.get('allow') or [])})
    return out


def merged_login(paths):
    """One saved session holding several logins (one per site): every cookie and every page's storage of each, for a
    video that uses two or more sites. Cookies stay on their own domains, so each login still only reaches its own
    site. Written with only the user able to read it, next to the logins, named after what went in, and remade when a
    login changes; never kept in a video's folder."""
    import hashlib
    key = hashlib.sha1('|'.join(f'{p}:{os.path.getmtime(p)}' for p in sorted(paths)).encode()).hexdigest()[:16]
    d = os.path.join(data_dir(), 'logins', '_joined')
    os.makedirs(d, mode=0o700, exist_ok=True)
    out = os.path.join(d, key + '.json')
    if os.path.exists(out):
        return out
    for old in os.listdir(d):         # older joins of logins that have since changed
        if old.endswith('.json'):
            os.remove(os.path.join(d, old))
    cookies, origins = {}, {}
    for p in paths:
        st = _read(p, {}) or {}
        for c in st.get('cookies', []):
            cookies[(c.get('name'), c.get('domain'), c.get('path'))] = c
        for o in st.get('origins', []):
            origins[o.get('origin')] = o
    tmp = out + '.part'
    with open(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f:
        json.dump({'cookies': list(cookies.values()), 'origins': list(origins.values())}, f)
    os.replace(tmp, out)
    return out


def guard_config(script, log, mode='enforce', allow_test_deletes=False):
    """The action guard's settings for a recording/explore of this script (scripts/guard/guard.mjs)."""
    s = for_script(script)
    return {'site': s['site'], 'seat': s['seat'], 'view': s['view'], 'business': s['business'], 'allow': s['allow'], 'mode': mode,
            # every site whose login the video uses: the guard checks each request against its own site's pack
            'sites': [x['site'] for x in s['seats']],
            'allowTestDeletes': allow_test_deletes, 'log': log,
            # 'pages': a business's own pages outside the dashboard (whop.com/navi-test/...: courses live there), so the
            # guard knows whose they are; without it the recorder took NAVI Test's course pages for the real account
            'businesses': [dict({k: b[k] for k in ('key', 'name', 'id', 'test', 'real')}, pages=b.get('pages') or [])
                           for x in s['seats'] for b in businesses(x['site'])]}


def main():
    a = sys.argv[1:]
    if a[:1] == ['list']:
        site = a[a.index('--site') + 1] if '--site' in a else None
        print(json.dumps(seats(site), indent=1))
    elif a[:1] == ['login'] and len(a) == 3:
        site, seat = site_of(a[1]), _name(a[2], 'seat')
        if seat == LOGGED_OUT:
            sys.exit('The logged-out seat never holds a login: a video in it shows the pages as a visitor sees them.')
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
