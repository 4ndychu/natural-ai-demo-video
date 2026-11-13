"""NAVI's per-job models: every job that needs a model runs as its own headless Claude Code subagent
(`claude -p`), with the model and effort that config/defaults.json names for that job ("jobs").

  jobs.py show                          each job's model, effort and fallbacks, plus any warnings
  jobs.py run <job> --prompt-file F     run one job (planning, explore, writing, checks, batch_qa) and print its answer
              [--attended]              a person is at the session (default: headless, nobody watching)
              [--log jobs.jsonl] [--demo ID] [--tools none] [--model ID --effort E]
  jobs.py ping                          ask every model in the config for one word, to see which are available

Rules (Andy, 12 Nov 2026):
- Full model IDs only (claude-opus-5-5), never an alias (opus): an alias moves when a new model ships.
- If a job's model is unavailable, the next one in its "fallback" list runs and a warning goes in the batch report.
- A headless run never falls back to Fable (config "headless_never_fallback_to"); a job whose own model is Fable
  still uses it.
- A model past its warning date (claude-opus-4-6 after 2027-01-15) is flagged wherever it is used.
- Every run is logged with its model, effort, time and tokens (jobs.jsonl in the batch folder; $NAVI_JOBS_LOG).

NAVI_CLAUDE_BIN: another `claude` (the tests use a fake one). NAVI_TODAY: today's date, YYYY-MM-DD (tests).
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CONFIG_PATH = os.path.join(ROOT, 'config', 'defaults.json')
JOBS = ('planning', 'explore', 'writing', 'checks', 'batch_qa')
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')
FULL_ID = re.compile(r'^claude-[a-z]+-\d+-\d+(-\d{8})?$')
LABELS = {'planning': 'Planning', 'explore': 'Exploring', 'writing': 'Writing', 'checks': 'Checks', 'batch_qa': 'Batch check'}

# What each job's subagent may touch: the fewest tools that do the job. No job gets MCP servers, skills, the web, the
# user's own Claude settings or a free shell: only its files and the one or two NAVI scripts it runs. Planning and the
# line reviews get no tools at all (their answer is the result). Fewer tools is also most of the saving in tokens:
# the default tool set and instructions were about 41,000 tokens on every turn; this is about 5,000 (12 Nov 2026).
_PY = 'Bash(.venv/bin/python scripts/{}:*)'
TOOLS = {
    'planning': None,
    'explore': ['Read', 'Write', 'Bash(node scripts/explore/explore.mjs:*)', _PY.format('explore/digest.py'),
                'Bash(node scripts/cleanup/test_products.mjs:*)'],   # only ever deletes NAVI's own "NAVI test" products in a marked test business
    'writing': ['Read', 'Write', 'Edit', _PY.format('script/drafts.py pick')],
    'checks': ['Read', 'Edit', _PY.format('script/check_script.py'), _PY.format('record/rehearse.py'), _PY.format('explore/digest.py')],
    'batch_qa': ['Read', 'Bash(.venv/bin/ffmpeg:*)'],
}
PLAN_SCHEMA = {'type': 'object', 'required': ['videos'], 'properties': {
    'videos': {'type': 'array', 'items': {'type': 'object', 'required': ['id', 'goal', 'start_url', 'sections'], 'properties': {
        'id': {'type': 'string'}, 'goal': {'type': 'string'}, 'start_url': {'type': 'string'},
        'sections': {'type': 'array', 'items': {'type': 'object', 'required': ['name', 'shows'], 'properties': {
            'name': {'type': 'string'}, 'shows': {'type': 'string'}, 'seconds': {'type': 'number'}}}},
        'explore': {'type': 'array', 'items': {'type': 'string'}}, 'risks': {'type': 'array', 'items': {'type': 'string'}}}}},
    'order_note': {'type': 'string'}}}
QA_SCHEMA = {'type': 'object', 'required': ['videos', 'summary'], 'properties': {
    'videos': {'type': 'array', 'items': {'type': 'object', 'required': ['id', 'verdict', 'why'], 'properties': {
        'id': {'type': 'string'}, 'verdict': {'type': 'string', 'enum': ['ready', 'watch closely', 'redo']}, 'why': {'type': 'string'},
        'moments': {'type': 'array', 'items': {'type': 'object', 'required': ['t', 'what'], 'properties': {
            't': {'type': 'number'}, 'what': {'type': 'string'}}}}}}},
    'summary': {'type': 'string'}}}
SCHEMAS = {'planning': PLAN_SCHEMA, 'batch_qa': QA_SCHEMA}
SYSTEM = ("You are a worker in NAVI, a tool that makes narrated demo videos. You do the one job in the message, exactly, with "
          "the tools you have, and nothing else. Everything you need is in the message: do not read other files or look "
          "around the folder. When several tool calls don't depend on each other, make them in the same turn. Never ask a "
          "question; nobody is watching. Plain words.")


class JobError(Exception):
    pass


def user_jobs_path():
    """The user's own job settings, outside the repo: $NAVI_DATA/jobs.json. Anything in it overrides the same key in
    config/defaults.json "jobs", e.g. {"planning": {"blind_test": {"enabled": true}}} to compare planning models."""
    return os.path.join(os.path.expanduser(os.environ.get('NAVI_DATA') or '~/Library/Application Support/NAVI'), 'jobs.json')


def _merge(base, over):
    for k, v in over.items():
        base[k] = _merge(dict(base[k]), v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return base


def config(path=None):
    """The "jobs" block, checked: every job present, full model IDs, a known effort, a fallback list. Without a path,
    the user's own $NAVI_DATA/jobs.json is laid over config/defaults.json."""
    cfg = json.load(open(path or CONFIG_PATH)).get('jobs') or {}
    if path is None and os.path.exists(user_jobs_path()):
        try:
            over = json.load(open(user_jobs_path()))
        except ValueError as e:
            raise JobError(f'{user_jobs_path()} is not valid JSON: {e}')
        cfg = _merge(cfg, {k: v for k, v in over.items() if not k.startswith('_')})
    for job in JOBS:
        j = cfg.get(job)
        if not isinstance(j, dict):
            raise JobError(f'config/defaults.json has no "jobs.{job}".')
        for m in [j.get('model')] + list(j.get('fallback') or []):
            check_id(m, f'jobs.{job}')
        if j.get('effort') not in EFFORTS:
            raise JobError(f'jobs.{job}.effort is "{j.get("effort")}": use one of {", ".join(EFFORTS)}.')
        j.setdefault('fallback', [])
        for arm in (j.get('blind_test') or {}).get('arms', []):
            check_id(arm.get('model'), f'jobs.{job}.blind_test')
            if arm.get('effort') not in EFFORTS:
                raise JobError(f'jobs.{job}.blind_test: effort "{arm.get("effort")}" is not one of {", ".join(EFFORTS)}.')
    return cfg


def check_id(model, where='model'):
    if not isinstance(model, str) or not FULL_ID.match(model):
        raise JobError(f'{where}: "{model}" is not a full model ID (like claude-opus-5-5). Aliases are never used.')
    return model


def today():
    t = os.environ.get('NAVI_TODAY')
    return datetime.date.fromisoformat(t) if t else datetime.date.today()


def _models_in(node, path=''):
    """Every model named anywhere under "jobs" (a job's model, its fallbacks, blind-test arms): [(where, id)]."""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            p = f'{path}.{k}' if path else k
            if k == 'model' and isinstance(v, str):
                out.append((path, v))
            elif k == 'fallback' and isinstance(v, list):
                out += [(f'{path} (fallback)', m) for m in v]
            else:
                out += _models_in(v, p)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += _models_in(v, f'{path}[{i + 1}]')
    return out


def warnings(cfg=None, day=None):
    """Models past their warning date, wherever the config uses them. Plain lines for the report and the app."""
    cfg, day, out = cfg or config(), day or today(), []
    for w in cfg.get('warn_after', []):
        after = datetime.date.fromisoformat(w['after'])
        if day <= after:
            continue
        used = sorted({where for where, m in _models_in({k: v for k, v in cfg.items() if k != 'warn_after'}) if m == w['model']})
        if used:
            out.append(f"{w['model']} is still used by {', '.join(used)} and it is past {after.strftime('%-d %b %Y')}"
                       + (f" ({w['why']})" if w.get('why') else '') + ': change it in config/defaults.json.')
    return out


def chain(job, headless=True, cfg=None, model=None, effort=None, fallback=None):
    """The models to try, in order: [(model, effort)]. In a headless run a fallback is never Fable."""
    cfg = cfg or config()
    j = cfg[job]
    first = check_id(model, 'model') if model else j['model']
    never = cfg.get('headless_never_fallback_to', []) if headless else []
    rest = [m for m in (j['fallback'] if fallback is None else fallback) if m != first and m not in never]
    return [(m, effort or j['effort']) for m in [first] + rest]


def claude_bin():
    exe = os.environ.get('NAVI_CLAUDE_BIN') or shutil.which('claude')
    if not exe:
        raise JobError('The claude command was not found, so no job can run.')
    return exe


UNAVAILABLE = re.compile(r'unrecognized_model|not_found_error|model[^.\n]{0,60}(not (be )?(found|available|exist|supported)|unavailable|'
                         r'deprecated|retired|no longer|does not exist|access)|overloaded|do(es)? not have access', re.I)


def _result(stdout):
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith('{'):
            try:
                v = json.loads(line)
            except ValueError:
                continue
            if isinstance(v, dict) and v.get('type') == 'result':
                return v
    return None


def _once(model, effort, prompt, tools, cwd, timeout, add_dirs, schema=None):
    """One headless subagent. Returns (state, entry) with state 'ok', 'unavailable' or 'failed'."""
    cmd = [claude_bin(), '-p', '--model', model, '--effort', effort, '--output-format', 'json', '--strict-mcp-config',
           '--disable-slash-commands', '--no-session-persistence', '--permission-mode', 'dontAsk',
           '--setting-sources', '', '--system-prompt', SYSTEM]
    if tools:
        cmd += ['--tools', ','.join(dict.fromkeys(t.split('(')[0] for t in tools)), '--allowedTools', *tools]
        for d in add_dirs:
            cmd += ['--add-dir', d]
    else:
        cmd += ['--tools', '']
    if schema:      # the answer is data (a plan, a verdict): the CLI holds the model to this shape
        cmd += ['--json-schema', json.dumps(schema)]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        out, err = r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 'failed', {'seconds': round(time.time() - t0, 1), 'error': f'no answer after {int(timeout / 60)} min'}
    res = _result(out) or {}
    used = res.get('modelUsage') or {}
    e = {'seconds': round(time.time() - t0, 1),
         'tokens_in': sum(u.get('inputTokens', 0) + u.get('cacheReadInputTokens', 0) + u.get('cacheCreationInputTokens', 0) for u in used.values()),
         'tokens_out': sum(u.get('outputTokens', 0) for u in used.values()),
         # tokens_in counts every turn's re-read of the same context (cache reads, billed at about a tenth); the real
         # work is what was new: fresh input, what was written to the cache once, and the output
         'tokens_fresh': sum(u.get('inputTokens', 0) for u in used.values()),
         'tokens_cache_write': sum(u.get('cacheCreationInputTokens', 0) for u in used.values()),
         'tokens_cache_read': sum(u.get('cacheReadInputTokens', 0) for u in used.values()),
         'cost_usd': round(res.get('total_cost_usd') or 0, 4), 'turns': res.get('num_turns'),
         'answered_by': sorted(used, key=lambda m: -used[m].get('outputTokens', 0)), 'text': res.get('result') or ''}
    if schema:
        e['data'] = res.get('structured_output') if isinstance(res.get('structured_output'), dict) else last_json(e['text'])
    denied = [str((d.get('tool_input') or {}).get('command') or d.get('tool_name'))[:200] for d in res.get('permission_denials') or []]
    if denied:
        e['denied'] = denied    # what the subagent tried that its job doesn't allow (it carried on without)
    if res and not res.get('is_error') and res.get('subtype') == 'success':
        return 'ok', e
    why = (str(res.get('result') or '') + ' ' + err).strip()
    e['error'] = why[-300:] or 'no answer'
    gone = res.get('api_error_status') in (404, 529, 503) or UNAVAILABLE.search(why)
    return ('unavailable' if gone else 'failed'), e


def doc(path, keep=None):
    """A rules file for a prompt: all of it, or only the sections whose heading starts with one of `keep` (a "## "
    heading brings its "### " parts with it). So a job loads the rules it works to and nothing else."""
    text = open(os.path.join(ROOT, path)).read()
    if keep:
        parts, cur, on, level = [], [], False, 0
        for ln in text.splitlines():
            m = re.match(r'^(#{1,3}) (.*)', ln)
            if m:
                lv = len(m.group(1))
                if any(m.group(2).startswith(k) for k in keep):
                    on, level = True, lv
                elif on and lv <= level:
                    on = False
            if on:
                parts.append(ln)
        text = '\n'.join(parts)
    return f'<file path="{path}">\n{text.strip()}\n</file>'


def attach(path, label=None, limit=60000):
    """A work file, inside the prompt, so the subagent doesn't spend a turn reading it."""
    try:
        text = open(path).read()
    except OSError:
        return f'<file path="{label or path}">(not there)</file>'
    return f'<file path="{label or path}">\n{text[:limit].strip()}\n</file>'


def last_json(text):
    """The last JSON object in an answer (a job whose answer is its result), or None."""
    dec, last = json.JSONDecoder(), None
    whole = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip())
    try:
        v = json.loads(whole)
        if isinstance(v, dict):
            return v
    except ValueError:
        pass
    i = text.find('{')
    while i >= 0:
        try:
            v, end = dec.raw_decode(text[i:])
            if isinstance(v, dict):
                last = v
                i = text.find('{', i + end)
                continue
        except ValueError:
            pass
        i = text.find('{', i + 1)
    return last


def log_path(explicit=None):
    return explicit or os.environ.get('NAVI_JOBS_LOG')


def run(job, prompt, *, headless=True, tools='job', cwd=None, timeout=None, log=None, demo=None, note=None, model=None,
        effort=None, fallback=None, add_dirs=(), schema=None):
    """Run one job as a subagent on its configured model. Falls back down the job's list when a model is unavailable,
    and says so. Returns the log entry ({job, model, effort, seconds, tokens_in, tokens_out, warning, text, ...});
    raises JobError when no model could do it. `tools`: 'job' (the job's own set), None (no tools), or a list."""
    cfg = config()
    if job not in JOBS:
        raise JobError(f'No job called {job}.')
    tl = TOOLS[job] if tools == 'job' else tools
    tried, entry = [], None
    for m, eff in chain(job, headless, cfg, model, effort, fallback):
        state, e = _once(m, eff, prompt, tl, cwd or ROOT, timeout or cfg.get('timeout_min', 30) * 60, [d for d in add_dirs if d], schema)
        entry = {'t': time.time(), 'job': job, 'demo': demo or os.environ.get('NAVI_JOBS_DEMO') or None, 'note': note, 'model': m, 'effort': eff, 'wanted': tried[0] if tried else m,
                 'headless': headless, 'ok': state == 'ok', **e}
        if state == 'ok':
            if tried:
                entry['warning'] = (f"{LABELS[job]}: {', '.join(tried)} {'was' if len(tried) == 1 else 'were'} unavailable, "
                                    f"so {m} did it instead.")
            elif entry['answered_by'] and m not in entry['answered_by']:
                entry['warning'] = f"{LABELS[job]}: asked for {m}, but {', '.join(entry['answered_by'])} answered."
            break
        tried.append(m)
        _log(dict(entry, text=''), log)
        if state == 'failed':
            raise JobError(f"{LABELS[job]} failed on {m}: {e.get('error')}")
    else:
        skipped = [x for x in (cfg[job]['fallback'] if fallback is None else fallback) if x in cfg.get('headless_never_fallback_to', [])] if headless else []
        raise JobError(f"{LABELS[job]}: no model was available (tried {', '.join(tried)})"
                       + (f"; {', '.join(skipped)} is never a fallback when nobody is watching" if skipped else '') + '.')
    for w in warnings(cfg):
        if entry['model'] in w:
            entry['warning'] = (entry.get('warning', '') + ' ' + w).strip()
    _log(entry, log)
    return entry


def _log(entry, explicit=None):
    path = log_path(explicit)
    if not path:
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    slim = dict(entry, text=(entry.get('text') or '')[:1500])
    with open(path, 'a') as f:
        f.write(json.dumps(slim, ensure_ascii=False) + '\n')


def read_log(path):
    out = []
    try:
        for line in open(path):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    except OSError:
        pass
    return out


def _mins(s):
    return f'{s:.0f} s' if s < 90 else f'{s / 60:.1f} min'


def new_in(e):
    """Input tokens that were new: fresh input plus what was written to the cache once. Without cache re-reads."""
    return e.get('tokens_fresh', 0) + e.get('tokens_cache_write', 0) if 'tokens_fresh' in e else e.get('tokens_in', 0)


def report_lines(entries, titles=None, cfg=None):
    """The "Models" part of the batch report: warnings first, then one row per job run."""
    titles = titles or {}
    warns = [w for w in dict.fromkeys([e['warning'] for e in entries if e.get('warning')] + warnings(cfg))]
    lines = ['## Models', '']
    if warns:
        lines += [f'- **Warning:** {w}' for w in warns] + ['']
    if not entries:
        return lines + ['No model jobs ran in this batch.', '']
    lines += ['| Job | Video | Model | Effort | Time | New tokens in | Tokens out | Re-read from cache |', '|---|---|---|---|---|---|---|---|']
    rows, small = [], {}
    for e in entries:      # the small repeated runs (a line review per draft) are one row per video and model
        k = (e['job'], e.get('note'), e.get('demo'), e['model'], e['effort'], bool(e.get('ok')))
        if e.get('note') and k in small:
            r = small[k]
            r['n'] += 1
            for f in ('seconds', 'tokens_in', 'tokens_out', 'tokens_fresh', 'tokens_cache_write', 'tokens_cache_read', 'cost_usd'):
                r[f] = r.get(f, 0) + e.get(f, 0)
            continue
        r = dict(e, n=1)
        rows.append(r)
        if e.get('note'):
            small[k] = r
    for e in rows:
        if e.get('note'):
            e = dict(e, note=e['note'] + (f", {e['n']} times" if e['n'] > 1 else ''))
        lines.append(f"| {LABELS.get(e['job'], e['job'])}{' (' + e['note'] + ')' if e.get('note') else ''} | {titles.get(e.get('demo'), e.get('demo') or 'whole batch')} "
                     f"| {e['model']}{'' if e.get('ok') else ' (unavailable)' if 'error' in e else ''} | {e['effort']} | {_mins(e.get('seconds', 0))} "
                     f"| {new_in(e):,} | {e.get('tokens_out', 0):,} | {e.get('tokens_cache_read', 0):,} |")
    by, vids = {}, {e.get('demo') for e in entries if e.get('demo')}
    for e in entries:
        t = by.setdefault(e['job'], [0, 0, 0, 0, 0])
        t[0] += 1
        t[1] += e.get('seconds', 0)
        t[2] += new_in(e)
        t[3] += e.get('tokens_out', 0)
        t[4] += e.get('cost_usd', 0)
    lines += ['', 'Totals: ' + '; '.join(f"{LABELS.get(j, j).lower()} {n} run{'s' if n != 1 else ''}, {_mins(s)}, {i:,} new in / {o:,} out"
                                           for j, (n, s, i, o, c) in by.items()) + '.']
    ti, to, tc = sum(v[2] for v in by.values()), sum(v[3] for v in by.values()), sum(v[4] for v in by.values())
    n = max(len(vids), 1)
    lines += ['', f"Per video ({n}): about {ti // n:,} new tokens in and {to // n:,} out; about ${tc / n:.2f} at list prices "
              f"(${tc:.2f} for the batch). \"New tokens in\" leaves out re-reads of the same context from the cache, which are "
              "billed at about a tenth.", '']
    return lines


def summary(entries):
    """For the app and batch.json: [{job, demo, model, effort, seconds, tokens_in, tokens_out, ok, warning}]."""
    keep = ('t', 'job', 'demo', 'note', 'model', 'effort', 'seconds', 'tokens_out', 'tokens_cache_read', 'cost_usd', 'ok', 'warning')
    return [{**{k: e.get(k) for k in keep}, 'tokens_in': new_in(e)} for e in entries]


def show(cfg=None):
    cfg = cfg or config()
    never = cfg.get('headless_never_fallback_to', [])
    rows = []
    for job in JOBS:
        j = cfg[job]
        fb = ', '.join(j['fallback']) or 'none'
        skip = [m for m in j['fallback'] if m in never]
        rows.append(f"{LABELS[job]:12} {j['model']:20} {j['effort']:7} then {fb}" + (f" (not {', '.join(skip)} when nobody is watching)" if skip else ''))
    return rows, warnings(cfg)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('show')
    sub.add_parser('ping')
    r = sub.add_parser('run')
    r.add_argument('job', choices=JOBS)
    r.add_argument('--prompt-file', required=True, help='the prompt, or - for stdin')
    r.add_argument('--attended', action='store_true', help='a person is at the session (Fable may be a fallback)')
    r.add_argument('--log')
    r.add_argument('--demo')
    r.add_argument('--tools', choices=['job', 'none'], default='job')
    r.add_argument('--model')
    r.add_argument('--effort', choices=EFFORTS)
    a = ap.parse_args()
    try:
        if a.cmd == 'show':
            rows, warns = show()
            print('\n'.join(rows))
            for w in warns:
                print('WARNING: ' + w)
        elif a.cmd == 'ping':
            cfg = config()
            bad = 0
            for m in dict.fromkeys(m for _, m in _models_in({k: v for k, v in cfg.items() if k != 'warn_after'})):
                state, e = _once(m, 'low', 'Reply with the single word ok.', None, ROOT, 120, [])
                bad += state != 'ok'
                print(f"{m:22} {'available' if state == 'ok' else state + ': ' + e.get('error', '')[:120]}")
            sys.exit(1 if bad else 0)
        else:
            prompt = sys.stdin.read() if a.prompt_file == '-' else open(a.prompt_file).read()
            e = run(a.job, prompt, headless=not a.attended, tools=None if a.tools == 'none' else 'job', log=a.log, demo=a.demo,
                    model=a.model, effort=a.effort)
            if e.get('warning'):
                print('WARNING: ' + e['warning'], file=sys.stderr)
            print(f"[{e['job']}: {e['model']} / {e['effort']}, {_mins(e['seconds'])}, {new_in(e):,} new in / {e['tokens_out']:,} out]", file=sys.stderr)
            print(e['text'])
    except JobError as err:
        sys.exit(str(err))


if __name__ == '__main__':
    main()
