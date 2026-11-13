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

    print(f'\n{len(FAILS)} FAILED' if FAILS else '\nall seat checks passed')
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
