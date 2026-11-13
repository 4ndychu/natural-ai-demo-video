"""NAVI batch mode (Phase 7): a list of videos in, one approval for all the scripts, recorded one after another,
paused if credits run low, a review queue, then export plus a list file. Nothing is ever uploaded or published.

  batch.py new --name "Course week 1" --list videos.txt --site https://app.example.com [--kind course]
               [--voice alex] [--privacy standard] [--export-to ~/Movies/NAVI] [--captions burn] [--speed 1.35]
      One demo per line of the list ("Title" or "Title | what to show"). Each demo gets script.template.json with the
      shared settings filled in; Claude writes each script.json from it (reference/script-writing.md).
      Or a JSON list (a file starting with "["), one object per video, carrying everything its row says:
        {"title", "what", "site" (its start page; else --site), "seats": [{"site", "seat"}] (two or more logins),
         "length_min", "spelling" ("UK"/"US", captions), "never_name": [words never said or captioned],
         "privacy": {"preset", "blur", "show", "hide_words", "blur_selectors"}, "lesson_file" (copied into the video's
         folder for the explorer and the writer), "brief": {any other fields: what it's for, start to end, what gets
         created, what must never show...}}
  batch.py write <batch>                plan the batch, then for each video in order: explore its pages, write three
                                        drafts and keep the best, and run the checks. Each of these is a subagent on
                                        the model and effort config/defaults.json names for that job ("jobs";
                                        scripts/jobs/jobs.py). Picks up where it stopped if run again.
  batch.py qa <batch>                   the last check on the recorded videos before the user watches (also run at
                                        the end of `run`)
  batch.py mac                          how busy the Mac is, and which apps to quit before a batch (also on the Go screen)
  batch.py status <batch>               where every video is
  batch.py sheet <batch>                every script in one list (talking and caption versions side by side), the
                                        total credits against the credits left. Writes batch-scripts.md.
  batch.py approve <batch>              approve every script at once (refused while any script has checker errors)
  batch.py plan <batch>                 the Go screen: every video with its seat, cost and start page, the logins
                                        it needs, the total against the credits left and the spending limit
  batch.py preflight <batch>            before a batch starts: every login it needs checked live, every video's
                                        start page opened with its login, credits against the limit. Re-logins are
                                        asked for here, up front, never mid-run.
  batch.py go <batch> [--auto]          the Go click: approve, preflight, then run. --auto (Claude, once every script
                                        is written) starts only when the "start without the Go click" setting is on;
                                        otherwise the batch waits on the Go screen.
  batch.py run <batch>                  voice, timing and recording, one video after another, never asking anything:
                                        a video that breaks, is blocked by the action guard or can't be paid for is
                                        skipped with the reason and the batch carries on. A video is never
                                        part-generated. Before each recording it waits (a while) for a quiet Mac.
                                        Ends with the morning report (batch-report.md): done, skipped, why.
  batch.py queue <batch>                the review queue: recorded videos waiting for the user's review
  batch.py review <batch> <demo> approve [--anyway]
  batch.py export <batch>               export every approved video into <export folder>/<batch name>/, plus
                                        "<batch name> - list.csv" and ".md" (title, files, length, folder)

NAVI_FAKE_CREDITS simulates the credit balance (tests).
"""
import argparse
import csv
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PY = os.path.join(ROOT, '.venv', 'bin', 'python')
for p in ('app', 'script', 'render', 'jobs'):
    sys.path.insert(0, os.path.join(ROOT, 'scripts', p))
import store  # noqa: E402
from check_script import check  # noqa: E402
import variety  # noqa: E402
import style as style_mod  # noqa: E402
import jobs  # noqa: E402
import blind  # noqa: E402

CONFIG = store.CONFIG
B = CONFIG['app']['batch']
SHARED = ('kind', 'voice', 'privacy_preset', 'hide_words', 'video_style', 'captions', 'caption_look', 'corner_label', 'corner_text',
          'export_to', 'speed_copy')


def bdir(bid):
    if not re.fullmatch(r'[a-z0-9-]+', bid or ''):
        raise ValueError('Not a batch id.')
    return os.path.join(store.work_dir(), 'batches', bid)


def load(bid):
    b = store._read(os.path.join(bdir(bid), 'batch.json'), None)
    if b is None:
        sys.exit(f'No batch called {bid}.')
    return b


def save(b):
    b['updated'] = time.time()
    store._write(os.path.join(bdir(b['id']), 'batch.json'), b)


def log(b, text):
    b.setdefault('log', []).append({'t': time.time(), 'text': text})
    print(text, flush=True)


def parse_list(text):
    if text.lstrip().startswith('['):          # the rich list: one object per video
        items = []
        for it in json.loads(text):
            if not isinstance(it, dict) or not str(it.get('title', '')).strip():
                raise ValueError('Each video in a JSON list needs a "title".')
            items.append({**it, 'title': it['title'].strip(), 'what': (it.get('what') or '').strip()})
        return items
    items = []
    for line in text.splitlines():
        line = re.sub(r'^\s*(?:[-*•]|\d+[.)])\s*', '', line).strip()
        if not line or line.startswith('#'):
            continue
        title, _, what = line.partition('|')
        items.append({'title': title.strip(), 'what': what.strip()})
    return items


def new(name, lines, site, no_blind=False, length_min=None, **shared):
    s = {**store.settings(), **{k: v for k, v in shared.items() if v is not None}}
    for k in SHARED:
        store.check_setting(k, s[k])
    bid = f"{store.slug(name)}-{time.strftime('%m%d%H%M')}"
    b = {'id': bid, 'name': name, 'site': site, 'created': time.time(), 'state': 'writing', 'shared': {k: s[k] for k in SHARED},
         'items': [], 'log': []}
    if no_blind:
        b['no_blind'] = True
    voice_id = CONFIG['voices'][s['voice']]['voice_id']
    styles = []
    for pos, it in enumerate(parse_list(lines)):
        isite = it.get('site') or site
        d = store.new_demo(it['title'], site=isite, kind=s['kind'], what=it['what'], batch=bid, length_min=it.get('length_min') or length_min,
                           settings={k: s[k] for k in SHARED if k not in ('kind', 'voice')})
        ip = it.get('privacy') or {}
        tmpl = {'title': it['title'], 'site': isite, 'kind': s['kind'], 'voice_id': voice_id, 'what': it['what'],
                'privacy': {'preset': ip.get('preset') or s['privacy_preset'],
                            'hide_words': list(s['hide_words'] or []) + [w for w in ip.get('hide_words', []) if w not in (s['hide_words'] or [])],
                            **{k: ip[k] for k in ('blur', 'show', 'blur_selectors') if ip.get(k)}},
                'captions': s['captions'], 'caption_look': s['caption_look'], 'sections': []}
        # what the row says about this one video, carried into its script so every job sees it
        for k in ('spelling', 'never_name', 'seats', 'brief', 'video_no', 'device'):
            if it.get(k):
                tmpl[k] = it[k]
        if tmpl.get('seats'):     # each login's allowed changes, from the job's own words (the site pack's phrases)
            import seats as seats_mod
            job_words = f"{it['title']}. {it['what']}"
            tmpl['seats'] = [dict(x, allow=x.get('allow') or seats_mod.guard_allow(x['site'], job_words)) for x in tmpl['seats']]
        # the lesson file(s) the row names, copied into the video's folder (the jobs read nothing outside NAVI's
        # folders); the first is the lesson, the rest (its live text, a planned fixed version) sit beside it
        files = it.get('lesson_file') or []
        for i, src in enumerate([files] if isinstance(files, str) else files):
            src = os.path.expanduser(src)
            br = tmpl.setdefault('brief', {})
            if not os.path.exists(src):
                br.setdefault('lesson_missing', []).append(src)
                continue
            name = 'lesson.md' if i == 0 else f"{i}-{os.path.basename(os.path.dirname(src))}-{os.path.basename(src)}"
            dst = os.path.join(store.demo_dir(d['id']), 'brief', name)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, encoding='utf-8') as f_in, open(dst, 'w', encoding='utf-8') as f_out:
                f_out.write(f_in.read())
            if i == 0:
                br['lesson_copy'] = dst
            else:
                br.setdefault('lesson_also', []).append(dst)
        # the style of the day for this video, drawn away from the recent videos and the others in this batch
        # (scripts/script/style.py; Andy, 11 Nov 2026: every video sounded the same). The writer then drafts it three
        # times from three styles and keeps the best (scripts/script/drafts.py styles / pick), in batch order, so
        # each video is scored against the ones already picked; batch and batch_pos tell drafts.py where it sits.
        tmpl['batch'], tmpl['batch_pos'] = bid, pos
        tmpl['style'] = style_mod.draw(tmpl | {'sections': []}, variety.load_history(voice_id=voice_id), styles)
        styles.append(tmpl['style'])
        if it.get('seat'):   # the seat the list names for this video
            tmpl['seat'] = it['seat']
        elif d.get('seat'):   # the seat picked from this line's own words (scripts/seats/seats.py)
            tmpl['seat'] = {k: d['seat'][k] for k in ('seat', 'view', 'business', 'allow', 'why', 'preview_as', 'preview_name') if k in d['seat']}
        store._write(os.path.join(store.demo_dir(d['id']), 'script.template.json'), tmpl)
        b['items'].append(d['id'])
    if not b['items']:
        sys.exit('The list is empty.')
    save(b)
    print(f"Batch {bid}: {len(b['items'])} videos. In order, for each one: draw three styles "
          f"(scripts/script/drafts.py styles <folder>/script.template.json), write the three drafts, and keep the best "
          f"(drafts.py pick <folder>/draft*.json --base <folder>), which writes its script.json:")
    for did in b['items']:
        print(f'  {store.demo_dir(did)}')
    return b


# ---- the model jobs: each one a subagent on its own model (config "jobs"; Andy, 12 Nov 2026) -----------------------
def jobs_log(bid):
    return os.path.join(bdir(bid), 'jobs.jsonl')


def job(b, name, did=None, arm=None, prompt=None, **fill):
    """Run one job's prompt (scripts/jobs/prompts/<name>.md) as a headless subagent on that job's model. The prompt
    carries everything the job needs (its rules, its files), so the subagent reads nothing else. Logged to the batch's
    jobs.jsonl (so are the line reviews the script tools run underneath, through $NAVI_JOBS_LOG)."""
    os.environ['NAVI_JOBS_LOG'], os.environ['NAVI_JOBS_DEMO'] = jobs_log(b['id']), did or ''
    prompt = open(os.path.join(ROOT, 'scripts', 'jobs', 'prompts', (prompt or name) + '.md')).read().format(**fill)
    # arm: one arm of a blind test (scripts/batch/blind.py): that model and effort, and no fallback, since another
    # model standing in would be testing something else
    e = jobs.run(name, prompt, headless=True, demo=did, log=jobs_log(b['id']), add_dirs=[store.work_dir()], schema=jobs.SCHEMAS.get(name),
                 **({'model': arm['model'], 'effort': arm['effort'], 'fallback': [], 'note': 'blind test'} if arm else {}))
    took = f"{e['seconds']:.0f} s" if e['seconds'] < 90 else f"{e['seconds'] / 60:.1f} min"
    log(b, f"  {jobs.LABELS[name].lower()}: {e['model']} / {e['effort']}, {took}, {jobs.new_in(e):,} new tokens in, {e['tokens_out']:,} out")
    if e.get('warning'):
        log(b, '  WARNING: ' + e['warning'])
    save(b)
    return e


def rel(path):
    """Paths as the subagents use them: from the repo folder when inside it (shorter, and what their commands allow)."""
    return os.path.relpath(path, ROOT) if os.path.abspath(path).startswith(ROOT + os.sep) else path


def template_of(did):
    return store._read(os.path.join(store.demo_dir(did), 'script.template.json'), {}) or {}


def seat_words(tmpl):
    import seats
    if not tmpl.get('seat'):
        return 'none picked (the site\'s default login if it has one; a public page needs none)'
    return seats.describe(tmpl)['label'] + ': ' + json.dumps(tmpl['seat'], ensure_ascii=False)


def brief_words(t):
    """The row's own brief for a video, for the planner (and, through the plan, the explorer and the writer)."""
    out = []
    br = t.get('brief') or {}
    for k, v in br.items():
        if k in ('lesson_copy', 'lesson_missing', 'lesson_also') or not v:
            continue
        out.append(f"{k.replace('_', ' ')}: {v}")
    if br.get('lesson_copy'):
        out.append(f"the lesson it belongs to (read it): {rel(br['lesson_copy'])}")
    for f in br.get('lesson_also') or []:
        out.append(f"also beside it: {rel(f)}")
    if len(t.get('seats') or []) > 1:
        out.append('logins: ' + ' + '.join(f"{x['site']} ({x.get('seat', 'owner')})" for x in t['seats'])
                   + ' (one browser holds all of them; each section names the site whose login its steps use, as "seat")')
    if t.get('spelling'):
        out.append(f"captions in {'American' if t['spelling'].upper() == 'US' else 'British'} spelling")
    if t.get('never_name'):
        out.append('never say or caption: ' + ', '.join(t['never_name']))
    return ('\n   ' + '\n   '.join(out)) if out else ''


def videos_block(b):
    rows = []
    for i, did in enumerate(b['items'], 1):
        d, t = store.demo(did), template_of(did)
        rows.append(f"{i}. {did}: \"{d['title']}\"" + (f" | {d['what']}" if d.get('what') else '') + (f"; about {d['length_min']:g} minutes long" if d.get('length_min') else '')
                    + f"; site {d.get('site') or b.get('site')}; login: {seat_words(t)}" + brief_words(t))
    return '\n'.join(rows)


def explore_cmd(did, start_url, sub=None):
    """The explorer's command for this video. `sub`: a folder inside explore/ and no steps (only the start page)."""
    import seats
    t = template_of(did)
    s = seats.for_script(dict(t, sections=[{'actions': [{'do': 'goto', 'target': start_url}]}]))
    out = rel(os.path.join(store.demo_dir(did), 'explore', *([sub] if sub else [])))
    cmd = f"node scripts/explore/explore.mjs --url {start_url} --site {s['site']} --out {out}" + ('' if sub else f" --steps {out}/steps.json")
    if len(s['seats']) > 1:      # a video on two or more logins: one browser holding all of them
        cmd += f" --seat {s['seat']} --seats " + ','.join(f"{x['site']}:{x['seat']}" for x in s['seats'])
    elif s['seat'] == seats.LOGGED_OUT:
        cmd += ' --logged-out'
    elif s['login']:
        cmd += f" --seat {s['seat']}"
    if s['allow'] and s['view'] != 'member':      # the changes the job asks for (a Grok or Claude prompt), as in the take
        cmd += ' --allow ' + ','.join(s['allow'])
    if t.get('device'):      # filmed on a phone: the explorer uses the same phone profile
        cmd += f" --device '{t['device']}'"
    seat = t.get('seat') or {}
    if s['view'] == 'member' and s['business'] and seat.get('preview_as'):
        cmd += f" --member {s['business']['key']} --preview-as {seat['preview_as']}"
    return cmd


def account_words(did):
    """What the explorer may do in this account. In a business the user marked as a test it must walk the whole
    flow for real, create and save steps too: a writer can't describe a page nobody opened (the first timing video
    came out 53 s long and stopped before Create, because its explorer wouldn't click it). Anywhere else, nothing."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts', 'privacy'))
    import privacy
    t = template_of(did)
    biz = privacy.test_business(dict(t, sections=[{'actions': [{'do': 'goto', 'target': t.get('site', '')}]}]))
    if biz and (t.get('seat') or {}).get('view', 'dashboard') != 'member':
        clean = f"node scripts/cleanup/test_products.mjs --business {biz['match']}" if biz.get('cleanup') else ''
        return (f"This is {biz.get('name', 'a test business')}, a test business the user set up for exactly this, with fake data. Do every step of the plan for real, "
                "including the steps that create and save things: type the names and amounts the plan gives, click the create and save buttons, and go on "
                "to the pages that only exist afterwards. The writer can only describe what you opened, so a flow you stop halfway is a video that stops "
                "halfway. Name whatever you create as the plan says (\"NAVI test 1\"). Still never: publish or share anything, pay, or touch another business."
                + (f" Before each run after the first, and once at the very end, clear what the runs created with:  {clean}" if clean else '')
                + (f" This video starts from a ready state made off camera ({rel(os.path.join(store.demo_dir(did), 'prepare.json'))}: "
                   f"{json.load(open(os.path.join(store.demo_dir(did), 'prepare.json'))).get('expect', 'see the file')}). After each cleanup, make it again before your run with:  "
                   f"node scripts/explore/explore.mjs --url {json.load(open(os.path.join(store.demo_dir(did), 'prepare.json')))['url']} --site whop.com --seat owner "
                   f"--out {rel(os.path.join(store.demo_dir(did), 'explore', 'prepare-run'))} --steps {rel(os.path.join(store.demo_dir(did), 'prepare-steps.json'))}  "
                   "(it is already there for your first run). Explore from that state; don't film or describe making it."
                   if os.path.exists(os.path.join(store.demo_dir(did), 'prepare.json')) else ''))
    member = (t.get('seat') or {}).get('view') == 'member'
    return ("This is a real account. Change nothing: open, hover, scroll and read only. Where the plan needs a step that would change something, "
            "stop before it and write down exactly what is on screen there."
            + (" This is a buyer's view: course and module pages only. Never open a lesson page (an address with /lessons/ in it): the owner's "
               "login sees the course editor there, and a take that opens one fails. Don't click a lesson's title; hover it on the module page instead."
               if member else ''))


def explore_help():
    src = open(os.path.join(ROOT, 'scripts', 'explore', 'explore.mjs')).read().splitlines()
    i = next(n for n, ln in enumerate(src) if ln.startswith('// steps.json'))
    return '\n'.join(ln[3:] for ln in src[i:] if ln.startswith('//'))[:1500] if i else ''


def me():
    return sys.modules[__name__]


def known_block(b, did=None, job_name=None, start_url=None):
    """What NAVI already knows about the site (scripts/explore/memory.py), for the explorer: it then only walks what
    this video needs and the earlier notes don't cover. The explorer's own notes carry it on to the writer. With
    `start_url`, the start page is opened first (no model) to see whether it still looks as remembered."""
    if not did or job_name != 'explore' or os.environ.get('NAVI_NO_SITE_MEMORY'):
        return ''
    sys.path.insert(0, os.path.join(ROOT, 'scripts', 'explore'))
    import memory
    check = None
    if start_url and memory.recall(template_of(did)):
        check = memory.fresh(template_of(did), store.demo_dir(did), explore_cmd(did, start_url, 'fresh').split())
        if check:
            log(b, f"  the start page {'still looks as remembered' if check['same'] else 'has changed since it was explored'} "
                   f"({check['kept']} of {check['of']} controls the same, {check['seconds']} s)")
    return memory.known(template_of(did), store.demo_dir(did), check)


def writer_rules():
    return jobs.doc('reference/voice-rules.md', WRITER_RULES) + '\n' + jobs.doc('reference/script-writing.md')


def check_one(b, did, sp, notes):
    """The checks job on one script file (the video's, or one draft of a blind test). Returns the errors left."""
    folder = store.demo_dir(did)
    others = [rel(os.path.join(store.demo_dir(o), 'script.json')) for o in b['items'] if o != did and script_of(o)]
    full = [os.path.join(ROOT, o) if not os.path.isabs(o) else o for o in others]
    cmd = f'.venv/bin/python scripts/script/check_script.py {rel(sp)}' + (' --batch ' + ' '.join(others) if others else '')
    _, out = step([PY, os.path.join(ROOT, 'scripts', 'script', 'check_script.py'), sp] + (['--batch'] + full if others else []))
    e = job(b, 'checks', did, script_path=rel(sp), script=jobs.attach(sp, rel(sp)), check_out=out.strip(), check_cmd=cmd,
            notes=jobs.attach(notes, rel(notes)), rules=jobs.doc('reference/voice-rules.md', ('Lines to avoid', 'Fillers')))
    sc = store._read(sp, None)
    pos = b['items'].index(did)
    feats = [] if os.environ.get('NAVI_VARIETY_OFF') else [dict(variety.features(script_of(o)), pos=i) for i, o in enumerate(b['items']) if o != did and script_of(o)]
    errs = [x for x in check(dict(sc, batch_pos=pos), os.path.dirname(sp), batch=feats) if x['level'] == 'error'] if sc else [{'level': 'error'}]
    return errs, (e['text'].strip().splitlines() or [''])[-1][:200]


def rehearse(b, did, sp, notes):
    """Play the script's actions once in the recorder's own browser, before any credits are spent (scripts/record/
    rehearse.py); what can't be done goes to the checks model to repair, and is rehearsed again. Returns '' when every
    step can be done, else why not. NAVI_NO_REHEARSAL=1 skips it (tests on saved scripts)."""
    if os.environ.get('NAVI_NO_REHEARSAL'):
        return ''
    cmd = [PY, os.path.join(ROOT, 'scripts', 'record', 'rehearse.py'), sp]
    t0 = time.time()
    code, out = step(cmd)
    took(b, did, 'rehearsal', t0)
    if code == 0:
        log(b, '  rehearsal: every step can be done')
        return ''
    log(b, '  rehearsal: ' + (out.strip().splitlines() or ['failed'])[-2 if len(out.strip().splitlines()) > 1 else -1][:200])
    folder = store.demo_dir(did)
    voiced = os.path.exists(os.path.join(folder, 'voice.json'))
    try:
        job(b, 'checks', did, prompt='repair', script_path=rel(sp), script=jobs.attach(sp, rel(sp)), report=out.strip()[-3000:],
            notes=jobs.attach(notes, rel(notes)), digest_cmd=f".venv/bin/python scripts/explore/digest.py {rel(os.path.join(folder, 'explore'))}",
            rehearse_cmd=f'.venv/bin/python scripts/record/rehearse.py {rel(sp)}', check_cmd=f'.venv/bin/python scripts/script/check_script.py {rel(sp)}',
            talk_rule=("The voice for this script is already recorded: do not change any \"talk\" or caption, or any cue word (\"on\"). Only targets."
                       if voiced else "Keep the talk and the captions as they are. Only if a step truly can't be done as written, change the fewest words so the voice and the screen agree, and keep every cue word (\"on\") in its talk line."))
    except jobs.JobError as err:
        return f"the rehearsal found a step that can't be done, and the repair didn't run ({err})"
    t0 = time.time()
    code, out = step(cmd)
    took(b, did, 'rehearsal (after the repair)', t0)
    if code == 0:
        log(b, '  rehearsal: every step can be done now')
        return ''
    why = next((l for l in out.strip().splitlines() if l.startswith('- ')), 'a step still could not be done')[2:200]
    return 'the rehearsal still fails: ' + why


WRITER_RULES = ('Voice rules', '1. The talking script', '5. Kind of demo', '6. Fillers that follow the screen')


def write(bid):
    """Every script in the batch, written without anyone watching: one plan for the batch, then per video, in order,
    explore, three drafts and the pick, and the checks. A video whose pages or script can't be done is left without a
    script, with the reason; the rest carry on. Run again, it picks up where it stopped."""
    b = load(bid)
    b['state'], b['reason'] = 'writing', None
    for w in jobs.warnings():
        log(b, 'WARNING: ' + w)
    plan_file = os.path.join(bdir(bid), 'plan.json')
    save(b)
    bp = (b.get('blind') or {}).get('plan')
    if bp and bp['status'] == 'waiting':
        print('Plans are waiting for your pick (batch.py blind / pick-plan).')
        return {'ready': 0, 'videos': len(b['items']), 'waiting': 'plan'}
    if not store._read(plan_file, None) and blind.on('planning', b) and not bp:
        if blind.plan(me(), b):
            return {'ready': 0, 'videos': len(b['items']), 'waiting': 'plan'}
    if not store._read(plan_file, None):
        log(b, f"Planning {len(b['items'])} videos")
        try:
            e = job(b, 'planning', videos=videos_block(b), known=known_block(b))
            plan_json = e.get('data')
            if not plan_json or not isinstance(plan_json.get('videos'), list):
                raise jobs.JobError('the planner gave no plan that could be read')
            store._write(plan_file, plan_json)
        except jobs.JobError as err:
            log(b, f'  the plan was not made ({err}); each video is explored and written from its own line')
    plans = {v.get('id'): v for v in (store._read(plan_file, None) or {}).get('videos', []) if isinstance(v, dict)}
    b.setdefault('written', {})
    for n, did in enumerate(b['items'], 1):
        d, folder = store.demo(did), store.demo_dir(did)
        if script_of(did) and b['written'].get(did, {}).get('checked'):
            continue
        fr, tmpl = rel(folder), template_of(did)
        plan = plans.get(did) or {'goal': d.get('what') or d['title'], 'start_url': d.get('site') or b['site'],
                                  'note': 'no plan was made: work from the title and what to show'}
        rules = {k: tmpl[k] for k in ('spelling', 'never_name', 'seats') if tmpl.get(k)}
        if tmpl.get('brief') or rules:      # the row's own brief and rules, so the explorer and writer never guess
            plan = dict(plan, brief={k: v for k, v in (tmpl.get('brief') or {}).items() if k != 'lesson_missing'}, **rules)
            if (tmpl.get('brief') or {}).get('lesson_copy'):
                plan['brief']['lesson_copy'] = rel(tmpl['brief']['lesson_copy'])
            if (tmpl.get('brief') or {}).get('lesson_also'):
                plan['brief']['lesson_also'] = [rel(x) for x in tmpl['brief']['lesson_also']]
        plan_txt = json.dumps(plan, indent=1, ensure_ascii=False)
        notes = os.path.join(folder, 'explore', 'notes.md')
        log(b, f"\"{d['title']}\" ({n} of {len(b['items'])})")
        try:
            if not script_of(did):
                if not os.path.exists(notes):
                    store.update_demo(did, {'progress': 'Exploring the pages'})
                    os.makedirs(os.path.join(folder, 'explore'), exist_ok=True)
                    if os.path.exists(os.path.join(folder, 'prepare.json')):    # the ready state, for the explorer's first run
                        sys.path.insert(0, os.path.join(ROOT, 'scripts', 'record'))
                        import record as rec_mod
                        rec_mod.cleanup(dict(tmpl, sections=[{'actions': [{'do': 'goto', 'target': tmpl.get('site', '')}]}]))   # start page: the business
                        try:
                            rec_mod.prepare(tmpl, folder)
                        except rec_mod.RecorderFailed as e:
                            raise jobs.JobError(str(e))
                    start = plan.get('start_url') or d.get('site') or b['site']
                    known = known_block(b, did, 'explore', start)
                    if known:
                        log(b, '  this site was explored before: only what is new gets explored')
                    job(b, 'explore', did, title=d['title'], site=d.get('site') or b['site'], seat=seat_words(tmpl), plan=plan_txt, known=known,
                        demo_dir=fr, explore_help=explore_help(), account=account_words(did), explore_cmd=explore_cmd(did, start))
                    sys.path.insert(0, os.path.join(ROOT, 'scripts', 'privacy'))
                    import privacy
                    tb = privacy.test_business(dict(tmpl, sections=[{'actions': [{'do': 'goto', 'target': tmpl.get('site', '')}]}]))
                    if tb and tb.get('cleanup'):      # whatever the explorer created in the test business goes again
                        step(['node', os.path.join(ROOT, 'scripts', 'cleanup', 'test_products.mjs'), '--business', tb['match']])
                    if not os.path.exists(notes):
                        raise jobs.JobError("the pages couldn't be explored (no notes were written)")
                    if not os.environ.get('NAVI_NO_SITE_MEMORY'):
                        sys.path.insert(0, os.path.join(ROOT, 'scripts', 'explore'))
                        import memory
                        memory.remember(tmpl, folder, d['title'])
                store.update_demo(did, {'progress': 'Writing script'})
                if not (did in blind.lessons_for(b) and blind.write(me(), b, did, plan_txt, notes)):
                    code, styles = step([PY, os.path.join(ROOT, 'scripts', 'script', 'drafts.py'), 'styles', os.path.join(folder, 'script.template.json')])
                    drafts = sorted(glob.glob(os.path.join(folder, 'draft[0-9].json')))
                    if code != 0 or not drafts:
                        raise jobs.JobError('the styles of the day could not be drawn: ' + styles.strip()[-200:])
                    pick = '.venv/bin/python scripts/script/drafts.py pick ' + ' '.join(rel(x) for x in drafts) + f' --base {fr}'
                    job(b, 'writing', did, rules=writer_rules(), plan=plan_txt, notes=jobs.attach(notes, rel(notes)), known=known_block(b, did),
                        styles=styles.strip(), drafts='\n'.join(jobs.attach(x, rel(x)) for x in drafts), pick_cmd=pick, demo_dir=fr)
                if not script_of(did):
                    raise jobs.JobError('no draft passed the checker, so no script was kept')
            if blind.lesson(b, did):      # its drafts were each checked as they were written
                b.setdefault('written', {})[did] = {'checked': True, 'errors': 0, 'note': f"{len(blind.lesson(b, did)['letters'])} versions for you to pick from by ear"}
                log(b, f"  {len(blind.lesson(b, did)['letters'])} versions ready (blind test): you pick by ear once they are voiced")
            else:
                store.update_demo(did, {'progress': 'Checking the script'})
                sp = os.path.join(folder, 'script.json')
                errs, note = check_one(b, did, sp, notes)
                why = '' if errs else rehearse(b, did, sp, notes)
                if why:
                    raise jobs.JobError(why)
                b.setdefault('written', {})[did] = {'checked': not errs, 'errors': len(errs), 'note': note}
                log(b, '  script ready' if not errs else f'  {len(errs)} checker errors left: it will not be recorded until they are fixed')
            store.update_demo(did, {'progress': None})
        except jobs.JobError as err:
            b.setdefault('written', {})[did] = {'checked': False, 'why': str(err)}
            store.update_demo(did, {'progress': 'No script: ' + str(err)[:160]})
            log(b, f'  no script: {err}')
        save(b)
    ready = sum(1 for did in b['items'] if b['written'].get(did, {}).get('checked'))
    log(b, f"{ready} of {len(b['items'])} scripts written and checked.")
    save(b)
    return {'ready': ready, 'videos': len(b['items'])}


def qa_frames(did, most=8):
    """A few frames of a recorded video for the last check: the first half second, just after each click or key, and
    the end. Small JPEGs in <demo>/qa/. Returns [(seconds, path)]."""
    folder = store.demo_dir(did)
    rep = store._read(os.path.join(folder, 'recording', 'report.json'), {}) or {}
    tim = store._read(os.path.join(folder, 'timing.json'), {}) or {}
    off, dur = rep.get('voice_offset_s') or 0, rep.get('duration_s') or 0
    clicks = [a['t'] + off + 0.35 for a in tim.get('actions', []) if a.get('do') in ('click', 'press') and isinstance(a.get('t'), (int, float))]
    if len(clicks) > most - 2:
        clicks = [clicks[round(i * (len(clicks) - 1) / (most - 3))] for i in range(most - 2)]
    times = sorted({round(t, 1) for t in [0.5] + clicks + ([dur - 0.4] if dur > 1 else []) if 0 <= t < max(dur, 1)})
    qdir, out = os.path.join(folder, 'qa'), []
    os.makedirs(qdir, exist_ok=True)
    for t in times:
        f = os.path.join(qdir, f'f-{t:.1f}.jpg')
        code, _ = step([os.path.join(ROOT, '.venv', 'bin', 'ffmpeg'), '-v', 'error', '-y', '-ss', str(t), '-i', os.path.join(folder, 'recording', 'recording.mp4'),
                        '-frames:v', '1', '-vf', 'scale=1280:-1', '-q:v', '4', f])
        if code == 0 and os.path.exists(f):
            out.append((t, f))
    return out


def qa(bid):
    """The last check before the user watches: one subagent gets every recorded video's script, reports and a few
    frames, and says which are ready, which to watch closely and which to redo. It changes nothing."""
    b = load(bid)
    done = [did for did in b['items'] if store.demo(did)['recorded']]
    if not done:
        return None
    qa_file = os.path.join(bdir(bid), 'qa.json')
    log(b, f'Checking {len(done)} recorded video(s) before you watch')
    blocks = []
    for did in done:
        d, folder, sc = store.demo(did), store.demo_dir(did), script_of(did) or {}
        frames = qa_frames(did)
        lines = '\n'.join(f"  [{x.get('name')}] says: {re.sub(r'^\\[relaxed\\] ', '', x.get('talk', ''))}\n      caption: {x.get('caption', '')}" for x in sc.get('sections', []))
        blocks.append(f"### {did}: \"{d['title']}\"" + (f" (what it should show: {d['what']})" if d.get('what') else '') + f"\nfolder: {rel(folder)}\n"
                      f"privacy setting: {json.dumps(sc.get('privacy', {}))}\nScript:\n{lines}\n"
                      + jobs.attach(os.path.join(folder, 'timing.md'), 'timing.md', 6000) + '\n'
                      + jobs.attach(os.path.join(folder, 'recording', 'report.md'), 'recording/report.md', 6000) + '\n'
                      + jobs.attach(os.path.join(folder, 'recording', 'privacy.md'), 'recording/privacy.md', 6000) + '\n'
                      + 'Frames: ' + ', '.join(f'{t:.1f} s = {rel(f)}' for t, f in frames))
    skipped = [f"{store.demo(x)['title']}: {b.get('results', {}).get(x, {}).get('why') or 'not recorded'}" for x in b['items'] if x not in done]
    try:
        e = job(b, 'batch_qa', rules=jobs.doc('reference/recording-rules.md', ('Picture follows the voice', 'Look')) + '\n' + jobs.doc('reference/voice-rules.md', ('Lines to avoid',)),
                videos='\n\n'.join(blocks) + ('\n\nNot recorded (no entry for these): ' + '; '.join(skipped) if skipped else ''))
        found = e.get('data')
        if found and isinstance(found.get('videos'), list):
            store._write(qa_file, found)
        else:
            log(b, "  the last check gave no answer that could be read")
    except jobs.JobError as err:
        log(b, f"  the last check didn't run: {err}")
    b['qa'] = store._read(qa_file, None)
    save(b)
    return b['qa']


def script_of(did):
    return store._read(os.path.join(store.demo_dir(did), 'script.json'), None)


def checked(bid):
    """Every script in the batch through the checker, each also against the batch's other scripts (variety: two
    videos in one batch never share an opening, a step starter or a phrase). {demo id: issues, or None: no script}."""
    b = load(bid)
    scripts = {did: script_of(did) for did in b['items']}
    pos = {did: i for i, did in enumerate(b['items'])}
    feats = {} if os.environ.get('NAVI_VARIETY_OFF') else {did: dict(variety.features(sc), pos=pos[did]) for did, sc in scripts.items() if sc}
    return {did: check(dict(sc, batch_pos=pos[did]), store.demo_dir(did), batch=[f for o, f in feats.items() if o != did]) if sc else None
            for did, sc in scripts.items()}


def credits_needed(did, takes=None):
    """Characters (credits) still to generate for this video: only takes that don't exist yet."""
    d0 = store._read(os.path.join(store.demo_dir(did), 'demo.json'), {}) or {}
    b0 = store._read(os.path.join(bdir(d0['batch']), 'batch.json'), None) if d0.get('batch') else None
    if b0 and blind.lesson(b0, did):          # a blind-test video: one take of each version, then only the picked one
        c = blind.cost(b0, did)
        if c is not None:
            return c
        takes = 1
    takes = takes or B['takes']
    sc, folder = script_of(did), store.demo_dir(did)
    have = lambda n, k: os.path.exists(os.path.join(folder, f'{n}_take{k}.json')) or (
        os.path.exists(os.path.join(folder, f'{n}_take{k}.mp3')) and os.path.exists(os.path.join(folder, f'{n}_take{k}.words.json')))
    return sum(len(s['talk']) for s in sc['sections'] for k in range(1, takes + 1) if not have(s['name'], k)) if sc else 0


def status(bid):
    b = load(bid)
    rows = []
    for i, did in enumerate(b['items'], 1):
        d = store.demo(did)
        rows.append(f"{i:2}. {d['title'][:46]:46}  {d['status']}" + (f"  ({d['length_s']:.0f} s)" if d['length_s'] else ''))
    print(f"{b['name']} ({b['id']}): {b['state']}" + (f" ({b.get('reason')})" if b.get('reason') else ''))
    print('\n'.join(rows))
    return b


def sheet(bid):
    b = load(bid)
    out, total, problems = [f"# {b['name']}: every script", ''], 0, []
    all_issues = checked(bid)
    for i, did in enumerate(b['items'], 1):
        d, sc = store.demo(did), script_of(did)
        if not sc:
            problems.append(f'{d["title"]}: no script yet')
            continue
        r = subprocess.run([PY, os.path.join(ROOT, 'scripts', 'script', 'show_script.py'), os.path.join(store.demo_dir(did), 'script.json')],
                           capture_output=True, text=True)
        out += [f'## {i}. {d["title"]}', '', r.stdout.split('\n', 2)[2] if r.stdout.count('\n') > 2 else r.stdout]
        errs = [x for x in all_issues[did] if x['level'] == 'error']
        if errs:
            problems.append(f'{d["title"]}: {len(errs)} checker errors: ' + '; '.join(sorted({x['code'] for x in errs})))
        total += credits_needed(did)
    left = store.credits_left()
    out += ['---', '', f"**Credits:** about {total:,} for the whole batch ({B['takes']} takes a section); "
            + (f"{left:,} left." if left is not None else "credits left unknown.")
            + (" Enough." if left is not None and left - total >= B['credit_margin'] else
               " Not enough for all of it: the batch will pause when credits run low." if left is not None else '')]
    if problems:
        out += ['', '**Not ready to approve:**'] + [f'- {p}' for p in problems]
    path = os.path.join(bdir(bid), 'batch-scripts.md')
    open(path, 'w').write('\n'.join(out) + '\n')
    b['estimate'] = total
    save(b)
    print('\n'.join(out[-4:]))
    print(f'Every script in one list: {path}')
    return {'path': path, 'credits': total, 'left': left, 'problems': problems}


def not_ready(bid):
    """{demo id: why} for the videos that can't be recorded as they are: no script, or checker errors left."""
    b, issues, out = load(bid), checked(bid), {}
    for did in b['items']:
        if issues[did] is None:
            out[did] = 'it has no script: ' + (b.get('written', {}).get(did, {}).get('why') or 'none was written')
        else:
            n = sum(1 for x in issues[did] if x['level'] == 'error')
            w = b.get('written', {}).get(did, {})
            if n:
                out[did] = f"its script still has {n} checker error{'s' if n != 1 else ''}"
            elif w.get('why') and not w.get('checked'):       # for example a step the rehearsal couldn't do
                out[did] = w['why']
    return out


def approve(bid):
    """Approve every script that is ready, together. A video whose script couldn't be written (or still has checker
    errors) doesn't hold the others back: it is skipped with its reason and listed in the report (Andy, 12 Nov
    2026). Refused only when no script at all is ready."""
    b = load(bid)
    bad = not_ready(bid)
    if len(bad) == len(b['items']):
        raise ValueError('No script is ready yet: ' + '; '.join(f"{store.demo(d)['title']} ({w})" for d, w in bad.items()))
    for did in b['items']:
        if did not in bad:
            store.update_demo(did, {'script_approved': True})
    b['state'], b['approved_at'] = 'approved', time.time()
    log(b, f"{len(b['items']) - len(bad)} script{'s' if len(b['items']) - len(bad) != 1 else ''} approved together."
        + (f" {len(bad)} will be skipped: " + '; '.join(f"\"{store.demo(d)['title']}\" ({w})" for d, w in bad.items()) if bad else ''))
    save(b)
    return {k: b[k] for k in ('id', 'name', 'state')} | {'skipping': [store.demo(d)['title'] for d in bad]}


def step(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


# ---- the Go screen, the preflight and the run (Andy, 11 Nov 2026: "batch this" just works) -----------------------
def credits_now():
    sim = os.environ.get('NAVI_FAKE_CREDITS')
    return int(sim) if sim is not None else store.credits_left()


def start_page(sc):
    return next((a.get('target', '') for x in (sc or {}).get('sections', []) for a in x.get('actions', []) if a.get('do') == 'goto'), '')


def first_page_on(sc, site):
    """The first page a script opens on one of its logins (a section whose "seat" is that site), or None."""
    import seats
    for sec in (sc or {}).get('sections', []):
        st = sec.get('seat')
        st = st.get('site') if isinstance(st, dict) else st
        if st and seats.login_site(seats.site_of(st)) == site:
            for a in sec.get('actions', []):
                if a.get('do') == 'goto':
                    return a.get('target')
    return None


def plan(bid):
    """Everything the Go screen shows: each video with its seat, cost and start page; the logins the batch needs
    with their last live status; the total against the credits left and the spending limit."""
    import seats
    b = load(bid)
    st = store.settings()
    status = {f"{l['site']}/{l['seat']}": l for l in store.logins()}
    videos, need = [], {}
    all_issues = checked(bid)
    for did in b['items']:
        d, sc = store.demo(did), script_of(did)
        errs = [x for x in all_issues[did] if x['level'] == 'error'] if sc else []
        seat = seats.describe(sc) if sc else (d.get('seat') or None)
        login = None
        if sc:
            s = seats.for_script(sc)
            # every login the video uses (two or more for a video on X and Google Sheets); a site recorded logged
            # out needs none
            pages = {}
            for x in s['seats']:
                if x['seat'] != seats.LOGGED_OUT and (seats.config().get(x['site'], {}).get('seats') or x['login']):
                    key = f"{x['site']}/{x['seat']}"
                    login = login or key
                    need.setdefault(key, {'site': x['site'], 'seat': x['seat'], 'videos': 0})['videos'] += 1
                    pages[key] = start_page(sc) if x is s['seats'][0] else first_page_on(sc, x['site'])
        videos.append({'id': did, 'title': d['title'], 'seat': seat['label'] if isinstance(seat, dict) and 'label' in seat else None,
                       'real': bool(isinstance(seat, dict) and '(real business)' in seat.get('label', '')), 'login': login,
                       'logins': pages if sc else {},
                       'cost': credits_needed(did), 'start': start_page(sc), 'ready': bool(sc) and not errs,
                       'problem': None if sc and not errs else ('no script yet' if not sc and did not in b.get('written', {}) else
                                                                   (b['written'][did].get('why') or 'no script') if not sc else f'{len(errs)} checker errors'),
                       'done': bool(d['recorded'])})
    logins = []
    for k, v in need.items():
        l = status.get(k, {})
        logins.append({**v, 'label': l.get('label', v['seat'].title()), 'status': l.get('status', 'needs login'), 'checked': l.get('checked')})
    total = sum(v['cost'] for v in videos if not v['done'] and v['ready'])
    left = credits_now()
    out = {'mac': store.mac_load(), 'videos': videos, 'logins': logins, 'total': total, 'left': left, 'limit': st['credit_limit'], 'auto_go': st['auto_go'],
           'margin': B['credit_margin'], 'over_limit': total > st['credit_limit'],
           'short': left is None or total and left - total < B['credit_margin'],
           'ready': any(v['ready'] for v in videos), 'skipping': [v['title'] for v in videos if not v['ready']],
           'preflight': b.get('preflight')}
    b['plan'] = {k: out[k] for k in ('total', 'left', 'limit', 'over_limit', 'short', 'ready')}
    save(b)
    return out


def preflight(bid):
    """At batch start: every login the batch needs checked live (headless, guard on), each video's start page opened
    with its login, the credits against the limit. Saved on the batch for the Go screen."""
    p = plan(bid)
    b = load(bid)
    by_login = {}
    for v in p['videos']:
        if v['done'] or not v['ready']:
            continue
        for key, page in (v.get('logins') or ({v['login']: v['start']} if v['login'] else {})).items():
            # every login the video uses is checked, with the first page it opens on that login
            by_login.setdefault(key, [])
            if page:
                by_login[key].append(page)
    res = {'logins': [], 'pages': [], 'checked': time.time()}
    for key, pages in by_login.items():
        site, seat = key.split('/', 1)
        r = subprocess.run(['node', os.path.join(ROOT, 'scripts', 'seats', 'check_logins.mjs'), '--site', site, '--seat', seat]
                           + (['--pages', ','.join(sorted(set(pages)))] if pages else []), capture_output=True, text=True)
        try:
            out = json.loads(r.stdout.strip().splitlines()[-1])[0]
        except (ValueError, IndexError):
            out = {'site': site, 'seat': seat, 'status': 'unreachable', 'detail': (r.stderr or r.stdout)[-200:]}
        res['logins'].append({k: out.get(k) for k in ('site', 'seat', 'status', 'detail')})
        for pg in out.get('pages', []):
            res['pages'].append({'login': key, **pg})
    res['relogin'] = [f"{x['site']}/{x['seat']}" for x in res['logins'] if x['status'] == 'needs login']
    res['unreachable'] = [x['url'] for x in res['pages'] if not x['ok']] + [f"{x['site']}" for x in res['logins'] if x['status'] == 'unreachable']
    res['credits'] = {'total': p['total'], 'left': p['left'], 'limit': p['limit'], 'over_limit': p['over_limit'], 'short': p['short']}
    res['ok'] = not res['relogin'] and not res['unreachable'] and not p['over_limit'] and not p['short'] and p['ready']
    b['preflight'] = res
    save(b)
    return res


def credit_cap(b):
    """The batch's own credit cap, or None: "credit_cap" on the batch, or credit_cap.json beside it ({"cap": 25000}),
    which can be set while the batch's runner holds batch.json."""
    return b.get('credit_cap') or (store._read(os.path.join(bdir(b['id']), 'credit_cap.json'), {}) or {}).get('cap')


def go(bid, auto=False):
    """The Go click. Approves every script, runs the preflight, then the batch. Returns why it didn't start, if so:
    the only things that stop a batch are the ones Andy listed (a login to redo, spending over the limit, the Go
    click itself when it's switched on), all asked before anything runs."""
    b = load(bid)
    if auto and not store.settings()['auto_go']:
        b['state'], b['reason'] = 'ready', 'waiting for Go'
        log(b, 'Every script is written and checked: waiting for Go.')
        save(b)
        return {'started': False, 'reason': 'waiting for Go'}
    if b['state'] not in ('approved',):
        approve(bid)
    pf = preflight(bid)
    b = load(bid)
    why = []
    if pf['relogin']:
        why.append('log in again first: ' + ', '.join(pf['relogin']))
    if pf['unreachable']:
        why.append("these didn't open: " + ', '.join(pf['unreachable'][:3]))
    c = pf['credits']
    # a batch with its own cap (credit_cap) is held to it video by video in run(), so it starts even when the whole
    # list would cost more than the cap or the credits left: it records what fits, in order, and skips the rest
    capped = bool(credit_cap(b))
    if c['over_limit'] and not capped:
        why.append(f"it costs about {c['total']:,} credits, over your limit of {c['limit']:,}")
    if c['short'] and not (capped and c['left'] is not None):
        why.append(f"it needs about {c['total']:,} credits and {c['left']:,} are left" if c['left'] is not None else "the credits left can't be read")
    if why:
        b['state'], b['reason'] = 'needs you', '; '.join(why)
        log(b, 'Not started: ' + b['reason'] + '. Nothing was spent.')
        save(b)
        return {'started': False, 'reason': b['reason'], 'preflight': pf}
    log(b, f"Go: preflight passed ({len(pf['logins'])} login(s) working, {len(pf['pages'])} page(s) open, about {c['total']:,} credits).")
    mac = store.mac_load()
    if mac['busy'] or mac['heavy']:      # never a reason to stop (Andy: no mid-run prompts); said up front and in the report
        log(b, '  ' + mac['line'])
    b['mac_at_go'] = mac
    save(b)
    return {'started': True, 'preflight': pf}


def wait_quiet(b):
    """Live recording drifts on a busy Mac (11 Nov 2026: a game at 200% CPU put clicks seconds off their words). Wait
    a while for the 1-minute load average to drop; then record anyway, and say so."""
    if os.environ.get('NAVI_NO_QUIET_WAIT'):
        return None
    start = time.time()
    while time.time() - start < B['quiet_wait_min'] * 60:
        load1 = os.getloadavg()[0]
        if load1 < B['quiet_load']:
            return None if time.time() - start < 5 else f"waited {int((time.time() - start) / 60)} min for a quiet Mac"
        time.sleep(30)
    return f"the Mac stayed busy (load {os.getloadavg()[0]:.0f}), so it recorded anyway: check the timing"


def took(b, did, what, t0):
    """Where a video's time goes (Andy, 12 Nov 2026): seconds per stage, kept on the batch for the report."""
    b.setdefault('timings', {}).setdefault(did or 'batch', []).append([what, round(time.time() - t0, 1)])


def skip(b, did, d, why):
    b.setdefault('results', {})[did] = {'status': 'skipped', 'why': why}
    store.update_demo(did, {'progress': 'Skipped: ' + why})
    log(b, f"  skipped \"{d['title']}\": {why}")
    save(b)


class Recorders:
    """Recording, in two parts that can overlap (Andy, 12 Nov 2026): the live take ("capture") and everything after
    it ("render": the privacy scan of the frames, Recordly drawing the video, the voice and the join checks).

    - The render of one video runs while the next one is voiced and timed: always. The render's output doesn't
      depend on what else the Mac is doing.
    - It also runs while the next one is being captured only if `render_while_recording` is on in config/defaults.json
      (app.batch), and up to `record_parallel` videos are captured at once: both are switched on only when
      scripts/focus/load_check.py showed a live take comes out the same that way on this Mac.
    - A video that changes things in a test business is always captured alone: its cleanup deletes every "NAVI test"
      product, which would pull the floor from under another take in the same business.

    Each video's work runs in its own thread; nothing in a thread touches the batch. The main loop collects what has
    finished (`collect`) and writes it down."""

    def __init__(self, style):
        import threading
        self.t = threading
        self.n = max(1, int(B.get('record_parallel', 1)))
        self.overlap = bool(B.get('render_while_recording', False))
        self.style = style
        self.cap = threading.Semaphore(self.n)       # live takes at once
        self.render = threading.Lock()               # one render at a time
        self.cv = threading.Condition()
        self.active = 0                              # takes being captured now
        self.rendering = 0
        self.alone = False                           # a take that must be alone is running or waiting
        self.jobs = {}                               # did: {'thread', 'captured' (Event), 'res'}

    def _run(self, did, folder, alone, res):
        script = os.path.join(folder, 'script.json')
        base = [PY, os.path.join(ROOT, 'scripts', 'record', 'record.py'), script, folder, '--name', 'recording', '--style', self.style]
        out = os.path.join(folder, 'recording')
        resume = os.path.exists(os.path.join(out, 'capture.json')) and not os.path.exists(os.path.join(out, 'report.json'))
        with self.cv:                                # wait for a free slot (and for no render, when they may not overlap)
            if alone:
                self.alone = True
            self.cv.wait_for(lambda: (self.active == 0 if alone else (self.active < self.n and (not self.alone or self.active == 0)))
                             and (self.overlap or self.rendering == 0))
            self.active += 1
        t0 = time.time()
        try:
            code, text = (0, '') if resume else step(base + ['--capture-only'])
        finally:
            with self.cv:
                self.active -= 1
                if alone:
                    self.alone = False
                self.cv.notify_all()
        res.update(capture_s=0 if resume else round(time.time() - t0, 1), code=code, out=text)
        self.jobs[did]['captured'].set()
        if code != 0:
            return
        with self.render:
            with self.cv:
                self.cv.wait_for(lambda: self.overlap or self.active == 0)
                self.rendering += 1
            t0 = time.time()
            try:
                code, text = step(base + ['--finish'])
            finally:
                with self.cv:
                    self.rendering -= 1
                    self.cv.notify_all()
        res.update(render_s=round(time.time() - t0, 1), code=code, out=text)

    def start(self, did, folder, alone, quiet):
        res = {'quiet': quiet}
        th = self.t.Thread(target=self._run, args=(did, folder, alone, res))
        self.jobs[did] = {'thread': th, 'captured': self.t.Event(), 'res': res, 'folder': folder}
        th.start()
        if self.n == 1 or alone:          # one take at a time: the next video's voice and timing wait for this take, not for its render
            self.jobs[did]['captured'].wait()

    def collect(self, b, wait=False):
        """Write down every video whose recording has finished (all of them, with wait)."""
        for did, j in list(self.jobs.items()):
            if wait:
                j['thread'].join()
            if j['thread'].is_alive():
                continue
            del self.jobs[did]
            d, res, folder = store.demo(did), j['res'], j['folder']
            b.setdefault('timings', {}).setdefault(did, []).append(['recording', round(res.get('capture_s', 0) + res.get('render_s', 0), 1)])
            blocked = store._read(os.path.join(folder, 'recording', 'blocked.json'), None)
            rep = store._read(os.path.join(folder, 'recording', 'report.json'), None)
            if res.get('code') == 4 and blocked:
                skip(b, did, d, blocked['reason'])
            elif not rep:
                skip(b, did, d, 'the recording failed: ' + ((res.get('out') or '').strip().splitlines() or [''])[-1][:200])
            else:
                ok, quiet = rep['checks']['pass'], res.get('quiet')
                b.setdefault('results', {})[did] = {'status': 'done', 'why': ('' if ok else 'recorded, but a join check failed (see report.md)') + (f'; {quiet}' if quiet else '')}
                store.update_demo(did, {'progress': None if ok else 'Recorded, but a join check failed: see report.md'})
                log(b, f"  \"{d['title']}\": recorded, {rep['duration_s']:.0f} s, join checks {'pass' if ok else 'FAIL'}; in the review queue")
            save(b)


def changes_things(did):
    """A video whose takes are cleaned up after in a test business (it creates things there): always recorded alone."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts', 'privacy'))
    import privacy
    sc = script_of(did) or {}
    biz = privacy.test_business(sc)
    return bool(biz and biz.get('cleanup') and (sc.get('seat') or {}).get('view', 'dashboard') != 'member')


def run(bid):
    """Every video, one after another, never asking anything (Andy, 11 Nov 2026): a video that breaks, is blocked by
    the action guard or can't be paid for is skipped with the reason, and the batch carries on. The morning report
    lists what's done, what was skipped and why."""
    b = load(bid)
    if b['state'] not in ('approved', 'paused', 'running', 'review', 'ready', 'needs you'):
        sys.exit('Approve the scripts first (batch.py approve), or press Go (batch.py go).')
    b['state'], b['reason'], b['started'] = 'running', None, time.time()
    b.setdefault('results', {})
    save(b)
    sim = os.environ.get('NAVI_FAKE_CREDITS')
    sim = int(sim) if sim is not None else None
    bad = not_ready(bid)
    rec = Recorders(b['shared']['video_style'])
    for did in b['items']:
        rec.collect(b)
        save(b)
        if blind.apply_requests(me(), bid):      # A/B/C picks made while another video was recording
            b = load(bid)
            b.setdefault('results', {})
        d = store.demo(did)
        if d['recorded']:
            b['results'].setdefault(did, {'status': 'done', 'why': 'recorded earlier'})
            continue
        folder = store.demo_dir(did)
        if did in bad:
            skip(b, did, d, bad[did])
            continue
        need = credits_needed(did)
        bl = blind.lesson(b, did)
        if bl and bl['status'] == 'waiting':
            b['results'][did] = {'status': 'waiting', 'why': 'waiting for your pick'}
            continue
        left = sim if sim is not None else store.credits_left()
        # a batch cap (Andy, 13 Nov 2026: "stop before spending more than 25,000 credits"): spending is counted from
        # the credits left when the run began; a video that would take it past the cap is skipped, with that reason,
        # and nothing of it is generated (videos after it are still tried: a shorter one may fit)
        cap = credit_cap(b)
        if cap and left is not None:
            b.setdefault('credits_at_start', left)
            spent = b['credits_at_start'] - left
            if need and spent + need > cap:
                skip(b, did, d, f"over the batch's {cap:,}-credit cap: about {spent:,} spent so far and this video needs about "
                                f"{need:,}; nothing of it was generated")
                continue
        if need and (left is None or left - need < B['credit_margin']):
            skip(b, did, d, (f"not enough credits: it needs about {need:,} and {left:,} are left (NAVI keeps {B['credit_margin']:,} spare); "
                             "nothing of it was generated") if left is not None else "the credits left couldn't be read, so nothing was spent")
            continue
        if bl and bl['status'] == 'written':      # blind test: each version voiced once, then it waits for the pick
            store.update_demo(did, {'progress': 'Voice'})
            log(b, f"\"{d['title']}\": voice, {len(bl['letters'])} versions, one take each ({need:,} credits)")
            ready = blind.voice(me(), b, did)
            if sim is not None:
                sim -= need
            if not ready:
                skip(b, did, d, 'the voice failed for every version')
            elif len(ready) == 1:
                blind.pick(me(), bid, did, ready[0], auto=True)
                b = load(bid)
                b.setdefault('results', {})
            else:
                b['results'][did] = {'status': 'waiting', 'why': 'waiting for your pick'}
                store.update_demo(did, {'progress': f"Pick {', '.join(ready[:-1])} or {ready[-1]}"})
                log(b, f"  {len(ready)} versions voiced: waiting for your pick")
                save(b)
            if not (len(ready) == 1):
                continue
            need = 0
        takes = 1 if (blind.lesson(b, did) or {}).get('takes') == 1 else B['takes']
        store.update_demo(did, {'progress': 'Voice'})
        log(b, f"\"{d['title']}\": voice ({need:,} credits)")
        t0 = time.time()
        code, out = step([PY, os.path.join(ROOT, 'scripts', 'voice', 'generate.py'), os.path.join(folder, 'script.json'), '--out', folder,
                          '--takes', str(takes), '--yes'])
        took(b, did, 'voice', t0)
        if code != 0:
            skip(b, did, d, 'the voice failed: ' + (out.strip().splitlines() or [''])[-1][:200])
            continue
        if sim is not None:
            sim -= need
        store.update_demo(did, {'progress': 'Timing'})
        t0 = time.time()
        code, out = step([PY, os.path.join(ROOT, 'scripts', 'timing', 'timing.py'), os.path.join(folder, 'script.json'), folder])
        took(b, did, 'word timing', t0)
        if code != 0 or store._read(os.path.join(folder, 'timing.json'), {}).get('problems'):
            skip(b, did, d, 'the timing found problems (see timing.md)')
            continue
        t0 = time.time()
        quiet = None if rec.jobs else wait_quiet(b)      # with NAVI's own work still going, the Mac won't be quiet
        if quiet:
            log(b, '  ' + quiet)
            took(b, did, 'waiting for a quiet Mac', t0)
        store.update_demo(did, {'progress': 'Recording'})
        log(b, f"  recording" + (' (its video is drawn while the next one is made)' if did != b['items'][-1] else ''))
        save(b)
        rec.start(did, folder, changes_things(did), quiet)
    rec.collect(b, wait=True)
    save(b)
    if blind.apply_requests(me(), bid):
        b = load(bid)
    b['state'], b['finished'] = 'review', time.time()
    wait = blind.waiting(b)
    if wait:
        b['state'], b['reason'] = 'needs you', f"{len(wait)} video{'s are' if len(wait) != 1 else ' is'} waiting for your A/B/C pick"
        log(b, b['reason'][0].upper() + b['reason'][1:] + ': each records as soon as you pick.')
    save(b)
    if not os.environ.get('NAVI_NO_QA') and not wait:
        qa(bid)
        b = load(bid)
    report(b)
    log(b, 'Done. The morning report is batch-report.md.')
    save(b)
    return 0


def report(b):
    """The morning report: what's done, what was skipped and why. Also kept on the batch for the app."""
    done, skipped, waiting = [], [], []
    for did in b['items']:
        d = store.demo(did)
        r = b.get('results', {}).get(did) or ({'status': 'done', 'why': ''} if d['recorded'] else {'status': 'skipped', 'why': 'not reached'})
        (done if r['status'] == 'done' else waiting if r['status'] == 'waiting' else skipped).append((d, r))
    took = (b.get('finished', time.time()) - b.get('started', time.time())) / 60
    lines = [f"# {b['name']}: the morning report", '', f"{len(done)} done, {len(skipped)} skipped" + (f", {len(waiting)} waiting for your pick" if waiting else '') + f", in {took:.0f} min. Nothing was published.", '']
    if done:
        lines += ['## Done (waiting for your review)', ''] + [f"- **{d['title']}**" + (f" ({d['length_s']:.0f} s)" if d.get('length_s') else '')
                                                             + (f": {r['why']}" if r.get('why') else '') for d, r in done] + ['']
    mac = b.get('mac_at_go') or {}
    if mac.get('busy') or mac.get('heavy'):
        lines += [f"**At Go:** {mac['line']}" + (' Join-check failures and slow renders in this batch may come from that.' if mac.get('busy') else ''), '']
    if waiting:
        lines += ['## Waiting for your pick (A, B or C)', ''] + [f"- **{d['title']}**: listen to the versions in the review queue and pick one; it records straight after" for d, r in waiting] + ['']
    lines += blind.report_lines(b)
    if skipped:
        lines += ['## Skipped', ''] + [f"- **{d['title']}**: {r['why']}" for d, r in skipped] + ['']
    titles = {did: store.demo(did)['title'] for did in b['items']}
    q = b.get('qa') or {}
    if q.get('videos'):
        lines += ['## Before you watch', '', q.get('summary', ''), '']
        for v in q['videos']:
            lines.append(f"- **{titles.get(v.get('id'), v.get('id'))}**: {v.get('verdict', '?')}. {v.get('why', '')}"
                         + ''.join(f"\n  - {int(m['t'] // 60)}:{m['t'] % 60:04.1f} {m.get('what', '')}" for m in v.get('moments', []) if isinstance(m.get('t'), (int, float))))
        lines.append('')
    entries = jobs.read_log(jobs_log(b['id']))
    lines += time_lines(b, entries, titles)
    lines += jobs.report_lines(entries, titles)
    open(os.path.join(bdir(b['id']), 'batch-report.md'), 'w').write('\n'.join(lines))
    b['report'] = {'done': [{'id': d['id'], 'title': d['title'], 'why': r.get('why', '')} for d, r in done],
                   'skipped': [{'id': d['id'], 'title': d['title'], 'why': r['why']} for d, r in skipped],
                   'waiting': [{'id': d['id'], 'title': d['title']} for d, r in waiting],
                   'jobs': jobs.summary(entries),
                   'warnings': list(dict.fromkeys([e['warning'] for e in entries if e.get('warning')] + jobs.warnings()))}


def stage_times(b, did, entries):
    """[(stage, seconds)] for one video, start to finish: the model jobs, then voice, timing and the recording's own parts."""
    rows = {}
    for e in entries:
        if e.get('demo') == did:
            k = jobs.LABELS.get(e['job'], e['job']).lower() + (' (line reviews)' if e.get('note') == 'line review' else '')
            rows[k] = rows.get(k, 0) + e.get('seconds', 0)
    out = [[k, round(v, 1)] for k, v in rows.items()]
    for what, secs in b.get('timings', {}).get(did, []):
        if what == 'recording':
            rep = store._read(os.path.join(store.demo_dir(did), 'recording', 'report.json'), {}) or {}
            parts = rep.get('stages') or []
            out += [['recording: ' + w, t] for w, t in parts] or [[what, secs]]
            if parts and secs - sum(t for _, t in parts) > 1:
                out.append(['recording: starting up', round(secs - sum(t for _, t in parts), 1)])
        else:
            out.append([what, secs])
    return out


def time_lines(b, entries, titles):
    mins = lambda s: f'{s:.0f} s' if s < 90 else f'{s / 60:.1f} min'
    lines, any_ = ['## Time per video', ''], False
    whole = [e for e in entries if not e.get('demo')]
    if whole:
        lines.append('Whole batch: ' + '; '.join(f"{jobs.LABELS.get(e['job'], e['job']).lower()} {mins(e.get('seconds', 0))}" for e in whole) + '.')
        lines.append('')
    for did in b['items']:
        rows = stage_times(b, did, entries)
        if not rows:
            continue
        any_ = True
        d = store.demo(did)
        total = sum(t for _, t in rows)
        lines += [f"**{titles.get(did, did)}**" + (f" ({d['length_s']:.0f} s long)" if d.get('length_s') else '') + f": {mins(total)} in all", '',
                  '| Stage | Time |', '|---|---|'] + [f'| {w} | {mins(t)} |' for w, t in rows] + ['']
    return lines if any_ else []


def queue_(bid):
    b = load(bid)
    q = []
    for did in b['items']:
        d = store.demo(did)
        if d['recorded'] and d['review'] != 'approved':
            q.append({'id': did, 'title': d['title'], 'length_s': d['length_s'], 'unsure_blurs': d['unsure_blurs'], 'marks': len(d['marks']),
                      'video': os.path.join(store.demo_dir(did), 'recording', 'recording.mp4'), 'checks_pass': d['checks_pass']})
    for i, x in enumerate(q, 1):
        print(f"{i}. {x['title']} ({x['length_s']:.0f} s), {x['unsure_blurs']} unsure blurs, {x['marks']} marks: {x['video']}")
    if not q:
        print('Nothing waiting for review.')
    return q


def review(bid, did, decision, anyway=False):
    if did not in load(bid)['items']:
        raise ValueError('That video is not in this batch.')
    if decision != 'approve':
        raise ValueError('Use approve, or redo the marked sections with scripts/render/redo.py.')
    d = store.demo(did)
    if d['unsure_blurs'] and not anyway:
        raise ValueError(f"{d['unsure_blurs']} unsure blurs not sorted yet (keep or show each one), or approve --anyway.")
    return store.update_demo(did, {'review': 'approved'})


def export_all(bid):
    import export as ex
    b = load(bid)
    sh = b['shared']
    folder = os.path.join(os.path.expanduser(sh['export_to']), ex.safe_name(b['name']))
    rows = []
    for did in b['items']:
        d = store.demo(did)
        if d['review'] != 'approved':
            continue
        s = d['settings']
        t0 = time.time()
        r = ex.export(script_of(did), store.demo_dir(did), 'recording', s['captions'], s['corner_label'], s['corner_text'], None, folder,
                      None, s.get('speed_copy'), s['caption_look'])
        files = [os.path.basename(f) for f in r['files'].values()]
        store.update_demo(did, {'exports': [{'t': time.time(), 'folder': folder, 'files': files}], 'progress': None})
        rows.append({'title': d['title'], 'length': f"{int(d['length_s'] // 60)}:{int(d['length_s'] % 60):02d}", 'files': files, 'folder': folder})
        took(b, did, 'export', t0)
        log(b, f"Exported \"{d['title']}\"")
    if not rows:
        print('Nothing approved to export yet.')
        return None
    name = ex.safe_name(b['name'])
    with open(os.path.join(folder, f'{name} - list.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['#', 'Title', 'Length', 'Files', 'Folder'])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r['title'], r['length'], '; '.join(r['files']), r['folder']])
    md = [f"# {b['name']}", '', f"{len(rows)} videos, exported {time.strftime('%d %b %Y %H:%M')} to {folder}. Nothing was uploaded.", '']
    md += [f"{i}. **{r['title']}** ({r['length']}): " + ', '.join(f'`{x}`' for x in r['files']) for i, r in enumerate(rows, 1)]
    open(os.path.join(folder, f'{name} - list.md'), 'w').write('\n'.join(md) + '\n')
    b['state'] = 'exported' if all(store.demo(x)['exported'] for x in b['items']) else b['state']
    save(b)
    print(f'Exported {len(rows)} videos and the list to {folder}')
    return {'folder': folder, 'videos': len(rows)}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    n = sub.add_parser('new')
    n.add_argument('--name', required=True)
    n.add_argument('--list', required=True, help='a file with one video per line, or - to read the list from stdin')
    n.add_argument('--site', required=True)
    for k in ('kind', 'voice', 'export-to', 'captions', 'caption-look', 'video-style'):
        n.add_argument('--' + k)
    n.add_argument('--privacy')
    n.add_argument('--speed', type=float)
    n.add_argument('--length', type=float, help='about how long each video should be, in minutes')
    n.add_argument('--no-blind', action='store_true', help='not a real batch: no blind A/B/C tests in it')
    for c in ('status', 'sheet', 'approve', 'run', 'queue', 'export', 'plan', 'preflight', 'write', 'qa', 'report'):
        sub.add_parser(c).add_argument('batch')
    sub.add_parser('mac', help="how busy the Mac is, and which apps to quit before a batch")
    for c in ('blind', 'blind-results'):
        sub.add_parser(c).add_argument('batch', nargs='?')
    pp = sub.add_parser('pick-plan')
    pp.add_argument('batch')
    pp.add_argument('letter')
    pk = sub.add_parser('pick')
    pk.add_argument('batch')
    pk.add_argument('demo')
    pk.add_argument('letter')
    g = sub.add_parser('go')
    g.add_argument('batch')
    g.add_argument('--auto', action='store_true', help='start only if "start without the Go click" is on')
    r = sub.add_parser('review')
    r.add_argument('batch')
    r.add_argument('demo')
    r.add_argument('decision')
    r.add_argument('--anyway', action='store_true')
    a = ap.parse_args()
    try:
        if a.cmd == 'new':
            text = sys.stdin.read() if a.list == '-' else open(a.list).read()
            new(a.name, text, a.site, kind=a.kind, voice=a.voice, export_to=a.export_to, captions=a.captions,
                caption_look=a.caption_look, video_style=a.video_style, privacy_preset=a.privacy, speed_copy=a.speed, no_blind=a.no_blind, length_min=a.length)
        elif a.cmd == 'status':
            status(a.batch)
        elif a.cmd == 'sheet':
            sheet(a.batch)
        elif a.cmd == 'approve':
            print(approve(a.batch))
        elif a.cmd == 'run':
            sys.exit(run(a.batch))
        elif a.cmd == 'blind':
            v = blind.view(load(a.batch))
            if v['plan']:
                print(f"Plan: {v['plan']['status']}" + (f" ({v['plan']['picked']})" if v['plan'].get('picked') else ''))
                for o in v['plan']['options'] if v['plan']['status'] == 'waiting' else []:
                    print(f"\n=== Plan {o['letter']} ===")
                    for pv in o['plan'].get('videos', []):
                        print(f"- {pv.get('id')}: {pv.get('goal')}")
                        for sec in pv.get('sections', []):
                            print(f"    {sec.get('name')}: {sec.get('shows')}")
                    print('  Order: ' + str(o['plan'].get('order_note', '')))
            for l in v['lessons']:
                print(f"\n{l['title']} ({l['demo']}): {l['status']}" + (f" ({l['picked']})" if l.get('picked') else ''))
                for o in l['options'] if l['status'] == 'waiting' else []:
                    print(f"  {o['letter']}: {os.path.join(store.demo_dir(l['demo']), o['audio']) if o['audio'] else 'not voiced'}")
            if v['revealed']:
                print('\n' + '\n'.join(blind.report_lines(load(a.batch))))
        elif a.cmd == 'mac':
            m = store.mac_load()
            print(m['line'])
            for h in m['heavy']:
                print(f"  {h['app']}: {h['cpu']}% of a core")
        elif a.cmd == 'blind-results':
            for kind, rows in blind.tally().items():
                print(('Plans' if kind == 'planning' else 'Scripts') + ': ' + '; '.join(f"{r['arm']} picked {r['picked']} of {r['shown']}" for r in rows))
        elif a.cmd == 'pick-plan':
            print(json.dumps(blind.pick_plan(me(), a.batch, a.letter)))
        elif a.cmd == 'pick':
            print(json.dumps(blind.pick(me(), a.batch, a.demo, a.letter)))
        elif a.cmd == 'write':
            print(json.dumps(write(a.batch)))
        elif a.cmd == 'qa':
            print(json.dumps(qa(a.batch), indent=1))
            b = load(a.batch)
            report(b)
            save(b)
        elif a.cmd == 'report':
            b = load(a.batch)
            report(b)
            save(b)
            print(os.path.join(bdir(a.batch), 'batch-report.md'))
        elif a.cmd == 'plan':
            print(json.dumps(plan(a.batch), indent=1))
        elif a.cmd == 'preflight':
            print(json.dumps(preflight(a.batch), indent=1))
        elif a.cmd == 'go':
            r = go(a.batch, a.auto)
            print(json.dumps({k: v for k, v in r.items() if k != 'preflight'}))
            if r['started']:
                sys.exit(run(a.batch))
            sys.exit(2)
        elif a.cmd == 'queue':
            queue_(a.batch)
        elif a.cmd == 'review':
            print(review(a.batch, a.demo, a.decision, a.anyway)['status'])
        elif a.cmd == 'export':
            export_all(a.batch)
    except ValueError as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
