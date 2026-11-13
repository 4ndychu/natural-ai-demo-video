// NAVI app <-> engine (Phase 7).
// Served by NAVI's local server (scripts/app/server.py, http://127.0.0.1:4747/), the app shows the engine's real state
// and sends what the user does to it (docs/app-api.md). Opened as a file (file://), or with ?sample, it keeps the
// sample data, so the prototype and the layout check (ui/tests/layout-check.js) still work.
(function () {
  const q = new URLSearchParams(location.search);
  const LIVE = /^https?:$/.test(location.protocol) && !q.has('sample');
  const LENS = [1, 3, 5, 8];
  const WHO = ['beginners', 'some experience', 'pros'];
  const PRESET_IN = { strict: 'strict', standard: 'standard', test_account: 'test' };
  const PRESET_OUT = { strict: 'strict', standard: 'standard', test: 'test_account' };
  const COVERS = ['assets/cover-1.jpg', 'assets/cover-3.jpg', 'assets/cover-4.jpg'];
  const BUSY = /writing|recording|voicing|making|timing|rewriting|exporting|rendering|redoing|checking/i;
  const hash = (s) => { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return Math.abs(h); };
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  async function post(type, body) {
    const r = await fetch('/api/action', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.assign({ type: type }, body || {})) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || 'NAVI didn’t accept that.');
    return j;
  }

  const methods = {
    // ---- start and keep in step ------------------------------------------------------------------------------
    liveReset() {
      this.live = true;
      Object.assign(this.state, { demos: [], batches: [], sites: [], credits: 0, keyOn: false, tools: 'idle', loading: true, heardVoices: {}, hide: [] });
    },
    async engineBoot(startOn) {
      try { await this.refresh(true); } catch (e) { this.setState({ loading: false }); this.say('Can’t reach NAVI’s engine. Is the server running?'); return; }
      const s = this.engineState;
      const first = !s.key.stored || !s.tools_ready;
      const want = startOn && startOn !== 'welcome' ? startOn : (first ? 'welcome' : 'home');
      this.setState({ loading: false, screen: ['home', 'welcome', 'settings', 'new'].indexOf(want) >= 0 ? want : 'home' });
      this.every('poll', 2000, () => { if (!document.hidden) this.refresh().catch(() => {}); });
      document.addEventListener('visibilitychange', () => { if (!document.hidden) this.refresh().catch(() => {}); });
      this.bindVideo();
    },
    async refresh(force) {
      if (!force && (this.inflight > 0 || Date.now() - (this.lastSend || 0) < 900)) return;
      const r = await fetch('/api/state', { cache: 'no-store' });
      if (!r.ok) throw new Error('state');
      const s = await r.json();
      if (!force && (this.inflight > 0 || Date.now() - (this.lastSend || 0) < 900)) return;
      this.fromEngine(s);
    },
    async act(type, body, opts) {
      opts = opts || {};
      this.inflight = (this.inflight || 0) + 1; this.lastSend = Date.now();
      try {
        const res = await post(type, body);
        if (res.demo) this.mergeDemo(res.demo);
        if (opts.ok) this.say(typeof opts.ok === 'function' ? opts.ok(res) : opts.ok);
        return res;
      } catch (e) {
        if (!opts.quiet) this.say(e.message || 'Something went wrong.');
        if (opts.fail) opts.fail(e);
        return null;
      } finally {
        this.inflight--; this.lastSend = Date.now();
        clearTimeout(this.refreshSoon); this.refreshSoon = setTimeout(() => this.refresh().catch(() => {}), 950);
      }
    },
    // Undo-able removals (a login, the key, saved settings) wait until their toast is gone before NAVI does them.
    deferred(name, run) {
      this.pending = this.pending || {};
      if (this.pending[name]) clearTimeout(this.pending[name].t);
      const t = setTimeout(() => { delete this.pending[name]; run(); }, 4600);
      this.pending[name] = { t: t };
      return () => { if (this.pending[name]) { clearTimeout(this.pending[name].t); delete this.pending[name]; } };
    },
    fromEngine(s) {
      this.engineState = s;
      const st = this.state; const st0 = s.settings;
      const prevById = {}; st.demos.forEach((d) => { prevById[d.id] = d; });
      const demos = s.demos.map((d) => this.toAppDemo(d, prevById[d.id]));
      const byId = {}; demos.forEach((d) => { byId[d.id] = d; });
      this.applying = true;
      const patch = {
        demos: demos,
        batches: (s.batches || []).map((b) => this.toAppBatch(b, byId)),
        credits: s.key.credits_left || 0, keyOn: !!s.key.works && !(this.pending && this.pending.key), keyStored: !!s.key.stored, keyProblem: s.key.problem || '',
        tools: s.tools_ready ? 'done' : (st.tools === 'busy' || st.tools === 'ask' ? st.tools : 'idle'),
        sites: s.logins.filter((l) => !(this.pending && this.pending['site:' + l.site + '/' + l.seat])).map((l) => ({ u: l.site, seat: l.seat, label: l.label, home: l.home, saved: !!l.saved, note: l.saved ? 'Saved ' + l.saved : '',
          status: s.logins_checking && l.saved && l.status !== 'window open' ? 'checking' : l.status, ago: l.checked ? this.ago(l.checked) : '',
          biz: (l.businesses || []).map((b) => b.name + (b.test ? ' (test)' : ' (real)')).join(' and ') })),
        loginsChecking: !!s.logins_checking,
        defVoice: st0.voice, defCap: st0.captions, defCorner: st0.corner_label, defCornerText: st0.corner_text,
        defStyle: st0.video_style, defLook: st0.caption_look, defSpeed: st0.speed_copy || null,
        creditLimit: st0.credit_limit, autoGo: !!st0.auto_go,
        jobs: (s.jobs || []).map((j) => ({ label: j.label, model: j.model, effort: j.effort, then: (j.fallback || []).join(', ') })), jobWarnings: s.job_warnings || []
      };
      if (st0.speed_copy) patch.defSpeedDraft = String(st0.speed_copy);
      if (st0.credit_limit != null && Number(String(st.limitDraft || '').replace(/[,\s]/g, '')) !== st0.credit_limit) patch.limitDraft = String(st0.credit_limit);
      // Settings open: check the logins live (headless) when a check is missing or over 10 minutes old
      if (this.state.screen === 'settings' && !s.logins_checking && Date.now() - (this.loginCheckAt || 0) > 600000 &&
          s.logins.some((l) => l.saved && (!l.checked || Date.now() / 1000 - l.checked > 600))) {
        this.loginCheckAt = Date.now();
        this.act('logins.check', {}, { quiet: true });
      }
      // Recording progress from the engine ("Recording 4 of 9") moves Record's section list.
      const cd = s.demos.find((d) => d.id === st.cur);
      const m = cd && cd.progress && /(\d+)\s*(?:of|\/)\s*(\d+)/.exec(cd.progress);
      if (m && !cd.recorded) patch.recPos = Math.max(0, Number(m[1]) - 1);
      // A line Claude was asked to rewrite has changed: stop showing "Rewriting this line…".
      const pl = this.pendingLine;
      if (pl) { const sec = (cd && cd.id === pl.id ? cd.script_sections || [] : [])[pl.i]; if ((sec && sec.talk !== pl.v) || Date.now() - pl.at > 180000) { this.pendingLine = null; patch.scPending = null; if (sec && sec.talk !== pl.v) setTimeout(() => this.say('Line rewritten'), 0); } }
      if (st.demos.length === 0 || !byId[st.cur]) { if (st.screen === 'demo' && !byId[st.cur]) patch.screen = 'home'; }
      this.lastSettings = this.settingsOf(Object.assign({}, st, patch));
      this.setState(patch);
      this.applying = false;
      const D = byId[st.cur];
      if (D && D.id !== this.syncedDemo) this.syncDemoLocal(D);
    },
    toAppDemo(d, prev) {
      const secs = d.script_sections || [];
      if (secs.length) this.scripts[d.id] = secs.map((x) => ({ n: x.title, name: x.name, d: Math.max(2, Math.round(x.seconds)), v: x.talk, c: x.caption, cost: x.cost }));
      else delete this.scripts[d.id];
      const idx = {}; secs.forEach((x, i) => { idx[x.name] = i; });
      const starts = []; let acc = 0; secs.forEach((x) => { starts.push(acc); acc += Math.max(2, Math.round(x.seconds)); });
      const secAt = (t) => { for (let i = starts.length - 1; i >= 0; i--) if (t >= starts[i]) return i; return 0; };
      const notes = {};
      (d.marks || []).forEach((m, ei) => { const k = idx[m.section] != null ? idx[m.section] : secAt(m.t); (notes[k] = notes[k] || []).push({ t: m.t, text: m.text, ei: ei }); });
      const ss = d.settings || {};
      const exportsN = (d.exports || []).length; const last = exportsN ? d.exports[exportsN - 1] : null;
      const recReq = !!(prev && prev.recReq && !d.recorded && !d.voiced);
      const max = !d.written || !d.script_approved ? 0 : (d.review === 'approved' || d.exported) ? 5 : d.recorded ? 4 : (d.voiced || recReq || (d.progress && BUSY.test(d.progress))) ? 3 : 2;
      const date = (t) => new Date(t * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      const exportedOn = last ? date(last.t) : '';
      const status = d.progress || ({ 'Writing script': 'Claude is writing the script', 'Script ready to read': 'Read the script →', 'Script has problems': 'Claude is fixing the script', 'Script approved': 'Pick the voice →', 'Recording next': 'Ready to record →', 'Ready to watch': 'Watch the draft →', 'Ready to export': 'Export it →', 'Exported': 'Exported ' + exportedOn + ' · Open the video →' }[d.status] || d.status);
      const dot = d.exported ? 'done' : BUSY.test(status) || status === 'Claude is writing the script' ? 'busy' : 'ready';
      const lenIdx = (() => { const m = d.length_min || 1; let b = 0; LENS.forEach((x, i) => { if (Math.abs(x - m) < Math.abs(LENS[b] - m)) b = i; }); return b; })();
      const p = prev || {};
      return Object.assign({}, p, {
        id: d.id, title: d.title, what: d.what || '', site: d.site || '',
        seat: d.seat ? d.seat.label.replace(/ \((test|real) business\)/, '') : '', seatSaved: d.seat ? !!d.seat.login_saved : null,
        seatKey: d.seat && d.seat.site && d.seat.seat ? d.seat.site + '/' + d.seat.seat : '', len: lenIdx, who: Math.max(0, WHO.indexOf(String(d.audience || '').toLowerCase())),
        voice: d.voice || 'alex', model: ss.voice_model || 'v4', kind: d.kind || 'saas', max: max, cover: p.cover || COVERS[hash(d.id) % 3],
        status: status, dot: dot, recorded: !!d.recorded, written: !!d.written, exported: !!d.exported, exportedOn: exportedOn, exportFolder: last ? last.folder : '',
        dirty: exportsN > (p.exportsN || 0) ? false : !!p.dirty, exportsN: exportsN, exporting: exportsN > (p.exportsN || 0) ? false : !!p.exporting, recReq: recReq,
        notes: notes, blurs: (d.blurs || []).filter((b) => b.unsure).map((b) => ({ id: b.id, t: this.fmt(b.t || 0), what: b.what, s: b.s || '' })),
        capMode: ss.captions, corner: ss.corner_label, cornerText: ss.corner_text || '', style: ss.video_style, look: ss.caption_look, speed: ss.speed_copy || null, p720: !!ss.preview_720p,
        video: d.video ? '/media/' + d.id + '/' + d.video : null, cost: d.voice_cost || 0, lengthS: d.length_s, reminder: d.privacy_reminder || '', progress: d.progress || '',
        privacy: { preset: ss.privacy_preset, custom: ss.privacy_custom || {}, hide: ss.hide_words || [] }, sliders: ss.sliders || {},
        scriptCheck: d.script_check, scriptApproved: !!d.script_approved, review: d.review, batchOf: d.batch || null, lines: {}, engine: true
      });
    },
    toAppBatch(b, byId) {
      // blind A/B/C picks, by letter only (the engine never sends which model made which before every pick is made)
      const bv = b.blind_view || {}; const bl = { lessons: {}, plan: null, revealed: bv.revealed || null };
      (bv.lessons || []).forEach((l) => { bl.lessons[l.demo] = { status: l.status, picked: l.picked || '', options: (l.options || []).map((o) => ({ letter: o.letter, audio: o.audio ? '/media/' + l.demo + '/' + o.audio : '', seconds: o.seconds || 0, lines: (o.sections || []).map((x) => x.talk) })) }; });
      if (bv.plan) bl.plan = { status: bv.plan.status, picked: bv.plan.picked || '', options: (bv.plan.options || []).map((o) => ({ letter: o.letter, note: (o.plan || {}).order_note || '', videos: ((o.plan || {}).videos || []).map((v) => ({ t: (byId[v.id] || {}).title || v.id, goal: v.goal || '', sections: (v.sections || []).map((x) => x.shows || x.name) })) })) };
      const rn = b.runner || null;
      const items = (b.items || []).map((id, i) => {
        const D = byId[id] || {};
        const res = (b.results || {})[id] || {};
        const pk = bl.lessons[id];
        const noScript = !D.written && (b.written || {})[id] && (b.written || {})[id].why;   // its script couldn't be written: skipped, never blocking the rest
        const st = pk && pk.status === 'waiting' ? 'pick' : noScript ? 'skipped' : !D.written ? 'writing' : D.exported ? 'exported' : D.review === 'approved' ? 'approved' : D.recorded ? 'recorded' : res.status === 'skipped' ? 'skipped' : (D.progress && BUSY.test(D.progress)) ? 'recording' : b.state === 'writing' || b.state === 'approve' || b.state === 'ready' || b.state === 'needs you' ? 'script' : 'waiting';
        return { t: D.title || id, lesson: 'Lesson ' + (i + 1), min: (this.engineState.demos.find((x) => x.id === id) || {}).length_min || 3, st: st, did: id,
          seat: D.seat || '', seatKey: D.seatKey || '', cost: D.cost || 0, why: res.why || (noScript ? 'No script: ' + noScript : '') };
      });
      // the Go screen: the logins this batch needs, with their live status
      const logins = [];
      items.forEach((x) => { if (x.seatKey && !logins.some((l) => l.key === x.seatKey)) { const l = (this.engineState.logins || []).find((y) => y.site + '/' + y.seat === x.seatKey) || {}; const [site, seat] = x.seatKey.split('/'); logins.push({ key: x.seatKey, site: site, seat: seat, label: site + ' · ' + (l.label || seat), status: this.engineState.logins_checking && l.saved ? 'checking' : (l.status || 'needs login'), home: l.home || 'https://' + site + '/' }); } });
      const sh = b.shared || {};
      const planWaiting = !!(bl.plan && bl.plan.status === 'waiting'); const picking = items.some((x) => x.st === 'pick');
      const stage = planWaiting ? 'writing' : b.state === 'needs you' && (picking || b.started) ? 'recording' : b.state === 'writing' ? (items.length && items.every((x) => x.st !== 'writing') ? 'approve' : 'writing') : b.state === 'ready' || b.state === 'needs you' ? 'approve' : b.state === 'approved' || b.state === 'running' || b.state === 'paused' ? 'recording' : b.state === 'exported' ? 'done' : 'review';
      return { id: b.id, name: b.name, site: b.site, voice: sh.voice || 'alex', kind: sh.kind || 'course', preset: PRESET_IN[sh.privacy_preset] || 'standard', folder: (sh.export_to || '~/Movies/NAVI') + '/' + b.name, stage: rn && rn.paused && rn.phase === 'writing' ? 'writing' : stage, paused: b.state === 'paused' || (rn && rn.paused) ? (/credit/i.test(b.reason || '') ? 'credits' : true) : false,
        blind: bl, runner: rn ? { alive: !!rn.alive, awake: !!rn.awake, line: rn.line || '', waitingFor: rn.waiting_for || '', at: (rn.position || {}).at || 0, total: (rn.position || {}).total || 0 } : null, items: items, engine: true,
        mac: b.mac ? { line: b.mac.line, busy: !!b.mac.busy, heavy: (b.mac.heavy || []).map((h) => h.app) } : null,
        logins: logins, needsYou: b.state === 'needs you' && !planWaiting && !picking && !b.started ? b.reason || '' : '', report: b.report || null };
    },
    mergeDemo(d) {
      const st = this.state; const prev = st.demos.find((x) => x.id === d.id);
      const nd = this.toAppDemo(d, prev);
      this.applying = true;
      this.setState({ demos: prev ? st.demos.map((x) => x.id === d.id ? nd : x) : [nd].concat(st.demos) });
      this.applying = false;
      return nd;
    },
    // When a demo opens, its privacy and fine-tune settings become the controls' values.
    syncDemoLocal(D) {
      this.syncedDemo = D.id;
      const pv = D.privacy || {}; const preset = PRESET_IN[pv.preset] || 'standard';
      const shown = Object.assign({}, PRESETS[preset], pv.custom || {});
      const vals = Object.assign(this.recFor(D.voice, D.kind), D.sliders || {});
      this.applying = true;
      this.setState({ shown: shown, hide: (pv.hide || []).slice(), vals: vals });
      this.applying = false;
      this.lastLocal = this.localOf(this.state);
    },
    // ---- what the user changed, sent on -----------------------------------------------------------------------
    settingsOf(st) { return { voice: st.defVoice, captions: st.defCap, corner_label: st.defCorner, corner_text: st.defCornerText, video_style: st.defStyle, caption_look: st.defLook, speed_copy: st.defSpeed || null, credit_limit: st.creditLimit, auto_go: !!st.autoGo }; },
    localOf(st) { const preset = this.presetOf(st.shown); return { privacy_preset: PRESET_OUT[preset] || 'standard', privacy_custom: preset === 'custom' ? Object.assign({}, st.shown) : {}, hide_words: st.hide.slice(), sliders: Object.assign({}, st.vals) }; },
    watchLocal() {
      if (!this.live || this.applying || this.state.loading) return;
      const st = this.state;
      const s = this.settingsOf(st);
      if (this.lastSettings && !same(s, this.lastSettings)) {
        const patch = {}; Object.keys(s).forEach((k) => { if (!same(s[k], this.lastSettings[k])) patch[k] = s[k]; });
        this.lastSettings = s;
        this.setPatch = Object.assign(this.setPatch || {}, patch);
        clearTimeout(this.setTimer); this.setTimer = setTimeout(() => { const all = this.setPatch; this.setPatch = null; this.act('settings.set', { patch: all }); }, 300);
      }
      if (st.screen === 'demo' && this.syncedDemo === st.cur) {
        const l = this.localOf(st);
        if (this.lastLocal && !same(l, this.lastLocal)) {
          const patch = {}; Object.keys(l).forEach((k) => { if (!same(l[k], this.lastLocal[k])) patch[k] = l[k]; });
          this.lastLocal = l; const id = st.cur;
          if (this.localFor !== id) this.localPatch = null;
          this.localFor = id; this.localPatch = Object.assign(this.localPatch || {}, patch);
          clearTimeout(this.localTimer); this.localTimer = setTimeout(() => { const all = this.localPatch; this.localPatch = null; this.act('demo.update', { demo: id, patch: { settings: all } }); }, 400);
        }
      }
    },
    pushDemo(prev, p) {
      if (!this.live || this.applying || !prev || !prev.engine) return;
      const id = prev.id; const settings = {}; const top = {};
      const map = { capMode: 'captions', corner: 'corner_label', cornerText: 'corner_text', style: 'video_style', look: 'caption_look', speed: 'speed_copy', p720: 'preview_720p', model: 'voice_model' };
      Object.keys(p).forEach((k) => { if (map[k] && !same(p[k], prev[k])) settings[map[k]] = p[k] == null ? null : p[k]; });
      ['voice', 'kind', 'title', 'what', 'site'].forEach((k) => { if (k in p && !same(p[k], prev[k])) top[k] = p[k]; });
      if (Object.keys(settings).length) top.settings = settings;
      if (Object.keys(top).length) {
        this.demoTimer = this.demoTimer || {}; this.demoPatch = this.demoPatch || {};
        const acc = this.demoPatch[id] = this.demoPatch[id] || {};
        Object.keys(top).forEach((k) => { if (k === 'settings') acc.settings = Object.assign(acc.settings || {}, top.settings); else acc[k] = top[k]; });
        clearTimeout(this.demoTimer[id]);
        const send = () => { const all = this.demoPatch[id]; delete this.demoPatch[id]; if (all) this.act('demo.update', { demo: id, patch: all }); };
        if ('corner_text' in settings) this.demoTimer[id] = setTimeout(send, 500); else send();
      }
      // marks: what was added or removed (Undo puts a mark back, so it's an add)
      if ('notes' in p) {
        const flat = (n) => { const out = []; Object.keys(n || {}).forEach((k) => (n[k] || []).forEach((m) => out.push({ k: Number(k), t: m.t, text: m.text, ei: m.ei }))); return out; };
        const a = flat(prev.notes), b = flat(p.notes); const key = (m) => m.k + '|' + m.t + '|' + m.text;
        const A = new Set(a.map(key)), B = new Set(b.map(key));
        const removed = a.filter((m) => !B.has(key(m))).sort((x, y) => (y.ei || 0) - (x.ei || 0));
        const added = b.filter((m) => !A.has(key(m)));
        const secs = this.scripts[id] || [];
        (async () => {
          for (const m of removed) if (m.ei != null) await this.act('demo.unmark', { demo: id, index: m.ei }, { quiet: true });
          for (const m of added) await this.act('demo.mark', { demo: id, t: m.t, section: (secs[m.k] || {}).name || null, text: m.text }, { quiet: true });
        })();
      }
      if ('blurs' in p) (p.blurs || []).forEach((b) => { const o = (prev.blurs || []).find((x) => x.id === b.id); if (o && o.s !== b.s) this.act('demo.blur', { demo: id, id: b.id, s: b.s || '' }, { quiet: true }); });
    },
    // ---- Review's player: the real recording -----------------------------------------------------------------
    bindVideo() {
      const v = () => document.getElementById('revvideo');
      document.addEventListener('timeupdate', (e) => { if (e.target.id === 'revvideo' && !this.scrubbing) { const t = Math.round(e.target.currentTime); if (t !== this.state.revT) { this.videoT = t; this.setState({ revT: t }); } } }, true);
      ['play', 'pause', 'ended'].forEach((ev) => document.addEventListener(ev, (e) => { if (e.target.id === 'revvideo') this.setState({ player: !e.target.paused && !e.target.ended }); }, true));
      this.seekVideo = () => { const el = v(); if (!el) return; if (!this.state.player && !el.paused) el.pause(); if (el.readyState > 0 && this.videoT !== this.state.revT && Math.abs(el.currentTime - this.state.revT) > 0.6) { el.currentTime = this.state.revT; this.videoT = this.state.revT; } };
    },
    // ---- actions --------------------------------------------------------------------------------------------
    liveNewDemo(f) {
      const st = this.state;
      const settings = { captions: f.cap, corner_label: f.corner, corner_text: f.cornerText, video_style: st.defStyle, caption_look: st.defLook, speed_copy: st.defSpeed || null };
      if (f.hide) settings.hide_words = [f.hide];
      const body = { title: f.title, site: f.site, kind: f.kind, length_min: LENS[f.len], audience: WHO[f.who], what: f.what, voice: f.voice, settings: settings };
      const newSite = !st.sites.some((s) => s.u === f.site);
      this.setState({ screen: 'home' });
      this.act('demo.new', body).then((res) => {
        if (!res || !res.demo) return;
        this.setState({ cur: res.demo.id, screen: 'demo', step: 0, scSel: 0, recPos: 0, recStopped: false });
        this.syncDemoLocal(this.demo());
        // the login window opens only from Settings > Logins, on a click (Andy, 11 Nov 2026)
        if (newSite) this.say(f.site + ' needs a login first. Claude explores it once you’re in.', null, () => this.setState({ screen: 'settings' }), 'Logins');
        else this.say('Claude is exploring ' + f.site + ' and writing the script');
      });
    },
    liveEditBrief(D, f) {
      this.act('demo.update', { demo: D.id, patch: { title: f.title, what: f.what, site: f.site, kind: f.kind, length_min: LENS[f.len], audience: WHO[f.who], voice: f.voice, settings: { captions: f.cap, corner_label: f.corner, corner_text: f.cornerText } } }).then((res) => {
        if (!res) return;
        this.act('demo.brief', { demo: D.id }, { quiet: true });
        this.setState({ screen: 'demo', step: 0 });
        this.say('Claude is updating the script');
      });
    },
    liveRecordCost(D) { return D.cost || 0; },
    liveRecord(D, again) {
      this.patchDemo({ recReq: true, status: 'Waiting for Claude to start recording', dot: 'busy' });
      this.setState({ recPos: 0, recPaused: false, recStopped: false });
      this.act('demo.record', { demo: D.id, again: !!again, credits: D.cost || 0 }, { ok: 'Sent to Claude. The voice and recording start in a moment.' });
    },
    liveRedo(D, secIdx) {
      const secs = this.scripts[D.id] || []; const names = secIdx.map((k) => (secs[k] || {}).name).filter(Boolean);
      const credits = secIdx.reduce((s, k) => s + ((secs[k] || {}).cost || 0), 0);
      this.act('demo.redo', { demo: D.id, sections: names, credits: credits }, { ok: 'Sent to Claude. Only ' + (names.length === 1 ? 'that section is' : 'those sections are') + ' redone.' });
    },
    liveExport(D) {
      this.patchDemo({ exporting: true, status: 'Exporting…', dot: 'busy' });
      this.act('demo.export', { demo: D.id }, { ok: 'Exporting. The files land in ' + (this.engineState.settings.export_to || '~/Movies/NAVI').replace(/^~\//, '') });
    },
    liveTestKey(k, done) {
      post('key.test', { key: k }).then((r) => done(r.result, r)).catch(() => done('offline', {}));
    }
  };

  window.NaviEngine = {
    live: LIVE,
    install(C) { Object.assign(C.prototype, methods); },
    post: post
  };
})();
