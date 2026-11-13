"""Phase 6 check: the script checker catches each banned pattern in a test script.

examples/script-checker/bad-script.json has one section per banned pattern (each says which error it expects) and
"ok-" sections that follow the rules. Passes when every expected error is raised in its section, no other error is
raised anywhere, and the approved script (examples/test-todo-b.json) has no errors.

Usage: .venv/bin/python scripts/script/test_check.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from check_script import check  # noqa: E402

bad = json.load(open(os.path.join(ROOT, 'examples', 'script-checker', 'bad-script.json')))
issues = check(bad, os.path.join(ROOT, 'examples', 'script-checker'), history=[])   # recent videos: test_variety.py
ok, rows = True, []
for sec in bad['sections']:
    got = sorted({i['code'] for i in issues if i['section'] == sec['name'] and i['level'] == 'error'})
    want = sorted(sec['expect'])
    good = got == want
    ok &= good
    rows.append(f"| {sec['name']} | {', '.join(want) or 'no error'} | {', '.join(got) or 'no error'} | {'pass' if good else '**FAIL**'} |")
todo = json.load(open(os.path.join(ROOT, 'examples', 'test-todo-b.json')))
shipped = [i for i in check(todo, os.path.join(ROOT, 'examples'), history=[]) if i['level'] == 'error']
ok &= not shipped
rows.append(f"| the to-do example as shipped (test-todo-b) | no error | {', '.join(i['code'] for i in shipped) or 'no error'} | {'pass' if not shipped else '**FAIL**'} |")
# The same example as first approved, before positions and starts were checked: "down at the bottom" (the bottom of
# the to-do list, not of the screen) twice, and the old recipe's starts ("Right, so," then "Okay. So now,"). The
# position check must catch exactly those two, the variety check that start-marker, and nothing else may fail.
old = json.loads(json.dumps(todo).replace('Now down at the bottom of the list you can', 'Okay. So now, down at the bottom you can')
                 .replace('At the bottom of the list, switch', 'At the bottom, switch'))
all_old = [i for i in check(old, os.path.join(ROOT, 'examples'), history=[]) if i['level'] == 'error']
others = [i for i in all_old if i['code'] not in ('position', 'start-marker')]
pos = [i for i in all_old if i['code'] == 'position']
good = not others and len(pos) == 2 and all('bottom' in i['message'] for i in pos) and any(i['code'] == 'start-marker' for i in all_old)
ok &= good
rows.append(f"| the to-do example as first approved | its 2 position errors and the old recipe's start-marker | "
            f"{', '.join(i['code'] for i in all_old) or 'no error'} | {'pass' if good else '**FAIL**'} |")
whop = json.load(open(os.path.join(ROOT, 'examples', 'script-checker', 'position-whop.json')))
got = [i['message'] for i in check(whop, os.path.join(ROOT, 'examples', 'script-checker')) if i['code'] == 'position']
good = len(got) == 2 and all('bottom right' in m for m in got)
ok &= good
rows.append(f"| \"Create product, bottom left\" (whop, bottom right of the form) | position error | "
            f"{len(got)} position errors | {'pass' if good else '**FAIL**'} |")
print('\n'.join(['| Section | Expected | Raised | Result |', '|---|---|---|---|'] + rows + ['', f"**{'PASS' if ok else 'FAIL'}**"]))
sys.exit(0 if ok else 1)
