// NAVI local UI. Interactive prototype: every screen and control works with sample data.
// The real skill serves this page locally and swaps the sample data for the engine's.
// Open ui/index.html in a browser. Optional: ?start=home|new|batch|voice|review|settings&theme=light|dark
class DCLogic { constructor(p) { this.props = p || {}; } setState(s) { Object.assign(this.state, s); } }
const PRESETS = {
  strict: { email: false, phone: false, names: false, address: false, money: false, customers: false, counts: false, usage: false, prices: false, dates: false },
  standard: { email: false, phone: false, names: false, address: false, money: false, customers: false, counts: false, usage: true, prices: true, dates: true },
  test: { email: true, phone: true, names: true, address: true, money: false, customers: false, counts: false, usage: true, prices: true, dates: true }
};
const SAMPLE_COST = 120; // credits to hear a voice the first time (preview card, Hear badge, library)
const ITEM_NAMES = { email: 'emails', phone: 'phone numbers', names: 'names and photos', address: 'addresses', money: 'revenue and balances', customers: 'customer details', counts: 'follower and member counts', usage: 'usage stats', prices: 'public prices', dates: 'dates' };
const COURSE = ['Welcome to the course', 'Create your whop', 'Add the Courses app', 'Plan your modules', 'Chapters and lessons', 'Pick a lesson type', 'Upload videos and files', 'Write lesson text', 'Add a quiz', 'Drip or open access', 'Brand your course', 'Set a cover image', 'Preview as a buyer', 'Check it on a phone', 'Write the product page', 'Set a price', 'Add a free trial', 'Connect payouts', 'Invite your first members', 'Post an announcement', 'Answer comments', 'Read your stats', 'What to do next'];
const WHOP = [
      { n: 'Intro', d: 22, v: 'Okay so… you’ve got your course all planned out, right? And now you’ve basically gotta get all of it into, um, into Whop.', c: 'Your course is planned out. Now you need to get it all into Whop.' },
      { n: 'Create the whop', d: 24, v: 'Okay, cool. So first, whop dot com slash start. It kind of asks what you’re here for.', c: 'First, go to whop.com/start. It asks what you’re here for.' },
      { n: 'Add the Courses app', d: 28, v: 'Now this is the part where people get stuck, honestly. It, well, it didn’t live in the app store when we checked.', c: 'This is where people get stuck. The Courses app wasn’t in the app store when we checked.' },
      { n: 'One card per module', d: 34, v: 'Name it by what the buyer actually walks away with. One’s a topic. One’s a result.', c: 'Name it by what the buyer walks away with. One’s a topic, one’s a result.' },
      { n: 'Chapters, then lessons', d: 32, v: 'Put something in the wrong order? You… you just drag the handle, it’s fine.', c: 'Wrong order? Drag the handle.' },
      { n: 'Lesson type', d: 34, v: 'Most of yours are gonna be Multimedia, so text, video, downloads, all in one.', c: 'Most will be Multimedia: text, video and downloads together.' },
      { n: 'Content and files', d: 30, v: 'Each file lives in one lesson. Its home. Not like three of them.', c: 'Each file lives in one lesson.' },
      { n: 'Timing', d: 26, v: 'Honestly? Leave it open. Delays kind of just annoy people.', c: 'Leave it open. Delays annoy people.' },
      { n: 'Branding', d: 22, v: 'The three dots up in the header, Edit branding.', c: 'Three dots in the header, then Edit branding.' },
      { n: 'Open it as a buyer', d: 28, v: 'Squash it down to phone size and do it all again. That’s where stuff breaks.', c: 'Check it at phone size too. That’s where things break.' },
      { n: 'Wrap-up', d: 16, v: 'And, remember, nothing’s on sale yet. That’s the next one.', c: 'Nothing’s on sale yet. That’s next.' }
    ];
const PAYOUTS = [
      { n: 'Intro', d: 9, v: 'Okay, so you’ve made a sale. Nice. Now let’s actually get paid.', c: 'You made a sale. Now let’s get paid.' },
      { n: 'Open payouts', d: 10, v: 'Top right, your balance. Click it, and then Payouts.', c: 'Click your balance, then Payouts.' },
      { n: 'Add a bank', d: 12, v: 'Add a bank account. It asks for, um, the usual stuff.', c: 'Add a bank account.' },
      { n: 'Verify', d: 11, v: 'It sends two tiny deposits. You type them in here, a day or two later.', c: 'Confirm the two small test deposits.' },
      { n: 'Pick a schedule', d: 9, v: 'Weekly is fine for most people. Honestly.', c: 'Weekly works for most people.' },
      { n: 'Wrap-up', d: 7, v: 'And that’s it. Money lands on its own now.', c: 'Payouts now run on their own.' }
];
const POSTS = [
      { n: 'Intro', d: 22, v: 'So, a whole week of posts, in about ten minutes. Let’s go.', c: 'A week of posts in about ten minutes.' },
      { n: 'Connect accounts', d: 30, v: 'First, connect the accounts. It’s, um, one click each.', c: 'Connect your accounts, one click each.' },
      { n: 'Write once', d: 36, v: 'Write the post once. It kind of reshapes it for each network.', c: 'Write once; it adapts for each network.' },
      { n: 'Pick the times', d: 34, v: 'Drag them onto the calendar. The green slots are when people are actually around.', c: 'Drag posts onto the green slots.' },
      { n: 'Check the preview', d: 32, v: 'Open the preview, because that’s where the line breaks go weird.', c: 'Check the preview for odd line breaks.' },
      { n: 'Wrap-up', d: 26, v: 'Hit schedule, and you’re done till next Monday.', c: 'Schedule it. Done until next Monday.' }
];
class Component extends DCLogic {
  constructor(props) {
    super(props);
    const start = props.startOn || 'welcome';
    this.scripts = { whop: WHOP, pay: PAYOUTS, posts: POSTS };
    this.useScript(null);
    this.VO = {
      alex: { name: 'ALEX', desc: 'Relaxed, low', g: 'm', img: 'assets/voice-alex.png', c: '#0000F2', adj: {}, models: ['v3', 'v4'] },
      jessica: { name: 'JESSICA', desc: 'Warm, clear', g: 'f', img: 'assets/voice-jessica.png', c: '#C2300C', adj: { energy: 1 }, models: ['v4'] },
      george: { name: 'GEORGE', desc: 'Deep, steady', g: 'm', img: 'assets/voice-george.png', c: '#0B4F37', adj: { energy: -1, pace: -2 }, models: ['v3'] },
      brian: { name: 'BRIAN', desc: 'Gravelly, casual', g: 'm', img: 'assets/voice-brian.png', c: '#111111', adj: { casual: 1 }, models: ['v4'] },
      lily: { name: 'LILY', desc: 'Bright, quick', g: 'f', img: 'assets/voice-lily.png', c: '#4B22D6', adj: { pace: 2, energy: 1 }, models: ['v3', 'v4'] },
      matilda: { name: 'MATILDA', desc: 'Soft, calm', g: 'f', img: 'assets/voice-matilda.png', c: '#000091', adj: { energy: -1 }, models: ['v4'] }
    };
    this.presetVals = { course: { casual: 7, energy: 3, pace: 100, hes: 1, breath: 1, swear: 0 }, saas: { casual: 8, energy: 5, pace: 105, hes: 2, breath: 1, swear: 0 }, tour: { casual: 5, energy: 4, pace: 100, hes: 0, breath: 1, swear: 0 } };
    this.ranges = { casual: [3, 8], energy: [1, 6], pace: [94, 108], hes: [0, 3], breath: [0, 2], swear: [0, 2] };
    const whop = { id: 'whop', title: 'Build it in Whop', site: 'whop.com', len: 2, who: 0, voice: 'alex', model: 'v4', kind: 'course', max: 4, cover: 'assets/cover-1.jpg', status: 'Watch the draft →', dot: 'ready', recorded: true, written: true,
      notes: { 2: [{ t: 60, text: 'Too cheerful after Add app' }], 4: [{ t: 125, text: 'Too fast' }] },
      blurs: [{ id: 'b1', t: '1:58', what: 'A name inside the course cover image', s: '' }, { id: 'b2', t: '3:53', what: 'What might be a price in a banner', s: '' }] };
    const demos = [whop,
      { id: 'pay', title: 'Connect payouts', site: 'whop.com', len: 0, who: 0, voice: 'alex', model: 'v4', kind: 'course', max: 5, cover: 'assets/cover-3.jpg', status: 'Exported Nov 2 · Open →', exportedOn: 'Nov 2', dot: 'done', recorded: true, written: true, exported: true, notes: {}, blurs: [] },
      { id: 'posts', title: 'Schedule a week of posts', site: 'app.yourproduct.com', len: 1, who: 1, voice: 'jessica', model: 'v4', kind: 'saas', max: 5, cover: 'assets/cover-4.jpg', status: 'Exported Oct 28 · Open →', exportedOn: 'Oct 28', dot: 'done', recorded: true, written: true, exported: true, notes: {}, blurs: [] }];
    demos.forEach((d) => Object.assign(d, { capMode: 'burn', corner: 'off', cornerText: '', lines: {} }));
    const batch = { id: 'b-whop2', name: 'Whop course, module 2', site: 'whop.com', voice: 'alex', kind: 'course', preset: 'standard', folder: '~/Movies/NAVI/Whop course, module 2', stage: 'recording', paused: false,
      items: COURSE.map((t, i) => ({ t: t, lesson: 'Lesson ' + (i + 1), min: [2, 3, 3, 4, 3, 2, 4, 3, 3, 2, 2, 2, 3, 3, 4, 2, 2, 3, 2, 2, 2, 3, 2][i], st: i < 2 ? 'approved' : i < 7 ? 'recorded' : i === 7 ? 'recording' : 'waiting' })) };
    const screen = start === 'voice' || start === 'review' ? 'demo' : start;
    this.state = {
      screen: screen, step: start === 'review' ? 4 : 1, cur: 'whop', demos: demos, batches: [batch], curBatch: 'b-whop2', theme: null, help: false,
      keyOn: start !== 'welcome', key: '', keyType: 'password', keyRes: null, keyEdit: false,
      tools: start === 'welcome' ? 'idle' : 'done', logged: false, wSite: '',
      credits: 26400, mine: ['alex', 'jessica', 'george'], defVoice: 'alex',
      vals: Object.assign({}, this.presetVals.course), caps: false, lock: true, heardVoices: {}, lastSample: null, sampling: false, sliderHelp: false,
      shown: Object.assign({}, PRESETS.standard), hide: ['Acme Studio'], hideDraft: '', pvMore: false,
      scSel: 0, scCaps: false, scChange: false, scDraft: '', scPending: null,
      revT: 86, player: false, markOpen: false, markDraft: '', blurOpen: false, p720: false,
      recPos: 4, recPaused: false, recStopAsk: false, recStopped: false, confirm: null,
      sites: [{ u: 'whop.com', note: 'Logged in to Demo Academy, saved Nov 4' }, { u: 'app.yourproduct.com', note: 'Saved Oct 28' }], siteDraft: '', wipeConfirm: false,
      lib: false, libF: 'all', chat: [], chatDraft: '', chatAct: null,
      defCap: 'burn', defCorner: 'off', defCornerText: '',
      mode: 'one', bMore: false, bKind: 'course', recDoneOpen: false, markOther: false, bWhat: '', bSite: 'whop.com', bSiteNew: false, bNew: '', bWho: 0, bLen: 2, bHide: '', bVoice: 'alex', bCap: 'burn', bCorner: 'off', bCornerText: '', editing: false,
      btSiteNew: false, btNew: '', btAll: false, fromBatch: null, batchItem: null, btText: '', btName: '', btFile: '', btSite: 'whop.com', btVoice: 'alex', btKind: 'course', btPreset: 'standard', btFolder: '', btOpen: null, bConfirm: false,
      toast: '', toastUndo: null, toastGo: null, toastGoLabel: ''
    };
    this.timers = {};
  }
  useScript(D) { const k = D && this.scripts[D.script || D.id] ? (D.script || D.id) : 'whop'; this.secs = this.scripts[k]; this.starts = []; let acc = 0; this.secs.forEach((x) => { this.starts.push(acc); acc += x.d; }); this.total = acc; }
  componentWillUnmount() { Object.keys(this.timers).forEach((k) => { clearTimeout(this.timers[k]); clearInterval(this.timers[k]); }); }
  later(name, ms, fn) { if (this.timers[name]) clearTimeout(this.timers[name]); this.timers[name] = setTimeout(fn, ms); }
  every(name, ms, fn) { if (this.timers[name]) clearInterval(this.timers[name]); this.timers[name] = setInterval(fn, ms); }
  stop(name) { if (this.timers[name]) { clearInterval(this.timers[name]); clearTimeout(this.timers[name]); delete this.timers[name]; } }
  focusLater(sel) { this.focusAt = Date.now(); requestAnimationFrame(() => { const el = typeof sel === 'string' ? document.querySelector(sel) : typeof sel === 'function' ? sel() : sel; if (el && el.focus) el.focus(); }); }
  // Focus model helpers: describe a control so it can be found again after a re-render (Undo, swapped buttons).
  describe(el) { if (!el || el === document.body || !el.getAttribute) return null; return { id: el.id || '', aria: el.getAttribute('aria-label') || '', text: (el.innerText || '').trim(), tag: el.tagName }; }
  findDesc(d) { if (!d) return null; const ok = (e) => e && e.isConnected && !e.disabled && e.offsetParent !== null; if (d.id) { const e = document.getElementById(d.id); if (ok(e)) return e; } const all = [...document.querySelectorAll(d.tag || 'button')].filter(ok); return (d.aria && all.find((e) => e.getAttribute('aria-label') === d.aria)) || (d.text && all.find((e) => (e.innerText || '').trim() === d.text)) || null; }
  heading() { return document.querySelector('#step-h, #batch-h, #demos-h, #set-h'); }
  escape() {
    const st = this.state; const back = (sel) => this.focusLater(sel);
    if (st.lib) { this.setState({ lib: false }); back('#vmore'); return true; }
    if (st.help) { this.setState({ help: false }); back('#helpbtn'); return true; }
    if (st.chat.length) { this.setState({ chat: [], chatAct: null }); back('#chatin'); return true; }
    if (st.markOpen) { this.setState({ markOpen: false, markOther: false, markDraft: '' }); back('#markbtn'); return true; }
    if (st.wipeConfirm) { this.setState({ wipeConfirm: false }); back('#wipebtn'); return true; }
    if (st.confirm) { this.setState({ confirm: null }); back('.stepfoot .pri'); return true; }
    if (st.screen === 'batch' && st.bConfirm) { this.setState({ bConfirm: false }); back('.bprimary'); return true; }
    if (st.screen === 'new' && st.bSiteNew) { this.setState({ bSiteNew: false, bNew: '' }); back('#bnewchip'); return true; }
    if (st.screen === 'new' && st.btSiteNew) { this.setState({ btSiteNew: false, btNew: '' }); back('#btnewchip'); return true; }
    if (st.screen === 'settings' && st.keyEdit) { this.setState({ keyEdit: false, key: '', keyRes: null }); back('#keytoggle'); return true; }
    return false;
  }
  outside(t) {
    const st = this.state; const inside = (sel) => { const el = document.querySelector(sel); return el && el.contains(t); };
    if (st.help && !inside('#helpdlg') && !inside('#helpbtn')) this.setState({ help: false });
    if (st.markOpen && !inside('.markslot')) this.setState({ markOpen: false, markOther: false, markDraft: '' });
    if (st.wipeConfirm && !inside('#wiperow')) this.setState({ wipeConfirm: false });
    if (st.chat.length && !inside('.chatinner')) this.setState({ chat: [], chatAct: null });
  }
  say(msg, undo, go, goLabel) { if (undo) this.undoFrom = this.describe(document.activeElement); this.toastWhere = this.state.screen + '/' + this.state.step; this.setState({ toast: msg, toastUndo: undo || null, toastGo: go || null, toastGoLabel: goLabel || '' }); this.later('toast', 4200, () => this.setState({ toast: '', toastUndo: null, toastGo: null })); }
  fmt(t) { const m = Math.floor(t / 60); const s = Math.floor(t % 60); return m + ':' + (s < 10 ? '0' : '') + s; }
  num(n) { return n.toLocaleString('en-US'); }
  plural(n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); }
  demo() { return this.state.demos.find((d) => d.id === this.state.cur) || this.state.demos[0]; }
  batch() { return this.state.batches.find((b) => b.id === this.state.curBatch) || this.state.batches[0]; }
  patchDemo(p) { const id = this.state.cur; this.setState({ demos: this.state.demos.map((d) => d.id === id ? Object.assign({}, d, p) : d) }); }
  patchBatch(p, id) { const bid = id || this.state.curBatch; this.setState({ batches: this.state.batches.map((b) => b.id === bid ? Object.assign({}, b, typeof p === 'function' ? p(b) : p) : b) }); }
  recFor(voice, kind) { const base = Object.assign({}, this.presetVals[kind]); const adj = (this.VO[voice] || {}).adj || {}; Object.keys(adj).forEach((k) => { const r = this.ranges[k]; base[k] = Math.max(r[0], Math.min(r[1], base[k] + adj[k])); }); return base; }
  spend(n) { this.setState({ credits: Math.max(0, this.state.credits - n) }); }
  needKey() { if (this.state.keyOn) return false; this.say('Connect your ElevenLabs key first', null, () => this.setState({ screen: 'settings', keyEdit: true }), 'Connect'); return true; }
  presetOf(shown) { const keys = Object.keys(PRESETS); for (let i = 0; i < keys.length; i++) { const p = PRESETS[keys[i]]; if (Object.keys(p).every((k) => p[k] === shown[k])) return keys[i]; } return 'custom'; }
  perVideo(min) { return Math.round(min * 930 / 10) * 10; }
  fitsText(n) { return 'Enough credits for about ' + this.plural(n, 'more video') + '. The batch pauses there until you top up. Nothing fails.'; }
  startRecording(from) {
    this.useScript(this.demo()); const N = this.secs.length;
    this.setState({ recPos: from || 0, recPaused: false, recStopped: false, recSlide: 0, recSliding: false });
    this.patchDemo({ status: 'Recording, section ' + ((from || 0) + 1) + ' of ' + N, dot: 'busy' });
    this.every('rec', 900, () => {
      const p = this.state.recPos + 1;
      if (p >= N) { this.stop('rec'); this.setState({ recPos: N }); this.patchDemo({ recorded: true, max: Math.max(this.demo().max, 4), status: 'Watch the draft →', dot: 'ready', blurs: [{ id: 'n1', t: '0:41', what: 'What might be an email in a sidebar', s: '' }] }); this.spend(4600); this.say('Draft 1 is ready', null, () => this.setState({ step: 4 }), 'Watch it'); }
      else { this.setState({ recPos: p }); this.patchDemo({ status: 'Recording, section ' + (p + 1) + ' of ' + N }); }
    });
  }
  runBatch() {
    this.every('batch', 2400, () => {
      const b = this.batch(); if (!b || b.stage !== 'recording' || b.paused) return;
      const i = b.items.findIndex((x) => x.st === 'recording');
      if (i < 0) { this.stop('batch'); return; }
      const cost = this.perVideo(b.items[i].min);
      if (this.state.credits < cost) { this.patchBatch({ paused: 'credits' }); this.say('Batch paused: not enough credits for the next video'); return; }
      this.spend(cost);
      const items = b.items.map((x, k) => k === i ? Object.assign({}, x, { st: 'recorded' }) : (k === i + 1 && x.st === 'waiting' ? Object.assign({}, x, { st: 'recording' }) : x));
      this.patchBatch({ items: items, stage: items.some((x) => x.st === 'recording') ? 'recording' : 'review' });
    });
  }
  // Each batch video gets its own demo record the first time it's watched (no marks, no blurs), so Review shows that video.
  batchDemos(b, i) { const id = b.id + '#' + i; if (this.state.demos.some((d) => d.id === id)) return { id: id, demos: this.state.demos }; const it = b.items[i]; const vo = this.VO[b.voice] || this.VO.alex; const d = { id: id, batchOf: b.id, title: it.t, site: b.site, len: 1, who: 0, voice: b.voice, model: vo.models.indexOf('v4') >= 0 ? 'v4' : vo.models[0], kind: b.kind, max: 4, cover: ['assets/cover-1.jpg', 'assets/cover-3.jpg', 'assets/cover-4.jpg'][i % 3], status: '', dot: '', recorded: true, written: true, notes: {}, blurs: [], lines: {}, capMode: 'burn', corner: 'off', cornerText: '' }; return { id: id, demos: this.state.demos.concat([d]) }; }
  openBatch(id) { this.setState({ screen: 'batch', curBatch: id || this.state.curBatch, btOpen: null, help: false, confirm: null, bConfirm: false }); }
  renderVals() {
    const st = this.state; const D = this.demo(); this.useScript(D); const N = this.secs.length; const v = st.vals; const B = this.batch();
    const voice = D.voice; const VO = this.VO; const vInfo = VO[voice]; const model = D.model || 'v4';
    const rec = this.recFor(voice, D.kind);
    let theme = st.theme || this.props.theme || 'system';
    if (theme === 'system') { try { theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; } catch (e) { theme = 'light'; } }
    const vcol = (k) => theme === 'dark' ? ({ alex: '#7C88FF', jessica: '#FF7A57', george: '#4FC08F', brian: '#C8C8C8', lily: '#A48FFF', matilda: '#7C88FF' }[k] || VO[k].c) : VO[k].c;
    const pretty = (k) => VO[k].name.charAt(0) + VO[k].name.slice(1).toLowerCase();
    const voicePretty = pretty(voice);
    const lineOf = (i) => (D.lines && D.lines[i]) || this.secs[i].v;
    // ---- marks (flattened) ----
    const secAt = (t) => { for (let i = this.secs.length - 1; i >= 0; i--) if (t >= this.starts[i]) return i; return 0; };
    const allMarks = []; Object.keys(D.notes || {}).forEach((k) => (D.notes[k] || []).forEach((n, j) => allMarks.push({ k: k, j: j, t: n.t, text: n.text })));
    allMarks.sort((a, b) => a.t - b.t);
    const marks = allMarks.length;
    const markedSecs = Object.keys(D.notes || {}).filter((k) => D.notes[k].length);
    const unsureBlurs = (D.blurs || []).filter((b) => !b.s); const unsure = unsureBlurs.length;
    // ---- privacy ----
    const preset = this.presetOf(st.shown);
    const blurredItems = Object.keys(ITEM_NAMES).filter((k) => !st.shown[k]); const shownItems = Object.keys(ITEM_NAMES).filter((k) => st.shown[k]);
    const blurCount = 7 + blurredItems.length + st.hide.length;
    const listText = (ks) => { const w = ks.map((k) => ITEM_NAMES[k]); if (!w.length) return ''; if (w.length === 1) return w[0]; return w.slice(0, -1).join(', ') + ' and ' + w[w.length - 1]; };
    const presetName = { strict: 'Strict', standard: 'Standard', test: 'Test account', custom: 'Custom' };
    // ---- length / pace ----
    const pace = model === 'v3' ? v.pace : 100;
    const baseSec = this.total;
    const lengthSec = Math.round(baseSec * 100 / pace);
    const videoCost = Math.round(4600 * baseSec / this.total / 10) * 10; const leftAfter = Math.max(0, st.credits - videoCost);
    const lengthText = this.fmt(lengthSec);
    const paceText = (pace / 100).toFixed(2) + 'x';
    const kindName = { course: 'course walkthrough', saas: 'quick demo', tour: 'product tour' }[D.kind];
    const isPhone = (() => { try { return window.matchMedia('(max-width: 860px)').matches; } catch (e) { return false; } })();
    const recording = !D.recorded && st.recPos < N && !st.recStopped;
    const voiceOk = vInfo.models.indexOf(model) >= 0;
    const S = [
      { name: 'Script', sub: D.written ? N + ' sections' : 'Writing…', title: 'Read the script', help: 'Pick a section to read it. Change one line here, or ask Claude below for bigger changes.', cta: D.max > 0 ? 'Next: Voice' : 'Approve script' },
      { name: 'Voice', sub: voicePretty + ', ' + (model === 'v4' ? 'Eleven v4' : 'Eleven v3'), title: 'Pick the voice', help: 'Click a face to pick it. NAVI switches the model if that voice needs it. Press Hear to listen.', cta: 'Use ' + voicePretty },
      { name: 'Privacy', sub: presetName[preset], title: 'Choose what gets blurred', help: 'Blurring happens while recording, then every frame is checked again. Anything unclear shows up in Review.', cta: D.recorded ? 'Use these blurs' : 'Use these blurs and record' },
      { name: 'Record', sub: D.recorded ? 'Done, ' + lengthText : (st.recStopped ? 'Stopped' : (recording && st.cur === D.id && D.max >= 3 ? 'Section ' + Math.min(N, st.recPos + 1) + ' of ' + N : 'Not yet')), title: D.recorded ? 'Recorded' : (st.recStopped ? 'Recording stopped' : 'Recording'), help: D.recorded ? 'Every section is recorded. Watch the draft next.' : 'The browser does the clicks while ' + voicePretty + ' talks. You can close this page: NAVI keeps going and the draft shows up on All demos.', helpHold: 'The browser does the clicks while ' + voicePretty + ' talks. You can close this page: NAVI keeps going and the draft shows up on All demos.', cta: 'Watch the draft', second: D.recorded ? 'Record again' : '' },
      { name: 'Review', sub: marks ? this.plural(marks, 'mark') : (D.recorded ? 'No marks' : 'Not yet'), title: 'Watch the draft', help: 'Press Mark this moment when something is off. Only marked sections are redone.', cta: marks ? 'Redo ' + this.plural(markedSecs.length, 'section') : (st.fromBatch ? 'Approve and watch next' : 'Looks good, go to Export'), ctaShort: marks ? 'Redo ' + this.plural(markedSecs.length, 'section') : (st.fromBatch ? 'Approve, next' : 'Go to Export'), second: '', skip: marks ? 'Skip redo, keep as is' : '' },
      { name: 'Export', sub: D.exported ? 'Exported' : 'Not yet', title: D.exported ? 'Exported' : 'Export', help: D.exported ? 'Saved to Movies/NAVI. Change a setting to export again, free.' : 'Choose captions and a corner label. Changing these costs no credits.', cta: D.exported ? (D.dirty ? 'Export again' : 'Open folder') : 'Export video', second: D.exported && D.dirty ? 'Open folder' : '' }
    ];
    const bNextReady = (() => { if (!st.fromBatch) return false; const bb = st.batches.find((x) => x.id === st.fromBatch); return !!bb && bb.items.some((x, k) => k !== st.batchItem && x.st === 'recorded'); })();
    if (st.fromBatch && !marks) { S[4].cta = bNextReady ? 'Approve and watch next' : 'Approve, back to the batch'; S[4].ctaShort = bNextReady ? 'Approve, next' : 'Approve'; }
    const cur = S[st.step];
    const steps = S.map((s, i) => {
      const locked = i > D.max; const now = i === st.step; const done = (i < D.max && !(i === 3 && !D.recorded)) || (i === 5 && D.exported);
      return { name: s.name, sub: s.sub, cur: now ? 'step' : 'false', locked: locked, cls: 'stepbtn' + (now ? ' now' : '') + (locked ? ' locked' : ''), tip: locked ? 'Finish the step before first' : '', mark: done ? '✓' : String(i + 1), dotCls: 'stepdot' + (done ? ' done' : ''), go: () => { if (!locked) this.setState({ step: i, confirm: null, markOpen: false }); } };
    });
    const setVals = (n, msg, prev) => { this.setState({ vals: n }); if (msg) this.say(msg, prev ? () => this.setState({ vals: prev }) : null); };
    const setV = (k, x) => { const n = Object.assign({}, this.state.vals); if (n[k] === x) return; n[k] = x; this.setState({ vals: n }); };
    const drag = (e, d) => { const el = e.currentTarget; if (!el || !el.getBoundingClientRect) return; const r = el.getBoundingClientRect(); let p = (e.clientX - r.left) / r.width; p = Math.max(0, Math.min(1, p)); setV(d.k, Math.round(d.min + p * (d.max - d.min))); };
    const defs = [
      { k: 'casual', label: 'Casualness', f: (x) => ['', '', '', 'Polished', 'Neat', 'Plain', 'Relaxed', 'Very casual', 'Loose'][x], low: 'Lower: cleaner, but can sound like a script.', high: 'Higher: more "gonna" and "kind of".' },
      { k: 'energy', label: 'Energy', f: (x) => ['', 'Very calm', 'Calm', 'Relaxed', 'Warm', 'Lively', 'Upbeat'][x], low: 'Lower: steady, can go flat.', high: 'Higher: livelier, can sound overexcited.' },
      { k: 'pace', label: 'Pace', f: (x) => (x / 100).toFixed(2) + 'x', low: 'Slower: easy to follow, can drag.', high: 'Faster: snappy, can rush the clicks.' },
      { k: 'hes', label: 'Hesitations', f: (x) => ['None', 'A few', 'Some', 'More'][x], low: 'Fewer: can sound too perfect.', high: 'More: human, but too many sounds nervous.' },
      { k: 'breath', label: 'Breaths', f: (x) => ['Trimmed', 'Natural', 'Kept'][x], low: 'Trimmed: can sound stitched together.', high: 'Kept: only natural breaths, never forced.' },
      { k: 'swear', label: 'Swearing', f: (x) => ['Off', 'One', 'A few'][x], low: 'Off: fine for any audience.', high: 'On: at natural reactions, never in instructions.' }
    ].filter((d) => d.k !== 'pace' || model === 'v3').map((d) => Object.assign(d, { min: this.ranges[d.k][0], max: this.ranges[d.k][1] }));
    const chipFor = (d) => { const W = 300; const w = d.f(v[d.k]).length * 8.6; const lo = (W - 14 - w) / W * 100; const hi = (W - 10) / W * 100; const p1 = (v[d.k] - d.min) / (d.max - d.min) * 100; const p2 = (rec[d.k] - d.min) / (d.max - d.min) * 100; return (p1 > lo && p1 < hi) || (p2 > lo && p2 < hi); };
    const sliders = defs.map((d) => ({ k: d.k, label: d.label, min: d.min, max: d.max, value: v[d.k], display: d.f(v[d.k]), pct: ((v[d.k] - d.min) / (d.max - d.min) * 100) + '%', rec: ((rec[d.k] - d.min) / (d.max - d.min) * 100) + '%', off: v[d.k] !== rec[d.k], low: d.low, high: d.high, isSwear: d.k === 'swear',
      reset: () => { const prev = this.state.vals; const n = Object.assign({}, prev); n[d.k] = rec[d.k]; setVals(n, d.label + ' back to recommended', prev); this.focusLater('#rng-' + d.k); },
      onChange: (e) => setV(d.k, Number(e.target.value)),
      down: (e) => { this.dragKey = d.k; const inp = e.currentTarget.querySelector('input'); if (inp) { e.preventDefault(); inp.focus({ preventScroll: true }); } try { e.currentTarget.setPointerCapture(e.pointerId); } catch (x) {} drag(e, d); },
      move: (e) => { if (this.dragKey === d.k) drag(e, d); },
      up: () => { this.dragKey = null; } }));
    const changed = defs.filter((d) => v[d.k] !== rec[d.k]).length;
    let line = (v.hes >= 1 ? 'Okay, cool. ' : '') + 'So first, ' + (v.hes >= 2 ? 'um, ' : '') + 'whop dot com slash start. ';
    line += v.casual >= 7 ? 'It kind of asks what you’re here for, so I’m gonna hit “I want a business”.' : 'It asks what you’re here for, so I’ll hit “I want a business”.';
    const caption = line;
    const sampleKey = voice + model + JSON.stringify(v);
    const sw = (on) => ({ cls: on ? 'sw on' : 'sw', onStr: on ? 'true' : 'false' });
    const warns = { email: 'Real people’s emails would be visible to anyone watching.', money: 'Showing earnings in marketing can count as a claim you have to back up.', customers: 'This is other people’s data. Only show it if it’s fake.' };
    const row = (id, label) => { const on = st.shown[id]; const s = sw(on); const w = on && warns[id]; return { id: 'pv-' + id, label: label, warn: w || '', hasWarn: !!w, cls: s.cls, onStr: s.onStr, toggle: () => { const m = Object.assign({}, this.state.shown); m[id] = !on; this.setState({ shown: m }); } }; };
    const addMark = (text) => { const t = st.revT; const i = secAt(t); const n = Object.assign({}, D.notes); n[i] = (n[i] || []).concat([{ t: t, text: text }]); this.patchDemo({ notes: n }); this.setState({ markOpen: false, markOther: false, markDraft: '' }); this.focusLater('#markbtn'); this.say('Marked ' + this.fmt(t) + ': ' + text); };
    const stopNow = () => { this.stop('rec'); this.setState({ recStopped: true, recPaused: false, recSlide: 0, recSliding: false }); this.patchDemo({ status: 'Stopped at ' + st.recPos + ' of ' + N, dot: 'wait' }); this.say('Stopped. ' + this.plural(st.recPos, 'finished section') + ' kept.'); this.focusLater('#reccarry'); };
    const goStep = (i) => { const p = { step: i, confirm: null, markOpen: false }; this.setState(p); if (D.max < i) this.patchDemo({ max: i }); };
    const doExport = () => { this.patchDemo({ exported: true, dirty: false, exportedOn: 'Nov 5', status: 'Exported Nov 5 · Open →', dot: 'done', max: 5 }); this.setState({ confirm: null }); this.focusAt = Date.now(); requestAnimationFrame(() => { const el = document.querySelector('.stepfoot .pri'); if (el) el.focus({ preventScroll: true }); }); this.say('Exported to Movies/NAVI', null, () => this.say('Opening Movies/NAVI'), 'Open folder'); };
    const primaryFor = [
      () => goStep(1),
      () => { if (!voiceOk) return; goStep(2); this.say(st.lock ? voicePretty + ' is set for every demo in this project' : 'Using ' + voicePretty + ' for this demo'); },
      () => { const fresh = !D.recorded && st.recPos === 0 && !this.timers.rec; if (fresh) { if (this.needKey()) return; this.setState({ confirm: 'record' }); this.focusLater('#cfyes'); return; } goStep(3); if (!D.recorded && !this.timers.rec && !st.recPaused && !st.recStopped) { if (this.needKey()) return; this.startRecording(st.recPos); } },
      () => goStep(4),
      () => { if (marks) { this.setState({ confirm: 'redo' }); return; } if (unsure) { this.setState({ confirm: 'approve' }); this.focusLater('#cfno'); return; } if (st.fromBatch) { batchApproveNext(); return; } goStep(5); },
      () => { if (!D.exported || D.dirty) doExport(); else this.say('Opening Movies/NAVI'); }
    ];
    const secondaryFor = [null, null, null, () => { if (this.needKey()) return; this.patchDemo({ recorded: false }); this.startRecording(); }, () => this.setState({ confirm: 'approve' }), () => this.say('Opening Movies/NAVI')];
    const confirms = {
      approve: { text: [marks ? this.plural(marks, 'mark') + ' kept, not redone' : '', unsure ? this.plural(unsure, 'blur') + ' not checked' : ''].filter(Boolean).join(', '), no: 'Go back', yes: 'Approve anyway', act: () => { if (st.fromBatch) { this.setState({ confirm: null }); batchApproveNext(); } else goStep(5); } },
      record: { text: 'Recording uses about ' + this.num(videoCost) + ' credits', no: 'Cancel', yes: 'Yes, record', act: () => { if (this.needKey()) return; this.setState({ confirm: null }); goStep(3); this.startRecording(0); } },
      redo: { text: 'Redo ' + this.plural(markedSecs.length, 'section') + ' for about ' + this.num(markedSecs.length * 420) + ' credits?', no: 'Cancel', yes: 'Redo them', act: () => { if (this.needKey()) return; this.spend(markedSecs.length * 420); const prev = D.notes; this.patchDemo({ notes: {} }); this.setState({ confirm: null }); this.say('Redoing ' + this.plural(markedSecs.length, 'section') + '. Draft 2 will be here in a few minutes.'); } }
    };
    const batchApproveNext = () => { const bid = st.fromBatch; const bb = st.batches.find((x) => x.id === bid); if (!bb) return; const items = bb.items.map((x, k) => k === st.batchItem ? Object.assign({}, x, { st: 'approved' }) : x); this.patchBatch({ items: items }, bid); const next = items.findIndex((x) => x.st === 'recorded'); this.say('Approved “' + bb.items[st.batchItem].t + '”'); if (next >= 0) { const r = this.batchDemos(Object.assign({}, bb, { items: items }), next); this.setState({ demos: r.demos, cur: r.id, batchItem: next, revT: 0, markOpen: false, confirm: null }); this.focusLater('#playbtn'); } else this.setState({ screen: 'batch', fromBatch: null, batchItem: null, confirm: null }); };
    const cf = st.confirm ? confirms[st.confirm] : null;
    const pvFoot = { strict: 'Strict', standard: 'Standard', test: 'Test account', custom: 'Custom' }[preset];
    const footTexts = [
      D.written ? (D.max > 0 ? 'Approved. You can still change any line.' : 'Not approved yet. ' + this.secs.length + ' sections, about ' + lengthText) : 'Claude is writing the script',
      voiceOk ? voicePretty + (changed ? ', ' + changed + ' setting' + (changed === 1 ? '' : 's') + ' changed' : ', recommended for a ' + kindName) : voicePretty + ' needs Eleven ' + vInfo.models[0] + '. Pick another voice, or',
      pvFoot + (D.recorded ? '' : ' · recording uses about ' + this.num(videoCost) + ' credits'),
      D.recorded ? 'Recorded, ' + lengthText : (st.recStopped ? 'Stopped. Finished sections are kept.' : (st.recPaused ? 'Paused. The draft is ready when recording finishes.' : 'The draft is ready when recording finishes.')),
      marks ? 'Marked sections are redone, then you watch them again. About ' + this.num(markedSecs.length * 420) + ' credits.' : (unsure ? this.plural(unsure, 'blur') + ' to check' : 'Nothing marked'),
      D.exported ? (D.dirty ? 'Changed. Export again to update the files.' : 'Exported ' + (D.exportedOn || 'Nov 5') + ' · ' + this.plural(1 + ((D.capMode || 'burn') === 'file' ? 1 : 0) + 1 + (st.p720 ? 1 : 0), 'file')) : 'Saves to Movies/NAVI'
    ];
    const footBad = (st.step === 1 && !voiceOk);
    const footKinds = [D.written ? (D.max > 0 ? 'done' : 'ready') : 'busy', 'ready', 'ready', D.recorded ? 'done' : (st.recPaused || st.recStopped ? 'wait' : 'busy'), 'ready', D.exported && !D.dirty ? 'done' : 'ready'];
    const foot = cf ? { text: cf.text, dot: 'ready', color: 'var(--ink)' } : { text: footTexts[st.step], dot: footBad ? 'bad' : footKinds[st.step], color: footBad ? 'var(--ink)' : 'var(--ink2)' };
    const wsw = (done) => done ? 'wnum done' : 'wnum';
    const l = sw(st.lock), p = sw(st.p720), a = sw(st.caps);
    const dataDefs = [{ id: 'settings', n: 'Voice, privacy and learned preferences', w: 'Stored on this Mac. You can undo a reset.', l: 'Reset to defaults' }, { id: 'videos', n: 'Finished videos', w: 'Movies/NAVI. Never deleted from here.', l: 'Open folder' }];
    const dataAct = {
      logins: () => { const prev = st.sites; this.setState({ sites: [] }); this.focusAt = Date.now(); requestAnimationFrame(() => { const el = document.getElementById('addsite'); if (!el) return; el.focus({ preventScroll: true }); const band = document.querySelector('.chatband'); if (band && el.getBoundingClientRect().bottom > band.getBoundingClientRect().top - 8) el.scrollIntoView({ block: 'center', behavior: 'instant' }); }); this.say('All saved logins forgotten', () => this.setState({ sites: prev })); },
      videos: () => this.say('Opening Movies/NAVI'),
      settings: () => { const prev = { vals: st.vals, hide: st.hide, shown: st.shown, defVoice: st.defVoice, defCap: st.defCap, defCorner: st.defCorner, defCornerText: st.defCornerText }; this.setState({ vals: Object.assign({}, this.presetVals.course), hide: [], shown: Object.assign({}, PRESETS.standard), defVoice: 'alex', defCap: 'burn', defCorner: 'off', defCornerText: '' }); this.say('Settings reset', () => this.setState(prev)); }
    };
    const keyMsg = st.keyRes === 'empty' ? 'Paste the key first.' : st.keyRes === 'ok' ? 'Connected. Starter plan, ' + this.num(st.credits) + ' of 30,000 credits left. Saved in your Mac’s Keychain.' : st.keyRes === 'bad' ? 'That key didn’t work. Check you copied all of it and it has text to speech access.' : '';
    const chatClean = (m) => { let s = m.replace(/^(actually|no|ok|okay|wait)[,!.\s]*/i, '').replace(/^(make|do|change)( it| this)?( into)?( a)? demo (of|for|on|about)\s*/i, '').replace(/\s*instead[.!]*$/i, ''); return s.charAt(0).toUpperCase() + s.slice(1); };
    const segOf = (opts, cur2, fn) => opts.map((o) => ({ label: o[1], on: cur2 === o[0] ? 'true' : 'false', pick: () => fn(o[0]) }));
    const capOpts = [['burn', 'In the video'], ['file', 'Separate file'], ['off', 'Off']];
    const posOpts = [['off', 'Off'], ['tl', 'Top left'], ['tr', 'Top right'], ['bl', 'Bottom left'], ['br', 'Bottom right']];
    const capName = { burn: 'burned in', file: 'as a separate file', off: 'off' };
    const cornerCtl = (cur2, set, fid) => { const on = cur2 !== 'off'; return { on: on, onStr: on ? 'true' : 'false', cls: on ? 'sw on' : 'sw', toggle: () => { set(on ? 'off' : (this.lastCorner || 'tr')); if (!on && fid) requestAnimationFrame(() => { const el = document.getElementById(fid); if (el) el.focus(); }); }, seg: [['tl', 'Top left'], ['tr', 'Top right'], ['bl', 'Bottom left'], ['br', 'Bottom right']].map((o) => ({ label: o[1], on: cur2 === o[0] ? 'true' : 'false', pick: () => { this.lastCorner = o[0]; set(o[0]); } })) }; };
    const posCss = { tl: 'left: 14px; top: 14px', tr: 'right: 14px; top: 14px', bl: 'left: 14px; bottom: 14px', br: 'right: 14px; bottom: 14px' };
    const dCap = D.capMode || 'burn'; const dCorner = D.corner || 'off'; const dCornerText = D.cornerText || '';
    const base = D.title.replace(/…$/, '');
    // ---- new demo ----
    const siteOk = (u) => /^[a-z0-9-]+(\.[a-z0-9-]+)+(\/.*)?$/i.test((u || '').trim().replace(/^https?:\/\//i, ''));
    const lenOpts = [1, 3, 5, 8];
    const suggestLen = (() => { const w = st.bWhat.trim(); if (!w) return -1; const n = 1 + (w.match(/,| then | and /gi) || []).length; const mins = Math.max(1, n + (st.bWho === 0 ? 1 : st.bWho === 2 ? -1 : 0)); let best = 0; lenOpts.forEach((o, i) => { if (Math.abs(o - mins) < Math.abs(lenOpts[best] - mins)) best = i; }); return best; })();
    const bSiteVal = st.bSiteNew ? st.bNew.trim() : st.bSite;
    const posName = { tl: 'top left', tr: 'top right', bl: 'bottom left', br: 'bottom right' };
    const kindLabel = { course: 'course walkthrough', saas: 'quick demo', tour: 'product tour' };
    const summaryParts = [['Beginners', 'Some experience', 'Pros'][st.bWho], kindLabel[st.bKind].charAt(0).toUpperCase() + kindLabel[st.bKind].slice(1), lenOpts[st.bLen] + ' min' + (st.bLen === suggestLen ? ' (suggested)' : ''), pretty(st.bVoice), { burn: 'Captions on', file: 'Captions as a file', off: 'No captions' }[st.bCap]].concat(st.bCorner === 'off' ? [] : ['label' + (st.bCornerText.trim() ? ': ' + st.bCornerText.trim() + ',' : '') + ' ' + posName[st.bCorner]]);
    if (st.bHide.trim()) summaryParts.push('keep “' + st.bHide.trim() + '” off screen');
    // ---- batch (new) ----
    const btLines = st.btText.split(/\r?\n/).map((s) => s.replace(/^\s*(?:[-*•]|\d+[.)]|#+)\s*/, '').split(/\t|,(?=(?:[^"]*"[^"]*")*[^"]*$)/)[0].replace(/^"|"$/g, '').trim()).filter((s) => s && !/^(title|lesson|name)$/i.test(s));
    const btCount = btLines.length; const btMin = btCount * 3; const btCost = btCount * this.perVideo(3);
    const btShort = btCost > st.credits; const btFits = Math.floor(st.credits / this.perVideo(3));
    const btName = st.btName.trim() || (st.btFile ? st.btFile.replace(/\.[a-z]+$/i, '') : 'New batch');
    const btFolder = st.btFolder.trim() || '~/Movies/NAVI/' + btName;
    // ---- batch (screen) ----
    const bItems = B ? B.items : []; const cnt = (s) => bItems.filter((x) => x.st === s).length;
    const bRecorded = bItems.filter((x) => ['recorded', 'approved', 'exported'].indexOf(x.st) >= 0).length;
    const bApproved = cnt('approved'); const bExported = cnt('exported'); const bToRecord = bItems.filter((x) => x.st === 'waiting' || x.st === 'recording');
    const bLeftCost = bToRecord.reduce((s, x) => s + this.perVideo(x.min), 0); const bLeftMin = bToRecord.reduce((s, x) => s + x.min * 3, 0);
    const bFits = (() => { let c = st.credits, n = 0; for (const x of bToRecord) { const k = this.perVideo(x.min); if (c < k) break; c -= k; n++; } return n; })();
    const stLabel = { writing: 'Writing script', script: 'Script ready', waiting: 'Waiting', recording: 'Recording now', recorded: 'Ready to watch', approved: 'Approved', exported: 'Exported' };
    const bReady = cnt('recorded');
    const stDot = { writing: 'busy', script: 'ready', waiting: 'wait', recording: 'busy', recorded: 'ready', approved: 'done', exported: 'done' };
    const bStageIdx = B ? ({ writing: 0, approve: 1, recording: 2, review: 3, done: 4 }[B.stage]) : 0;
    const nowIdx = bStageIdx === 2 && bReady > 0 ? 3 : bStageIdx;
    const bStages = [['Write scripts', B && B.stage === 'writing' ? 'Writing…' : 'Done'], ['Approve scripts', bStageIdx > 1 ? 'Done' : bStageIdx === 1 ? cnt('script') + ' to read' : 'Not yet'], ['Record', bStageIdx < 2 ? 'Not yet' : bRecorded + ' of ' + bItems.length + ' recorded'], ['Review', bStageIdx < 2 ? 'Not yet' : (bReady ? bReady + ' ready to watch' : (bApproved + bExported) + ' approved')], ['Export', bExported ? bExported + ' exported' : (bApproved ? bApproved + ' approved' : 'Not yet')]].map((o, i) => { const done = i < Math.min(bStageIdx, 2) || (i === 2 && bRecorded === bItems.length && bItems.length > 0) || (i === 4 && bExported === bItems.length && bItems.length > 0); const now = i === nowIdx; return { n: o[0], sub: o[1], now: now, busy: i === 2 && B && B.stage === 'recording' && !B.paused && !now, cls: 'stepbtn' + (now ? ' now' : '') + (!done && !now && i > Math.max(bStageIdx, nowIdx) && !(i === 4 && bApproved > 0) ? ' locked' : ''), dotCls: 'stepdot' + (done ? ' done' : ''), mark: done ? '✓' : String(i + 1) }; });
    const recIdx = bItems.findIndex((x) => x.st === 'recording');
    // The list shows a fixed window of 7 rows that always holds the recording row and the one after it, so the page never grows as videos finish and Watch next stays clear of the chat bar.
    const bCollapse = bItems.length > 10 && !st.btAll; const bAnchor = recIdx >= 0 ? recIdx : bItems.findIndex((x) => x.st === 'recorded'); const bStart = !bCollapse ? 0 : Math.max(0, Math.min(bItems.length - 6, bAnchor - 5)); const bEnd = bCollapse ? bStart + (bStart > 0 ? 6 : 7) : bItems.length;
    // When the window starts later in the list, its first slot sums up the rows above it ("✓ 2 approved"), so the list never seems to start at #3.
    const bAbove = bItems.slice(0, bStart); const bAboveText = ['approved', 'exported', 'recorded'].map((k) => { const n = bAbove.filter((x) => x.st === k).length; return n ? n + ' ' + { approved: 'approved', exported: 'exported', recorded: 'ready to watch' }[k] : ''; }).filter(Boolean).join(' · '); const hLeft = Math.max(1, Math.round(bLeftMin / 60));
    const bHead = !B ? '' : B.stage === 'writing' ? 'Claude is writing ' + this.plural(bItems.length, 'script') + '.' : B.stage === 'approve' ? this.plural(cnt('script'), 'script') + ' ready to approve.' : B.stage === 'done' ? 'All ' + bItems.length + ' exported.' : (bReady ? bReady + ' ready to watch.' : 'None ready to watch yet.');
    const bSub = !B ? '' : B.stage === 'writing' ? 'Takes about a minute per script. Nothing records until you approve them.' : B.stage === 'approve' ? 'Open any script to read or change it, or approve them all.' : B.paused === 'credits' ? 'Paused: the next video needs about ' + this.num(this.perVideo((bToRecord[0] || { min: 3 }).min)) + ' credits. Top up at ElevenLabs, then resume.' : B.paused ? 'Paused at #' + (recIdx + 1) + '.' : B.stage === 'recording' ? 'Recording #' + (recIdx + 1) + ' now, about ' + hLeft + ' h left. You can leave it running overnight.' : B.stage === 'done' ? '' : 'Approved videos can be exported any time.';
    const bCreditNote = B && B.stage === 'recording' && !B.paused && bFits < bToRecord.length ? 'You have ' + this.num(st.credits) + ': enough for about ' + bFits + ' more. Recording pauses there until you top up.' : '';
    const watchItem = (i) => { const r = this.batchDemos(B, i); this.setState({ demos: r.demos, screen: 'demo', cur: r.id, step: 4, markOpen: false, confirm: null, fromBatch: B.id, batchItem: i, revT: 0, player: false, vals: this.recFor(B.voice, B.kind) }); };
    const approveItem = (i) => { const prev = B.items; const items = B.items.map((x, k) => k === i ? Object.assign({}, x, { st: 'approved' }) : x); this.patchBatch({ items: items }); this.say('Approved “' + B.items[i].t + '”', () => this.patchBatch({ items: prev })); };
    let bPrimary = !B ? { label: '', act: () => {}, off: true } : B.stage === 'writing' ? { label: 'Approve all scripts', off: true, act: () => {} } : B.stage === 'approve' ? { label: 'Approve all and record', off: false, act: () => { if (this.needKey()) return; this.setState({ bConfirm: true }); this.focusLater('#bcfyes'); }, start: () => { if (this.needKey()) return; const items = B.items.map((x, k) => Object.assign({}, x, { st: k === 0 ? 'recording' : 'waiting' })); this.setState({ bConfirm: false }); this.patchBatch({ items: items, stage: 'recording', paused: false }); this.runBatch(); this.focusLater('#batch-h'); this.say('Recording ' + this.plural(items.length, 'video') + ', one after another'); } } : { label: bApproved ? 'Export ' + this.plural(bApproved, 'approved video') : 'Export approved videos', off: !bApproved, act: () => { const n = bApproved; const items = B.items.map((x) => x.st === 'approved' ? Object.assign({}, x, { st: 'exported' }) : x); const done = items.every((x) => x.st === 'exported'); this.patchBatch({ items: items, stage: done ? 'done' : B.stage }); this.focusLater('.bprimary'); this.say('Exported ' + this.plural(n, 'video') + ' and the list file to ' + B.folder.replace(/^~\/Movies\//, 'Movies/')); } };
    const bAllCost = bItems.reduce((s, x) => s + this.perVideo(x.min), 0); const bAllFits = (() => { let c = st.credits, n = 0; for (const x of bItems) { const k = this.perVideo(x.min); if (c < k) break; c -= k; n++; } return n; })();
    const bConfirmText = 'Recording ' + this.plural(bItems.length, 'video') + ' uses about ' + this.num(bAllCost) + ' credits' + (bAllFits < bItems.length ? '. It pauses after ' + bAllFits + ' until you top up.' : '');
    const bStartAll = bPrimary.start || (() => {});
    const exportAct = bPrimary.act; const exportLabel = bPrimary.label; const exportOff = bPrimary.off;
    const firstReady = bItems.findIndex((x) => x.st === 'recorded');
    let bSecondary = null;
    if (B && (B.stage === 'recording' || B.stage === 'review')) { bSecondary = { label: exportLabel, act: exportAct, off: exportOff }; bPrimary = { label: 'Watch next', off: firstReady < 0, act: () => { if (firstReady >= 0) watchItem(firstReady); } }; }
    const bPauseObj = B && B.stage === 'recording' ? (B.paused ? { label: 'Resume recording', act: () => { this.patchBatch({ paused: false }); this.runBatch(); } } : { label: 'Pause recording', act: () => { this.patchBatch({ paused: true }); this.say('Paused. The video being recorded finishes first.'); } }) : null;
    return {
      themeClass: theme === 'dark' ? 't-dark' : 't-light', isDark: theme === 'dark', isLight: theme !== 'dark', themeAria: theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode', toggleTheme: () => this.setState({ theme: theme === 'dark' ? 'light' : 'dark' }),
      isWelcome: st.screen === 'welcome', inApp: st.screen !== 'welcome', isHome: st.screen === 'home', isDemo: st.screen === 'demo', isSettings: st.screen === 'settings', isNew: st.screen === 'new', isBatch: st.screen === 'batch',
      crumb: st.screen !== 'home', crumbBatch: st.screen === 'demo' && !!st.fromBatch, crumbBatchName: st.fromBatch ? (st.batches.find((x) => x.id === st.fromBatch) || {}).name : '', goBatch: () => this.setState({ screen: 'batch', fromBatch: null, batchItem: null }), crumbText: st.screen === 'demo' ? (st.fromBatch && B ? (B.items[st.batchItem] || {}).t : D.title) : st.screen === 'batch' ? (B ? B.name : '') : st.screen === 'new' ? (st.editing ? 'Edit brief' : 'New demo') : 'Settings',
      showNewBtn: false, isPhone: isPhone,
      goHome: () => this.setState({ screen: 'home', help: false, confirm: null }), goSettings: () => this.setState({ screen: 'settings', help: false }),
      helpOpen: st.help, toggleHelp: () => { const was = st.help; this.setState({ help: !was }); this.focusLater(was ? '#helpbtn' : '#helpok'); },
      keyOn: st.keyOn, keyOff: !st.keyOn, creditsText: this.num(st.credits),  creditPct: (st.credits / 30000 * 100) + '%',
      demos: st.demos.filter((d) => !d.batchOf).map((d) => ({ tint: d.tint || '', title: d.title, meta: d.site + ', ' + pretty(d.voice), status: d.status, dot: d.dot, cover: d.cover, open: () => { const s = d.exported ? 5 : Math.min(d.max, d.recorded ? 4 : d.max); this.setState({ screen: 'demo', cur: d.id, step: s, confirm: null, markOpen: false, scSel: 0, vals: this.recFor(d.voice, d.kind) }); } })),
      batchCards: st.batches.map((b) => { const r = b.items.filter((x) => ['recorded', 'approved', 'exported'].indexOf(x.st) >= 0).length; const rd = b.items.filter((x) => x.st === 'recorded').length; return { next: b.stage === 'approve' ? 'Approve the scripts →' : rd ? rd + ' ready to watch →' : 'See progress →', name: b.name, meta: 'Batch · ' + b.items.length + ' videos · ' + b.site, status: b.stage === 'writing' ? 'Writing scripts' : b.stage === 'approve' ? 'Scripts to approve' : b.paused ? 'Paused, ' + r + ' of ' + b.items.length : b.stage === 'done' ? 'All exported' : r + ' of ' + b.items.length + ' recorded', pct: (r / b.items.length * 100) + '%', open: () => this.openBatch(b.id) }; }),
      defNamePretty: pretty(st.defVoice), defImg: VO[st.defVoice].img, defC: VO[st.defVoice].c, defName: VO[st.defVoice].name,
      keyDot: st.keyOn ? 'done' : 'bad', keyStatus: st.keyOn ? 'ElevenLabs connected' : 'ElevenLabs not connected', keyAction: st.keyOn ? 'Change' : 'Connect',
      toolsDot: st.tools === 'done' ? 'done' : 'bad', toolsStatus: st.tools === 'done' ? 'Recording tools ready' : 'Recording tools not installed', toolsReady: st.tools === 'done' ? 'Ready' : 'Not installed',
      sitesStatus: st.sites.length ? this.plural(st.sites.length, 'saved login') : 'No saved logins',
      demoTitle: D.title, briefLine: D.site + ', about ' + (D.written ? Math.max(1, Math.round(this.total / 60)) : ['1', '3', '5', '8'][D.len]) + ' min', demoCover: D.cover,
      // ---- new demo ----
      newDemo: () => { requestAnimationFrame(() => { const el = document.getElementById('bw'); if (el) el.focus(); }); this.setState({ screen: 'new', mode: 'one', bKind: 'course', bMore: false, editing: false, bCap: st.defCap, bCorner: st.defCorner, bCornerText: st.defCornerText, bWhat: '', bNew: '', bSiteNew: false, bHide: '', bSite: st.sites[0] ? st.sites[0].u : '', bVoice: st.defVoice, bWho: 0, bLen: 2, help: false, btSite: st.sites[0] ? st.sites[0].u : '', btVoice: st.defVoice }); },
      editBrief: () => this.setState({ screen: 'new', mode: 'one', bMore: false, editing: true, bWhat: D.what || 'How to build a course in Whop, from creating the whop to checking it on a phone', bSite: D.site, bSiteNew: false, bNew: '', bWho: D.who, bLen: D.len, bVoice: D.voice, bCap: dCap, bCorner: dCorner, bCornerText: dCornerText }),
      newTitle: st.editing ? 'Edit the brief' : 'New demo', briefCta: st.editing ? 'Update the script' : 'Write the script',
      briefHint: st.editing ? 'Claude only rewrites what changed.' : 'Claude writes the script. Takes about a minute.',
      showModeSwitch: !st.editing, modeOne: st.mode === 'one', modeBatch: st.mode === 'batch',
      modes: segOf([['one', 'One demo'], ['batch', 'A batch']], st.mode, (x) => this.setState({ mode: x })),
      bWhat: st.bWhat, onBWhat: (e) => this.setState({ bWhat: e.target.value }), bHide: st.bHide, onBHide: (e) => this.setState({ bHide: e.target.value }), bNew: st.bNew, onBNew: (e) => this.setState({ bNew: e.target.value }),
      briefEmpty: !st.bWhat.trim() || (st.bSiteNew && !/^[a-z0-9-]+(\.[a-z0-9-]+)+(\/.*)?$/i.test(st.bNew.trim().replace(/^https?:\/\//i, ''))),
      briefWhy: !st.bWhat.trim() ? 'Type what the demo should show to continue.' : (st.bSiteNew && !/^[a-z0-9-]+(\.[a-z0-9-]+)+(\/.*)?$/i.test(st.bNew.trim().replace(/^https?:\/\//i, '')) ? 'Type the new site’s address first.' : ''),
      bSites: st.sites.map((s) => ({ label: s.u, on: !st.bSiteNew && st.bSite === s.u ? 'true' : 'false', pick: () => this.setState({ bSite: s.u, bSiteNew: false }) })),
      openBNew: () => { this.setState({ bSiteNew: true }); requestAnimationFrame(() => { const el = document.getElementById('bns'); if (el) el.focus(); }); }, closeBNew: () => this.setState({ bSiteNew: false, bNew: '' }),
      bSiteNew: st.bSiteNew, bNewBad: st.bSiteNew && !!st.bNew.trim() && !/^[a-z0-9-]+(\.[a-z0-9-]+)+(\/.*)?$/i.test(st.bNew.trim().replace(/^https?:\/\//i, '')), 
      bSummary: summaryParts.join(' · '), bSummaryShort: summaryParts.join(' · '), bMore: st.bMore, bLess: !st.bMore, toggleMore: () => this.setState({ bMore: !st.bMore }),
      bKinds: segOf([['course', 'Course walkthrough'], ['saas', 'Quick demo'], ['tour', 'Product tour']], st.bKind, (x) => this.setState({ bKind: x })).map((o, i) => Object.assign(o, { short: ['Course', 'SaaS', 'Tour'][i] })), bKindHint: { course: 'Step by step, at a teaching pace.', saas: 'Short and lively, for a product page.', tour: 'A calm look around the main screens.' }[st.bKind],
      bWho: ['Beginners', 'Some experience', 'Pros'].map((s, i) => ({ label: s, on: st.bWho === i ? 'true' : 'false', pick: () => this.setState({ bWho: i }) })),
      bLen: ['1 min', '3 min', '5 min', '8 min'].map((s, i) => ({ label: s, star: i === suggestLen, on: st.bLen === i ? 'true' : 'false', pick: () => this.setState({ bLen: i }) })),
      bVoices: st.mine.map((k) => ({ label: pretty(k), on: st.bVoice === k ? 'true' : 'false', pick: () => this.setState({ bVoice: k }) })),
      bCaps: segOf(capOpts, st.bCap, (x) => this.setState({ bCap: x })).map((o, i) => Object.assign(o, { short: ['In video', 'File', 'Off'][i] })),
      bCorner: cornerCtl(st.bCorner, (x) => this.setState({ bCorner: x }), 'bct'),
      bCornerText: st.bCornerText, onBCornerText: (e) => this.setState({ bCornerText: e.target.value }), bCornerOff: st.bCorner === 'off',
      bCornerPh: 'Text for the corner, e.g. your brand name',
      lenHint: suggestLen < 0 ? lenOpts[st.bLen] + ' min for now. Claude suggests a length once you say what to show.' : '★ Suggested for what you typed. Your pick wins.',
      cancelBrief: () => this.setState({ screen: st.editing ? 'demo' : 'home' }),
      submitBrief: () => {
        const w = st.bWhat.trim(); if (!w) return; const site = bSiteVal || 'whop.com'; if (!site) return; const t = w.length > 34 ? w.slice(0, 32).replace(/\s+\S*$/, '') + '…' : w;
        const newSite = !st.sites.some((s) => s.u === site);
        if (st.editing) { this.patchDemo({ title: t, what: w, site: site, who: st.bWho, len: st.bLen, voice: st.bVoice, capMode: st.bCap, corner: st.bCorner, cornerText: st.bCornerText, written: false }); this.setState({ screen: 'demo', step: 0, sites: newSite ? st.sites.concat([{ u: site, note: 'Saved Nov 5' }]) : st.sites }); this.later('write', 2200, () => { this.patchDemo({ written: true }); this.say('Script updated'); }); this.say('Updating the script'); return; }
        const id = 'd' + Date.now();
        const d = { id: id, title: t, what: w, site: site, len: st.bLen, who: st.bWho, voice: st.bVoice, model: 'v4', kind: st.bKind, max: 0, cover: 'assets/cover-4.jpg', status: 'Writing script', dot: 'busy', recorded: false, written: false, notes: {}, blurs: [], lines: {}, capMode: st.bCap, corner: st.bCorner, cornerText: st.bCornerText };
        this.setState({ demos: [d].concat(st.demos), cur: id, screen: 'demo', step: 0, scSel: 0, vals: this.recFor(st.bVoice, st.bKind), sites: newSite ? st.sites.concat([{ u: site, note: 'Saved Nov 5' }]) : st.sites, recPos: 0, recStopped: false });
        this.say(newSite ? 'A browser opens so you can log in to ' + site + '. Then Claude writes the script.' : 'Claude is exploring ' + site + ' and writing the script');
        this.later('write', 2600, () => { this.setState({ demos: this.state.demos.map((x) => x.id === id ? Object.assign({}, x, { written: true, status: 'Script ready', dot: 'ready' }) : x) }); this.say('Script ready to read'); });
      },
      // ---- new batch ----
      btText: st.btText, onBtText: (e) => this.setState({ btText: e.target.value }), btName: st.btName, onBtName: (e) => this.setState({ btName: e.target.value }), btNamePh: st.btFile ? btName : 'e.g. Whop course, module 3',
      btFolder: st.btFolder, onBtFolder: (e) => this.setState({ btFolder: e.target.value }), btFolderPh: btFolder, btFolderVal: st.btFolder || btFolder, btFolderShort: (() => { const f = st.btFolder || btFolder; const parts = f.split('/'); return f.length > 26 && parts.length > 3 ? '…/' + parts.slice(isPhone ? -1 : -2).join('/') : f; })(), chooseFolder: () => this.say('A folder picker opens on your Mac'),
      btRows: 7, btPresetHint: { strict: 'Standard, plus usage, prices, dates.', standard: 'Blurs personal info, money and counts.', test: 'Fake data: names show, money blurred.' }[st.btPreset], btFootText: 'Scripts are free. You approve every script before anything records.', btMore: btCount > 7, btKindHint: { course: 'Step by step, at a teaching pace.', saas: 'Short and lively, for a product page.', tour: 'A calm look around the main screens.' }[st.btKind],
      btFileName: st.btFile, btHasFile: !!st.btFile,
      pickFile: () => { const el = document.getElementById('btfile'); if (el) el.click(); },
      onFile: (e) => { const f = e.target.files && e.target.files[0]; if (!f) return; const r = new FileReader(); r.onload = () => { this.setState({ btText: String(r.result || ''), btFile: f.name }); this.say('Read ' + f.name); }; r.readAsText(f); e.target.value = ''; },
      btSites: st.sites.map((s) => ({ label: s.u, on: !st.btSiteNew && st.btSite === s.u ? 'true' : 'false', pick: () => this.setState({ btSite: s.u, btSiteNew: false }) })),
      btSiteNew: st.btSiteNew, btNew: st.btNew, onBtNew: (e) => this.setState({ btNew: e.target.value }), btNewBad: st.btSiteNew && !!st.btNew.trim() && !siteOk(st.btNew), openBtNew: () => { this.setState({ btSiteNew: true }); requestAnimationFrame(() => { const el = document.getElementById('btns'); if (el) el.focus(); }); }, closeBtNew: () => this.setState({ btSiteNew: false, btNew: '' }),
      btVoices: st.mine.map((k) => ({ label: pretty(k), on: st.btVoice === k ? 'true' : 'false', pick: () => this.setState({ btVoice: k }) })),
      btKinds: segOf([['course', 'Course walkthrough'], ['saas', 'Quick demo'], ['tour', 'Product tour']], st.btKind, (x) => this.setState({ btKind: x })).map((o, i) => Object.assign(o, { short: ['Course', 'SaaS', 'Tour'][i] })),
      btPresets: segOf([['strict', 'Strict'], ['standard', 'Standard'], ['test', 'Test account']], st.btPreset, (x) => this.setState({ btPreset: x })).map((o, i) => Object.assign(o, { short: ['Strict', 'Standard', 'Test'][i] })),
      btCount: btCount, btEmpty: !btCount || (st.btSiteNew && !siteOk(st.btNew)), btCountText: btCount ? this.plural(btCount, 'video') : 'No videos yet', btMinText: 'about ' + btMin + ' min', btCostText: 'about ' + this.num(btCost) + ' credits', btLine2: btShort && btCount > 0 ? 'You have ' + this.num(st.credits) + ': enough for about ' + btFits + '. Recording pauses there until you top up.' : 'You have ' + this.num(st.credits) + '. Claude picks a length for each video.', btLeftText: 'you have ' + this.num(st.credits) + '.', btLinesText: btCount ? this.plural(btCount, 'line') + ' → ' + this.plural(btCount, 'video') + (btCount > 7 ? ' · scroll for ' + (btCount - 7) + ' more' : '') : 'Nothing yet',
      btShort: btShort && btCount > 0, btShortText: 'Enough for about ' + btFits + '. Recording pauses there until you top up. Nothing fails.',
      btCta: btCount ? 'Write ' + this.plural(btCount, 'script') : 'Write the scripts',
      submitBatch: () => {
        if (!btCount || (st.btSiteNew && !siteOk(st.btNew))) return; const id = 'b' + Date.now();
        const b = { id: id, name: btName, site: st.btSiteNew ? st.btNew.trim() : st.btSite, voice: st.btVoice, kind: st.btKind, preset: st.btPreset, folder: btFolder, stage: 'writing', paused: false, items: btLines.map((t, i) => ({ t: t, lesson: 'Lesson ' + (i + 1), min: 3, st: 'writing' })) };
        this.setState({ batches: [b].concat(st.batches), curBatch: id, screen: 'batch', btText: '', btName: '', btFile: '', btFolder: '' });
        this.later('bwrite', 2600, () => { this.patchBatch((x) => ({ stage: 'approve', items: x.items.map((it) => Object.assign({}, it, { st: 'script' })) }), id); this.say('All scripts are ready to approve'); });
      },
      // ---- batch screen ----
      bName: B ? B.name : '', bMeta1: B ? B.site + ' · ' + pretty(B.voice) : '', bMeta2: B ? { course: 'Walkthrough', saas: 'SaaS demo', tour: 'Product tour' }[B.kind] + ' · ' + presetName[B.preset] + ' privacy' : '', bMeta: B ? [B.site, pretty(B.voice), { course: 'Course walkthrough', saas: 'Quick demo', tour: 'Product tour' }[B.kind], presetName[B.preset] + ' privacy'].join(', ') : '', bFolder: B ? B.folder : '',
      bStages: bStages, bRecLabel: B && (B.stage === 'recording' || B.stage === 'review') ? bRecorded + ' of ' + bItems.length + ' recorded' : '', bCreditSlot: !!(B && B.stage === 'recording'), bHead: bHead, bSub: bSub, bPct: (bItems.length ? (B.stage === 'approve' || B.stage === 'writing' ? 0 : bRecorded / bItems.length * 100) : 0) + '%', bCreditNote: bCreditNote, hasBCreditNote: !!bCreditNote, bPausedCredits: !!(B && B.paused === 'credits'),
      bItems: bItems.map((x, i) => ({ i: i, n: i + 1, t: x.t, min: x.min + ' min', st: x.st, status: stLabel[x.st], dot: stDot[x.st], ring: x.st === 'waiting', open: st.btOpen === i, openStr: st.btOpen === i ? 'true' : 'false', canOpen: x.st === 'script', canWatch: x.st === 'recorded' || x.st === 'approved', preview: 'Okay so… in this one we’re gonna ' + x.t.toLowerCase() + '. It’s, um, quicker than it looks.',
        noAct: !(x.st === 'script' || x.st === 'recorded' || x.st === 'approved'),
        toggle: () => this.setState({ btOpen: st.btOpen === i ? null : i }), watch: () => watchItem(i) })).slice(bStart, bEnd),
      bAbove: bStart > 0, bAboveNums: bStart > 1 ? '1–' + bStart : '1', bAboveText: bAboveText, bAboveDone: bAbove.every((x) => x.st === 'approved' || x.st === 'exported'), bWaiting: cnt('waiting'), bAllOpenRaw: st.btAll, bWaitingCollapsed: !st.btAll && cnt('waiting') > 1, bShowAll: () => this.setState({ btAll: !st.btAll }), bShowAllLabel: st.btAll ? 'Show less' : 'Show all ' + bItems.length, bAllOpen: st.btAll && bItems.length > 10, bShowToggle: bItems.length > 10,
      bReady: bReady, hasBReady: bReady > 0, bReadyText: this.plural(bReady, 'video') + ' ready to watch', bWatchFirst: () => { const k = bItems.findIndex((x) => x.st === 'recorded'); if (k >= 0) watchItem(k); },
      bFooter: B ? (B.stage === 'done' ? 'Everything is in ' + B.folder + ', with list.csv (title, file name, lesson). Nothing is published.' : B.stage === 'approve' || B.stage === 'writing' ? 'Nothing records until you approve the scripts.' : (firstReady >= 0 ? 'Next: ' + bItems[firstReady].t + '. Nothing is published automatically.' : 'Exports go to Movies/NAVI with a list file. Nothing is published automatically.')) : '',
      bPrimaryShort: /^Watch next/.test(bPrimary.label) ? 'Watch next' : (/^Export (\d+)/.test(bPrimary.label) ? 'Export ' + bPrimary.label.match(/\d+/)[0] : bPrimary.label), bSecondaryShort: bSecondary ? (/^Export (\d+)/.test(bSecondary.label) ? 'Export ' + bSecondary.label.match(/\d+/)[0] + ' approved' : 'Export') : '', bPrimaryLabel: bPrimary.label, bPrimaryOff: bPrimary.off, bPrimary: bPrimary.act, hasBSecondary: !!bSecondary, bSecondaryLabel: bSecondary ? bSecondary.label : '', bSecondary: bSecondary ? bSecondary.act : () => {}, bSecondaryOff: bSecondary ? !!bSecondary.off : false, hasBPause: !!bPauseObj, bPauseLabel: bPauseObj ? bPauseObj.label : '', bPause: bPauseObj ? bPauseObj.act : () => {}, bReviewing: !!(B && (B.stage === 'recording' || B.stage === 'review')),
      bConfirm: !!(st.bConfirm && B && B.stage === 'approve'), bNotConfirm: !(st.bConfirm && B && B.stage === 'approve'), bConfirmText: bConfirmText, bConfirmYes: () => bStartAll(), bConfirmNo: () => { this.setState({ bConfirm: false }); this.focusLater('.bprimary'); },
      // ---- demo steps ----
      steps: steps, cur: cur, st0: st.step === 0, st1: st.step === 1, st2: st.step === 2, st3: st.step === 3, st4: st.step === 4, st5: st.step === 5,
      writing: !D.written, scriptReady: !!D.written, skelRows: this.secs.map((x, i) => ['62%', '80%', '70%', '86%', '58%', '74%', '66%'][i % 7]),
      canBack: st.step > 0 && st.step < 5 && !(st.step === 3 && !D.recorded && !st.recStopped), recHold: st.step === 3 && !D.recorded && !st.recStopped, back: () => this.setState({ step: st.step - 1, confirm: null, markOpen: false }), hasSecondary: !!cur.second, secondary: secondaryFor[st.step] || (() => {}), primary: primaryFor[st.step],
      primaryBlocked: (st.step === 0 && !D.written) || (st.step === 3 && !D.recorded) || (st.step === 1 && !voiceOk),
      confirming: !!cf, notConfirming: !cf, confirmNo: cf ? cf.no : '', confirmYes: cf ? cf.yes : '', cancelConfirm: () => { this.setState({ confirm: null }); this.focusLater('.stepfoot .pri'); }, doConfirm: () => { if (cf) cf.act(); },
      footText: foot.text, footDot: foot.dot, footColor: foot.color,
      footLinkOn: !cf && footBad, footLinkLabel: 'switch back to ' + vInfo.models[0], footLinkAct: () => { this.patchDemo({ model: vInfo.models[0] }); this.say('Switched to Eleven ' + vInfo.models[0] + ' for ' + voicePretty); this.focusLater('.stepfoot .pri'); },
      // script
      scPickSel: (e) => this.setState({ scSel: Number(e.target.value), scChange: false, scDraft: '' }),
      scList: this.secs.map((s, i) => ({ i: i, t: this.fmt(this.starts[i]), n: s.n, on: st.scSel === i ? 'true' : 'false', edited: !!(D.lines && D.lines[i]), pick: () => this.setState({ scSel: i, scChange: false, scDraft: '' }) })),
      scNum: (st.scSel + 1) + ' of ' + this.secs.length, scTime: this.fmt(this.starts[st.scSel]) + '–' + this.fmt(this.starts[st.scSel] + this.secs[st.scSel].d), scName: this.secs[st.scSel].n, scLine: lineOf(st.scSel), scCaption: this.secs[st.scSel].c,
      scCaps: st.scCaps, scCapsLabel: st.scCaps ? 'Hide captions' : 'Show captions', toggleScCaps: () => this.setState({ scCaps: !st.scCaps }),
      scChange: st.scChange, scDraft: st.scDraft, onScDraft: (e) => this.setState({ scDraft: e.target.value }), openScChange: () => { this.setState({ scChange: !st.scChange, scDraft: '' }); this.later('focusSc', 30, () => { const el = document.getElementById('scd'); if (el) el.focus(); }); },
      scPending: st.scPending === st.scSel, scPendingText: 'Rewriting this line…',
      sendScChange: () => { const d = st.scDraft.trim(); if (!d) return; const i = st.scSel; const prevLines = D.lines || {}; this.setState({ scChange: false, scDraft: '', scPending: i }); requestAnimationFrame(() => { const b = document.getElementById('scopen'); if (b) b.focus(); }); this.later('scw', 1600, () => { const nl = Object.assign({}, prevLines); nl[i] = this.secs[i].v.replace(/\b(um|uh|kind of|basically|to be fair|well|like),?\s*/gi, '').replace(/\s+/g, ' ').replace(/^(\w)/, (m) => m.toUpperCase()); this.setState({ scPending: null }); this.patchDemo({ lines: nl }); this.say('Line rewritten', () => this.patchDemo({ lines: prevLines })); }); },
      scKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); const b = document.getElementById('scsend'); if (b) b.click(); } else if (e.key === 'Escape') { e.stopPropagation(); this.setState({ scChange: false }); requestAnimationFrame(() => { const b = document.getElementById('scopen'); if (b) b.focus(); }); } },
      scPrevOff: st.scSel === 0, scNextOff: st.scSel === this.secs.length - 1,
      scPrev: () => { if (st.scSel > 0) { this.setState({ scSel: st.scSel - 1, scChange: false }); if (st.scSel === 0) this.focusLater(() => [...document.querySelectorAll('[aria-label="Next section"]')].find((e) => e.offsetParent)); } }, scNext: () => { if (st.scSel < this.secs.length - 1) { this.setState({ scSel: st.scSel + 1, scChange: false }); if (st.scSel === this.secs.length - 1) this.focusLater(() => [...document.querySelectorAll('[aria-label="Previous section"]')].find((e) => e.offsetParent)); } },
      scListKey: (e) => { const n = this.secs.length; const k = e.key; let i = st.scSel; if (k === 'ArrowDown' || k === 'ArrowRight') i = Math.min(n - 1, i + 1); else if (k === 'ArrowUp' || k === 'ArrowLeft') i = Math.max(0, i - 1); else if (k === 'Home') i = 0; else if (k === 'End') i = n - 1; else return; e.preventDefault(); this.setState({ scSel: i, scChange: false, scDraft: '' }); this.focusLater('.sclist button[aria-pressed=true]'); },
      scriptLenLine: this.secs.length + ' sections, about ' + lengthText + (model === 'v3' ? ' at ' + paceText + ' pace' : ''),
      // voice
      voiceName: voicePretty, voiceColor: vcol(voice), line: line, caption: caption,
      voices: st.mine.map((k) => { const ok = VO[k].models.indexOf(model) >= 0; const mName = (m) => m === 'v4' ? 'v4' : 'v3'; return { name: VO[k].name, desc: VO[k].desc, img: VO[k].img, bg: VO[k].c, on: voice === k ? 'true' : 'false', cls: 'vcard' + (voice === k ? ' on' : ''), aria: 'Pick ' + VO[k].name, hearAria: 'Hear ' + VO[k].name + (st.heardVoices[k] ? ', free replay' : ', about ' + SAMPLE_COST + ' credits'), badge: st.heardVoices[k] ? 'Replay' : 'Hear', modelTag: VO[k].models.length === 2 ? 'Both models' : mName(VO[k].models[0]) + ' only',
        pick: () => { if (voice === k) return; const prevVoice = D.voice; const prevModel = model; const prevVals = st.vals; const switchModel = VO[k].models.indexOf(model) < 0; this.patchDemo({ voice: k, model: switchModel ? VO[k].models[0] : model }); this.setState({ vals: this.recFor(k, D.kind) }); this.say(switchModel ? 'Switched to Eleven ' + VO[k].models[0] + ' for ' + pretty(k) : 'Picked ' + pretty(k), () => { this.patchDemo({ voice: prevVoice, model: prevModel }); this.setState({ vals: prevVals }); }); },
        hear: () => { if (this.needKey()) return; const first = !st.heardVoices[k]; const h = Object.assign({}, st.heardVoices); h[k] = true; this.setState({ heardVoices: h }); if (first) this.spend(SAMPLE_COST); this.say('Playing ' + pretty(k) + (first ? ', ' + SAMPLE_COST + ' credits' : ', free replay')); } }; }),
      models: segOf([['v4', 'Eleven v4 (recommended)'], ['v3', 'Eleven v3']], model, (x) => this.patchDemo({ model: x })).map((o, i) => Object.assign(o, { short: ['v4 (recommended)', 'v3'][i] })),
      voiceWarn: !voiceOk,
      openLib: () => { this.setState({ lib: true }); this.focusLater('#libclose'); }, closeLib: () => { this.setState({ lib: false }); this.focusLater('#vmore'); }, libOpen: st.lib,
      libFilters: [['all', 'All'], ['f', 'Female'], ['m', 'Male']].map((o) => ({ label: o[1], on: st.libF === o[0] ? 'true' : 'false', pick: () => this.setState({ libF: o[0] }) })),
      lib: Object.keys(VO).filter((k) => st.libF === 'all' || VO[k].g === st.libF).map((k) => ({ name: VO[k].name, desc: VO[k].desc + ', ' + (VO[k].models.length === 2 ? 'both models' : VO[k].models[0] + ' only'), img: VO[k].img, c: VO[k].c, canAdd: st.mine.indexOf(k) < 0, added: st.mine.indexOf(k) >= 0, hearAria: 'Hear ' + VO[k].name,
        hear: () => { if (this.needKey()) return; const first = !st.heardVoices[k]; const h = Object.assign({}, st.heardVoices); h[k] = true; this.setState({ heardVoices: h }); if (first) this.spend(SAMPLE_COST); this.say('Playing ' + pretty(k) + (first ? ', ' + SAMPLE_COST + ' credits' : ', free replay')); },
        add: () => { this.setState({ mine: st.mine.concat([k]) }); this.say(pretty(k) + ' added to your voices', () => this.setState({ mine: this.state.mine.filter((x) => x !== k) })); } })),
      kinds: [['course', 'Course walkthrough'], ['saas', 'Quick demo'], ['tour', 'Product tour']].map((o) => ({ label: o[1], on: D.kind === o[0] ? 'true' : 'false', pick: () => { if (D.kind === o[0]) return; const prevV = st.vals; const prevK = D.kind; this.patchDemo({ kind: o[0] }); this.setState({ vals: this.recFor(voice, o[0]) }); this.say('Switched to ' + o[1].toLowerCase() + ' settings', () => { this.patchDemo({ kind: prevK }); this.setState({ vals: prevV }); }); } })),
      fineNote: changed ? changed + ' changed' : 'All recommended', sliders: sliders.filter((x) => x.k !== 'pace' && x.k !== 'swear'), paceSliders: sliders.filter((x) => x.k === 'pace'),
      swearPills: ['Off', 'One', 'A few'].map((l, i) => ({ label: l, on: v.swear === i ? 'true' : 'false', pick: () => setV('swear', i) })), swearHelp: 'Off: fine for any audience. On: at natural reactions, never in instructions.', sliderHelp: st.sliderHelp, toggleSliderHelp: () => this.setState({ sliderHelp: !st.sliderHelp }), sliderHelpLabel: st.sliderHelp ? 'Hide what these do' : 'What do these do?',
      resetAll: () => { const prev = st.vals; setVals(Object.assign({}, rec), 'Back to the recommended settings', prev); this.focusLater('#slhelp'); }, anyChanged: changed > 0,
      capsOn: a.onStr, capsCls: a.cls, toggleCaps: () => { if (v.swear > 0) this.setState({ caps: !st.caps }); },
      playSample: () => { if (st.sampling) { this.stop('sample'); this.setState({ sampling: false }); return; } if (this.needKey()) return; const free = st.lastSample === sampleKey; if (!free) this.spend(SAMPLE_COST); this.setState({ sampling: true, lastSample: sampleKey }); this.later('sample', 6000, () => this.setState({ sampling: false })); },
      samplePlaying: st.sampling, sampleStopped: !st.sampling, playAria: st.sampling ? 'Stop sample' : 'Play sample', wvClass: st.sampling ? 'wv on' : 'wv',
      wbars: [30, 55, 40, 75, 50, 90, 62, 100, 48, 70, 36, 64, 88, 52, 96, 58, 44, 80, 50, 72, 34, 60, 92, 46, 70, 40, 66, 30].map((h, i) => ({ h: h + '%', d: (i % 7) * 70 + 'ms' })),
      sampleCost: st.lastSample === sampleKey ? 'Replays are free.' : 'Hearing a voice the first time costs about ' + SAMPLE_COST + ' credits. Replays are free.', swearOn: v.swear > 0, isDefVoice: st.defVoice === voice, makeDefault: () => { const prev = st.defVoice; if (prev === voice) { if (this.prevDef && this.prevDef !== voice) { this.setState({ defVoice: this.prevDef }); this.say(pretty(this.prevDef) + ' is the default again'); } return; } this.prevDef = prev; this.setState({ defVoice: voice }); this.say(voicePretty + ' is now your default voice', () => this.setState({ defVoice: prev })); },
      videoCostText: this.num(videoCost), leftAfterText: this.num(leftAfter), creditsNowText: this.num(st.credits), thisPct: (D.recorded || !st.credits ? 0 : Math.min(1, videoCost / st.credits) * 100) + '%', restPct: (D.recorded || !st.credits ? 100 : Math.max(0, 1 - videoCost / st.credits) * 100) + '%',
      lengthText: lengthText, paceText: paceText, isV3: model === 'v3',
      lockOn: l.onStr, lockCls: l.cls, toggleLock: () => this.setState({ lock: !st.lock }),
      // privacy
      always: ['API keys and tokens', 'Passwords', '2FA and recovery codes', 'Card and bank numbers', 'ID numbers', 'Private keys', 'Login links'],
      presets: [['strict', 'Strict', 'Everything Standard blurs, plus usage, prices and dates.'], ['standard', 'Standard', 'Blur personal info, money and counts. Show usage, prices and dates.'], ['test', 'Test account', 'Fake data, so names and emails can show. Money, customers and counts stay blurred.']].map((o) => ({ id: o[0], name: o[1], desc: o[2], rec: o[0] === 'standard', on: preset === o[0] ? 'true' : 'false', cls: 'preset' + (preset === o[0] ? ' on' : ''), pick: () => { const prev = st.shown; if (preset === o[0]) return; this.setState({ shown: Object.assign({}, PRESETS[o[0]]) }); this.say(o[1] + ' privacy', () => this.setState({ shown: prev })); } })),
      isCustom: preset === 'custom', pvCount: String(Object.keys(ITEM_NAMES).length),
      pvBlurLine: (() => { const g = []; if (['email', 'phone', 'names', 'address'].every((k) => !st.shown[k])) g.push('personal info'); else ['email', 'phone', 'names', 'address'].filter((k) => !st.shown[k]).forEach((k) => g.push(ITEM_NAMES[k])); if (!st.shown.money) g.push('revenue'); if (!st.shown.customers) g.push('customers'); if (!st.shown.counts) g.push('counts'); ['usage', 'prices', 'dates'].filter((k) => !st.shown[k]).forEach((k) => g.push(ITEM_NAMES[k])); g.push('passwords and keys'); return g.join(', ') + '.'; })(),
      pvShowLine: shownItems.length ? shownItems.map((k) => ITEM_NAMES[k]).join(', ') + '.' : 'nothing that could be private.',
      pvMore: st.pvMore, togglePvMore: () => { this.setState({ pvMore: !st.pvMore }); if (!st.pvMore) requestAnimationFrame(() => { const el = document.getElementById('pvmore'); if (el && el.scrollIntoView) el.scrollIntoView({ block: 'start', behavior: 'smooth' }); }); }, pvMoreLabel: 'Customize each item',
      hide: st.hide.map((w, hi) => ({ w: w, aria: 'Remove ' + w, rm: () => { const prev = st.hide; this.setState({ hide: st.hide.filter((x) => x !== w) }); this.focusLater(() => { const xs = document.querySelectorAll('.chip button'); return xs[hi] || xs[hi - 1] || document.getElementById('hw'); }); this.say('Removed “' + w + '”', () => this.setState({ hide: prev })); } })),
      noHide: !st.hide.length, hideDup: !!st.hideDraft.trim() && st.hide.indexOf(st.hideDraft.trim()) >= 0, hideAddOff: !st.hideDraft.trim() || st.hide.indexOf(st.hideDraft.trim()) >= 0, alwaysText: 'API keys and tokens, passwords, 2FA and recovery codes, card and bank numbers, ID numbers, private keys and login links',
      hideDraft: st.hideDraft, onHideDraft: (e) => this.setState({ hideDraft: e.target.value }), addHide: () => { const w = st.hideDraft.trim(); if (w && st.hide.indexOf(w) < 0) { this.setState({ hide: st.hide.concat([w]), hideDraft: '' }); this.say('Will always blur “' + w + '”'); } },
      hideKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); const w = st.hideDraft.trim(); if (w && st.hide.indexOf(w) < 0) { this.setState({ hide: st.hide.concat([w]), hideDraft: '' }); this.say('Will always blur “' + w + '”'); } } },
      tier2: [row('email', 'Email addresses'), row('phone', 'Phone numbers'), row('names', 'Real names and profile photos'), row('address', 'Addresses'), row('money', 'Revenue and money figures'), row('customers', 'Customer details'), row('counts', 'Follower and member counts')],
      tier3: [row('usage', 'Usage stats, like token usage'), row('prices', 'Prices on public pages'), row('dates', 'Dates')],
      // record
      recBadge: D.recorded ? 'Recorded' : st.recStopped ? 'Stopped' : st.recPaused ? 'Paused' : 'Recording live', recCover: D.cover, recBadgeDot: D.recorded ? 'done' : st.recPaused || st.recStopped ? 'wait' : 'rec',
      isRecording: !D.recorded, recDone: !!D.recorded,
      recHeadWords: D.recorded ? 'All sections recorded' : st.recStopped ? 'Stopped after' : 'Section', recHeadNum: D.recorded ? '' : (st.recStopped ? st.recPos : Math.min(N, st.recPos + 1)) + ' of ' + N, recLeft: D.recorded ? lengthText : String(Math.max(1, Math.ceil((N - st.recPos) * 0.4))), recLeftWords: D.recorded ? '' : 'min left',
      recPct: (D.recorded ? 100 : st.recPos / N * 100) + '%',
      recNowName: this.secs[Math.min(N - 1, st.recPos)].n, recNowLine: lineOf(Math.min(N - 1, st.recPos)),
      recNext: [st.recPos + 1, st.recPos + 2].map((k) => ({ n: k < N ? this.secs[k].n : '' })), recMoreN: Math.max(0, N - st.recPos - 3),
      recHeadLine: D.recorded ? 'All ' + N + ' sections recorded · ' + lengthText : st.recStopped ? 'Stopped after ' + st.recPos + ' of ' + N + ' sections' : 'Section ' + Math.min(N, st.recPos + 1) + ' of ' + N + ' · about ' + Math.max(1, Math.ceil((N - st.recPos) * 0.4)) + ' min left',
      hasLastDone: st.recPos > 0 || st.recStopped, recLastDone: st.recStopped ? (isPhone ? 'Stopped at ' + Math.min(N, st.recPos + 1) + ' of ' + N + '. ' + (st.recPos ? this.plural(st.recPos, 'section') + ' kept.' : 'Nothing kept yet.') : 'Stopped at section ' + Math.min(N, st.recPos + 1) + '. ' + (st.recPos ? this.plural(st.recPos, 'finished section') + (st.recPos === 1 ? ' is' : ' are') + ' kept.' : 'Nothing finished yet.')) : this.plural(Math.min(N, st.recPos), 'section') + ' done', recDoneMark: st.recStopped && !st.recPos ? 'ring' : 'tick', recNowMark: st.recPaused || st.recStopped ? 'ring' : 'spin',
      recPaused: st.recPaused, recStopped: st.recStopped, recControls: !D.recorded && !st.recStopped,
      recSlidePct: String(st.recSlide || 0), recSlideNow: String(Math.round((st.recSlide || 0) * 100)), recSliding: !!st.recSliding,
      slideDown: (e) => { const el = e.currentTarget; const tr = el.parentElement.getBoundingClientRect(); this.slideDrag = { x0: e.clientX - (st.recSlide || 0) * (tr.width - 48), travel: tr.width - 48 }; try { el.setPointerCapture(e.pointerId); } catch (x) {} this.setState({ recSliding: true }); },
      slideMove: (e) => { const d = this.slideDrag; if (!d) return; const v = Math.max(0, Math.min(1, (e.clientX - d.x0) / d.travel)); this.setState({ recSlide: v }); },
      slideUp: () => { if (!this.slideDrag) return; this.slideDrag = null; if ((this.state.recSlide || 0) >= 0.85) { this.setState({ recSliding: false, recSlide: 1 }); stopNow(); } else this.setState({ recSliding: false, recSlide: 0 }); },
      slideKey: (e) => { const k = e.key; const v = this.state.recSlide || 0; if (k === 'Enter' || k === 'End') { e.preventDefault(); this.setState({ recSlide: 1 }); stopNow(); } else if (k === 'ArrowRight' || k === 'ArrowUp') { e.preventDefault(); const n = Math.min(1, v + 0.25); this.setState({ recSlide: n }); if (n >= 1) stopNow(); } else if (k === 'ArrowLeft' || k === 'ArrowDown') { e.preventDefault(); this.setState({ recSlide: Math.max(0, v - 0.25) }); } else if (k === 'Escape' || k === 'Home') { e.preventDefault(); e.stopPropagation(); this.setState({ recSlide: 0 }); } },
      pauseLabel: st.recPaused ? 'Resume' : 'Pause',
      pauseRec: () => { if (st.recPaused) { this.setState({ recPaused: false }); this.startRecording(st.recPos); this.setState({ recPos: st.recPos }); } else { this.stop('rec'); this.setState({ recPaused: true }); this.patchDemo({ status: 'Paused at ' + (st.recPos + 1) + ' of ' + N, dot: 'wait' }); } },
      resumeStopped: () => { if (this.needKey()) return; this.startRecording(st.recPos); this.focusLater('#recpause'); },
      recNote: D.recorded ? 'Want a fresh take? Record again redoes every section.' : 'You can close this page. Claude tells you in chat when the draft is ready.',
      // review
      totalSec: String(this.total), revSec: String(st.revT), revCaption: this.secs[secAt(st.revT)].c, revTime: this.fmt(st.revT), revLeft: (st.revT / this.total * 100) + '%', revSecName: this.secs[secAt(st.revT)].n,
      ticks: this.starts.slice(1).filter((s) => Math.abs(s - st.revT) > this.total * 0.03).map((s) => (s / this.total * 100) + '%'),
      markPins: (() => { const g = []; allMarks.forEach((m) => { const last = g[g.length - 1]; if (last && m.t - last.t <= this.total * 0.012) last.items.push(m); else g.push({ t: m.t, items: [m] }); }); return g.map((x) => ({ left: (x.t / this.total * 100) + '%', count: x.items.length, label: this.fmt(x.t) + ', ' + x.items.map((m) => m.text).join(', '), aria: x.items.length > 1 ? 'Jump to ' + x.items.length + ' marks at ' + this.fmt(x.t) : 'Jump to mark ' + this.fmt(x.t) + ', ' + x.items[0].text, jump: () => { this.stop('player'); this.setState({ revT: x.t, player: false }); } })); })(),
      scrub: (e) => { const el = e.currentTarget; if (!el || !el.getBoundingClientRect) return; this.stop('player'); this.scrubbing = true; try { el.setPointerCapture(e.pointerId); } catch (x) {} const r = el.getBoundingClientRect(); this.setState({ player: false, revT: Math.round(Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * this.total) }); },
      scrubMove: (e) => { if (!this.scrubbing) return; const r = e.currentTarget.getBoundingClientRect(); const t = Math.round(Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * this.total); if (t !== this.state.revT) this.setState({ revT: t }); },
      scrubUp: () => { this.scrubbing = false; },
      scrubKey: (e) => { const k = e.key; const T = this.total; const now = this.state.revT; let t = null; if (k === 'ArrowRight' || k === 'ArrowUp') t = now + 5; else if (k === 'ArrowLeft' || k === 'ArrowDown') t = now - 5; else if (k === 'PageUp') t = now + 30; else if (k === 'PageDown') t = now - 30; else if (k === 'Home') t = 0; else if (k === 'End') t = T; else if (k === ' ' || k === 'Spacebar') { e.preventDefault(); this.renderVals().togglePlayer(); return; } if (t === null) return; e.preventDefault(); this.stop('player'); this.setState({ player: false, revT: Math.max(0, Math.min(T, t)) }); },
      playerOn: st.player, playerOff: !st.player, playerAria: st.player ? 'Pause' : 'Play',
      togglePlayer: () => { if (st.player) { this.stop('player'); this.setState({ player: false }); return; } this.setState({ player: true, markOpen: false }); this.every('player', 250, () => { const t = this.state.revT + 1; if (t >= this.total) { this.stop('player'); this.setState({ player: false, revT: this.total }); return; } this.setState({ revT: t }); }); },
      markOpen: st.markOpen, markClosed: !st.markOpen, markOther: st.markOther, openOther: () => { this.setState({ markOther: true }); requestAnimationFrame(() => { const el = document.getElementById('mown'); if (el) el.focus(); }); }, openMark: () => { this.stop('player'); this.setState({ player: false, markOpen: true, markOther: false, markDraft: '' }); this.focusLater('#markfirst'); }, closeMark: () => { this.setState({ markOpen: false, markOther: false, markDraft: '' }); this.focusLater('#markbtn'); },
      markAi: () => addMark('Sounds like AI'), markBlur: () => addMark('Needs a blur'), markFast: () => addMark('Too fast'),
      markDraft: st.markDraft, onMarkDraft: (e) => this.setState({ markDraft: e.target.value }), markOwn: () => { const d = st.markDraft.trim(); if (d) addMark(d); },
      markKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); const d = (e.target.value || '').trim(); if (d) addMark(d); } },
      marks: allMarks.map((m) => ({ t: this.fmt(m.t), text: m.text, sec: this.secs[Number(m.k)].n, jumpAria: 'Jump to ' + this.fmt(m.t), jump: () => this.setState({ revT: m.t, player: false }), rmAria: 'Remove mark at ' + this.fmt(m.t),
        rm: () => { const prev = D.notes; const n = Object.assign({}, prev); n[m.k] = prev[m.k].filter((x, k) => k !== m.j); this.patchDemo({ notes: n }); this.say('Mark removed', () => this.patchDemo({ notes: prev })); } })),
      hasMarks: marks > 0, noMarks: marks === 0, marksCount: marks ? '(' + marks + ')' : '', revCover: D.cover,
      hasUnsure: unsure > 0, unsureText: this.plural(unsure, 'blur') + ' to check', hasSkip: !!cur.skip && !st.confirm, skipLabel: cur.skip || '', doSkip: () => { this.setState({ confirm: 'approve' }); this.focusLater('#cfno'); }, blurOpen: st.blurOpen, toggleBlurs: () => this.setState({ blurOpen: !st.blurOpen }),
      blurs: unsureBlurs.map((b) => ({ t: b.t, what: b.what, keep: () => { const prev = D.blurs; this.patchDemo({ blurs: D.blurs.map((x) => x.id === b.id ? Object.assign({}, x, { s: 'keep' }) : x) }); this.say('Kept blurred', () => this.patchDemo({ blurs: prev })); }, show: () => { const prev = D.blurs; this.patchDemo({ blurs: D.blurs.map((x) => x.id === b.id ? Object.assign({}, x, { s: 'show' }) : x) }); this.say('Will be shown', () => this.patchDemo({ blurs: prev })); } })),
      // export
      revCaps: segOf(capOpts, dCap, (x) => { this.patchDemo({ capMode: x, dirty: !!D.exported }); }),
      revCorner: cornerCtl(dCorner, (x) => this.patchDemo({ corner: x, dirty: !!D.exported }), 'rct'),
      revCornerText: dCornerText, onRevCornerText: (e) => this.patchDemo({ cornerText: e.target.value, dirty: !!D.exported }), revCornerOff: dCorner === 'off',
      showCapPreview: dCap === 'burn', cornerShown: dCorner !== 'off', cornerStyle: posCss[dCorner] || '', cornerTextShown: dCornerText.trim() || 'Your label here',
      files: [{ n: base + '.mp4', s: '1080p · ' + lengthText + (dCap === 'burn' ? ' · captions in the video' : '') }].concat(dCap === 'file' ? [{ n: base + '.srt', s: 'Captions file' }] : []).concat([{ n: base + '.txt', s: 'Transcript' }]).concat(st.p720 ? [{ n: base + ' (720p).mp4', s: 'Small preview' }] : []),
      filesHead: D.exported && !D.dirty ? 'Saved files' : 'You’ll get', fileMark: D.exported && !D.dirty ? '✓' : '', fileWill: D.exported && D.dirty,
      firstCaption: this.secs[0].c, showInFinder: () => this.say('Showing it in Finder'), p720On: p.onStr, p720Cls: p.cls, toggle720: () => { this.setState({ p720: !st.p720 }); if (D.exported) this.patchDemo({ dirty: true }); },
      
      // settings / welcome
      defCaps: segOf(capOpts, st.defCap, (x) => { this.setState({ defCap: x }); this.say('Saved'); }),
      defCorner: cornerCtl(st.defCorner, (x) => this.setState({ defCorner: x }), 'dct'),
      defCornerText: st.defCornerText, onDefCornerText: (e) => this.setState({ defCornerText: e.target.value }), defCornerOff: st.defCorner === 'off',
      key: st.key, onKey: (e) => { if (e.target.value !== this.state.key) this.setState({ key: e.target.value, keyRes: null }); }, keyType: st.keyType, keyTypeLabel: st.keyType === 'password' ? 'Show key' : 'Hide key', toggleKeyType: () => this.setState({ keyType: st.keyType === 'password' ? 'text' : 'password' }),
      testKey: () => { if (!st.key.trim()) { this.setState({ keyRes: 'empty' }); return; } const ok = st.key.trim().length > 8; this.setState({ keyRes: ok ? 'ok' : 'bad', keyOn: ok ? true : st.keyOn }); if (ok && st.screen === 'settings') this.later('keyclose', 1400, () => { const inEdit = document.activeElement && document.activeElement.closest && document.activeElement.closest('.fade'); this.setState({ keyEdit: false, key: '', keyRes: null }); if (inEdit) this.focusLater('#keytoggle'); }); },
      keyEnter: (e) => { if (e.key === 'Enter') { e.preventDefault(); this.state.key = e.target.value; this.renderVals().testKey(); } },
      wSiteKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); this.state.wSite = e.target.value; this.renderVals().loginSite(); } },
      siteKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); this.state.siteDraft = e.target.value; this.renderVals().addSite(); } },
      keyMsg: keyMsg, keyMsgColor: st.keyRes === 'bad' || st.keyRes === 'empty' ? 'var(--danger)' : 'var(--ink)',
      w1Cls: wsw(st.keyRes === 'ok'), w1Mark: st.keyRes === 'ok' ? '✓' : '1', w2Cls: wsw(st.tools === 'done'), w2Mark: st.tools === 'done' ? '✓' : '2', w3Cls: wsw(st.logged), w3Mark: st.logged ? '✓' : '3',
      toolsIdle: st.tools === 'idle', toolsAsking: st.tools === 'ask',
      toolsText: st.tools === 'done' ? 'Installed. NAVI can drive a browser and save video.' : st.tools === 'ask' ? 'Install now? About 300 MB, takes about 2 minutes, one time.' : st.tools === 'busy' ? 'Installing… about 2 minutes.' : 'Lets NAVI drive a browser and save video. About 300 MB, one time.',
      askTools: () => { this.setState({ tools: 'ask' }); this.focusLater('#toolsyes'); }, cancelTools: () => { this.setState({ tools: 'idle' }); this.focusLater('#toolsinstall'); }, installTools: () => { this.setState({ tools: 'busy' }); this.focusLater('#toolstext'); this.later('tools', 1600, () => this.setState({ tools: 'done' })); },
      wSite: st.wSite, onWSite: (e) => this.setState({ wSite: e.target.value }),
      loginLabel: st.logged ? 'Logged in' : 'Open browser', loginSite: () => { const u = st.wSite.trim(); if (!u) { this.say('Type the site first, e.g. whop.com'); return; } this.setState({ logged: true, sites: st.sites.some((s) => s.u === u) ? st.sites : [{ u: u, note: 'Saved Nov 5' }].concat(st.sites) }); },
      welcomeBlocked: !(st.keyRes === 'ok' && st.tools === 'done'), welcomeStatus: st.keyRes === 'ok' && st.tools === 'done' ? 'All set.' : (st.keyRes !== 'ok' && st.tools !== 'done' ? 'Connect ElevenLabs and install the tools to continue.' : st.keyRes !== 'ok' ? 'Connect ElevenLabs to continue.' : 'Install the tools to continue.') ||  ((st.keyRes === 'ok' ? 0 : 1) + (st.tools === 'done' ? 0 : 1)) + (((st.keyRes === 'ok' ? 0 : 1) + (st.tools === 'done' ? 0 : 1)) === 1 ? ' step left' : ' steps left'),
      finishWelcome: () => this.setState({ screen: 'home', keyOn: true, key: '', keyRes: null }),
      appear: [['system', 'Follow Mac'], ['light', 'Light'], ['dark', 'Dark']].map((o) => ({ label: o[1], on: (st.theme || 'system') === o[0] ? 'true' : 'false', pick: () => { this.setState({ theme: o[0] === 'system' ? null : o[0] }); this.say('Saved'); } })),
      defVoices: st.mine.map((k) => ({ label: pretty(k), on: st.defVoice === k ? 'true' : 'false', pick: () => { this.setState({ defVoice: k }); this.say(pretty(k) + ' is now the default for new demos'); } })),
      keyRow: st.keyOn ? 'Ending 4f2a · ' + this.num(st.credits) + ' credits left' : 'Not connected. Demos can’t be voiced until you add one.', keyRowColor: st.keyOn ? 'var(--ink2)' : 'var(--danger)',
      keyEdit: st.keyEdit, keyEditLabel: st.keyEdit ? 'Cancel' : (st.keyOn ? 'Change' : 'Add key'), toggleKeyEdit: () => this.setState({ keyEdit: !st.keyEdit, key: '', keyRes: null }),
      canRemoveKey: st.keyOn && !st.keyEdit, removeKey: () => { this.setState({ keyOn: false }); this.focusLater('#keytoggle'); this.say('Key removed here. It still works at ElevenLabs.', () => this.setState({ keyOn: true })); },
      sites: st.sites.map((s) => ({ u: s.u, note: s.note, relog: () => this.say('A browser opens so you can log in to ' + s.u + ' again'), forget: () => { const prev = st.sites; this.setState({ sites: st.sites.filter((x) => x.u !== s.u) }); this.say('Forgot ' + s.u, () => this.setState({ sites: prev })); } })),
      noSites: !st.sites.length,
      siteDraft: st.siteDraft, siteBad: !!st.siteBad, onSiteDraft: (e) => { if (e.target.value !== this.state.siteDraft) this.setState({ siteDraft: e.target.value, siteBad: false }); }, addSite: () => { const u = st.siteDraft.trim(); if (!u) return; if (!siteOk(u)) { this.setState({ siteBad: true }); return; } this.setState({ sites: st.sites.concat([{ u: u, note: 'Saved Nov 5' }]), siteDraft: '' }); this.say('A browser opens so you can log in to ' + u); },
      data: dataDefs.map((d) => ({ n: d.n, w: d.w, l: d.l, can: !!d.l, act: dataAct[d.id] || (() => {}) })), forgetAll: dataAct.logins,
      wipeConfirm: st.wipeConfirm, notWipeConfirm: !st.wipeConfirm, askWipe: () => { this.setState({ wipeConfirm: true }); this.focusLater('#wipecancel'); }, cancelWipe: () => { this.setState({ wipeConfirm: false }); this.focusLater('#wipebtn'); },
      doWipe: () => { this.focusLater('#wipebtn'); this.setState({ wipeConfirm: false, keyOn: false, sites: [], hide: [], vals: Object.assign({}, this.presetVals.course), defVoice: 'alex', mine: ['alex', 'jessica', 'george'], heardVoices: {}, tools: 'idle' }); this.say('Everything this skill saved is gone. Your videos are untouched.', null, () => this.setState({ screen: 'welcome', keyRes: null, logged: false, wSite: '' }), 'Set up again'); },
      showWelcome: () => this.setState({ screen: 'welcome', keyRes: null, key: '', tools: st.tools === 'done' ? 'done' : 'idle', logged: false, wSite: '' }),
      // chat + toast
      chatOpen: st.chat.length > 0, chatDraft: st.chatDraft, onChat: (e) => this.setState({ chatDraft: e.target.value }),
      chatPlaceholder: (() => { try { if (window.matchMedia('(max-width: 860px)').matches) return 'Ask Claude…'; } catch (e) {} return null; })() || (st.screen === 'demo' ? 'Tell Claude what to change, e.g. “make it about the payouts page instead”' : 'Ask Claude anything'),
      chat: st.chat.map((m) => ({ text: m.t, side: m.me ? 'flex-end' : 'flex-start', bg: m.me ? 'var(--ink)' : 'var(--wash)', fg: m.me ? 'var(--sheet)' : 'var(--ink)' })),
      chatKey: (e) => { if (e.key === 'Enter') { e.preventDefault && e.preventDefault(); this.sendChatNow(); } },
      sendChat: () => this.sendChatNow(),
      chatAction: !!st.chatAct, doChatAction: () => this.setState({ screen: 'new', mode: 'one', editing: false, bWhat: chatClean(st.chatAct), bNew: '', bSiteNew: false, bVoice: st.defVoice, bSite: st.sites[0] ? st.sites[0].u : '', chatAct: null, chat: [] }),
      closeChat: () => this.setState({ chat: [], chatAct: null }),
      hasToast: !!st.toast, toast: st.toast, toastUndo: !!st.toastUndo, undoToast: () => { const d = this.undoFrom; if (st.toastUndo) st.toastUndo(); this.setState({ toast: '', toastUndo: null, toastGo: null }); this.focusLater(() => this.findDesc(d) || this.heading()); },
      sampleCostText: String(SAMPLE_COST), toastGo: !!st.toastGo, toastGoLabel: st.toastGoLabel, goToast: () => { if (st.toastGo) st.toastGo(); this.setState({ toast: '', toastUndo: null, toastGo: null }); }
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
  const keepStepVisible = () => requestAnimationFrame(() => { const box = document.querySelector('.steplist'); const el = box && box.querySelector('.stepbtn.now'); if (!box) return; if (el && box.scrollWidth > box.clientWidth) { const prev = el.previousElementSibling && el.previousElementSibling.classList.contains('stepbtn') ? el.previousElementSibling : (el.parentElement.previousElementSibling && el.parentElement.previousElementSibling.querySelector ? el.parentElement.previousElementSibling.querySelector('.stepbtn') : null); const target = prev || el; box.scrollLeft = Math.max(0, box.scrollLeft + target.getBoundingClientRect().left - box.getBoundingClientRect().left - 6); } const upd = () => box.classList.toggle('at-start', box.scrollLeft < 4); upd(); if (!box._navi) { box._navi = 1; box.addEventListener('scroll', upd, { passive: true }); } });
  // Toasts sit above the chat bar, and lift above any footer buttons they would cover.
  const placeToast = () => { const el = document.getElementById('toast'); if (!el) return; el.style.bottom = ''; el.style.top = ''; const tr = el.getBoundingClientRect(); const hit = [...document.querySelectorAll('main .foot .fbtns')].map((f) => f.getBoundingClientRect()).find((f) => f.height && f.bottom > 0 && f.top < innerHeight && f.top < tr.bottom && f.bottom > tr.top); if (!hit) return; const room = hit.top - 8; if (room - tr.height > 72) el.style.bottom = (innerHeight - room) + 'px'; else { el.style.bottom = 'auto'; el.style.top = Math.min(innerHeight - tr.height - 96, hit.bottom + 8) + 'px'; } };
  window.addEventListener('scroll', () => placeToast(), { passive: true });
  let lastDesc = null, lastEl = null, where = comp.state.screen + '/' + comp.state.step;
  document.addEventListener('focusin', (e) => { lastEl = e.target; lastDesc = comp.describe(e.target); });
  // After every render: a new step or screen focuses its heading; if the focused control vanished, find its stand-in.
  const afterRender = () => requestAnimationFrame(() => requestAnimationFrame(() => {
    const now = comp.state.screen + '/' + comp.state.step; const moved = now !== where; where = now;
    const recent = comp.focusAt && Date.now() - comp.focusAt < 120;
    const ae = document.activeElement; const lost = !ae || ae === document.body;
    placeToast();
    // A new step or screen opens at the top of the page, so the header and its title are in view.
    if (moved) window.scrollTo(0, 0);
    if (moved && !recent && comp.state.screen !== 'welcome') { if (comp.state.screen === 'new') { if (lost || !document.querySelector('main').contains(ae)) { const f = document.getElementById(comp.state.mode === 'batch' ? 'btt' : 'bw'); if (f) f.focus({ preventScroll: true }); } } else { const hd = comp.heading(); if (hd) hd.focus({ preventScroll: true }); } return; }
    if (lost && !recent && lastEl && (!lastEl.isConnected || lastEl.disabled || lastEl.offsetParent === null)) { const el = comp.findDesc(lastDesc) || comp.heading(); if (el) el.focus(); }
  }));
  // An Undo belongs to the step it was offered on: leaving that step or screen drops the toast.
  comp.setState = function (s) { Object.assign(comp.state, s); if (comp.state.toastUndo && comp.toastWhere && comp.toastWhere !== comp.state.screen + '/' + comp.state.step) Object.assign(comp.state, { toast: '', toastUndo: null, toastGo: null }); Object.assign(scope, comp.renderVals()); keepStepVisible(); if (s && 'toast' in s) requestAnimationFrame(placeToast); afterRender(); };
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !e.defaultPrevented) { if (comp.escape()) e.preventDefault(); return; }
    if (e.key === 'Tab' && comp.state.lib) { const d = document.getElementById('libdlg'); if (!d) return; const f = [...d.querySelectorAll('button, input, [tabindex="0"]')].filter((x) => !x.disabled && x.offsetParent !== null); if (!f.length) return; const i = f.indexOf(document.activeElement); if (e.shiftKey && (i <= 0)) { e.preventDefault(); f[f.length - 1].focus(); } else if (!e.shiftKey && (i === f.length - 1 || i < 0)) { e.preventDefault(); f[0].focus(); } }
  });
  document.addEventListener('pointerdown', (e) => comp.outside(e.target), true);
  try { window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => comp.setState({})); } catch (e) {}
  PetiteVue.createApp(scope).mount('#app');
  keepStepVisible(); window.addEventListener('resize', () => comp.setState({}));
  window.navi = comp;
  if (q.get('start') === 'new' && q.get('mode') === 'batch') comp.setState({ mode: 'batch' });
})();
