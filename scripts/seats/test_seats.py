"""NAVI seats, the check: the seat picker on real kinds of jobs, the saved-login files (including a login saved before
seats existed), and a script's seat. Runs on a temporary $NAVI_DATA; touches nothing of the user's.

  .venv/bin/python scripts/seats/test_seats.py     (exit 1 on any failure)
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILS = []


def check(label, ok, extra=''):
    print(('ok    ' if ok else 'FAIL  ') + label + (f'  ({extra})' if extra else ''))
    if not ok:
        FAILS.append(label)


def main():
    tmp = tempfile.mkdtemp(prefix='navi-seats-')
    os.environ['NAVI_DATA'] = tmp
    import seats
    json.dump({'whop.com': {
        'seats': {'owner': {'label': 'Owner', 'account': 'owner-login'}},
        'businesses': {'real-biz': {'name': 'Real Biz', 'aliases': ['RB'], 'id': 'biz_REAL', 'seat': 'owner', 'pages': ['/real-biz/']},
                       'navi-test': {'name': 'NAVI Test', 'id': 'biz_TEST', 'seat': 'owner', 'pages': ['/navi-test/']}}}}, open(os.path.join(tmp, 'seats.json'), 'w'))
    json.dump([{'site': 'whop.com', 'match': 'whop.com/dashboard/biz_TEST', 'name': 'NAVI Test'}], open(os.path.join(tmp, 'test-businesses.json'), 'w'))

    # businesses: only the user's own mark makes one a test; the rest are real
    b = {x['key']: x for x in seats.businesses('whop.com')}
    check('NAVI Test is a test business (marked by the user)', b['navi-test']['test'] and not b['navi-test']['real'])
    check('Real Biz is real (not marked)', b['real-biz']['real'])

    # the picker
    jobs = [
        ('Open the RB course and play the first lesson', 'member', 'real-biz'),
        ('Show what members see in Real Biz: the modules and lessons', 'member', 'real-biz'),
        ('Open Real Biz courses as a buyer', 'member', 'real-biz'),
        ('Open the Real Biz course', 'member', 'real-biz'),
        ('How to watch a lesson and mark it complete', 'member', 'navi-test'),
        ('How to build a course on Whop', 'owner', 'navi-test'),
        ('Create a product with a one-time price', 'owner', 'navi-test'),
        ('How to set up a promo code', 'owner', 'navi-test'),
        ('How to create a product like the ones in Real Biz', 'owner', 'navi-test'),
        ('Walk through the RB dashboard analytics', 'owner', 'real-biz'),
        ('Tour the payouts and balance pages in Real Biz', 'owner', 'real-biz'),
        ('As the owner, show the Real Biz customers list', 'owner', 'real-biz'),
    ]
    for job, seat, biz in jobs:
        p = seats.pick('whop.com', job)
        want_view = 'member' if seat == 'member' else 'dashboard'
        check(f'"{job}" -> owner, {want_view} view, {biz}',
              p['seat'] == 'owner' and p['view'] == want_view and p['business'] == biz, f"{p['label']}: {p['why']}")
        if seat == 'member':
            check(f'"{job}": a member view allows no changes', p['allow'] == [], p['allow'])
    p = seats.pick('whop.com', 'Rename the Real Biz product to Real Course 2')
    check('a real-business job that asks for a product change allows only that', p['business'] == 'real-biz' and p['allow'] == ['product'], p['allow'])
    p = seats.pick('whop.com', 'Walk through the RB dashboard analytics')
    check('a real-business tour allows no changes', p['allow'] == [], p['allow'])
    check('the picker says the owner isn\'t logged in yet (nothing saved in this test folder)', seats.pick('whop.com', 'Open the RB course')['login_saved'] is False)

    # login files: a login saved before seats existed becomes the owner seat's
    legacy = os.path.join(tmp, 'logins', 'whop.com.json')
    os.makedirs(os.path.dirname(legacy))
    json.dump({'cookies': [], 'origins': []}, open(legacy, 'w'))
    path = seats.login_file('whop.com', 'owner')
    check('an old login moves to logins/whop.com/owner.json', path.endswith('logins/whop.com/owner.json') and os.path.exists(path) and not os.path.exists(legacy))
    check('another seat would have its own file', seats.login_file('whop.com', 'helper').endswith('logins/whop.com/helper.json'))
    listed = {s['seat']: s for s in seats.seats('whop.com')}
    check('seats list: only the owner, saved', list(listed) == ['owner'] and listed['owner']['saved'])
    check('seats list: owner opens both businesses', {x['key'] for x in listed['owner']['businesses']} == {'real-biz', 'navi-test'})
    for bad in ('../x', 'Owner', 'a/b'):
        try:
            seats.login_file('whop.com', bad)
            check(f'refuses seat name {bad!r}', False)
        except ValueError:
            check(f'refuses seat name {bad!r}', True)

    # a script's seat
    script = {'site': 'whop.com', 'sections': [{'actions': [{'do': 'goto', 'target': 'https://whop.com/dashboard/biz_TEST/products/'}]}]}
    s = seats.for_script(script)
    check('a script without a seat uses the owner seat, in the business its page belongs to', s['seat'] == 'owner' and s['business']['key'] == 'navi-test' and s['login'] == path)
    s = seats.for_script({**script, 'seat': {'seat': 'owner', 'view': 'member', 'business': 'real-biz', 'allow': ['product']}})
    check('a member-view script uses the owner login and drops any allowance', s['seat'] == 'owner' and s['view'] == 'member' and s['login'] == path and s['allow'] == [])
    g = seats.guard_config({**script, 'seat': {'seat': 'owner', 'business': 'real-biz', 'allow': ['product']}}, '/tmp/log')
    check('the guard gets the seat, business and the job\'s allowance', g['seat'] == 'owner' and g['business']['real'] and g['allow'] == ['product'])
    gb = {x['key']: x for x in g['businesses']}
    check("the recorder's guard knows each business's own pages (13 Nov 2026: without them NAVI Test's course pages counted as the real account)",
          gb['navi-test']['pages'] == ['/navi-test/'] and gb['real-biz']['pages'] == ['/real-biz/'] and gb['real-biz']['real'] and gb['navi-test']['test'], gb)

    # the app's login list: status from the last live check, unless the login is newer than the check
    sys.path.insert(0, os.path.join(HERE, '..', 'app'))
    import store
    import time as _t
    json.dump({'whop.com/owner': {'status': 'working', 'checked': _t.time() + 5}}, open(os.path.join(tmp, 'login-status.json'), 'w'))
    row = next(l for l in store.logins() if l['seat'] == 'owner')
    check('app: a live check newer than the login gives its status', row['status'] == 'working' and row['businesses'], row)
    json.dump({'whop.com/owner': {'status': 'working', 'checked': _t.time() - 3600}}, open(os.path.join(tmp, 'login-status.json'), 'w'))
    os.utime(path, None)
    row = next(l for l in store.logins() if l['seat'] == 'owner')
    check('app: a check older than the last login counts as not checked', row['status'] == 'unchecked', row['status'])
    s2 = json.load(open(os.path.join(tmp, 'seats.json')))
    s2['whop.com']['seats']['helper'] = {'label': 'Helper'}
    json.dump(s2, open(os.path.join(tmp, 'seats.json'), 'w'))
    row = next(l for l in store.logins() if l['seat'] == 'helper')
    check('app: a seat never logged in needs login', row['status'] == 'needs login' and not row['saved'], row)

    logged_out_checks(tmp, seats, store)
    print(f'\n{len(FAILS)} FAILED' if FAILS else '\nall seat checks passed')
    sys.exit(1 if FAILS else 0)


def logged_out_checks(tmp, seats, store):
    """A video marked "no login / public pages" uses the logged-out seat, everywhere (FG08, 14 Nov 2026: its row said
    public pages, logged out, on a phone; the video was given the owner's X login, and a real X session ended up saved
    under the name "logged-out")."""
    import subprocess
    sys.path.insert(0, os.path.join(HERE, '..', 'record'))
    s = json.load(open(os.path.join(tmp, 'seats.json')))
    s['x.com'] = {'seats': {'owner': {'label': 'Owner (your real X account)'}}}
    json.dump(s, open(os.path.join(tmp, 'seats.json'), 'w'))
    for site, job in [('x.com', 'FG08 What a funnel is. The @0xROAS funnel walked on a phone, logged out, from his X bio to the checkout'),
                      ('x.com', 'Eight sellers: no login / public pages'),
                      ('whop.com', 'Open the Real Biz store page as a visitor, not logged in'),
                      ('whop.com', 'The checkout, public pages only')]:
        p = seats.pick(site, job)
        check(f'"{job[:50]}" on {site} -> logged-out seat, nothing allowed, no login needed',
              p['seat'] == seats.LOGGED_OUT and p['allow'] == [] and p['login_saved'] and p['business'] is None, p)
    p = seats.pick('whop.com', 'As the owner, show the Real Biz dashboard while logged out of X')
    check('an owner phrase wins over "logged out"', p['seat'] == 'owner', p)
    check('a plain X job still uses the owner login', seats.pick('x.com', 'Ask Grok for five post ideas')['seat'] == 'owner')

    # a real login saved under the logged-out seat's name is never loaded, listed or checked
    os.makedirs(os.path.join(tmp, 'logins', 'x.com'), exist_ok=True)
    for name in ('owner', seats.LOGGED_OUT):
        json.dump({'cookies': [{'name': 'auth_token', 'value': name, 'domain': '.x.com', 'path': '/'}], 'origins': []},
                  open(os.path.join(tmp, 'logins', 'x.com', name + '.json'), 'w'))
    script = {'site': 'https://x.com/', 'seat': {'seat': seats.LOGGED_OUT},
              'seats': [{'site': 'x.com', 'seat': seats.LOGGED_OUT}, {'site': 'whop.com', 'seat': seats.LOGGED_OUT}],
              'sections': [{'actions': [{'do': 'goto', 'target': 'https://x.com/0xROAS'}]}]}
    f = seats.for_script(script)
    check('a two-site logged-out video holds no login at all', f['login'] is None and all(x['login'] is None for x in f['seats']), f)
    d = seats.describe(script)
    check('a logged-out video never says "not logged in yet"', d['login_saved'] and 'not logged in' not in d['label'], d['label'])
    one = dict(script, seats=[])
    check('a one-site logged-out video holds no login', seats.for_script(one)['login'] is None)
    check('its preview label says logged out', seats.describe(one)['label'] == seats.LOGGED_OUT_LABEL, seats.describe(one)['label'])
    import record
    check('the off-camera ready state runs a logged-out video logged out', record.seat_args(seats.for_script(one)) == ['--logged-out'])
    check('the off-camera ready state passes every seat of a two-site video',
          record.seat_args(f) == ['--seat', 'logged-out', '--seats', 'x.com:logged-out,whop.com:logged-out'], record.seat_args(f))
    js = ("const s = await import(process.argv[1]); console.log(JSON.stringify([s.sessionFile('x.com', 'logged-out') ?? null, "
          "s.joinedSession([['x.com', 'logged-out'], ['whop.com', 'logged-out']]) ?? null, "
          "(s.joinedSession([['x.com', 'owner'], ['whop.com', 'logged-out']]) || '').endsWith('owner.json')]))")
    r = subprocess.run(['node', '--input-type=module', '-e', js, os.path.join(HERE, 'seats.mjs')], capture_output=True, text=True, env=dict(os.environ))
    out = json.loads(r.stdout.strip() or 'null')
    check('seats.mjs: the logged-out seat loads no file, even one saved under its name', out and out[0] is None and out[1] is None, r.stdout + r.stderr)
    check('seats.mjs: a logged-out site adds nothing to a joined login', out and out[2] is True, r.stdout + r.stderr)
    check('app: a file under the logged-out name is not listed as a login',
          not any(l['seat'] == seats.LOGGED_OUT for l in store.logins()), [l['seat'] for l in store.logins()])
    try:
        store.start_login('https://x.com/', seats.LOGGED_OUT)
        check('app: the logged-out seat cannot be logged in', False)
    except ValueError:
        check('app: the logged-out seat cannot be logged in', True)


if __name__ == '__main__':
    main()
