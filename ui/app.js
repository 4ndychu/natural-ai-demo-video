// NAVI local UI. Interactive prototype: every screen and control works with sample data.
// The real skill serves this page locally and swaps the sample data for the engine's.
// Open ui/index.html in a browser. Optional: ?start=home|voice|review|settings&theme=light|dark
class DCLogic { constructor(p) { this.props = p || {}; } setState(s) { Object.assign(this.state, s); } }
class Component extends DCLogic {
  constructor(props) {
    super(props);
    const start = props.startOn || 'welcome';
    this.secs = [
      { n: 'Intro', d: 22, v: 'Okay so… you’ve got your course all planned out, right? And now you’ve basically gotta get all of it into, um, into Whop.', c: 'Your course is planned out. Now you need to get it all into Whop.' },
      { n: 'Create the whop', d: 24, v: 'Okay, cool. So first, whop dot com slash start. It kind of asks what you’re here for.', c: 'First, go to whop.com/start. It asks what you’re here for.' },
      { n: 'Add the Courses app', d: 28, v: 'Now this is the bit where people get stuck, to be fair. It, well, it didn’t live in the app store when we checked.', c: 'This is where people get stuck. The Courses app wasn’t in the app store when we checked.' },
      { n: 'One card per module', d: 34, v: 'Name it by what the buyer actually walks away with. One’s a topic. One’s a result.', c: 'Name it by what the buyer walks away with. One’s a topic, one’s a result.' },
      { n: 'Chapters, then lessons', d: 32, v: 'Put something in the wrong order? You- you just drag the handle, it’s fine.', c: 'Wrong order? Drag the handle.' },
      { n: 'Lesson type', d: 34, v: 'Most of yours are gonna be Multimedia, so text, video, downloads, all in one.', c: 'Most will be Multimedia: text, video and downloads together.' },
      { n: 'Content and files', d: 30, v: 'Each file lives in one lesson. Its home. Not like three of them.', c: 'Each file lives in one lesson.' },
      { n: 'Timing', d: 26, v: 'Honestly? Leave it open. Delays kind of just annoy people.', c: 'Leave it open. Delays annoy people.' },
      { n: 'Branding', d: 22, v: 'The three dots up in the header, Edit branding.', c: 'Three dots in the header, then Edit branding.' },
      { n: 'Open it as a buyer', d: 28, v: 'Squash it down to phone size and do it all again. That’s where stuff breaks.', c: 'Check it at phone size too. That’s where things break.' },
      { n: 'Wrap-up', d: 16, v: 'And, remember, nothing’s on sale yet. That’s the next one.', c: 'Nothing’s on sale yet. That’s next.' }
    ];
    this.starts = []; let acc = 0; this.secs.forEach((s) => { this.starts.push(acc); acc += s.d; }); this.total = acc;
    this.VO = {
      alex: { name: 'ALEX', desc: 'Relaxed, low', g: 'm', img: 'assets/voice-alex.png', c: '#0000F2', adj: {} },
      jessica: { name: 'JESSICA', desc: 'Warm, clear', g: 'f', img: 'assets/voice-jessica.png', c: '#C2300C', adj: { energy: 1 } },
      george: { name: 'GEORGE', desc: 'Deep, steady', g: 'm', img: 'assets/voice-george.png', c: '#0B4F37', adj: { energy: -1, pace: -2 } },
      brian: { name: 'BRIAN', desc: 'Male, gravelly, casual', g: 'm', img: 'assets/voice-brian.png', c: '#111111', adj: { casual: 1 } },
      lily: { name: 'LILY', desc: 'Female, bright, quick', g: 'f', img: 'assets/voice-lily.png', c: '#4B22D6', adj: { pace: 2, energy: 1 } },
      matilda: { name: 'MATILDA', desc: 'Female, soft, calm', g: 'f', img: 'assets/voice-matilda.png', c: '#000091', adj: { energy: -1 } }
    };
    this.presetVals = { course: { casual: 7, energy: 3, pace: 100, hes: 1, breath: 1, swear: 0 }, saas: { casual: 8, energy: 5, pace: 105, hes: 2, breath: 1, swear: 1 }, tour: { casual: 5, energy: 4, pace: 100, hes: 0, breath: 1, swear: 0 } };
    this.ranges = { casual: [3, 8], energy: [1, 6], pace: [94, 108], hes: [0, 3], breath: [0, 2], swear: [0, 2] };
    const whop = { id: 'whop', title: 'Build it in Whop', site: 'whop.com', len: 2, who: 0, voice: 'alex', kind: 'course', max: 4, cover: 'assets/cover-1.jpg', status: 'Ready to watch', dot: '#E5484D', recorded: true, written: true,
      notes: { 2: [{ t: 80, text: 'Too cheerful after Add app' }], 4: [{ t: 140, text: 'Too fast' }] },
      blurs: [{ id: 'b1', t: '1:58', what: 'A name inside the course cover image', s: '' }, { id: 'b2', t: '3:53', what: 'What might be a price in a banner', s: '' }] };
    const demos = [whop,
      { id: 'page', title: 'Write the product page', site: 'whop.com', len: 2, who: 0, voice: 'alex', kind: 'course', max: 3, cover: 'assets/cover-2.jpg', status: 'Recording 4 of 9', dot: '#E0A100', recorded: false, written: true, notes: {}, blurs: [] },
      { id: 'pay', title: 'Connect payouts', site: 'whop.com', len: 1, who: 0, voice: 'alex', kind: 'course', max: 5, cover: 'assets/cover-3.jpg', status: 'Exported Nov 2', dot: 'var(--okDot)', recorded: true, written: true, exported: true, notes: {}, blurs: [] },
      { id: 'posts', title: 'Schedule a week of posts', site: 'app.yourproduct.com', len: 2, who: 1, voice: 'jessica', kind: 'saas', max: 5, cover: 'assets/cover-4.jpg', status: 'Exported Oct 28', dot: 'var(--okDot)', recorded: true, written: true, exported: true, notes: {}, blurs: [] }];
    demos.forEach((d) => Object.assign(d, { capMode: 'burn', corner: 'off', cornerText: '' }));
    const screen = start === 'voice' || start === 'review' ? 'demo' : start;
    this.state = {
      screen: screen, step: start === 'review' ? 4 : 1, cur: 'whop', demos: demos, theme: null, help: false,
      keyOn: start !== 'welcome', key: '', keyType: 'password', keyRes: null, keyEdit: false,
      tools: start === 'welcome' ? 'idle' : 'done', logged: false, wSite: '',
      credits: 26400, mine: ['alex', 'jessica', 'george'], defVoice: 'alex',
      vals: Object.assign({}, this.presetVals.course), caps: false, lock: true, heardVoices: {}, lastSample: null, sampling: false,
      shown: { email: false, phone: false, names: false, address: false, money: false, customers: false, counts: false, usage: true, prices: true, dates: true }, hide: ['[Client name]', '[Your surname]'], hideDraft: '',
      sel: 2, revT: 86, player: false, noteDraft: '', p720: false, recPos: 11, confirm: null,
      sites: [{ u: 'whop.com', note: 'Logged in to Demo Academy, saved Nov 4' }, { u: 'app.yourproduct.com', note: 'Saved Oct 28' }], siteDraft: '', cleared: {}, wipeConfirm: false,
      lib: false, libF: 'all', chat: [], chatDraft: '', chatAct: null,
      defCap: 'burn', defCorner: 'off', defCornerText: '', bCap: 'burn', bCorner: 'off', bCornerText: '',
      bWhat: '', bSite: 'whop.com', bNew: '', bWho: 0, bLen: 2, bHide: '', bVoice: 'alex', editing: false,
      toast: '', toastUndo: null, toastGo: null, toastGoLabel: ''
    };
    this.timers = {};
  }
  componentWillUnmount() { Object.keys(this.timers).forEach((k) => { clearTimeout(this.timers[k]); clearInterval(this.timers[k]); }); }
  later(name, ms, fn) { if (this.timers[name]) clearTimeout(this.timers[name]); this.timers[name] = setTimeout(fn, ms); }
  every(name, ms, fn) { if (this.timers[name]) clearInterval(this.timers[name]); this.timers[name] = setInterval(fn, ms); }
  stop(name) { if (this.timers[name]) { clearInterval(this.timers[name]); clearTimeout(this.timers[name]); delete this.timers[name]; } }
  say(msg, undo, go, goLabel) { this.setState({ toast: msg, toastUndo: undo || null, toastGo: go || null, toastGoLabel: goLabel || '' }); this.later('toast', 3600, () => this.setState({ toast: '', toastUndo: null, toastGo: null })); }
  fmt(t) { const m = Math.floor(t / 60); const s = Math.floor(t % 60); return m + ':' + (s < 10 ? '0' : '') + s; }
  num(n) { return n.toLocaleString('en-US'); }
  demo() { return this.state.demos.find((d) => d.id === this.state.cur) || this.state.demos[0]; }
  patchDemo(p) { const id = this.state.cur; this.setState({ demos: this.state.demos.map((d) => d.id === id ? Object.assign({}, d, p) : d) }); }
  recFor(voice, kind) { const base = Object.assign({}, this.presetVals[kind]); const adj = (this.VO[voice] || {}).adj || {}; Object.keys(adj).forEach((k) => { const r = this.ranges[k]; base[k] = Math.max(r[0], Math.min(r[1], base[k] + adj[k])); }); return base; }
  spend(n) { this.setState({ credits: Math.max(0, this.state.credits - n) }); }
  needKey() { if (this.state.keyOn) return false; this.say('Connect your ElevenLabs key first', null, () => this.setState({ screen: 'settings', keyEdit: true }), 'Connect'); return true; }
  startRecording() {
    this.setState({ recPos: 0 });
    this.every('rec', 700, () => {
      const p = this.state.recPos + 1;
      if (p >= 11) { this.stop('rec'); this.setState({ recPos: 11 }); this.patchDemo({ recorded: true, max: Math.max(this.demo().max, 4), status: 'Ready to watch', dot: '#E5484D', blurs: [{ id: 'n1', t: '0:41', what: 'What might be an email in a sidebar', s: '' }] }); this.spend(4600); this.say('Draft 1 is ready', null, () => this.setState({ step: 4 }), 'Watch it'); }
      else this.setState({ recPos: p });
    });
  }
  renderVals() {
    const st = this.state; const D = this.demo(); const v = st.vals;
    const voice = D.voice; const VO = this.VO; const vInfo = VO[voice];
    const rec = this.recFor(voice, D.kind);
    let theme = st.theme || this.props.theme || 'system';
    if (theme === 'system') { try { theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; } catch (e) { theme = 'light'; } }
    const pretty = (k) => VO[k].name.charAt(0) + VO[k].name.slice(1).toLowerCase();
    const voicePretty = pretty(voice);
    const marks = Object.keys(D.notes || {}).reduce((a, k) => a + D.notes[k].length, 0);
    const markedSecs = Object.keys(D.notes || {}).filter((k) => D.notes[k].length);
    const unsure = (D.blurs || []).filter((b) => !b.s).length;
    const blurCount = 7 + Object.keys(st.shown).filter((k) => !st.shown[k]).length + st.hide.length;
    const kindName = { course: 'course walkthrough', saas: 'quick SaaS demo', tour: 'product tour' }[D.kind];
    const S = [
      { name: 'Script', sub: D.written ? '11 sections' : 'Writing…', title: 'Read the script', help: 'Left is what the voice says, with the ums and restarts that make it sound human. Right is what the captions show. Want a change? Type it in the bar below.', cta: 'Script looks right' },
      { name: 'Voice', sub: voicePretty, title: 'Pick the voice', help: 'Tap a face to pick it and hear it. The recommended settings are already on. Drag any slider to change how it sounds.', cta: 'Use ' + voicePretty },
      { name: 'Privacy', sub: blurCount + ' things blurred', title: 'Check what gets blurred', help: 'Blurring happens before recording, then every frame is checked again. Anything it isn’t sure about shows up in Review.', cta: D.recorded ? 'Blurs look right' : 'Blurs look right, record' },
      { name: 'Record', sub: D.recorded ? 'Done, 4:56' : (st.cur === D.id && st.recPos < 11 && st.step === 3 ? 'Recording…' : 'Not yet'), title: D.recorded ? 'Recorded' : 'Recording', help: 'The browser runs the clicks while ' + voicePretty + ' talks. You can walk away.', cta: 'Watch the draft', second: D.recorded ? 'Record again' : '' },
      { name: 'Review', sub: marks ? marks + (marks === 1 ? ' mark' : ' marks') : (D.recorded ? 'No marks' : 'Not yet'), title: 'Watch the draft', help: 'Pause on anything that’s off and tap a reason, or say it your way. Only marked sections get redone.', cta: 'Approve and export', second: marks ? 'Redo marked sections' : '' },
      { name: 'Export', sub: D.exported ? 'MP4 + captions' : 'Not yet', title: 'Exported', help: 'Your video and captions are ready.', cta: 'Open folder', second: 'Back to all demos' }
    ];
    const cur = S[st.step];
    const steps = S.map((s, i) => {
      const locked = i > D.max; const now = i === st.step; const done = i < D.max || (i === 5 && D.exported) || (i <= D.max && i < st.step);
      return { name: s.name, sub: s.sub, cur: now ? 'step' : 'false', locked: locked, op: locked ? 0.4 : 1, tip: locked ? 'Finish the step before first' : '', bg: now ? 'var(--tray)' : 'transparent', mark: done && !now ? '✓' : String(i + 1), dotBg: done && !now ? 'var(--ink)' : 'transparent', dotFg: done && !now ? 'var(--sheet)' : 'var(--ink)', ring: done && !now ? 'transparent' : 'var(--ink)', go: () => { if (!locked) this.setState({ step: i, confirm: null }); } };
    });
    const setVals = (n, msg, prev) => { this.setState({ vals: n }); if (msg) this.say(msg, prev ? () => this.setState({ vals: prev }) : null); };
    const setV = (k, x) => { const n = Object.assign({}, this.state.vals); if (n[k] === x) return; n[k] = x; this.setState({ vals: n }); };
    const drag = (e, d) => { const el = e.currentTarget; if (!el || !el.getBoundingClientRect) return; const r = el.getBoundingClientRect(); let p = (e.clientX - r.left) / r.width; p = Math.max(0, Math.min(1, p)); setV(d.k, Math.round(d.min + p * (d.max - d.min))); };
    const defs = [
      { k: 'casual', label: 'Casualness', f: (x) => x + ' / 8', low: 'Lower: cleaner, but can sound like a script.', high: 'Higher: more "gonna" and "kind of".' },
      { k: 'energy', label: 'Energy', f: (x) => ['', 'Very calm', 'Calm', 'Relaxed', 'Warm', 'Lively', 'Upbeat'][x], low: 'Lower: steady, can go flat.', high: 'Higher: livelier, can sound overexcited.' },
      { k: 'pace', label: 'Pace', f: (x) => (x / 100).toFixed(2) + 'x', low: 'Slower: easy to follow, can drag.', high: 'Faster: snappy, can rush the clicks.' },
      { k: 'hes', label: 'Hesitations', f: (x) => ['None', 'A few', 'Some', 'More'][x], low: 'Fewer: can sound too perfect.', high: 'More: human, but too many sounds nervous.' },
      { k: 'breath', label: 'Breaths', f: (x) => ['Trimmed', 'Natural', 'Kept'][x], low: 'Trimmed: can sound stitched together.', high: 'Kept: only natural breaths, never forced.' },
      { k: 'swear', label: 'Swearing', f: (x) => ['Off', 'One', 'A few'][x], low: 'Off: fine for any audience.', high: 'On: at natural reactions, never in instructions.' }
    ].map((d) => Object.assign(d, { min: this.ranges[d.k][0], max: this.ranges[d.k][1] }));
    const sliders = defs.map((d) => ({ label: d.label, min: d.min, max: d.max, value: v[d.k], display: d.f(v[d.k]), pct: ((v[d.k] - d.min) / (d.max - d.min) * 100) + '%', rec: ((rec[d.k] - d.min) / (d.max - d.min) * 100) + '%', off: v[d.k] !== rec[d.k], open: st.open === d.k, low: d.low, high: d.high, isSwear: d.k === 'swear',
      toggle: () => this.setState({ open: st.open === d.k ? null : d.k }),
      reset: () => { const prev = this.state.vals; const n = Object.assign({}, prev); n[d.k] = rec[d.k]; setVals(n, d.label + ' back to recommended', prev); },
      onChange: (e) => setV(d.k, Number(e.target.value)),
      down: (e) => { this.dragKey = d.k; try { e.currentTarget.setPointerCapture(e.pointerId); } catch (x) {} drag(e, d); },
      move: (e) => { if (this.dragKey === d.k) drag(e, d); },
      up: () => { this.dragKey = null; } }));
    const changed = defs.filter((d) => v[d.k] !== rec[d.k]).length;
    let line = (v.hes >= 1 ? 'Okay, cool. ' : '') + 'So first, ' + (v.hes >= 2 ? 'um, ' : '') + 'whop dot com slash start. ';
    line += v.casual >= 7 ? 'It kind of asks what you’re here for, so I’m gonna hit “I want a business”.' : 'It asks what you’re here for, so I’ll hit “I want a business”.';
    if (v.swear >= 1) line += ' Skip this and shit breaks later.';
    const caption = st.caps ? line : line.replace(/shit/g, 'stuff');
    const sampleKey = voice + JSON.stringify(v);
    const sw = (on) => ({ track: on ? 'var(--ink)' : 'var(--fill)', x: on ? '18px' : '0px', onStr: on ? 'true' : 'false' });
    const warns = { email: 'Real people’s emails would be visible to anyone watching.', money: 'Showing earnings in marketing can count as a claim you have to back up.', customers: 'This is other people’s data. Only show it if it’s fake.' };
    const row = (id, label) => { const on = st.shown[id]; const s = sw(on); const w = on && warns[id]; return { id: 'pv-' + id, label: label, sub: w ? w : (on ? 'Shown' : 'Blurred'), subColor: w ? 'var(--danger)' : 'var(--ink2)', track: s.track, x: s.x, onStr: s.onStr, toggle: () => { const m = Object.assign({}, st.shown); m[id] = !on; this.setState({ shown: m }); } }; };
    const revSec = (() => { for (let i = this.secs.length - 1; i >= 0; i--) if (st.revT >= this.starts[i]) return i; return 0; })();
    const addNote = (i, text) => { const t = (st.revT >= this.starts[i] && st.revT < this.starts[i] + this.secs[i].d) ? st.revT : this.starts[i] + 3; const n = Object.assign({}, D.notes); n[i] = (n[i] || []).concat([{ t: t, text: text }]); this.patchDemo({ notes: n }); this.setState({ noteDraft: '' }); this.say('Marked at ' + this.fmt(t)); };
    const revSecs = this.secs.map((s, i) => { const ns = (D.notes || {})[i] || []; return { t: this.fmt(this.starts[i]), n: s.n, line: s.v, open: st.sel === i, bg: st.sel === i ? 'var(--tray)' : 'transparent', count: ns.length ? ns.length + (ns.length === 1 ? ' mark' : ' marks') : '', noteId: 'note-' + i,
      notes: ns.map((nn, j) => ({ text: nn.text, at: this.fmt(nn.t), rm: () => { const prev = D.notes; const n = Object.assign({}, prev); n[i] = ns.filter((x, k) => k !== j); this.patchDemo({ notes: n }); this.say('Mark removed', () => this.patchDemo({ notes: prev })); } })),
      pick: () => this.setState({ sel: st.sel === i ? -1 : i, revT: this.starts[i] + 3 }), ai: () => addNote(i, 'Sounds like AI'), blur: () => addNote(i, 'Needs a blur'), fast: () => addNote(i, 'Too fast'), addNote: () => { const d = st.noteDraft.trim(); if (d) addNote(i, d); } }; });
    const goStep = (i) => { const p = { step: i, confirm: null }; this.setState(p); if (D.max < i) this.patchDemo({ max: i }); };
    const primaryFor = [
      () => goStep(1),
      () => { goStep(2); this.say(st.lock ? voicePretty + ' locked for every demo in this project' : 'Using ' + voicePretty + ' for this demo'); },
      () => { goStep(3); if (!D.recorded) { if (this.needKey()) return; this.startRecording(); } },
      () => goStep(4),
      () => { if (marks || unsure) { this.setState({ confirm: 'export' }); return; } this.patchDemo({ exported: true, status: 'Exported Nov 4', dot: 'var(--okDot)', max: 5 }); goStep(5); this.say('Exported to your Videos folder'); },
      () => this.say('Opening your Videos folder')
    ];
    const secondaryFor = [null, null, null, () => { if (this.needKey()) return; this.patchDemo({ recorded: false }); this.startRecording(); }, () => this.setState({ confirm: 'redo' }), () => this.setState({ screen: 'home' })];
    const confirms = {
      export: { text: (marks ? marks + (marks === 1 ? ' mark' : ' marks') : '') + (marks && unsure ? ' and ' : '') + (unsure ? unsure + ' unsure ' + (unsure === 1 ? 'blur' : 'blurs') : '') + ' not sorted yet', no: 'Go back', yes: 'Export anyway', act: () => { this.patchDemo({ exported: true, status: 'Exported Nov 4', dot: 'var(--okDot)', max: 5 }); goStep(5); this.say('Exported to your Videos folder'); } },
      redo: { text: 'Redo ' + markedSecs.length + (markedSecs.length === 1 ? ' section' : ' sections') + ' for about ' + this.num(markedSecs.length * 420) + ' credits?', no: 'Cancel', yes: 'Redo them', act: () => { if (this.needKey()) return; this.spend(markedSecs.length * 420); this.patchDemo({ notes: {} }); this.setState({ confirm: null }); this.say('Redoing ' + markedSecs.length + (markedSecs.length === 1 ? ' section' : ' sections') + '. Draft 2 will be here in a few minutes.'); } }
    };
    const cf = st.confirm ? confirms[st.confirm] : null;
    const foot = cf ? { text: cf.text, dot: 'var(--danger)', color: 'var(--ink)' } : (st.step === 4 ? { text: marks ? 'Redo ' + markedSecs.length + ' sections, about ' + this.num(markedSecs.length * 420) + ' credits' : (unsure ? unsure + ' blurs to check' : 'Nothing marked'), dot: marks || unsure ? '#E5484D' : 'var(--okDot)', color: 'var(--ink2)' } : { text: [D.written ? 'Approved' : 'Claude is writing the script', voicePretty + ', ' + kindName + ' settings', blurCount + ' things will be blurred', D.recorded ? 'Recorded 4:56' : 'Recording ' + st.recPos + ' of 11', '', D.exported ? 'Done' : ''][st.step], dot: 'var(--okDot)', color: 'var(--ink2)' });
    const wsw = (done) => ({ bg: done ? 'var(--ink)' : 'transparent', fg: done ? 'var(--sheet)' : 'var(--ink)' });
    const w1 = wsw(st.keyRes === 'ok'), w2 = wsw(st.tools === 'done'), w3 = wsw(st.logged);
    const a = sw(st.caps), l = sw(st.lock), p = sw(st.p720);
    const dataDefs = [{ id: 'key', n: 'ElevenLabs API key', w: 'In your Mac’s Keychain', l: 'Remove' }, { id: 'logins', n: 'Saved logins', w: st.sites.length + ' saved', l: 'Forget all' }, { id: 'settings', n: 'Voice, privacy and learned preferences', w: 'In the skill’s settings folder', l: 'Reset' }, { id: 'videos', n: 'Finished videos', w: 'In your Videos folder. Never deleted from here.', l: '' }];
    const dataAct = {
      key: () => { this.setState({ keyOn: false }); this.say('Key removed', () => this.setState({ keyOn: true })); },
      logins: () => { const prev = st.sites; this.setState({ sites: [] }); this.say('All saved logins forgotten', () => this.setState({ sites: prev })); },
      settings: () => { const prev = { vals: st.vals, hide: st.hide, shown: st.shown, defVoice: st.defVoice, defCap: st.defCap, defCorner: st.defCorner, defCornerText: st.defCornerText }; this.setState({ vals: Object.assign({}, this.presetVals.course), hide: [], shown: { email: false, phone: false, names: false, address: false, money: false, customers: false, counts: false, usage: true, prices: true, dates: true }, defVoice: 'alex', defCap: 'burn', defCorner: 'off', defCornerText: '' }); this.say('Settings reset', () => this.setState(prev)); }
    };
    const keyMsg = st.keyRes === 'ok' ? 'Connected. Starter plan, ' + this.num(st.credits) + ' of 30,000 credits left. Saved in your Mac’s Keychain.' : st.keyRes === 'bad' ? 'That key didn’t work. Check you copied all of it and it has text to speech access.' : '';
    const videoCost = 4600; const leftAfter = Math.max(0, st.credits - (D.recorded ? 0 : videoCost));
    const chatClean = (m) => { let s = m.replace(/^(actually|no|ok|okay|wait)[,!.\s]*/i, '').replace(/^(make|do|change)( it| this)?( into)?( a)? demo (of|for|on|about)\s*/i, '').replace(/\s*instead[.!]*$/i, ''); return s.charAt(0).toUpperCase() + s.slice(1); };
    const dSel = (k) => ({ label: pretty(k), on: st.defVoice === k ? 'true' : 'false', pick: () => { this.setState({ defVoice: k }); this.say(pretty(k) + ' is now the default for new demos'); } });
    const capOpts = [['burn', 'Burned in'], ['file', 'Separate file'], ['off', 'Off']];
    const posOpts = [['off', 'Off'], ['tl', 'Top left'], ['tr', 'Top right'], ['bl', 'Bottom left'], ['br', 'Bottom right']];
    const capName = { burn: 'burned in', file: 'as a separate file', off: 'off' };
    const segOf = (opts, cur, fn) => opts.map((o) => ({ label: o[1], on: cur === o[0] ? 'true' : 'false', pick: () => fn(o[0]) }));
    const posCss = { tl: 'left: 14px; top: 14px', tr: 'right: 14px; top: 14px', bl: 'left: 14px; bottom: 14px', br: 'right: 14px; bottom: 14px' };
    const dCap = D.capMode || 'burn'; const dCorner = D.corner || 'off'; const dCornerText = D.cornerText || '';
    const base = D.title.replace(/\u2026$/, '');
    return {
      themeClass: theme === 'dark' ? 't-dark' : 't-light', isDark: theme === 'dark', isLight: theme !== 'dark', themeAria: theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode', toggleTheme: () => this.setState({ theme: theme === 'dark' ? 'light' : 'dark' }),
      isWelcome: st.screen === 'welcome', inApp: st.screen !== 'welcome', isHome: st.screen === 'home', isDemo: st.screen === 'demo', isSettings: st.screen === 'settings', isNew: st.screen === 'new',
      crumb: st.screen !== 'home', crumbText: st.screen === 'demo' ? D.title : st.screen === 'new' ? (st.editing ? 'Edit brief' : 'New demo') : 'Settings', crumbHomeColor: st.screen === 'home' ? 'var(--ink)' : 'var(--ink2)',
      goHome: () => this.setState({ screen: 'home', help: false, confirm: null }), goSettings: () => this.setState({ screen: 'settings', help: false }),
      helpOpen: st.help, toggleHelp: () => this.setState({ help: !st.help }),
      keyOn: st.keyOn, keyOff: !st.keyOn, creditsText: this.num(st.credits), creditPct: (st.credits / 30000 * 100) + '%',
      demos: st.demos.map((d) => ({ title: d.title, meta: d.site + ', ' + pretty(d.voice), status: d.status, dot: d.dot, cover: d.cover, open: () => { const s = d.exported ? 5 : Math.min(d.max, d.recorded ? 4 : d.max); this.setState({ screen: 'demo', cur: d.id, step: s, sel: 2, confirm: null, vals: this.recFor(d.voice, d.kind) }); } })),
      defImg: VO[st.defVoice].img, defC: VO[st.defVoice].c, defName: VO[st.defVoice].name,
      keyDot: st.keyOn ? 'var(--okDot)' : 'var(--danger)', keyStatus: st.keyOn ? 'ElevenLabs connected' : 'ElevenLabs not connected', keyAction: st.keyOn ? 'Change' : 'Connect',
      toolsDot: st.tools === 'done' ? 'var(--okDot)' : 'var(--danger)', toolsStatus: st.tools === 'done' ? 'Recording tools ready' : 'Recording tools not installed',
      sitesStatus: st.sites.length ? st.sites.length + (st.sites.length === 1 ? ' saved login' : ' saved logins') : 'No saved logins',
      demoTitle: D.title, briefLine: D.site + ', about ' + ['1', '3', '5', '8'][D.len] + ' min', demoCover: D.cover,
      newDemo: () => this.setState({ screen: 'new', editing: false, bCap: st.defCap, bCorner: st.defCorner, bCornerText: st.defCornerText, bWhat: '', bNew: '', bHide: '', bSite: st.sites[0] ? st.sites[0].u : '', bVoice: st.defVoice, bWho: 0, bLen: 2, help: false }),
      editBrief: () => this.setState({ screen: 'new', editing: true, bWhat: D.what || 'How to build a course in Whop, from creating the whop to checking it on a phone', bSite: D.site, bNew: '', bWho: D.who, bLen: D.len, bVoice: D.voice, bCap: dCap, bCorner: dCorner, bCornerText: dCornerText }),
      newTitle: st.editing ? 'Edit the brief' : 'New demo', briefCta: st.editing ? 'Update the script' : 'Write the script',
      briefHint: st.editing ? 'Claude only rewrites what changed.' : 'Takes about a minute. You can keep using the page.',
      bWhat: st.bWhat, onBWhat: (e) => this.setState({ bWhat: e.target.value }), bHide: st.bHide, onBHide: (e) => this.setState({ bHide: e.target.value }), bNew: st.bNew, onBNew: (e) => this.setState({ bNew: e.target.value }),
      briefEmpty: !st.bWhat.trim(),
      bSites: st.sites.map((s) => ({ label: s.u, on: !st.bNew.trim() && st.bSite === s.u ? 'true' : 'false', pick: () => this.setState({ bSite: s.u, bNew: '' }) })),
      bWho: ['Complete beginners', 'Some experience', 'Pros'].map((s, i) => ({ label: s, on: st.bWho === i ? 'true' : 'false', pick: () => this.setState({ bWho: i }) })),
      bLen: ['1 min', '3 min', '5 min', '8 min'].map((s, i) => ({ label: s, on: st.bLen === i ? 'true' : 'false', pick: () => this.setState({ bLen: i }) })),
      bVoices: st.mine.map((k) => ({ label: pretty(k), on: st.bVoice === k ? 'true' : 'false', pick: () => this.setState({ bVoice: k }) })),
      bCaps: segOf(capOpts, st.bCap, (x) => this.setState({ bCap: x })),
      bCorner: segOf(posOpts, st.bCorner, (x) => this.setState({ bCorner: x })),
      bCornerText: st.bCornerText, onBCornerText: (e) => this.setState({ bCornerText: e.target.value }), bCornerOff: st.bCorner === 'off', bCornerOp: st.bCorner === 'off' ? 0.45 : 1,
      bCornerPh: 'Text to show in the corner, e.g. your brand name',
      revCaps: segOf(capOpts, dCap, (x) => { this.patchDemo({ capMode: x }); this.say('Captions ' + capName[x]); }),
      revCorner: segOf(posOpts, dCorner, (x) => this.patchDemo({ corner: x })),
      revCornerText: dCornerText, onRevCornerText: (e) => this.patchDemo({ cornerText: e.target.value }), revCornerOff: dCorner === 'off', revCornerOp: dCorner === 'off' ? 0.45 : 1,
      showCapPreview: dCap === 'burn', cornerShown: dCorner !== 'off', cornerStyle: posCss[dCorner] || '', cornerTextShown: dCornerText.trim() || 'Your label here',
      defCaps: segOf(capOpts, st.defCap, (x) => this.setState({ defCap: x })),
      defCorner: segOf(posOpts, st.defCorner, (x) => this.setState({ defCorner: x })),
      defCornerText: st.defCornerText, onDefCornerText: (e) => this.setState({ defCornerText: e.target.value }), defCornerOff: st.defCorner === 'off', defCornerOp: st.defCorner === 'off' ? 0.45 : 1,
      cancelBrief: () => this.setState({ screen: st.editing ? 'demo' : 'home' }),
      submitBrief: () => {
        const w = st.bWhat.trim(); if (!w) return; const t = w.length > 34 ? w.slice(0, 32).replace(/\s+\S*$/, '') + '…' : w; const site = st.bNew.trim() || st.bSite || 'whop.com';
        const newSite = st.bNew.trim() && !st.sites.some((s) => s.u === site);
        if (st.editing) { this.patchDemo({ title: t, what: w, site: site, who: st.bWho, len: st.bLen, voice: st.bVoice, capMode: st.bCap, corner: st.bCorner, cornerText: st.bCornerText, written: false }); this.setState({ screen: 'demo', step: 0, sites: newSite ? st.sites.concat([{ u: site, note: 'Saved Nov 4' }]) : st.sites }); this.later('write', 2200, () => { this.patchDemo({ written: true }); this.say('Script updated'); }); this.say('Updating the script'); return; }
        const id = 'd' + Date.now();
        const d = { id: id, title: t, what: w, site: site, len: st.bLen, who: st.bWho, voice: st.bVoice, kind: 'course', max: 0, cover: 'assets/cover-4.jpg', status: 'Writing script', dot: '#E0A100', recorded: false, written: false, notes: {}, blurs: [], capMode: st.bCap, corner: st.bCorner, cornerText: st.bCornerText };
        this.setState({ demos: [d].concat(st.demos), cur: id, screen: 'demo', step: 0, vals: this.recFor(st.bVoice, 'course'), sites: newSite ? st.sites.concat([{ u: site, note: 'Saved Nov 4' }]) : st.sites, recPos: 0 });
        this.say(newSite ? 'A browser opens so you can log in to ' + site + '. Then Claude writes the script.' : 'Claude is exploring ' + site + ' and writing the script');
        this.later('write', 2600, () => { this.setState({ demos: this.state.demos.map((x) => x.id === id ? Object.assign({}, x, { written: true, status: 'Script ready', dot: '#E0A100' }) : x) }); this.say('Script ready to read'); });
      },
      steps: steps, cur: cur, st0: st.step === 0, st1: st.step === 1, st2: st.step === 2, st3: st.step === 3, st4: st.step === 4, st5: st.step === 5,
      writing: !D.written, scriptReady: !!D.written, skelRows: ['92%', '80%', '88%', '70%', '84%', '76%'],
      canBack: st.step > 0, back: () => this.setState({ step: st.step - 1, confirm: null }), hasSecondary: !!cur.second, secondary: secondaryFor[st.step] || (() => {}), primary: primaryFor[st.step],
      primaryBlocked: (st.step === 0 && !D.written) || (st.step === 3 && !D.recorded),
      confirming: !!cf, notConfirming: !cf, confirmNo: cf ? cf.no : '', confirmYes: cf ? cf.yes : '', cancelConfirm: () => this.setState({ confirm: null }), doConfirm: () => { if (cf) cf.act(); },
      footText: foot.text, footDot: foot.dot, footColor: foot.color,
      script: this.secs.map((s, i) => ({ t: this.fmt(this.starts[i]), n: s.n, v: s.v, c: s.c })),
      voiceName: voicePretty, voiceColor: vInfo.c, line: line, caption: caption,
      voices: st.mine.map((k) => ({ name: VO[k].name, desc: VO[k].desc, img: VO[k].img, bg: VO[k].c, on: voice === k ? 'true' : 'false', ring: voice === k ? 'var(--ink)' : 'transparent', aria: 'Pick and hear ' + VO[k].name, badge: st.heardVoices[k] ? 'Replay' : 'Hear',
        pick: () => { if (this.needKey()) return; const first = !st.heardVoices[k]; const h = Object.assign({}, st.heardVoices); h[k] = true; this.patchDemo({ voice: k }); this.setState({ heardVoices: h, vals: this.recFor(k, D.kind) }); if (first) this.spend(120); this.say('Playing ' + pretty(k) + (first ? ', 120 credits' : ', free replay')); } })),
      openLib: () => this.setState({ lib: true }), closeLib: () => this.setState({ lib: false }), libOpen: st.lib,
      libFilters: [['all', 'All'], ['f', 'Female'], ['m', 'Male']].map((o) => ({ label: o[1], on: st.libF === o[0] ? 'true' : 'false', pick: () => this.setState({ libF: o[0] }) })),
      lib: Object.keys(VO).filter((k) => st.libF === 'all' || VO[k].g === st.libF).map((k) => ({ name: VO[k].name, desc: VO[k].desc, img: VO[k].img, c: VO[k].c, canAdd: st.mine.indexOf(k) < 0, added: st.mine.indexOf(k) >= 0, hearAria: 'Hear ' + VO[k].name,
        hear: () => { if (this.needKey()) return; const first = !st.heardVoices[k]; const h = Object.assign({}, st.heardVoices); h[k] = true; this.setState({ heardVoices: h }); if (first) this.spend(120); this.say('Playing ' + pretty(k) + (first ? ', 120 credits' : ', free replay')); },
        add: () => { this.setState({ mine: st.mine.concat([k]) }); this.say(pretty(k) + ' added to your voices', () => this.setState({ mine: this.state.mine.filter((x) => x !== k) })); } })),
      kinds: [['course', 'Course walkthrough'], ['saas', 'Quick SaaS demo'], ['tour', 'Product tour']].map((o) => ({ label: o[1], on: D.kind === o[0] ? 'true' : 'false', pick: () => { if (D.kind === o[0]) return; const prevV = st.vals; const prevK = D.kind; this.patchDemo({ kind: o[0] }); this.setState({ vals: this.recFor(voice, o[0]) }); this.say('Switched to ' + o[1].toLowerCase() + ' settings', () => { this.patchDemo({ kind: prevK }); this.setState({ vals: prevV }); }); } })),
      moods: [[2, 'Calm'], [3, 'Relaxed'], [4, 'Warm'], [5, 'Lively']].map((o) => ({ label: o[1], on: v.energy === o[0] ? 'true' : 'false', pick: () => setV('energy', o[0]) })),
      fineNote: changed ? changed + ' changed' : 'All recommended', sliders: sliders,
      resetAll: () => { const prev = st.vals; setVals(Object.assign({}, rec), 'Back to the recommended settings', prev); },
      capsOn: a.onStr, capsTrack: a.track, capsX: a.x, toggleCaps: () => this.setState({ caps: !st.caps }),
      playSample: () => { if (st.sampling) { this.stop('sample'); this.setState({ sampling: false }); return; } if (this.needKey()) return; const free = st.lastSample === sampleKey; if (!free) this.spend(300); this.setState({ sampling: true, lastSample: sampleKey }); this.later('sample', 6000, () => this.setState({ sampling: false })); },
      samplePlaying: st.sampling, sampleStopped: !st.sampling, playAria: st.sampling ? 'Stop sample' : 'Play sample', wvClass: st.sampling ? 'wv on' : 'wv',
      wbars: [30, 55, 40, 75, 50, 90, 62, 100, 48, 70, 36, 64, 88, 52, 96, 58, 44, 80, 50, 72, 34, 60, 92, 46, 70, 40, 66, 30].map((h, i) => ({ h: h + '%', d: (i % 7) * 70 + 'ms' })),
      sampleCost: st.lastSample === sampleKey ? 'free replay' : '~300 cr',
      videoCostText: this.num(videoCost), leftAfterText: this.num(leftAfter), usedPct: ((30000 - st.credits) / 30000 * 100) + '%', thisPct: (D.recorded ? 0 : Math.min(videoCost, st.credits) / 30000 * 100) + '%',
      lockOn: l.onStr, lockTrack: l.track, lockX: l.x, toggleLock: () => this.setState({ lock: !st.lock }),
      always: ['API keys and tokens', 'Passwords', '2FA and recovery codes', 'Card and bank numbers', 'ID numbers', 'Private keys', 'Login links'],
      hide: st.hide.map((w) => ({ w: w, aria: 'Remove ' + w, rm: () => { const prev = st.hide; this.setState({ hide: st.hide.filter((x) => x !== w) }); this.say('Removed “' + w + '”', () => this.setState({ hide: prev })); } })),
      hideDraft: st.hideDraft, onHideDraft: (e) => this.setState({ hideDraft: e.target.value }), addHide: () => { const w = st.hideDraft.trim(); if (w && st.hide.indexOf(w) < 0) { this.setState({ hide: st.hide.concat([w]), hideDraft: '' }); this.say('Will always blur “' + w + '”'); } },
      tier2: [row('email', 'Email addresses'), row('phone', 'Phone numbers'), row('names', 'Real names and profile photos'), row('address', 'Addresses'), row('money', 'Revenue and money figures'), row('customers', 'Customer details'), row('counts', 'Follower and member counts')],
      tier3: [row('usage', 'Usage stats, like token usage'), row('prices', 'Prices on public pages'), row('dates', 'Dates')],
      recBadge: D.recorded ? 'Recorded' : 'Recording live', recBadgeDot: D.recorded ? 'var(--okDot)' : '#FF5A4E',
      recHead: D.recorded ? 'All 11 sections recorded' : 'Section ' + Math.min(11, st.recPos + 1) + ' of 11', recLeft: D.recorded ? '4:56' : 'about ' + Math.max(1, Math.ceil((11 - st.recPos) * 0.3)) + ' min left',
      recPct: (D.recorded ? 100 : st.recPos / 11 * 100) + '%', recNote: D.recorded ? 'Want a fresh take? Record again redoes every section.' : 'You can close this page. Claude will tell you in chat when the draft is ready.',
      recRows: this.secs.map((s, i) => { const done = D.recorded || i < st.recPos; const now = !D.recorded && i === st.recPos; return { n: s.n, mark: done ? '✓' : now ? '•' : '', c: done || now ? 'var(--ink)' : 'var(--ink2)' }; }),
      revSecs: revSecs, noteDraft: st.noteDraft, onNote: (e) => this.setState({ noteDraft: e.target.value }),
      revCaption: this.secs[revSec].c, revTime: this.fmt(st.revT), revLeft: (st.revT / this.total * 100) + '%',
      ticks: this.starts.map((s) => (s / this.total * 100) + '%'),
      markPins: Object.keys(D.notes || {}).reduce((acc2, k) => acc2.concat(D.notes[k].map((n) => (n.t / this.total * 100) + '%')), []),
      scrub: (e) => { const el = e.currentTarget; if (!el || !el.getBoundingClientRect) return; const r = el.getBoundingClientRect(); const t = Math.round(Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * this.total); let s = 0; for (let i = 0; i < this.secs.length; i++) if (t >= this.starts[i]) s = i; this.setState({ revT: t, sel: s }); },
      playerOn: st.player, playerOff: !st.player, playerAria: st.player ? 'Pause' : 'Play',
      togglePlayer: () => { if (st.player) { this.stop('player'); this.setState({ player: false }); return; } this.setState({ player: true }); this.every('player', 250, () => { const t = this.state.revT + 1; if (t >= this.total) { this.stop('player'); this.setState({ player: false, revT: this.total }); return; } let s = 0; for (let i = 0; i < this.secs.length; i++) if (t >= this.starts[i]) s = i; this.setState({ revT: t, sel: s }); }); },
      blurs: (D.blurs || []).map((b) => ({ t: b.t, what: b.what, unsure: !b.s, done: !!b.s, status: b.s === 'keep' ? 'Kept blurred' : 'Shown', keep: () => this.patchDemo({ blurs: D.blurs.map((x) => x.id === b.id ? Object.assign({}, x, { s: 'keep' }) : x) }), show: () => this.patchDemo({ blurs: D.blurs.map((x) => x.id === b.id ? Object.assign({}, x, { s: 'show' }) : x) }), undo: () => this.patchDemo({ blurs: D.blurs.map((x) => x.id === b.id ? Object.assign({}, x, { s: '' }) : x) }) })),
      autoBlurNote: (blurCount - 1) + ' other kinds of thing were blurred automatically wherever they appeared.',
      files: [{ n: base + '.mp4', s: '1080p, 4:58' + (dCap === 'burn' ? ', captions in' : '') }].concat(dCap !== 'off' ? [{ n: base + '.srt', s: 'captions' }] : []).concat([{ n: base + '.txt', s: 'transcript' }]).concat(st.p720 ? [{ n: base + ' (720p).mp4', s: 'preview' }] : []),
      p720On: p.onStr, p720Track: p.track, p720X: p.x, toggle720: () => this.setState({ p720: !st.p720 }),
      exportNote: 'Captions ' + capName[dCap] + (dCorner !== 'off' && dCornerText.trim() ? ', corner label \u201c' + dCornerText.trim() + '\u201d' : ', no corner label') + '. Saved in your Videos folder. Your marks on this demo were used to tune ' + voicePretty + '’s defaults for next time.',
      key: st.key, onKey: (e) => this.setState({ key: e.target.value, keyRes: null }), keyType: st.keyType, keyTypeLabel: st.keyType === 'password' ? 'Show' : 'Hide', toggleKeyType: () => this.setState({ keyType: st.keyType === 'password' ? 'text' : 'password' }),
      testKey: () => { const ok = st.key.trim().length > 8; this.setState({ keyRes: ok ? 'ok' : 'bad', keyOn: ok ? true : st.keyOn }); if (ok && st.screen === 'settings') this.later('keyclose', 1400, () => this.setState({ keyEdit: false, key: '', keyRes: null })); },
      keyMsg: keyMsg, keyMsgColor: st.keyRes === 'bad' ? 'var(--danger)' : 'var(--ok)',
      w1Bg: w1.bg, w1Fg: w1.fg, w1Mark: st.keyRes === 'ok' ? '✓' : '1', w2Bg: w2.bg, w2Fg: w2.fg, w2Mark: st.tools === 'done' ? '✓' : '2', w3Bg: w3.bg, w3Fg: w3.fg, w3Mark: st.logged ? '✓' : '3',
      toolsIdle: st.tools === 'idle', toolsAsking: st.tools === 'ask',
      toolsText: st.tools === 'done' ? 'Playwright, ffmpeg and the recorder are installed.' : st.tools === 'ask' ? 'Install Playwright, ffmpeg and the recorder? About 400 MB, once.' : st.tools === 'busy' ? 'Installing…' : 'Playwright, ffmpeg and the recorder. Installed once, after you say yes.',
      askTools: () => this.setState({ tools: 'ask' }), cancelTools: () => this.setState({ tools: 'idle' }), installTools: () => { this.setState({ tools: 'busy' }); this.later('tools', 1600, () => this.setState({ tools: 'done' })); },
      wSite: st.wSite, onWSite: (e) => this.setState({ wSite: e.target.value }),
      loginLabel: st.logged ? 'Logged in' : 'Open browser', loginSite: () => { const u = st.wSite.trim(); if (!u) { this.say('Type the site first, e.g. whop.com'); return; } this.setState({ logged: true, sites: st.sites.some((s) => s.u === u) ? st.sites : [{ u: u, note: 'Saved Nov 4' }].concat(st.sites) }); },
      welcomeBlocked: !(st.keyRes === 'ok' && st.tools === 'done'), welcomeStatus: st.keyRes === 'ok' && st.tools === 'done' ? 'All set.' : 'The key and tools are needed before your first demo.',
      finishWelcome: () => this.setState({ screen: 'home', keyOn: true, key: '', keyRes: null }),
      appear: [['system', 'Follow Mac'], ['light', 'Light'], ['dark', 'Dark']].map((o) => ({ label: o[1], on: (st.theme || 'system') === o[0] ? 'true' : 'false', pick: () => this.setState({ theme: o[0] === 'system' ? null : o[0] }) })),
      defVoices: st.mine.map(dSel),
      keyRow: st.keyOn ? 'Connected, ending …4f2a, ' + this.num(st.credits) + ' credits left' : 'Not connected. Demos can’t be voiced until you add one.', keyRowColor: st.keyOn ? 'var(--ink2)' : 'var(--danger)',
      keyEdit: st.keyEdit, keyEditLabel: st.keyEdit ? 'Cancel' : (st.keyOn ? 'Change key' : 'Add key'), toggleKeyEdit: () => this.setState({ keyEdit: !st.keyEdit, key: '', keyRes: null }),
      sites: st.sites.map((s) => ({ u: s.u, note: s.note, relog: () => this.say('A browser opens so you can log in to ' + s.u + ' again'), forget: () => { const prev = st.sites; this.setState({ sites: st.sites.filter((x) => x.u !== s.u) }); this.say('Forgot ' + s.u, () => this.setState({ sites: prev })); } })),
      noSites: !st.sites.length,
      siteDraft: st.siteDraft, onSiteDraft: (e) => this.setState({ siteDraft: e.target.value }), addSite: () => { const u = st.siteDraft.trim(); if (!u) return; this.setState({ sites: st.sites.concat([{ u: u, note: 'Saved Nov 4' }]), siteDraft: '' }); this.say('A browser opens so you can log in to ' + u); },
      data: dataDefs.map((d) => ({ n: d.n, w: d.id === 'key' && !st.keyOn ? 'Removed' : d.w, l: d.l, can: !!d.l && !(d.id === 'key' && !st.keyOn) && !(d.id === 'logins' && !st.sites.length), act: dataAct[d.id] || (() => {}) })),
      wipeConfirm: st.wipeConfirm, notWipeConfirm: !st.wipeConfirm, askWipe: () => this.setState({ wipeConfirm: true }), cancelWipe: () => this.setState({ wipeConfirm: false }),
      doWipe: () => { this.setState({ wipeConfirm: false, keyOn: false, sites: [], hide: [], vals: Object.assign({}, this.presetVals.course), defVoice: 'alex', mine: ['alex', 'jessica', 'george'], heardVoices: {}, tools: 'idle' }); this.say('Everything this skill saved is gone. Your videos are untouched.', null, () => this.setState({ screen: 'welcome', keyRes: null, logged: false, wSite: '' }), 'Set up again'); },
      showWelcome: () => this.setState({ screen: 'welcome', keyRes: null, key: '', tools: st.tools === 'done' ? 'done' : 'idle', logged: false, wSite: '' }),
      chatOpen: st.chat.length > 0, chatDraft: st.chatDraft, onChat: (e) => this.setState({ chatDraft: e.target.value }),
      chatPlaceholder: st.screen === 'demo' ? 'Tell Claude what to change, e.g. “make it a demo of the payouts page instead”' : 'Ask Claude anything, or describe a new demo',
      chat: st.chat.map((m) => ({ text: m.t, side: m.me ? 'flex-end' : 'flex-start', bg: m.me ? 'var(--ink)' : 'var(--wash)', fg: m.me ? 'var(--sheet)' : 'var(--ink)' })),
      chatKey: (e) => { if (e.key === 'Enter') { e.preventDefault && e.preventDefault(); this.sendChatNow(); } },
      sendChat: () => this.sendChatNow(),
      chatAction: !!st.chatAct, doChatAction: () => this.setState({ screen: 'new', editing: false, bWhat: chatClean(st.chatAct), bNew: '', bVoice: st.defVoice, bSite: st.sites[0] ? st.sites[0].u : '', chatAct: null, chat: [] }),
      closeChat: () => this.setState({ chat: [], chatAct: null }),
      hasToast: !!st.toast, toast: st.toast, toastUndo: !!st.toastUndo, undoToast: () => { if (st.toastUndo) st.toastUndo(); this.setState({ toast: '', toastUndo: null, toastGo: null }); },
      toastGo: !!st.toastGo, toastGoLabel: st.toastGoLabel, goToast: () => { if (st.toastGo) st.toastGo(); this.setState({ toast: '', toastUndo: null, toastGo: null }); }
    };
  }
  sendChatNow() {
    const st = this.state; const m = (st.chatDraft || '').trim(); if (!m) return;
    const switching = /instead|new demo|different|switch/i.test(m);
    const reply = switching ? 'Got it. I’ll keep this one as a draft and start a new brief from what you said. Check it before I write anything?' : (st.screen === 'demo' ? 'On it. I’ll change that and only redo the parts it touches. You’ll see it update here.' : 'Sure. Tell me what you’d like to show and I’ll set up a new demo.');
    this.setState({ chat: st.chat.concat([{ me: true, t: m }, { me: false, t: reply }]), chatDraft: '', chatAct: switching ? m : null });
  }
}

(function () {
  const q = new URLSearchParams(location.search);
  const comp = new Component({ startOn: q.get('start') || 'welcome', theme: q.get('theme') || 'system' });
  const scope = PetiteVue.reactive(comp.renderVals());
  comp.setState = function (s) { Object.assign(comp.state, s); Object.assign(scope, comp.renderVals()); };
  try { window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => comp.setState({})); } catch (e) {}
  PetiteVue.createApp(scope).mount('#app');
  window.navi = comp;
})();
