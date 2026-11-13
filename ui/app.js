// NAVI local UI. Interactive prototype: every screen and control works with sample data.
// The real skill serves this page locally and swaps the sample data for the engine's.
// Open ui/index.html in a browser. Optional: ?start=home|new|batch|voice|review|settings&theme=light|dark
class DCLogic { constructor(p) { this.props = p || {}; } setState(s) { Object.assign(this.state, s); } }
const PRESETS = {
  strict: { email: false, phone: false, names: false, address: false, money: false, customers: false, counts: false, usage: false, prices: false, dates: false },
  standard: { email: false, phone: false, names: false, address: false, money: false, customers: false, counts: false, usage: true, prices: true, dates: true },
  test: { email: true, phone: true, names: true, address: true, money: false, customers: false, counts: false, usage: true, prices: true, dates: true }
};
// R5 fix 11 (two weights): screens listed here keep the old third weight (500). Keys: welcome home new new-batch batch script voice privacy record review export settings.
const W2_OFF = ['home'];
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
    const whop = { id: 'whop', title: 'Build it in Whop', site: 'whop.com', seat: 'Owner in NAVI Test', seatSaved: true, len: 2, who: 0, voice: 'alex', model: 'v4', kind: 'course', max: 4, cover: 'assets/cover-1.jpg', status: 'Watch the draft →', dot: 'ready', recorded: true, written: true,
      notes: { 2: [{ t: 60, text: 'Sounds too cheerful' }], 4: [{ t: 125, text: 'Too fast' }] },
      blurs: [{ id: 'b1', t: '1:58', what: 'A name inside the course cover image', s: '' }, { id: 'b2', t: '3:53', what: 'What might be a price in a banner', s: '' }] };
    this.fallbackDemo = whop;
    const demos = [whop,
      { id: 'pay', title: 'Connect payouts', site: 'whop.com', len: 0, who: 0, voice: 'alex', model: 'v4', kind: 'course', max: 5, cover: 'assets/cover-3.jpg', status: 'Exported Nov 2 · Open the video →', exportedOn: 'Nov 2', dot: 'done', recorded: true, written: true, exported: true, notes: {}, blurs: [] },
      { id: 'posts', title: 'Schedule a week of posts', site: 'app.yourproduct.com', len: 1, who: 1, voice: 'jessica', model: 'v4', kind: 'saas', max: 5, cover: 'assets/cover-4.jpg', status: 'Exported Oct 28 · Open the video →', exportedOn: 'Oct 28', dot: 'done', recorded: true, written: true, exported: true, notes: {}, blurs: [] }];
    demos.forEach((d) => Object.assign(d, { capMode: 'burn', corner: 'off', cornerText: '', lines: {}, style: 'casual', look: 'mona-rounded', speed: null }));
    const batch = { id: 'b-whop2', name: 'Whop course, module 2', site: 'whop.com', voice: 'alex', kind: 'course', preset: 'standard', folder: '~/Movies/NAVI/Whop course, module 2', stage: 'recording', paused: false,
      items: COURSE.map((t, i) => ({ t: t, lesson: 'Lesson ' + (i + 1), min: [2, 3, 3, 4, 3, 2, 4, 3, 3, 2, 2, 2, 3, 3, 4, 2, 2, 3, 2, 2, 2, 3, 2][i], st: i < 2 ? 'approved' : i < 7 ? 'recorded' : i === 7 ? 'recording' : 'waiting', seat: i % 4 === 3 ? 'Owner, as a member of Demo Academy' : 'Owner in Demo Academy', seatKey: 'whop.com/owner' })),
      logins: [{ key: 'whop.com/owner', site: 'whop.com', seat: 'owner', label: 'whop.com · Owner', status: 'working', home: 'https://whop.com/' }] };
    const screen = start === 'voice' || start === 'review' ? 'demo' : start;
    this.state = {
      screen: screen, step: start === 'review' ? 4 : 1, cur: 'whop', demos: demos, batches: [batch], curBatch: 'b-whop2', theme: null, help: false, pickOpen: null, pickRead: '', pickPlaying: '', pickPos: 0,
      jobs: [{ label: 'Planning', model: 'claude-fable-5-2', effort: 'high', then: 'claude-opus-5-5' }, { label: 'Exploring', model: 'claude-haiku-5-5', effort: 'medium', then: 'claude-sonnet-5-5' }, { label: 'Writing', model: 'claude-opus-5-5', effort: 'medium', then: 'claude-sonnet-5-5' }, { label: 'Checks', model: 'claude-sonnet-5-5', effort: 'medium', then: 'claude-opus-5-5' }, { label: 'Batch check', model: 'claude-opus-5-5', effort: 'high', then: 'claude-sonnet-5-5' }], jobWarnings: [],
      keyOn: start !== 'welcome', key: '', keyType: 'password', keyRes: null, keyEdit: false,
      tools: start === 'welcome' ? 'idle' : 'done', logged: false, wSite: '', wSiteMsg: '',
      credits: 26400, mine: ['alex', 'jessica', 'george'], defVoice: 'alex',
      vals: Object.assign({}, this.presetVals.course), caps: false, lock: true, heardVoices: {}, lastSample: null, sampling: false, sliderHelp: false, fineOpen: false,
      shown: Object.assign({}, PRESETS.standard), hide: ['Acme Studio'], hideDraft: '', pvMore: false,
      scSel: 0, scCaps: false, scChange: false, scDraft: '', scPending: null,
      revT: 86, player: false, markOpen: false, markDraft: '', blurOpen: false, p720: false,
      recPos: 4, recPaused: false, recStopAsk: false, recStopped: false, confirm: null,
      sites: [{ u: 'whop.com', seat: 'owner', label: 'Owner', status: 'working', ago: '2 min ago', biz: 'Demo Academy (test)', saved: true, note: 'Saved Nov 4' }, { u: 'app.yourproduct.com', seat: 'owner', label: 'Owner', status: 'needs login', ago: '2 min ago', biz: '', saved: true, note: 'Saved Oct 28' }], siteDraft: '', wipeConfirm: false,
      lib: false, libF: 'all', chat: [], chatDraft: '', chatAct: null,
      defCap: 'burn', defCorner: 'off', defCornerText: '', defStyle: 'casual', defLook: 'mona-rounded', defSpeed: null, defSpeedDraft: '1.35', speedDraft: '1.35', creditLimit: 10000, limitDraft: '10000', autoGo: false,
      mode: 'one', bMore: false, bKind: 'course', recDoneOpen: false, markOther: false, bWhat: '', bSite: 'whop.com', bSiteNew: false, bNew: '', bWho: 0, bLen: 2, bHide: '', bVoice: 'alex', bCap: 'burn', bCorner: 'off', bCornerText: '', editing: false,
      btSiteNew: false, btNew: '', btAll: false, fromBatch: null, batchItem: null, btText: '', btName: '', btFile: '', btSite: 'whop.com', btVoice: 'alex', btKind: 'course', btPreset: 'standard', btFolder: '', btOpen: null, bConfirm: false,
      toast: '', toastUndo: null, toastGo: null, toastGoLabel: ''
    };
    this.timers = {};
    if (window.NaviEngine && NaviEngine.live) this.liveReset();
  }
  useScript(D) { const k = D && this.scripts[D.script || D.id] ? (D.script || D.id) : 'whop'; this.secs = this.scripts[k]; this.starts = []; let acc = 0; this.secs.forEach((x) => { this.starts.push(acc); acc += x.d; }); this.total = acc; }
  componentWillUnmount() { Object.keys(this.timers).forEach((k) => { clearTimeout(this.timers[k]); clearInterval(this.timers[k]); }); }
  later(name, ms, fn) { if (this.timers[name]) clearTimeout(this.timers[name]); this.timers[name] = setTimeout(fn, ms); }
  watchLive(did) {
    this.stopLive();
    if (!this.live || !did) return;
    this.every('live', 600, () => {
      if (document.hidden) return;
      fetch('/api/live/' + did, { cache: 'no-store' }).then((r) => r.status === 200 ? r.blob() : null).then((b) => {
        if (!b || !this.state.liveOpen) return;
        const url = URL.createObjectURL(b); const old = this.state.liveSrc; this.setState({ liveSrc: url }); if (old && old.startsWith('blob:')) URL.revokeObjectURL(old);
      }).catch(() => {});
    });
  }
  stopLive() { if (this.timers.live) { clearInterval(this.timers.live); this.timers.live = null; } }
  every(name, ms, fn) { if (this.timers[name]) clearInterval(this.timers[name]); this.timers[name] = setInterval(fn, ms); }
  stop(name) { if (this.timers[name]) { clearInterval(this.timers[name]); clearTimeout(this.timers[name]); delete this.timers[name]; } }
  focusLater(sel) { this.focusAt = Date.now(); requestAnimationFrame(() => { const el = typeof sel === 'string' ? document.querySelector(sel) : typeof sel === 'function' ? sel() : sel; if (el && el.focus) el.focus(); }); }
  // Focus model helpers: describe a control so it can be found again after a re-render (Undo, swapped buttons).
  describe(el) { if (!el || el === document.body || !el.getAttribute) return null; return { id: el.id || '', aria: el.getAttribute('aria-label') || '', text: (el.innerText || '').trim(), tag: el.tagName }; }
  findDesc(d) { if (!d) return null; const ok = (e) => e && e.isConnected && !e.disabled && e.offsetParent !== null; if (d.id) { const e = document.getElementById(d.id); if (ok(e)) return e; } const all = [...document.querySelectorAll(d.tag || 'button')].filter(ok); return (d.aria && all.find((e) => e.getAttribute('aria-label') === d.aria)) || (d.text && all.find((e) => (e.innerText || '').trim() === d.text)) || null; }
  // Where focus goes when a footer confirm closes without acting: the button that opened it.
  confirmFrom(c) { return c === 'rerecord' ? '#secbtn' : c === 'approve' ? () => document.getElementById('skipbtn') || document.querySelector('.stepfoot .pri') : '.stepfoot .pri'; }
  heading() { return document.querySelector('#step-h, #batch-h, #demos-h, #set-h'); }
  escape() {
    const st = this.state; const back = (sel) => this.focusLater(sel);
    if (st.lib) { this.setState({ lib: false }); back('#vmore'); return true; }
    if (st.help) { this.setState({ help: false }); back('#helpbtn'); return true; }
    if (st.chat.length) { this.setState({ chat: [], chatAct: null }); back('#chatin'); return true; }
    if (st.markOpen) { this.setState({ markOpen: false, markOther: false, markDraft: '' }); back('#markbtn'); return true; }
    if (st.wipeConfirm) { this.setState({ wipeConfirm: false }); back('#wipebtn'); return true; }
    if (st.confirm) { const sel = this.confirmFrom(st.confirm); this.setState({ confirm: null }); back(sel); return true; }
    if (st.screen === 'batch' && st.btOpen != null) { const i = st.btOpen; this.setState({ btOpen: null }); back('#bread-' + i); return true; }
    if (st.screen === 'batch' && st.bConfirm) { this.setState({ bConfirm: false }); back('.bprimary'); return true; }
    if (st.screen === 'new' && st.bSiteNew) { this.setState({ bSiteNew: false, bNew: '' }); back('#bnewchip'); return true; }
    if (st.screen === 'new' && st.btSiteNew) { this.setState({ btSiteNew: false, btNew: '' }); back('#btnewchip'); return true; }
    if (st.screen === 'welcome' && st.tools === 'ask') { this.setState({ tools: 'idle' }); back('#toolsinstall'); return true; }
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
  say(msg, undo, go, goLabel) { if (undo) this.undoFrom = this.describe(document.activeElement); this.toastWhere = this.state.screen + '/' + this.state.step; this.toastAt = Date.now(); this.setState({ toast: msg, toastUndo: undo || null, toastGo: go || null, toastGoLabel: goLabel || '' }); this.later('toast', 4200, () => this.setState({ toast: '', toastUndo: null, toastGo: null })); }
  ago(sec) { const d = Math.max(0, Date.now() / 1000 - sec); return d < 60 ? 'just now' : d < 3600 ? Math.round(d / 60) + ' min ago' : d < 86400 ? Math.round(d / 3600) + ' h ago' : new Date(sec * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }); }
  fmt(t) { const m = Math.floor(t / 60); const s = Math.floor(t % 60); return m + ':' + (s < 10 ? '0' : '') + s; }
  num(n) { return n.toLocaleString('en-US'); }
  plural(n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); }
  demo() { return this.state.demos.find((d) => d.id === this.state.cur) || this.state.demos[0] || this.fallbackDemo; }
  batch() { return this.state.batches.find((b) => b.id === this.state.curBatch) || this.state.batches[0]; }
  patchDemo(p) { const id = this.state.cur; const prev = this.state.demos.find((d) => d.id === id); this.setState({ demos: this.state.demos.map((d) => d.id === id ? Object.assign({}, d, p) : d) }); if (this.live) this.pushDemo(prev, p); }
  patchBatch(p, id) { const bid = id || this.state.curBatch; this.setState({ batches: this.state.batches.map((b) => b.id === bid ? Object.assign({}, b, typeof p === 'function' ? p(b) : p) : b) }); }
  recFor(voice, kind) { const base = Object.assign({}, this.presetVals[kind]); const adj = (this.VO[voice] || {}).adj || {}; Object.keys(adj).forEach((k) => { const r = this.ranges[k]; base[k] = Math.max(r[0], Math.min(r[1], base[k] + adj[k])); }); return base; }
  spend(n) { this.setState({ credits: Math.max(0, this.state.credits - n) }); }
  needKey() { if (this.state.keyOn) return false; this.say('Connect your ElevenLabs key first', null, () => this.setState({ screen: 'settings', keyEdit: true }), 'Connect'); return true; }
  presetOf(shown) { const keys = Object.keys(PRESETS); for (let i = 0; i < keys.length; i++) { const p = PRESETS[keys[i]]; if (Object.keys(p).every((k) => p[k] === shown[k])) return keys[i]; } return 'custom'; }
  perVideo(min) { return Math.round(min * 930 / 10) * 10; }
  fitsText(n) { return 'Enough credits for about ' + this.plural(n, 'more video') + '. The batch pauses there until you add credits. Nothing fails.'; }
  startRecording(from) {
    if (this.live) { this.setState({ recPos: from || 0, recPaused: false, recStopped: false, recSlide: 0, recSliding: false }); return; }
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
    if (this.live) return;
    this.every('batch', 2400, () => {
      const b = this.batch(); if (!b || b.stage !== 'recording' || b.paused) return;
      const i = b.items.findIndex((x) => x.st === 'recording');
      if (i < 0) { this.stop('batch'); return; }
      const cost = this.perVideo(b.items[i].min);
      if (this.state.credits < cost) { this.patchBatch({ paused: 'credits' }); this.say('Batch paused: not enough credits for the next video'); return; }
      this.spend(cost);
      const nx = b.items[i + 1]; const short = !!(nx && nx.st === 'waiting' && this.state.credits < this.perVideo(nx.min));
      const items = b.items.map((x, k) => k === i ? Object.assign({}, x, { st: 'recorded' }) : (k === i + 1 && x.st === 'waiting' && !short ? Object.assign({}, x, { st: 'recording' }) : x));
      this.patchBatch({ items: items, stage: short || items.some((x) => x.st === 'recording') ? 'recording' : 'review', paused: short ? 'credits' : false });
      if (short) this.say('Batch paused: not enough credits for the next video');
    });
  }
  // Each batch video gets its own demo record the first time it's watched (no marks, no blurs), so Review shows that video.
  batchDemos(b, i) { const id = b.id + '#' + i; if (this.state.demos.some((d) => d.id === id)) return { id: id, demos: this.state.demos }; const it = b.items[i]; const vo = this.VO[b.voice] || this.VO.alex; const d = { id: id, batchOf: b.id, title: it.t, site: b.site, len: 1, who: 0, voice: b.voice, model: vo.models.indexOf('v4') >= 0 ? 'v4' : vo.models[0], kind: b.kind, max: 4, cover: ['assets/cover-1.jpg', 'assets/cover-3.jpg', 'assets/cover-4.jpg'][i % 3], status: '', dot: '', recorded: true, written: true, notes: {}, blurs: [], lines: {}, capMode: 'burn', corner: 'off', cornerText: '' }; return { id: id, demos: this.state.demos.concat([d]) }; }
  // All demos: delete a demo or a batch with an Undo toast (no confirm). Deletes in a row merge into one toast whose Undo restores all of them. Videos already exported stay in Movies/NAVI.
  deleteCard(kind, id) {
    const st = this.state; const key = kind + '-' + id;
    const order = st.batches.map((b) => 'b-' + b.id).concat(st.demos.filter((d) => !d.batchOf).map((d) => 'd-' + d.id));
    const i = order.indexOf(key); const next = order[i + 1] || order[i - 1];
    const item = kind === 'b' ? st.batches.find((b) => b.id === id) : st.demos.find((d) => d.id === id); if (!item) return;
    const run = this.delRun && this.delRun.at === this.toastAt && this.state.toast ? this.delRun : null;
    const first = run ? run.first : { demos: st.demos, batches: st.batches };
    const n = { d: (run ? run.n.d : 0) + (kind === 'd' ? 1 : 0), b: (run ? run.n.b : 0) + (kind === 'b' ? 1 : 0), ex: (run ? run.n.ex : false) || !!item.exported };
    this.setState({ demos: st.demos.filter((d) => kind === 'd' ? d.id !== id : d.batchOf !== id), batches: kind === 'b' ? st.batches.filter((b) => b.id !== id) : st.batches });
    this.focusLater(() => (next && document.getElementById('card-' + next)) || document.querySelector('main .newtile'));
    const name = kind === 'b' ? item.name : item.title;
    const msg = n.d + n.b === 1 ? 'Deleted “' + name + '”' + (n.ex ? '. Its video stays in Movies/NAVI.' : '') : [n.d ? this.plural(n.d, 'demo') : '', n.b ? n.b + (n.b === 1 ? ' batch' : ' batches') : ''].filter(Boolean).join(' and ') + ' deleted' + (n.ex ? '. Exported videos stay in Movies/NAVI.' : '');
    const from = run ? this.undoFrom : { id: 'card-' + key, aria: '', text: '', tag: 'BUTTON' };
    if (this.live) { if (kind === 'd') this.act('demo.update', { demo: id, patch: { hidden: true } }, { quiet: true }); else this.act('batch.hide', { batch: id, hidden: true }, { quiet: true }); }
    const hiddenNow = (this.delRun && run ? this.delRun.ids : []).concat([[kind, id]]);
    this.say(msg, () => { if (this.live) hiddenNow.forEach((x) => x[0] === 'd' ? this.act('demo.update', { demo: x[1], patch: { hidden: false } }, { quiet: true }) : this.act('batch.hide', { batch: x[1], hidden: false }, { quiet: true })); this.setState({ demos: first.demos, batches: first.batches }); });
    this.undoFrom = from; this.delRun = { first: first, n: n, at: this.toastAt, ids: hiddenNow };
  }
  openFolder(folder) { if (this.live) { this.act('app.open_folder', folder ? { folder: folder } : {}); return; } this.say('Opening ' + (folder || 'Movies/NAVI')); }
  // Sample states of the blind A/B/C screens (file mode and ui/tests/layout-check.js): 'lesson', 'plan', 'revealed', 'paused'.
  sampleBlind(kind) {
    const B = this.state.batches.find((b) => b.id === this.state.curBatch); if (!B) return;
    const talk = [['Okay so, lesson types. Most of yours are gonna be Multimedia, so that’s text, video and downloads all in one.', 'You pick it from the menu on the right, and it, well, it remembers it for the next lesson.', 'Quiz is the other one worth knowing, since it’s where people check they followed along.'], ['Lesson types are in the menu on the right of each lesson, and Multimedia is the one you’ll use for nearly all of them.', 'It takes text, video and files together, so you’re not making three lessons for one idea.', 'I’d only reach for Quiz at the end of a chapter.'], ['When you add a lesson it asks what kind it is, and for a course like this it’s pretty much always Multimedia.', 'That one holds the video, the write-up and any downloads in the same place.', 'There’s a Quiz type too, uh, which is worth one per chapter.']];
    if (kind === 'lesson') { const lessons = {}; [7, 8].forEach((i) => { lessons[i] = { status: 'waiting', picked: '', options: ['A', 'B', 'C'].map((l, k) => ({ letter: l, audio: '', seconds: 47 + k * 6, lines: talk[k] })) }; }); this.patchBatch({ stage: 'recording', paused: false, items: B.items.map((x, i) => Object.assign({}, x, { st: i < 7 ? (i < 2 ? 'approved' : 'recorded') : i < 9 ? 'pick' : i === 9 ? 'recording' : 'waiting' })), blind: { plan: null, lessons: lessons, revealed: null } }); this.setState({ pickOpen: 7, pickRead: '', liveOpen: false }); }
    if (kind === 'plan') { const mk = (l, k) => ({ letter: l, note: '', videos: B.items.map((x, i) => ({ t: x.t, goal: ['You can set it up from a blank account.', 'You’ll know where it lives and what to click first.', 'You finish with it working, start to end.'][(i + k) % 3], sections: [] })) }); this.patchBatch({ stage: 'writing', paused: false, items: B.items.map((x) => Object.assign({}, x, { st: 'writing' })), blind: { plan: { status: 'waiting', picked: '', options: ['A', 'B', 'C'].map(mk) }, lessons: {}, revealed: null } }); this.setState({ pickOpen: null, pickRead: '' }); }
    if (kind === 'revealed') this.patchBatch({ stage: 'review', paused: false, items: B.items.map((x, i) => Object.assign({}, x, { st: i < 4 ? 'approved' : 'recorded' })), blind: { plan: null, lessons: {}, revealed: { picks: [{ kind: 'planning', title: B.name, picked_letter: 'B', picked: 'claude-opus-5-5 / high' }, { kind: 'writing', title: B.items[0].t, picked_letter: 'A', picked: 'claude-opus-5-5 / low' }, { kind: 'writing', title: B.items[1].t, picked_letter: 'C', picked: 'claude-opus-5-5 / medium' }, { kind: 'writing', title: B.items[2].t, picked_letter: 'A', picked: 'claude-opus-4-6 / medium' }], tally: { writing: [{ arm: 'claude-opus-5-5 / low', picked: 1, shown: 3 }, { arm: 'claude-opus-5-5 / medium', picked: 1, shown: 3 }, { arm: 'claude-opus-4-6 / medium', picked: 1, shown: 3 }] } } } });
    if (kind === 'paused') this.patchBatch({ stage: 'recording', paused: true, runner: { alive: false, awake: false, line: 'paused at video 8 of ' + B.items.length, waitingFor: '', at: 8, total: B.items.length } });
  }
  // One voice at a time for the A/B/C versions. With no audio (sample data) the bar just runs.
  pickPlay(key, src, secs) {
    const stop = () => { if (this.pickAudio) { this.pickAudio.pause(); } clearInterval(this.timers.pickbar); };
    if (this.state.pickPlaying === key) { stop(); this.setState({ pickPlaying: '' }); return; }
    stop(); this.setState({ pickPlaying: key, pickPos: 0 });
    if (src) {
      const a = this.pickAudio || (this.pickAudio = new Audio()); a.src = src;
      a.ontimeupdate = () => { if (this.state.pickPlaying === key && a.duration) this.setState({ pickPos: a.currentTime / a.duration }); };
      a.onended = () => { if (this.state.pickPlaying === key) this.setState({ pickPlaying: '', pickPos: 0 }); };
      a.play().catch(() => { this.setState({ pickPlaying: '' }); this.say('That version couldn’t be played.'); });
    } else { const t0 = Date.now(); this.every('pickbar', 250, () => { const f = (Date.now() - t0) / 1000 / (secs || 30); if (f >= 1 || this.state.pickPlaying !== key) { clearInterval(this.timers.pickbar); if (this.state.pickPlaying === key) this.setState({ pickPlaying: '', pickPos: 0 }); } else this.setState({ pickPos: f }); }); }
  }
  pickStop() { if (this.pickAudio) this.pickAudio.pause(); if (this.timers.pickbar) clearInterval(this.timers.pickbar); if (this.state.pickPlaying) this.setState({ pickPlaying: '', pickPos: 0 }); }
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
    const redoCost = this.live ? markedSecs.reduce((s, k) => s + ((this.secs[Number(k)] || {}).cost || 0), 0) : markedSecs.length * 420;
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
    const videoCost = this.live ? (D.cost || 0) : Math.round(4600 * baseSec / this.total / 10) * 10; const leftAfter = Math.max(0, st.credits - videoCost);
    const lengthText = this.fmt(lengthSec);
    const paceText = (pace / 100).toFixed(2) + 'x';
    const kindName = { course: 'walkthrough', saas: 'quick demo', tour: 'product tour' }[D.kind];
    const isPhone = (() => { try { return window.matchMedia('(max-width: 860px)').matches; } catch (e) { return false; } })();
    const recording = !D.recorded && st.recPos < N && !st.recStopped;
    const voiceOk = vInfo.models.indexOf(model) >= 0;
    const S = [
      { name: 'Script', sub: D.written ? N + ' sections' : 'Writing…', title: 'Read the script', help: 'Pick a section to read it. Change one line here, or ask Claude below for bigger changes.', cta: D.max > 0 ? 'Next: Voice' : 'Approve script' },
      { name: 'Voice', sub: voicePretty + ', ' + (model === 'v4' ? 'Eleven v4' : 'Eleven v3'), title: 'Pick the voice', help: 'Click a face to pick it. Press Hear to listen. NAVI switches the model if needed.', cta: 'Use ' + voicePretty },
      { name: 'Privacy', sub: presetName[preset], title: 'Choose what gets blurred', help: 'Blurring happens while recording, then every frame is checked again. Anything unclear shows up in Review.', cta: D.recorded ? 'Use these blurs' : 'Use these blurs and record' },
      { name: 'Record', sub: D.recorded ? 'Done, ' + lengthText : (st.recStopped ? 'Stopped' : (recording && st.cur === D.id && D.max >= 3 ? 'Section ' + Math.min(N, st.recPos + 1) + ' of ' + N : 'Not yet')), title: D.recorded ? 'Recorded' : (st.recStopped ? 'Recording stopped' : 'Recording'), help: D.recorded ? 'Every section is recorded. Watch the draft next.' : st.recStopped ? 'Carry on to record the rest, or record again from the start.' : st.recPaused ? 'Recording is paused. Resume carries on from section ' + Math.min(N, st.recPos + 1) + ', and finished sections are kept.' : 'The browser does the clicks while ' + voicePretty + ' talks. You can close this page: NAVI keeps going and the draft shows up on All demos.', helpHold: 'The browser does the clicks while ' + voicePretty + ' talks. You can close this page: NAVI keeps going and the draft shows up on All demos.', cta: 'Watch the draft', second: D.recorded || st.recStopped ? 'Record again' : '' },
      { name: 'Review', sub: marks ? this.plural(marks, 'mark') : (D.recorded ? 'No marks' : 'Not yet'), title: 'Watch the draft', help: 'Press Mark this moment when something is off. Only marked sections are redone.', cta: marks ? 'Redo ' + this.plural(markedSecs.length, 'section') : (st.fromBatch ? 'Approve and watch next' : 'Looks good, go to Export'), ctaShort: marks ? 'Redo ' + this.plural(markedSecs.length, 'section') : (st.fromBatch ? 'Approve, next' : 'Go to Export'), second: '', skip: marks ? 'Skip redo, keep as is' : '' },
      { name: 'Export', sub: D.exported ? 'Exported' : 'Not yet', title: D.exported ? 'Exported' : 'Export', help: D.exported ? 'Saved to Movies/NAVI. Change a setting to export again, free.' : 'Choose the style, captions and any extra copies. Changing these costs no credits.', cta: D.exported ? (D.dirty ? 'Export again' : 'Open folder') : 'Export video', second: '' }
    ];
    const bNextReady = (() => { if (!st.fromBatch) return false; const bb = st.batches.find((x) => x.id === st.fromBatch); return !!bb && bb.items.some((x, k) => k !== st.batchItem && x.st === 'recorded'); })();
    if (st.fromBatch && !marks) { S[4].cta = bNextReady ? 'Approve and watch next' : 'Approve, back to the batch'; S[4].ctaShort = bNextReady ? 'Approve, next' : 'Approve'; }
    const cur = S[st.step];
    const steps = S.map((s, i) => {
      const locked = i > D.max; const now = i === st.step; const done = (i < D.max && !(i === 3 && !D.recorded)) || (i === 5 && D.exported);
      return { name: s.name, sub: s.sub, cur: now ? 'step' : 'false', locked: locked, cls: 'stepbtn' + (now ? ' now' : '') + (locked ? ' locked' : ''), tip: locked ? 'Finish ' + S[D.max].name + ' first' : '', mark: done ? '✓' : String(i + 1), dotCls: 'stepdot' + (done ? ' done' : ''), go: () => { if (!locked) this.setState({ step: i, confirm: null, markOpen: false }); } };
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
    // Fine-tune folds into one line: which settings are off their recommended spot, or "All recommended for Alex".
    const offDefs = defs.filter((d) => v[d.k] !== rec[d.k]);
    const offWord = (d) => d.k === 'pace' ? 'pace ' + d.f(v.pace) : d.k === 'swear' ? 'swearing ' + ['off', 'once', 'a few times'][v.swear] : d.label.toLowerCase() + ' ' + d.f(v[d.k]).toLowerCase();
    const cap1 = (x) => x.charAt(0).toUpperCase() + x.slice(1);
    const fineLine = !offDefs.length ? 'All recommended for ' + voicePretty : offDefs.length === defs.length ? 'All ' + defs.length + ' changed from the recommended spot' : offDefs.length === 1 ? cap1(offWord(offDefs[0])) + ', the rest recommended' : offDefs.length + ' changed, the rest recommended';
    let line = (v.hes >= 1 ? 'Okay, cool. ' : '') + 'So first, ' + (v.hes >= 2 ? 'um, ' : '') + 'whop dot com slash start. ';
    line += v.casual >= 7 ? 'It kind of asks what you’re here for, so I’m gonna hit “I want a business”.' : 'It asks what you’re here for, so I’ll hit “I want a business”.';
    const caption = line;
    const sampleKey = voice + model + JSON.stringify(v);
    const sw = (on) => ({ cls: on ? 'sw on' : 'sw', onStr: on ? 'true' : 'false' });
    const warns = { email: 'Real people’s emails would be visible to anyone watching.', money: 'Showing earnings in marketing can count as a claim you have to back up.', customers: 'This is other people’s data. Only show it if it’s fake.' };
    const row = (id, label) => { const on = st.shown[id]; const s = sw(on); const w = on && warns[id]; return { id: 'pv-' + id, label: label, warn: w || '', hasWarn: !!w, cls: s.cls, onStr: s.onStr, toggle: () => { const m = Object.assign({}, this.state.shown); m[id] = !on; this.setState({ shown: m }); } }; };
    const addMark = (text) => { const t = st.revT; const i = secAt(t); const prev = D.notes; const at = this.fmt(t); const was = (prev[i] || []).some((m) => this.fmt(m.t) === at); const n = Object.assign({}, prev); n[i] = (prev[i] || []).filter((m) => this.fmt(m.t) !== at).concat([{ t: t, text: text }]); this.patchDemo({ notes: n }); this.setState({ markOpen: false, markOther: false, markDraft: '' }); this.focusLater('#markbtn'); if (!was) { this.say('Marked ' + at + ': ' + text); return; } this.say('Changed ' + at + ' to: ' + text, () => this.patchDemo({ notes: prev })); this.undoFrom = { id: 'markbtn', aria: '', text: '', tag: 'BUTTON' }; };
    const stopNow = () => { if (this.live) this.act('demo.stop', { demo: D.id }, { quiet: true }); this.stop('rec'); this.setState({ recStopped: true, recPaused: false, recSlide: 0, recSliding: false, toast: '', toastUndo: null, toastGo: null }); this.patchDemo({ status: 'Stopped at ' + st.recPos + ' of ' + N, dot: 'wait' }); this.focusLater('#reccarry'); };
    const goStep = (i) => { const p = { step: i, confirm: null, markOpen: false }; this.setState(p); if (D.max < i) this.patchDemo({ max: i }); };
    const doExport = () => { if (this.live) { this.setState({ confirm: null }); this.liveExport(D); return; } this.patchDemo({ exported: true, dirty: false, exportedOn: 'Nov 5', status: 'Exported Nov 5 · Open the video →', dot: 'done', max: 5 }); this.setState({ confirm: null }); this.focusAt = Date.now(); requestAnimationFrame(() => { const el = document.querySelector('.stepfoot .pri'); if (el) el.focus({ preventScroll: true }); }); this.say('Exported to Movies/NAVI'); };
    const primaryFor = [
      () => { if (this.live && !D.scriptApproved) { this.act('demo.approve_script', { demo: D.id }).then((r) => { if (r) goStep(1); }); return; } goStep(1); },
      () => { if (!voiceOk) { this.patchDemo({ model: vInfo.models[0] }); goStep(2); this.say('Switched to Eleven ' + vInfo.models[0] + ' for ' + voicePretty); return; } goStep(2); },
      () => { const fresh = this.live ? (!D.recorded && !D.recReq && D.max < 3) : (!D.recorded && st.recPos === 0 && !this.timers.rec); if (fresh) { if (this.needKey()) return; this.setState({ confirm: 'record' }); this.focusLater('#cfno'); return; } goStep(3); if (!D.recorded && !this.timers.rec) { if (this.needKey()) return; this.startRecording(st.recPos); this.focusLater('#recpause'); } },
      () => goStep(4),
      () => { if (marks) { this.setState({ confirm: 'redo' }); this.focusLater('#cfno'); return; } if (unsure) { this.setState({ confirm: 'approve' }); this.focusLater('#cfno'); return; } if (this.live) this.act('demo.approve_review', { demo: D.id }, { quiet: true }); if (st.fromBatch) { batchApproveNext(); return; } goStep(5); },
      () => { if (!D.exported || D.dirty) doExport(); else this.openFolder(D.exportFolder); }
    ];
    const secondaryFor = [null, null, null, () => { if (this.needKey()) return; this.setState({ confirm: 'rerecord' }); this.focusLater('#cfno'); }, () => { this.setState({ confirm: 'approve' }); this.focusLater('#cfno'); }, () => this.openFolder(D.exportFolder)];
    const confirms = {
      approve: { text: [marks ? this.plural(marks, 'mark') + ' kept, not redone' : '', unsure ? this.plural(unsure, 'blur') + ' not checked' : ''].filter(Boolean).join(', '), no: 'Go back', yes: 'Approve anyway', act: () => { if (this.live) this.act('demo.approve_review', { demo: D.id, anyway: true }, { quiet: true }); if (st.fromBatch) { this.setState({ confirm: null }); batchApproveNext(); } else goStep(5); } },
      record: { text: this.live ? 'The voice uses ' + this.num(videoCost) + ' credits' : 'Recording uses about ' + this.num(videoCost) + ' credits', no: 'Cancel', yes: 'Yes, record', act: () => { if (this.needKey()) return; this.setState({ confirm: null }); goStep(3); if (this.live) { this.liveRecord(D); return; } this.startRecording(0); } },
      rerecord: { text: 'Record again uses about ' + this.num(videoCost) + ' credits', no: 'Cancel', yes: 'Yes, record again', act: () => { if (this.needKey()) return; this.setState({ confirm: null }); if (this.live) { this.liveRecord(D, true); return; } this.patchDemo({ recorded: false }); this.startRecording(); } },
      redo: { text: 'Redo ' + this.plural(markedSecs.length, 'section') + ' for about ' + this.num(redoCost) + ' credits?', no: 'Cancel', yes: 'Redo them', act: () => { if (this.needKey()) return; if (this.live) { this.setState({ confirm: null }); this.liveRedo(D, markedSecs.map(Number)); return; } this.spend(markedSecs.length * 420); const prev = D.notes; this.patchDemo({ notes: {} }); this.setState({ confirm: null }); this.say('Redoing ' + this.plural(markedSecs.length, 'section') + '. Draft 2 will be here in a few minutes.'); } }
    };
    const batchApproveNext = () => { const bid = st.fromBatch; const bb = st.batches.find((x) => x.id === bid); if (!bb) return; const items = bb.items.map((x, k) => k === st.batchItem ? Object.assign({}, x, { st: 'approved' }) : x); this.patchBatch({ items: items }, bid); const next = items.findIndex((x) => x.st === 'recorded'); this.say('Approved “' + bb.items[st.batchItem].t + '”'); if (next >= 0) { const r = this.batchDemos(Object.assign({}, bb, { items: items }), next); this.setState({ demos: r.demos, cur: r.id, batchItem: next, revT: 0, markOpen: false, confirm: null }); this.focusLater('#playbtn'); } else this.setState({ screen: 'batch', fromBatch: null, batchItem: null, confirm: null }); };
    const cf = st.confirm ? confirms[st.confirm] : null;
    const pvFoot = { strict: 'Strict', standard: 'Standard', test: 'Test account', custom: 'Custom' }[preset];
    const footTexts = [
      D.written ? (D.max > 0 ? 'Looks right? Next: Voice. You can still change any line.' : 'Not approved yet. ' + this.secs.length + ' sections, about ' + lengthText) : 'Claude is writing the script',
      voiceOk ? voicePretty + (changed ? ', ' + changed + ' setting' + (changed === 1 ? '' : 's') + ' changed' : ', recommended for a ' + kindName) : voicePretty + ' needs Eleven ' + vInfo.models[0] + '. NAVI switches to it when you go on.',
      pvFoot + (D.recorded ? '' : (isPhone ? ' · about ' : ' · recording uses about ') + this.num(videoCost) + ' credits'),
      D.recorded ? 'Recorded, ' + lengthText : (st.recStopped ? 'Stopped. Finished sections are kept.' : (st.recPaused ? 'Paused. The draft is ready when recording finishes.' : 'The draft is ready when recording finishes.')),
      marks ? 'About ' + this.num(redoCost) + ' credits to redo.' : (unsure ? this.plural(unsure, 'blur') + ' to check' : 'Nothing marked'),
      D.exported ? (D.dirty ? 'Changed. Export again to update the files.' : 'Exported ' + (D.exportedOn || 'Nov 5') + ' · ' + this.plural(1 + ((D.capMode || 'burn') === 'file' ? 1 : 0) + 1 + (st.p720 ? 1 : 0), 'file')) : 'Saves to Movies/NAVI'
    ];
    const footBad = false;
    const footKinds = [D.written ? 'ready' : 'busy', 'ready', 'ready', D.recorded ? 'done' : (st.recPaused || st.recStopped ? 'wait' : 'busy'), 'ready', D.exported && !D.dirty ? 'done' : 'ready'];
    const foot = cf ? { text: cf.text, dot: 'ready', color: 'var(--ink)' } : { text: footTexts[st.step], dot: footBad ? 'bad' : footKinds[st.step], color: footBad ? 'var(--ink)' : 'var(--ink2)' };
    const wsw = (done) => done ? 'wnum done' : 'wnum';
    const l = sw(st.lock), p = sw(D.p720 != null ? !!D.p720 : st.p720), a = sw(st.caps);
    const dataDefs = [{ id: 'settings', n: 'Your saved choices', w: 'Voice, captions, corner label and privacy. Stored on this Mac. You can undo a reset.', l: 'Reset to defaults' }, { id: 'videos', n: 'Finished videos', w: 'Movies/NAVI. Never deleted from here.', l: 'Open folder' }];
    const dataAct = {
      logins: () => { const prev = st.sites; if (this.live) prev.forEach((x) => this.deferred('site:' + x.u + '/' + (x.seat || ''), () => this.act('login.forget', { site: x.u, seat: x.seat }, { quiet: true }))); this.setState({ sites: [] }); this.focusAt = Date.now(); requestAnimationFrame(() => { const el = document.getElementById('logins-h'); if (el) el.focus({ preventScroll: true }); }); this.say('All saved logins forgotten', () => { prev.forEach((x) => { if (this.pending && this.pending['site:' + x.u + '/' + (x.seat || '')]) { clearTimeout(this.pending['site:' + x.u + '/' + (x.seat || '')].t); delete this.pending['site:' + x.u + '/' + (x.seat || '')]; } }); this.setState({ sites: prev }); }); },
      videos: () => this.openFolder(),
      settings: () => { if (this.live) { const cancel = this.deferred('settings', () => this.act('data.plan_delete', { what: 'settings' }, { quiet: true }).then((r) => r && r.token && this.act('data.confirm_delete', { token: r.token }, { quiet: true }))); this.say('Settings reset', cancel); return; } const prev = { vals: st.vals, hide: st.hide, shown: st.shown, defVoice: st.defVoice, defCap: st.defCap, defCorner: st.defCorner, defCornerText: st.defCornerText }; this.setState({ vals: Object.assign({}, this.presetVals.course), hide: [], shown: Object.assign({}, PRESETS.standard), defVoice: 'alex', defCap: 'burn', defCorner: 'off', defCornerText: '' }); this.say('Settings reset', () => this.setState(prev)); }
    };
    const keyMsg = { empty: 'Paste the key first.', checking: 'Checking…', ok: 'Works. ' + this.num(st.credits) + ' credits left.', bad: 'ElevenLabs didn’t accept this key. Check you copied all of it.', offline: 'Couldn’t reach ElevenLabs. Check your internet and try again.' }[st.keyRes] || '';
    const chatClean = (m) => { let s = m.replace(/^(actually|no|ok|okay|wait)[,!.\s]*/i, '').replace(/^(make|do|change)( it| this)?( into)?( a)? demo (of|for|on|about)\s*/i, '').replace(/\s*instead[.!]*$/i, ''); return s.charAt(0).toUpperCase() + s.slice(1); };
    const segOf = (opts, cur2, fn) => opts.map((o) => ({ label: o[1], on: cur2 === o[0] ? 'true' : 'false', pick: () => fn(o[0]) }));
    const capOpts = [['burn', 'In the video'], ['file', 'Separate file'], ['off', 'Off']];
    const posOpts = [['off', 'Off'], ['tl', 'Top left'], ['tr', 'Top right'], ['bl', 'Bottom left'], ['br', 'Bottom right']];
    const capName = { burn: 'burned in', file: 'as a separate file', off: 'off' };
    const cornerCtl = (cur2, set, fid) => { const on = cur2 !== 'off'; return { on: on, onStr: on ? 'true' : 'false', cls: on ? 'sw on' : 'sw', toggle: () => { set(on ? 'off' : (this.lastCorner || 'tr')); if (!on && fid) requestAnimationFrame(() => { const el = document.getElementById(fid); if (el) el.focus(); }); }, seg: [['tl', 'Top left'], ['tr', 'Top right'], ['bl', 'Bottom left'], ['br', 'Bottom right']].map((o) => ({ k: o[0], label: o[1], on: cur2 === o[0] ? 'true' : 'false', pick: () => { this.lastCorner = o[0]; set(o[0]); } })), pickVal: (e) => { const k = e.target.value; this.lastCorner = k; set(k); } }; };
    const posCss = { tl: 'left: 14px; top: 14px', tr: 'right: 14px; top: 14px', bl: 'left: 14px; bottom: 14px', br: 'right: 14px; bottom: 14px' };
    const dCap = D.capMode || 'burn'; const dCorner = D.corner || 'off'; const dCornerText = D.cornerText || ''; const dP720 = D.p720 != null ? !!D.p720 : st.p720;
    const speedOk = (x) => /^\d+(\.\d+)?$/.test(String(x).trim()) && Number(x) >= 1.05 && Number(x) <= 2;
    const base = D.title.replace(/…$/, '');
    // ---- new demo ----
    const loginNote = (s) => [({ working: 'Working', checking: 'Checking…', 'needs login': 'Needs login', unreachable: 'Couldn’t reach the site', unchecked: 'Not checked yet' }[s.status] || (s.note || '')) + (s.ago && s.status !== 'checking' ? ', checked ' + s.ago : ''), s.biz ? 'Opens ' + s.biz : ''].filter(Boolean).join(' · ');
    const siteOk = (u) => /^[a-z0-9-]+(\.[a-z0-9-]+)+(\/.*)?$/i.test((u || '').trim().replace(/^https?:\/\//i, ''));
    const lenOpts = [1, 3, 5, 8];
    const suggestLen = (() => { const w = st.bWhat.trim(); if (!w) return -1; const n = 1 + (w.match(/,| then | and /gi) || []).length; const mins = Math.max(1, n + (st.bWho === 0 ? 1 : st.bWho === 2 ? -1 : 0)); let best = 0; lenOpts.forEach((o, i) => { if (Math.abs(o - mins) < Math.abs(lenOpts[best] - mins)) best = i; }); return best; })();
    const bSiteVal = st.bSiteNew ? st.bNew.trim() : st.bSite;
    const posName = { tl: 'top left', tr: 'top right', bl: 'bottom left', br: 'bottom right' };
    const kindLabel = { course: 'walkthrough', saas: 'quick demo', tour: 'product tour' };
    const nb = (x) => x.replace(/ /g, '\u00a0');
    const summaryParts = [['Beginners', 'Some experience', 'Pros'][st.bWho], kindLabel[st.bKind].charAt(0).toUpperCase() + kindLabel[st.bKind].slice(1), lenOpts[st.bLen] + ' min' + (st.bLen === suggestLen ? ' (suggested)' : ''), pretty(st.bVoice), { burn: 'Captions on', file: 'Captions as a file', off: 'No captions' }[st.bCap]].map(nb).concat(st.bCorner === 'off' ? [] : ['Label' + (st.bCornerText.trim() ? ': ' + st.bCornerText.trim() + ', ' : '\u00a0') + nb(posName[st.bCorner])]);
    if (st.bHide.trim()) summaryParts.push('keep\u00a0“' + st.bHide.trim() + '”\u00a0off\u00a0screen');
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
    const stLabel = { writing: 'Writing script', script: 'Script ready', waiting: 'Waiting', recording: 'Recording now', recorded: 'Ready to watch', approved: 'Approved', exported: 'Exported', skipped: 'Skipped', pick: 'Pick A, B or C' };
    const bReady = cnt('recorded');
    const stDot = { writing: 'busy', script: 'ready', waiting: 'wait', recording: 'busy', recorded: 'ready', approved: 'done', exported: 'done', skipped: 'bad', pick: 'ready' };
    const costOf = (x) => B && B.engine ? (x.cost || 0) : this.perVideo(x.min);
    // the Go screen (Andy, 11 Nov 2026): every video's seat and cost, the logins the batch needs, the total, then Go
    const goLogins = B && B.stage === 'approve' ? (B.logins || []).map((l) => ({ text: l.label + ': ' + ({ working: 'working', checking: 'checking…', 'needs login': 'needs a login first', unreachable: 'couldn’t reach the site', unchecked: 'not checked yet' }[l.status] || l.status), dot: { working: 'k-done', checking: 'k-busy', 'needs login': 'k-bad' }[l.status] || 'k-wait', needs: l.status === 'needs login', login: () => { if (this.live) this.act('login.start', { url: l.home, seat: l.seat }, { quiet: true }); this.say('A browser opens on ' + l.site + '. Log in, then close it.'); } })) : [];
    const goTotal = bItems.filter((x) => x.st === 'script' || x.st === 'waiting').reduce((s, x) => s + costOf(x), 0);
    const goLimit = st.creditLimit || 10000;
    const goCost = 'About ' + this.num(goTotal) + ' credits · ' + this.num(st.credits) + ' left · your limit ' + this.num(goLimit) + (goTotal > goLimit ? '. That’s over your limit: Go asks first.' : '');
    const bStageIdx = B ? ({ writing: 0, approve: 1, recording: 2, review: 3, done: 4 }[B.stage]) : 0;
    const nowIdx = bStageIdx === 2 && bReady > 0 ? 3 : bStageIdx;
    const bStages = [['Write scripts', B && B.stage === 'writing' ? 'Writing…' : 'Done'], ['Approve scripts', bStageIdx > 1 ? 'Done' : bStageIdx === 1 ? cnt('script') + ' to read' : 'Not yet'], ['Record', bStageIdx < 2 ? 'Not yet' : bRecorded + ' of ' + bItems.length + ' recorded'], ['Review', bStageIdx < 2 ? 'Not yet' : (bReady ? bReady + ' ready to watch' : (bApproved + bExported) + ' approved')], ['Export', bExported ? bExported + ' exported' : (bApproved ? bApproved + ' approved' : 'Not yet')]].map((o, i) => { const done = i < Math.min(bStageIdx, 2) || (i === 2 && bRecorded === bItems.length && bItems.length > 0) || (i === 4 && bExported === bItems.length && bItems.length > 0); const now = i === nowIdx; return { n: o[0], sub: o[1], now: now, busy: i === 2 && B && B.stage === 'recording' && !B.paused && !now, cls: 'stepbtn' + (now ? ' now' : '') + (!done && !now && i > Math.max(bStageIdx, nowIdx) && !(i === 4 && bApproved > 0) ? ' locked' : ''), dotCls: 'stepdot' + (done ? ' done' : ''), mark: done ? '✓' : String(i + 1) }; });
    const recIdx = bItems.findIndex((x) => x.st === 'recording');
    // The list shows a fixed window of 7 rows that always holds the recording row and the one after it, so the page never grows as videos finish and Watch next stays clear of the chat bar.
    const bCollapse = bItems.length > 10 && !st.btAll; const bAnchor = recIdx >= 0 ? recIdx : bItems.findIndex((x) => x.st === 'waiting') >= 0 ? bItems.findIndex((x) => x.st === 'waiting') : bItems.findIndex((x) => x.st === 'recorded'); const bStart = !bCollapse ? 0 : Math.max(0, Math.min(bItems.length - 6, bAnchor - 5)); const bEnd = bCollapse ? bStart + (bStart > 0 ? 6 : 7) : bItems.length;
    // When the window starts later in the list, its first slot sums up the rows above it ("✓ 2 approved"), so the list never seems to start at #3.
    const bAbove = bItems.slice(0, bStart); const bAboveText = ['approved', 'exported', 'recorded'].map((k) => { const n = bAbove.filter((x) => x.st === k).length; return n ? n + ' ' + { approved: 'approved', exported: 'exported', recorded: 'ready to watch' }[k] : ''; }).filter(Boolean).join(' · '); const hLeft = Math.max(1, Math.round(bLeftMin / 60));
    const bHead = !B ? '' : B.stage === 'writing' ? 'Claude is writing ' + this.plural(bItems.length, 'script') + '.' : B.stage === 'approve' ? this.plural(cnt('script'), 'script') + ' ready.' : B.stage === 'done' ? 'All ' + bItems.length + ' exported.' : (bReady ? bReady + ' ready to watch.' : 'None ready to watch yet.');
    const bSub = !B ? '' : B.stage === 'writing' && B.paused ? 'Paused while writing the scripts. Resume?' : B.stage === 'writing' ? 'Takes about a minute per script. Nothing records until you press Go.' : B.stage === 'approve' ? 'Open any script to read or change it. Go checks every login first, then records them all without asking you anything.' : B.paused ? (B.runner && B.runner.line ? B.runner.line.charAt(0).toUpperCase() + B.runner.line.slice(1) : 'Paused at video ' + ((recIdx >= 0 ? recIdx : Math.max(0, bItems.findIndex((x) => x.st === 'waiting'))) + 1) + ' of ' + bItems.length) + '. Resume?' : B.stage === 'recording' ? (recIdx >= 0 ? 'Recording #' + (recIdx + 1) + ' now, about\u00a0' + hLeft + '\u00a0h\u00a0left. ' : '') + (B.engine ? 'NAVI keeps your Mac awake while it works, and carries on if you close this window.' : 'Keep your Mac on.') : B.stage === 'done' ? '' : 'Approved videos can be exported any time.';
    const bCreditNote = B && B.paused === 'credits' ? 'Paused: the next video needs about ' + this.num(this.perVideo((bToRecord[0] || { min: 3 }).min)) + ' credits. Add credits at ElevenLabs, then resume.' : B && B.stage === 'recording' && bFits < bToRecord.length ? 'You have ' + this.num(st.credits) + ' credits, enough for about ' + this.plural(bFits, 'more video') + (B.engine ? '. Videos after that are skipped, and the morning report says so.' : '. Recording pauses there until you add credits.') : '';
    const watchItem = (i) => { if (this.live && B.items[i].did) { const d = this.state.demos.find((x) => x.id === B.items[i].did); this.setState({ screen: 'demo', cur: B.items[i].did, step: 4, markOpen: false, confirm: null, fromBatch: B.id, batchItem: i, revT: 0, player: false }); if (d) this.syncDemoLocal(d); return; } const r = this.batchDemos(B, i); this.setState({ demos: r.demos, screen: 'demo', cur: r.id, step: 4, markOpen: false, confirm: null, fromBatch: B.id, batchItem: i, revT: 0, player: false, vals: this.recFor(B.voice, B.kind) }); };
    const approveItem = (i) => { if (this.live && B.items[i].did) this.act('demo.approve_review', { demo: B.items[i].did }, { quiet: true }); const prev = B.items; const items = B.items.map((x, k) => k === i ? Object.assign({}, x, { st: 'approved' }) : x); this.patchBatch({ items: items }); this.say('Approved “' + B.items[i].t + '”', () => this.patchBatch({ items: prev })); };
    let bPrimary = !B ? { label: '', act: () => {}, off: true } : B.stage === 'writing' ? { label: 'Approve all scripts', off: true, act: () => {} } : B.stage === 'approve' ? { label: 'Go', off: goLogins.some((l) => l.needs), act: () => { if (this.needKey()) return; this.setState({ bConfirm: true }); this.focusLater('#bcfno'); }, start: () => { if (this.needKey()) return; if (this.live) { this.setState({ bConfirm: false }); this.act('batch.go', { batch: B.id }, { ok: 'Go: checking the logins and pages, then recording ' + this.plural(B.items.length, 'video') + ', one after another.' }); return; } const items = B.items.map((x, k) => Object.assign({}, x, { st: k === 0 ? 'recording' : 'waiting' })); this.setState({ bConfirm: false }); this.patchBatch({ items: items, stage: 'recording', paused: false }); this.runBatch(); this.focusLater('#batch-h'); this.say('Recording ' + this.plural(items.length, 'video') + ', one after another'); } } : { label: bApproved ? 'Export ' + this.plural(bApproved, 'approved video') : 'Export approved videos', off: !bApproved, act: () => { if (this.live) { this.act('batch.export', { batch: B.id }, { ok: 'Sent to Claude. Exporting ' + this.plural(bApproved, 'video') + ' and the list file.' }); return; } const n = bApproved; const items = B.items.map((x) => x.st === 'approved' ? Object.assign({}, x, { st: 'exported' }) : x); const done = items.every((x) => x.st === 'exported'); this.patchBatch({ items: items, stage: done ? 'done' : B.stage }); this.focusLater(() => { const p = document.querySelector('.bprimary'); return done || !p || p.getAttribute('aria-disabled') === 'true' ? document.getElementById('batch-h') : p; }); this.say('Exported ' + this.plural(n, 'video') + ' and the list file to ' + B.folder.replace(/^~\/Movies\//, 'Movies/')); } };
    const bAllCost = bItems.reduce((s, x) => s + this.perVideo(x.min), 0); const bAllFits = (() => { let c = st.credits, n = 0; for (const x of bItems) { const k = this.perVideo(x.min); if (c < k) break; c -= k; n++; } return n; })();
    const bConfirmText = B && B.engine ? 'Go checks every login and page first, then records ' + this.plural(bItems.length, 'video') + ' one after another, about ' + this.num(goTotal) + ' credits. It won’t ask you anything until the morning report.' : 'Recording ' + this.plural(bItems.length, 'video') + ' uses about ' + this.num(bAllCost) + ' credits' + (bAllFits < bItems.length ? '. It pauses after ' + bAllFits + ' until you add credits.' : '');
    const bStartAll = bPrimary.start || (() => {});
    const exportAct = bPrimary.act; const exportLabel = bPrimary.label; const exportOff = bPrimary.off;
    const firstReady = bItems.findIndex((x) => x.st === 'recorded');
    let bSecondary = null;
    if (B && (B.stage === 'recording' || B.stage === 'review')) { bSecondary = { label: exportLabel, act: exportAct, off: exportOff }; bPrimary = { label: firstReady >= 0 ? 'Watch #' + (firstReady + 1) : 'Watch next', off: firstReady < 0, act: () => { if (firstReady >= 0) watchItem(firstReady); } }; }
    const bPauseObj = B && B.stage === 'recording' ? (B.paused ? { label: 'Resume recording', act: () => { const w = B.items.findIndex((x) => x.st === 'waiting'); const has = B.items.some((x) => x.st === 'recording'); if (!has && w >= 0 && this.state.credits < this.perVideo(B.items[w].min)) { this.say('Batch paused: not enough credits for the next video'); return; } const items = has || w < 0 ? B.items : B.items.map((x, k) => k === w ? Object.assign({}, x, { st: 'recording' }) : x); if (this.live) { this.act('batch.resume', { batch: B.id }, { ok: 'Carrying on from where it stopped.' }); this.patchBatch({ paused: false }); return; } this.patchBatch({ items: items, paused: false }); if (/^Paused\./.test(this.state.toast)) this.setState({ toast: '', toastUndo: null, toastGo: null }); this.runBatch(); } } : { label: 'Pause recording', act: () => { if (this.live) { this.act('batch.pause', { batch: B.id }, { ok: 'Paused. Everything made so far is kept.' }); this.patchBatch({ paused: true }); return; } this.patchBatch({ paused: true }); this.say('Paused. The video being recorded finishes first.'); } }) : (B && B.stage === 'writing' && B.paused ? { label: 'Resume', act: () => { if (this.live) this.act('batch.resume', { batch: B.id }, { ok: 'Carrying on from where it stopped.' }); this.patchBatch({ paused: false }); } } : null);
    // ---- blind A/B/C picks (Andy, 12 Nov 2026): the plans, and the first videos' versions, by letter only ----
    const bl = (B && B.blind) || { lessons: {}, plan: null, revealed: null };
    const planWaiting = !!(bl.plan && bl.plan.status === 'waiting');
    const pickIdx = bItems.findIndex((x) => x.st === 'pick');
    const pickSel = planWaiting ? 'plan' : (typeof st.pickOpen === 'number' && bItems[st.pickOpen] && bItems[st.pickOpen].st === 'pick' ? st.pickOpen : null);
    const lessonAt = (i) => bl.lessons[bItems[i].did || i] || { options: [] };
    const openPick = (i) => { this.pickStop(); this.setState({ pickOpen: i, pickRead: '', liveOpen: false }); this.focusLater('#bpick-h'); };
    const mmss = (s) => Math.floor(s / 60) + ':' + String(Math.round(s % 60)).padStart(2, '0');
    const doPick = (letter) => {
      this.pickStop();
      if (pickSel === 'plan') {
        if (this.live) this.act('blind.pick_plan', { batch: B.id, letter: letter }, { quiet: false });
        this.patchBatch({ blind: Object.assign({}, bl, { plan: Object.assign({}, bl.plan, { status: 'picked', picked: letter }) }) }); this.setState({ pickOpen: null, pickRead: '' });
        this.say('Plan ' + letter + ' picked. The scripts are being written now.'); this.focusLater('#batch-h'); return;
      }
      const i = pickSel; const it = bItems[i]; const key = it.did || i;
      if (this.live) this.act('blind.pick', { batch: B.id, demo: it.did, letter: letter }, { quiet: false });
      const lessons = Object.assign({}, bl.lessons); lessons[key] = Object.assign({}, lessons[key], { status: 'picked', picked: letter });
      const items = B.items.map((x, k) => k === i ? Object.assign({}, x, { st: 'waiting' }) : x);
      const next = items.findIndex((x) => x.st === 'pick');
      this.patchBatch({ items: items, blind: Object.assign({}, bl, { lessons: lessons }) }); this.setState({ pickOpen: next >= 0 ? next : null, pickRead: '' });
      this.say('Version ' + letter + ' picked for “' + it.t + '”. It records next.'); this.focusLater(next >= 0 ? '#bpick-h' : '#batch-h');
    };
    const pickOptions = pickSel == null ? [] : (pickSel === 'plan' ? bl.plan.options.map((o) => ({ letter: o.letter, meta: this.plural(o.videos.length, 'video'), audio: null, all: o.videos.map((v, k) => (k + 1) + '. ' + v.t + (v.goal ? ': ' + v.goal : '')), few: 4 }))
      : lessonAt(pickSel).options.map((o) => ({ letter: o.letter, meta: o.seconds ? mmss(o.seconds) : '', audio: o.audio, secs: o.seconds, all: o.lines, few: 1 }))).map((o) => {
      const key = pickSel + '/' + o.letter; const open = st.pickRead === o.letter; const playing = st.pickPlaying === key;
      return { letter: o.letter, meta: o.meta, hasAudio: o.audio !== null, playLabel: playing ? 'Pause' : 'Play', playAria: (playing ? 'Pause version ' : 'Play version ') + o.letter, pct: (playing ? Math.round(st.pickPos * 100) : 0) + '%',
        play: () => this.pickPlay(key, o.audio, o.secs), lines: open ? o.all : o.all.slice(0, o.few), hasMore: o.all.length > o.few, openStr: open ? 'true' : 'false', moreLabel: open ? 'Show less' : (pickSel === 'plan' ? 'Read the whole plan' : 'Read the script'),
        toggle: () => this.setState({ pickRead: open ? '' : o.letter }), pickLabel: 'Pick ' + o.letter, pick: () => doPick(o.letter) };
    });
    const pickLeft = bItems.filter((x) => x.st === 'pick').length;
    if (B && pickIdx >= 0 && pickSel == null) bPrimary = { label: 'Listen to #' + (pickIdx + 1), off: false, act: () => openPick(pickIdx) };
    const rev = bl.revealed; const armName = (a) => String(a).replace(' / ', ', ');
    const bReveal = rev ? rev.picks.map((p) => (p.kind === 'planning' ? 'The plan' : '“' + p.title + '”') + ': you picked ' + p.picked_letter + ', which was ' + armName(p.picked)).concat(Object.keys(rev.tally || {}).map((k) => (k === 'planning' ? 'Plans: ' : 'Scripts: ') + rev.tally[k].map((r) => armName(r.arm) + ' picked ' + r.picked + ' of ' + r.shown).join(' · '))) : [];
    const scrKey = st.screen === 'demo' ? ['script', 'voice', 'privacy', 'record', 'review', 'export'][st.step] : st.screen === 'new' ? (st.mode === 'batch' && !st.editing ? 'new-batch' : 'new') : st.screen;
    const tipHover = (e) => { if (this.scrubbing || e.pointerType === 'touch') return; const r = e.currentTarget.getBoundingClientRect(); let best = null; this.starts.forEach((s, i) => { if (!i) return; const x = r.left + s / this.total * r.width; if (Math.abs(e.clientX - x) <= 8 && (best == null || Math.abs(e.clientX - x) < Math.abs(e.clientX - (r.left + this.starts[best] / this.total * r.width)))) best = i; }); if (best !== this.state.tipSec) this.setState({ tipSec: best }); };
    return {
      themeClass: (theme === 'dark' ? 't-dark' : 't-light') + (W2_OFF.indexOf(scrKey) < 0 ? ' w2' : ''), scrKey: scrKey, isDark: theme === 'dark', isLight: theme !== 'dark', themeAria: theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode', toggleTheme: () => this.setState({ theme: theme === 'dark' ? 'light' : 'dark' }),
      isWelcome: st.screen === 'welcome', inApp: st.screen !== 'welcome', isHome: st.screen === 'home', isDemo: st.screen === 'demo', isSettings: st.screen === 'settings', isNew: st.screen === 'new', isBatch: st.screen === 'batch',
      crumb: st.screen !== 'home', crumbBatch: st.screen === 'demo' && !!st.fromBatch, crumbBatchName: st.fromBatch ? (st.batches.find((x) => x.id === st.fromBatch) || {}).name : '', goBatch: () => this.setState({ screen: 'batch', fromBatch: null, batchItem: null }), crumbText: st.screen === 'demo' ? (st.fromBatch && B ? (B.items[st.batchItem] || {}).t : D.title) : st.screen === 'batch' ? (B ? B.name : '') : st.screen === 'new' ? (st.editing ? 'Edit brief' : st.mode === 'batch' ? 'New batch' : 'New demo') : 'Settings',
      showNewBtn: false, isPhone: isPhone,
      goHome: () => this.setState({ screen: 'home', help: false, confirm: null }), phoneBackLabel: st.screen === 'demo' && st.fromBatch ? 'Back to the batch' : 'All demos', phoneBack: () => { if (st.screen === 'demo' && st.fromBatch) { const i = st.batchItem; this.setState({ fromBatch: null, batchItem: null, markOpen: false }); this.openBatch(st.fromBatch); this.focusLater('#bwatch-' + i); return; } this.setState({ screen: 'home', help: false, confirm: null }); }, goSettings: () => this.setState({ screen: 'settings', help: false }),
      helpOpen: st.help, toggleHelp: () => { const was = st.help; this.setState({ help: !was }); this.focusLater(was ? '#helpbtn' : '#helpok'); },
      keyOn: st.keyOn, keyOff: !st.keyOn, creditsText: this.num(st.credits),  creditPct: (st.credits / 30000 * 100) + '%',
      homeSub: st.demos.some((d) => !d.batchOf) || st.batches.length ? 'Open one to carry on, or start a new one.' : 'Start a new demo or batch.',
      demos: st.demos.filter((d) => !d.batchOf).map((d) => ({ cid: 'card-d-' + d.id, delAria: 'Delete ' + d.title, del: () => this.deleteCard('d', d.id), tint: d.tint || '', title: d.title, meta: d.site + ' · ' + pretty(d.voice), status: isPhone ? d.status.replace(' · Open the video →', ' · Open →') : d.status, dot: d.dot, cover: d.cover, open: () => { const s = d.exported ? 5 : Math.min(d.max, d.recorded ? 4 : d.max); this.setState({ screen: 'demo', cur: d.id, step: s, confirm: null, markOpen: false, scSel: 0, vals: this.recFor(d.voice, d.kind) }); if (this.live) this.syncDemoLocal(this.demo()); } })),
      batchCards: st.batches.map((b) => { const r = b.items.filter((x) => ['recorded', 'approved', 'exported'].indexOf(x.st) >= 0).length; const rd = b.items.filter((x) => x.st === 'recorded').length; return { cid: 'card-b-' + b.id, delAria: 'Delete ' + b.name, del: () => this.deleteCard('b', b.id), next: b.blind && b.blind.plan && b.blind.plan.status === 'waiting' ? 'Pick a plan →' : b.items.some((x) => x.st === 'pick') ? 'Listen and pick →' : b.paused ? 'Resume →' : b.stage === 'approve' ? 'Approve the scripts →' : rd ? rd + ' ready to watch →' : 'See progress →', name: b.name, meta: 'Batch · ' + b.items.length + ' videos · ' + b.site, status: b.stage === 'writing' ? 'Writing scripts' : b.stage === 'approve' ? 'Scripts to approve' : b.paused ? (b.runner && b.runner.line ? b.runner.line.charAt(0).toUpperCase() + b.runner.line.slice(1) : 'Paused, ' + r + ' of ' + b.items.length) : b.stage === 'done' ? 'All exported' : r + ' of ' + b.items.length + ' recorded', pct: (r / b.items.length * 100) + '%', open: () => this.openBatch(b.id) }; }),
      defNamePretty: pretty(st.defVoice), defImg: VO[st.defVoice].img, defC: VO[st.defVoice].c, defName: VO[st.defVoice].name,
      keyDot: st.keyOn ? 'done' : 'bad', keyStatus: st.keyOn ? 'ElevenLabs connected' : 'ElevenLabs not connected', keyAction: st.keyOn ? 'Change' : 'Connect',
      toolsDot: st.tools === 'done' ? 'done' : 'bad', setupDot: st.keyOn && st.tools === 'done' ? 'done' : 'bad', setupShort: st.keyOn && st.tools === 'done' ? 'All set' : (!st.keyOn ? 'ElevenLabs not connected' : 'Recording tools not installed'), toolsStatus: st.tools === 'done' ? 'Recording tools ready' : 'Recording tools not installed', toolsReady: st.tools === 'done' ? 'Ready' : 'Not installed',
      sitesStatus: st.sites.length ? this.plural(st.sites.length, 'saved login') : 'No saved logins',
      demoTitle: D.title, briefLine: D.site + ', about ' + (D.written ? Math.max(1, Math.round(this.total / 60)) : ['1', '3', '5', '8'][D.len]) + ' min', demoCover: D.cover,
      // ---- new demo ----
      newBatch: () => { requestAnimationFrame(() => { const el = document.getElementById('btt'); if (el) el.focus(); }); this.setState({ screen: 'new', mode: 'batch', editing: false, help: false, btSite: st.sites[0] ? st.sites[0].u : '', btSiteNew: false, btNew: '', btVoice: st.defVoice }); },
      newDemo: () => { requestAnimationFrame(() => { const el = document.getElementById('bw'); if (el) el.focus(); }); this.setState({ screen: 'new', mode: 'one', bKind: 'course', bMore: false, editing: false, bCap: st.defCap, bCorner: st.defCorner, bCornerText: st.defCornerText, bWhat: '', bNew: '', bSiteNew: false, bHide: '', bSite: st.sites[0] ? st.sites[0].u : '', bVoice: st.defVoice, bWho: 0, bLen: 2, help: false, btSite: st.sites[0] ? st.sites[0].u : '', btVoice: st.defVoice }); },
      editBrief: () => (st.step === 3 && !D.recorded && !st.recStopped) ? null : this.setState({ screen: 'new', mode: 'one', bMore: false, editing: true, bWhat: D.what || 'How to build a course in Whop, from creating the whop to checking it on a phone', bSite: D.site, bSiteNew: false, bNew: '', bWho: D.who, bLen: D.len, bVoice: D.voice, bCap: dCap, bCorner: dCorner, bCornerText: dCornerText }),
      newTitle: st.editing ? 'Edit the brief' : st.mode === 'batch' ? 'New batch' : 'New demo', batchExplain: st.mode === 'batch' && !st.editing, briefCta: st.editing ? 'Update the script' : 'Write the script',
      briefHint: st.editing ? 'Claude only rewrites what changed.' : 'Claude writes it in about a minute.',
      showModeSwitch: !st.editing, modeOne: st.mode === 'one', modeBatch: st.mode === 'batch',
      modes: segOf([['one', 'One demo'], ['batch', 'A batch']], st.mode, (x) => this.setState({ mode: x })),
      bWhat: st.bWhat, onBWhat: (e) => this.setState({ bWhat: e.target.value }), bHide: st.bHide, onBHide: (e) => this.setState({ bHide: e.target.value }), bNew: st.bNew, onBNew: (e) => this.setState({ bNew: e.target.value }),
      briefEmpty: !st.bWhat.trim() || (st.bSiteNew && !/^[a-z0-9-]+(\.[a-z0-9-]+)+(\/.*)?$/i.test(st.bNew.trim().replace(/^https?:\/\//i, ''))),
      briefWhy: !st.bWhat.trim() ? 'Type what the demo should show.' : (st.bSiteNew && !/^[a-z0-9-]+(\.[a-z0-9-]+)+(\/.*)?$/i.test(st.bNew.trim().replace(/^https?:\/\//i, '')) ? (st.bNew.trim() ? 'Fix the new site’s address first.' : 'Type the new site’s address first.') : ''),
      bSites: st.sites.filter((s, i, a) => a.findIndex((x) => x.u === s.u) === i).map((s) => ({ label: s.u, on: !st.bSiteNew && st.bSite === s.u ? 'true' : 'false', pick: () => this.setState({ bSite: s.u, bSiteNew: false }) })),
      openBNew: () => { if (st.bSiteNew) { this.setState({ bSiteNew: false, bNew: '' }); this.focusLater('#bnewchip'); return; } this.setState({ bSiteNew: true }); requestAnimationFrame(() => { const el = document.getElementById('bns'); if (el) el.focus(); }); }, closeBNew: () => this.setState({ bSiteNew: false, bNew: '' }),
      bSiteNew: st.bSiteNew, bNewBad: st.bSiteNew && !!st.bNew.trim() && !/^[a-z0-9-]+(\.[a-z0-9-]+)+(\/.*)?$/i.test(st.bNew.trim().replace(/^https?:\/\//i, '')), 
      bSummary: 'Using: ' + summaryParts.join(' · '), bSummaryShort: summaryParts.join('\u00a0· '), bSumList: summaryParts, bMore: st.bMore, bLess: !st.bMore, toggleMore: () => this.setState({ bMore: !st.bMore }),
      bKinds: segOf([['course', 'Walkthrough'], ['saas', 'Quick demo'], ['tour', 'Product tour']], st.bKind, (x) => this.setState({ bKind: x })).map((o, i) => Object.assign(o, { short: ['Course', 'SaaS', 'Tour'][i], ph: ['Walkthrough', 'Quick demo', 'Product tour'][i] })), bKindHint: { course: 'Step by step, at a teaching pace.', saas: 'Short and lively, for a product page.', tour: 'A calm look around the main screens.' }[st.bKind],
      bWho: ['Beginners', 'Some experience', 'Pros'].map((s, i) => ({ label: s, on: st.bWho === i ? 'true' : 'false', pick: () => this.setState({ bWho: i }) })),
      bLen: ['1 min', '3 min', '5 min', '8 min'].map((s, i) => ({ label: s, star: false, on: st.bLen === i ? 'true' : 'false', pick: () => this.setState({ bLen: i }) })),
      bVoices: st.mine.map((k) => ({ label: pretty(k), on: st.bVoice === k ? 'true' : 'false', pick: () => this.setState({ bVoice: k }) })),
      bCaps: segOf(capOpts, st.bCap, (x) => this.setState({ bCap: x })).map((o, i) => Object.assign(o, { short: ['In video', 'File', 'Off'][i] })),
      bCorner: cornerCtl(st.bCorner, (x) => this.setState({ bCorner: x }), 'bct'),
      bCornerText: st.bCornerText, onBCornerText: (e) => this.setState({ bCornerText: e.target.value }), bCornerOff: st.bCorner === 'off',
      bCornerPh: 'Text for the corner, e.g. your brand name',
      lenHint: suggestLen < 0 ? lenOpts[st.bLen] + ' min for now. Claude suggests a length once you say what to show.' : 'Claude suggests ' + lenOpts[suggestLen] + ' min for what you typed. Your pick wins.',
      cancelBrief: () => this.setState({ screen: st.editing ? 'demo' : 'home' }),
      submitBrief: () => {
        const w = st.bWhat.trim(); if (!w) { this.focusLater('#bw'); return; } if (st.bSiteNew && !siteOk(st.bNew)) { this.focusLater('#bns'); return; } const site = bSiteVal || 'whop.com'; if (!site) return; const t = w.length > 34 ? w.slice(0, 32).replace(/\s+\S*$/, '') + '…' : w;
        const newSite = !st.sites.some((s) => s.u === site);
        if (this.live) { const f = { title: t, what: w, site: site, kind: st.bKind, len: st.bLen, who: st.bWho, voice: st.bVoice, cap: st.bCap, corner: st.bCorner, cornerText: st.bCornerText, hide: st.bHide.trim() }; if (st.editing) this.liveEditBrief(D, f); else this.liveNewDemo(f); return; }
        if (st.editing) { this.patchDemo({ title: t, what: w, site: site, who: st.bWho, len: st.bLen, voice: st.bVoice, capMode: st.bCap, corner: st.bCorner, cornerText: st.bCornerText, written: false }); this.setState({ screen: 'demo', step: 0, sites: newSite ? st.sites.concat([{ u: site, note: 'Saved Nov 5' }]) : st.sites }); this.later('write', 2200, () => { this.patchDemo({ written: true }); this.say('Script updated'); }); this.say('Updating the script'); return; }
        const id = 'd' + Date.now();
        const d = { id: id, title: t, what: w, site: site, len: st.bLen, who: st.bWho, voice: st.bVoice, model: 'v4', kind: st.bKind, max: 0, cover: 'assets/cover-4.jpg', status: 'Writing script', dot: 'busy', recorded: false, written: false, notes: {}, blurs: [], lines: {}, capMode: st.bCap, corner: st.bCorner, cornerText: st.bCornerText, style: st.defStyle, look: st.defLook, speed: st.defSpeed };
        this.setState({ demos: [d].concat(st.demos), cur: id, screen: 'demo', step: 0, scSel: 0, vals: this.recFor(st.bVoice, st.bKind), sites: newSite ? st.sites.concat([{ u: site, note: 'Saved Nov 5' }]) : st.sites, recPos: 0, recStopped: false });
        this.say(newSite ? 'A browser opens so you can log in to ' + site + '. Then Claude writes the script.' : 'Claude is exploring ' + site + ' and writing the script');
        this.later('write', 2600, () => { this.setState({ demos: this.state.demos.map((x) => x.id === id ? Object.assign({}, x, { written: true, status: 'Script ready', dot: 'ready' }) : x) }); this.say('Script ready to read'); });
      },
      // ---- new batch ----
      btText: st.btText, onBtText: (e) => this.setState({ btText: e.target.value }), btName: st.btName, onBtName: (e) => this.setState({ btName: e.target.value }), btNamePh: st.btFile ? btName : 'e.g. Whop course, module 3',
      btFolder: st.btFolder, onBtFolder: (e) => this.setState({ btFolder: e.target.value }), btFolderPh: btFolder, btFolderVal: st.btFolder || btFolder, btFolderShort: (st.btFolder || btFolder).replace(/^~\//, ''), btFolderTail: (() => { const parts = (st.btFolder || btFolder).replace(/^~\//, '').split('/'); return parts.length > 1 ? '…/' + parts[parts.length - 1] : parts[0]; })(), chooseFolder: () => this.say('A folder picker opens on your Mac'),
      btRows: 7, btPresetHint: { strict: 'Standard, plus usage, prices, dates.', standard: 'Blurs personal info, money, customers, counts.', test: 'Fake data: names show, money blurred.' }[st.btPreset], btFootText: !btCount ? 'Paste one video per line.' : (st.btSiteNew && !siteOk(st.btNew) ? (st.btNew.trim() ? 'Fix the new site’s address first.' : 'Type the new site’s address first.') : 'Scripts are free. You approve each one.'), btMore: btCount > 7, btKindHint: { course: 'Step by step, at a teaching pace.', saas: 'Short and lively, for a product page.', tour: 'A calm look around the main screens.' }[st.btKind],
      btFileName: st.btFile, btHasFile: !!st.btFile,
      pickFile: () => { const el = document.getElementById('btfile'); if (el) el.click(); },
      onFile: (e) => { const f = e.target.files && e.target.files[0]; if (!f) return; const r = new FileReader(); r.onload = () => { this.setState({ btText: String(r.result || ''), btFile: f.name }); this.say('Read ' + f.name); }; r.readAsText(f); e.target.value = ''; },
      btSites: st.sites.filter((s, i, a) => a.findIndex((x) => x.u === s.u) === i).map((s) => ({ label: s.u, on: !st.btSiteNew && st.btSite === s.u ? 'true' : 'false', pick: () => this.setState({ btSite: s.u, btSiteNew: false }) })),
      btSiteNew: st.btSiteNew, btNew: st.btNew, onBtNew: (e) => this.setState({ btNew: e.target.value }), btNewBad: st.btSiteNew && !!st.btNew.trim() && !siteOk(st.btNew), openBtNew: () => { if (st.btSiteNew) { this.setState({ btSiteNew: false, btNew: '' }); this.focusLater('#btnewchip'); return; } this.setState({ btSiteNew: true }); requestAnimationFrame(() => { const el = document.getElementById('btns'); if (el) el.focus(); }); }, closeBtNew: () => this.setState({ btSiteNew: false, btNew: '' }),
      btVoices: st.mine.map((k) => ({ label: pretty(k), on: st.btVoice === k ? 'true' : 'false', pick: () => this.setState({ btVoice: k }) })),
      btKinds: segOf([['course', 'Walkthrough'], ['saas', 'Quick demo'], ['tour', 'Product tour']], st.btKind, (x) => this.setState({ btKind: x })).map((o, i) => Object.assign(o, { short: ['Course', 'SaaS', 'Tour'][i], ph: ['Walkthrough', 'Quick demo', 'Product tour'][i] })),
      btPresets: segOf([['strict', 'Strict'], ['standard', 'Standard'], ['test', 'Test account']], st.btPreset, (x) => this.setState({ btPreset: x })).map((o, i) => Object.assign(o, { short: ['Strict', 'Standard', 'Test'][i] })),
      btCount: btCount, btEmpty: !btCount || (st.btSiteNew && !siteOk(st.btNew)), btCountText: btCount ? this.plural(btCount, 'video') : 'No videos yet', btMinText: 'about\u00a0' + btMin + '\u00a0min', btCostText: 'about\u00a0' + this.num(btCost) + '\u00a0credits', btLine2: btShort && btCount > 0 ? 'You have ' + this.num(st.credits) + ' credits, enough for about ' + this.plural(btFits, 'video') + '. Recording pauses there until you add credits.' : 'You have ' + this.num(st.credits) + ' credits. Claude picks a length for each video.', btLeftText: 'you have ' + this.num(st.credits) + '.', btLinesText: btCount ? this.plural(btCount, 'line') + ' → ' + this.plural(btCount, 'video') + (btCount > 7 ? ' · scroll for ' + (btCount - 7) + ' more' : '') : 'Nothing yet',
      btShort: btShort && btCount > 0, btShortText: 'Enough for about ' + btFits + '. Recording pauses there until you add credits. Nothing fails.',
      btCta: btCount ? 'Write ' + this.plural(btCount, 'script') : 'Write the scripts',
      submitBatch: () => {
        if (!btCount) { this.focusLater('#btt'); return; } if (st.btSiteNew && !siteOk(st.btNew)) { this.focusLater('#btns'); return; } if (this.live) { const site = st.btSiteNew ? st.btNew.trim() : st.btSite; this.act('batch.new', { name: btName, list: btLines.join('\n'), site: site, kind: st.btKind, voice: st.btVoice, privacy_preset: { strict: 'strict', standard: 'standard', test: 'test_account' }[st.btPreset], export_to: st.btFolder.trim() || null }, { ok: 'Sent to Claude. ' + this.plural(btCount, 'script') + ' are written next, nothing records until you approve them.' }); this.setState({ screen: 'home', btText: '', btName: '', btFile: '', btFolder: '' }); return; } const id = 'b' + Date.now();
        const b = { id: id, name: btName, site: st.btSiteNew ? st.btNew.trim() : st.btSite, voice: st.btVoice, kind: st.btKind, preset: st.btPreset, folder: btFolder, stage: 'writing', paused: false, items: btLines.map((t, i) => ({ t: t, lesson: 'Lesson ' + (i + 1), min: 3, st: 'writing' })) };
        this.setState({ batches: [b].concat(st.batches), curBatch: id, screen: 'batch', btText: '', btName: '', btFile: '', btFolder: '' });
        this.later('bwrite', 2600, () => { this.patchBatch((x) => ({ stage: 'approve', items: x.items.map((it) => Object.assign({}, it, { st: 'script' })) }), id); this.say('All scripts are ready to approve'); });
      },
      // ---- batch screen ----
      bName: B ? B.name : '', bMeta1: B ? B.site + ' · ' + pretty(B.voice) : '', bMeta2: B ? { course: 'Walkthrough', saas: 'SaaS demo', tour: 'Product tour' }[B.kind] + ' · ' + presetName[B.preset] + ' privacy' : '', bMeta: B ? [B.site, pretty(B.voice), { course: 'Walkthrough', saas: 'Quick demo', tour: 'Product tour' }[B.kind], presetName[B.preset] + ' privacy'].join(', ') : '', bFolder: B ? B.folder : '',
      // Watch live: the newest frame of the video being recorded, about twice a second (the page's privacy blur is
      // already on it). Only while something is recording; the panel closes itself when it's done.
      bLive: !!(B && B.stage === 'recording' && recIdx >= 0 && !B.paused), bLiveOpen: !!(st.liveOpen && B && B.stage === 'recording' && recIdx >= 0 && !B.paused), bLiveSrc: st.liveSrc || (this.live ? '' : 'assets/cover-1.jpg'),
      bLiveLabel: st.liveOpen ? 'Hide live view' : 'Watch live', bLiveToggle: () => { const open = !st.liveOpen; this.setState({ liveOpen: open }); if (open) this.watchLive(recIdx >= 0 && B.items[recIdx].did); else this.stopLive(); },
      bStages: planWaiting ? bStages.map((x, i) => i === 0 ? Object.assign({}, x, { sub: 'Pick a plan first' }) : x) : bStages, bRecLabel: B && (B.stage === 'recording' || B.stage === 'review') ? bRecorded + ' of ' + bItems.length + ' recorded' : '', bCreditSlot: !!(B && B.stage === 'recording'), bHead: planWaiting ? this.plural(bl.plan.options.length, 'plan') + ' ready.' : pickLeft && !(B && B.paused) ? pickLeft + ' to pick.' : bHead, bSub: planWaiting ? 'Pick the one you’d rather make.' : pickLeft && !(B && B.paused) ? 'Listen to each version and pick one. It records straight after.' + (B && B.stage === 'recording' && recIdx >= 0 ? ' The rest of the batch carries on meanwhile.' : '') : bSub, bPct: (bItems.length ? (B.stage === 'approve' || B.stage === 'writing' ? 0 : bRecorded / bItems.length * 100) : 0) + '%', bCreditNote: bCreditNote, hasBCreditNote: !!bCreditNote, bCreditHidden: !!(B && B.paused && B.paused !== 'credits'), bPausedCredits: !!(B && B.paused === 'credits'),
      bItems: bItems.map((x, i) => ({ i: i, n: i + 1, t: x.t, min: x.min + ' min', st: x.st, status: planWaiting && x.st === 'writing' ? 'Not started' : B.paused && (x.st === 'recording' || x.st === 'writing') ? 'Paused here' : stLabel[x.st], dot: (planWaiting && x.st === 'writing') || (B.paused && (x.st === 'recording' || x.st === 'writing')) ? 'wait' : stDot[x.st], ring: x.st === 'waiting', open: st.btOpen === i, openStr: st.btOpen === i ? 'true' : 'false', canOpen: x.st === 'script', canWatch: x.st === 'recorded' || x.st === 'approved', canPick: x.st === 'pick', pickOpen: pickSel === i, pick: () => (pickSel === i ? this.setState({ pickOpen: null }) : openPick(i)), preview: 'Okay so… in this one we’re gonna ' + x.t.toLowerCase() + '. It’s, um, quicker than it looks.',
        noAct: !(x.st === 'script' || x.st === 'recorded' || x.st === 'approved' || x.st === 'pick'),
        sub: x.st === 'skipped' ? x.why.replace(/\s*\([^()]*\)\s*$/, '') : [x.seat, B.stage === 'approve' && costOf(x) ? this.num(costOf(x)) + ' credits' : ''].filter(Boolean).join(' · '),
        toggle: () => this.setState({ btOpen: st.btOpen === i ? null : i }), watch: () => watchItem(i) })).slice(bStart, bEnd),
      bAbove: bStart > 0, bAboveText: (bStart > 1 ? 'Videos 1–' + bStart : 'Video 1') + (bAboveText.indexOf(' · ') < 0 ? ' ' + bAboveText.replace(/^\d+ /, '') : ': ' + bAboveText), bAboveDone: bAbove.every((x) => x.st === 'approved' || x.st === 'exported'), bWaiting: cnt('waiting'), bAllOpenRaw: st.btAll, bWaitingCollapsed: !st.btAll && cnt('waiting') > 1, bShowAll: () => this.setState({ btAll: !st.btAll }), bShowAllLabel: st.btAll ? 'Show less' : 'Show all ' + bItems.length, bAllOpen: st.btAll && bItems.length > 10, bShowToggle: bItems.length > 10,
      bReady: bReady, hasBReady: bReady > 0, bReadyText: this.plural(bReady, 'video') + ' ready to watch', bWatchFirst: () => { const k = bItems.findIndex((x) => x.st === 'recorded'); if (k >= 0) watchItem(k); },
      bCfSlot: !!(B && B.stage === 'approve'), bFooterShort: B ? (B.stage === 'done' ? 'Everything is in ' + B.folder + ', with list.csv (title, file name, lesson). Nothing is published.' : B.stage === 'approve' || B.stage === 'writing' ? 'Nothing records until you press Go.' : 'Nothing is published automatically.') : '', bFooter: B ? (B.stage === 'done' ? 'Everything is in ' + B.folder + ', with list.csv (title, file name, lesson). Nothing is published.' : B.stage === 'approve' || B.stage === 'writing' ? 'Nothing records until you press Go.' : (firstReady >= 0 ? 'Nothing is published automatically.' : 'Exports go to Movies/NAVI with a list file. Nothing is published automatically.')) : '',
      bPrimaryShort: /^Watch /.test(bPrimary.label) ? bPrimary.label : (/^Export (\d+)/.test(bPrimary.label) ? 'Export ' + bPrimary.label.match(/\d+/)[0] : bPrimary.label), bSecondaryShort: bSecondary ? (/^Export (\d+)/.test(bSecondary.label) ? 'Export ' + bSecondary.label.match(/\d+/)[0] + ' approved' : 'Export') : '', bPrimaryLabel: bPrimary.label, bWatchBtn: /^Watch /.test(bPrimary.label), bPrimaryOff: bPrimary.off, bPrimary: (e) => { if (bPrimary.off) return; bPrimary.act(e); }, hasBSecondary: !!bSecondary, bSecondaryLabel: bSecondary ? bSecondary.label : '', bSecondary: (e) => { if (!bSecondary || bSecondary.off) return; bSecondary.act(e); }, bSecondaryOff: bSecondary ? !!bSecondary.off : false, hasBPause: !!bPauseObj, bPauseLabel: bPauseObj ? bPauseObj.label : '', bPause: bPauseObj ? bPauseObj.act : () => {}, bReviewing: !!(B && (B.stage === 'recording' || B.stage === 'review')),
      bPick: pickSel != null, bPickTitle: pickSel === 'plan' ? 'Pick a plan' : pickSel != null ? 'Pick a version of #' + (pickSel + 1) : '', bPickOptions: pickOptions,
      bPickSub: pickSel === 'plan' ? 'The same list of videos, planned ' + pickOptions.length + ' ways. Nothing is explored or written until you pick.' : pickSel != null ? '“' + bItems[pickSel].t + '”, written ' + pickOptions.length + ' ways and voiced once each. The one you pick is the one that’s recorded.' : '',
      bPickFoot: 'You’ll see what made each one once every pick in this batch is made.' + (pickLeft > 1 ? ' ' + pickLeft + ' videos to pick.' : ''),
      hasBReveal: bReveal.length > 0 && !!B && (B.stage === 'review' || B.stage === 'recording' || B.stage === 'done'), bReveal: bReveal,
      // the Mac's load on the Go screen, and which apps to quit first (Andy, 12 Nov 2026)
      hasBGoMac: !!(B && B.stage === 'approve' && B.mac), bGoMac: B && B.mac ? B.mac.line : '', bGoMacBusy: !!(B && B.mac && (B.mac.busy || (B.mac.heavy || []).length)),
      bGo: !!(B && B.stage === 'approve'), bGoLogins: goLogins, bGoCost: goCost, bGoReason: B && B.needsYou ? 'Not started: ' + B.needsYou + '. Nothing was spent.' : '',
      bConfirm: !!(st.bConfirm && B && B.stage === 'approve'), bNotConfirm: !(st.bConfirm && B && B.stage === 'approve'), bConfirmText: bConfirmText, bConfirmYes: () => bStartAll(), bConfirmNo: () => { this.setState({ bConfirm: false }); this.focusLater('.bprimary'); },
      // ---- demo steps ----
      steps: steps, cur: cur, st0: st.step === 0, st1: st.step === 1, st2: st.step === 2, st3: st.step === 3, st4: st.step === 4, st4b: st.step === 4 && !!st.fromBatch, st5: st.step === 5,
      scSeat: D.seat ? 'Records as ' + D.seat + (D.seatSaved === false ? ', not logged in yet' : '') : '',
      writing: !D.written, scriptReady: !!D.written, scLenInFoot: !!D.written && !D.max, skelRows: this.secs.map((x, i) => ['62%', '80%', '70%', '86%', '58%', '74%', '66%'][i % 7]),
      canBack: st.step > 0 && st.step < 5 && !(st.step === 3 && !D.recorded && !st.recStopped), recHold: st.step === 3 && !D.recorded && !st.recStopped, back: () => { const bid = st.step === 4 ? (st.fromBatch || D.batchOf) : null; if (bid) { const i = st.batchItem; this.setState({ fromBatch: null, batchItem: null, markOpen: false }); this.openBatch(bid); this.focusLater('#bwatch-' + i); return; } this.setState({ step: st.step - 1, confirm: null, markOpen: false }); }, hasSecondary: !!cur.second, secondary: secondaryFor[st.step] || (() => {}), primary: (e) => { if ((st.step === 0 && !D.written) || (st.step === 3 && !D.recorded)) return; primaryFor[st.step](e); },
      primaryBlocked: (st.step === 0 && !D.written) || (st.step === 3 && !D.recorded),
      confirming: !!cf, cfRerec: st.confirm === 'rerecord' && st.step === 3, cfApprove: st.confirm === 'approve' && st.step === 4, notConfirming: !cf, confirmNo: cf ? cf.no : '', confirmYes: cf ? cf.yes : '', cancelConfirm: () => { const sel = this.confirmFrom(st.confirm); this.setState({ confirm: null }); this.focusLater(sel); }, doConfirm: () => { if (cf) cf.act(); },
      footText: foot.text, footDot: foot.dot, footColor: foot.color,
      footLinkOn: !cf && footBad, footLinkLabel: 'switch back to ' + vInfo.models[0], footLinkAct: () => { this.patchDemo({ model: vInfo.models[0] }); this.say('Switched to Eleven ' + vInfo.models[0] + ' for ' + voicePretty); this.focusLater('.stepfoot .pri'); },
      // script
      scPickSel: (e) => this.setState({ scSel: Number(e.target.value), scChange: false, scDraft: '' }),
      scList: this.secs.map((s, i) => ({ i: i, t: this.fmt(this.starts[i]), n: s.n, on: st.scSel === i ? 'true' : 'false', edited: !!(D.lines && D.lines[i]), pick: () => this.setState({ scSel: i, scChange: false, scDraft: '' }) })),
      scNum: (st.scSel + 1) + ' of ' + this.secs.length, scName: this.secs[st.scSel].n, scLine: lineOf(st.scSel), scCaption: this.secs[st.scSel].c,
      scCaps: st.scCaps, scCapsLabel: st.scCaps ? 'Hide captions' : 'Show captions', toggleScCaps: () => this.setState({ scCaps: !st.scCaps }),
      scChange: st.scChange, scDraft: st.scDraft, onScDraft: (e) => this.setState({ scDraft: e.target.value }), closeScChange: () => { this.setState({ scChange: false, scDraft: '' }); this.focusLater('#scopen'); }, openScChange: () => { this.setState({ scChange: !st.scChange, scCaps: false, scDraft: '' }); this.later('focusSc', 30, () => { const el = document.getElementById('scd'); if (el) el.focus(); }); },
      scPending: st.scPending === st.scSel, scPendingText: 'Rewriting this line…',
      sendScChange: () => { const d = st.scDraft.trim(); if (!d) { this.focusLater('#scd'); return; } const i = st.scSel; const id = st.cur; const prevLines = D.lines || {}; if (this.live) { this.pendingLine = { id: id, i: i, v: this.secs[i].v, at: Date.now() }; this.setState({ scChange: false, scDraft: '', scPending: i }); this.act('demo.line', { demo: id, section: this.secs[i].name, request: d }, { fail: () => this.setState({ scPending: null }) }); return; } this.setState({ scChange: false, scDraft: '', scPending: i }); requestAnimationFrame(() => { const b = document.getElementById('scopen'); if (b) b.focus(); }); this.later('scw', 1600, () => { const nl = Object.assign({}, prevLines); nl[i] = this.secs[i].v.replace(/\b(um|uh|kind of|basically|to be fair|well|like),?\s*/gi, '').replace(/\s+/g, ' ').replace(/^(\w)/, (m) => m.toUpperCase()); this.setState({ scPending: null }); this.patchDemo({ lines: nl }); if (this.state.screen === 'demo' && this.state.cur === id && this.state.step === 0) this.say('Line rewritten', () => this.patchDemo({ lines: prevLines })); }); },
      scKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); const b = document.getElementById('scsend'); if (b) b.click(); } else if (e.key === 'Escape') { e.stopPropagation(); this.setState({ scChange: false }); requestAnimationFrame(() => { const b = document.getElementById('scopen'); if (b) b.focus(); }); } },
      scPrevOff: st.scSel === 0, scNextOff: st.scSel === this.secs.length - 1,
      scPrev: () => { if (st.scSel > 0) { this.setState({ scSel: st.scSel - 1, scChange: false }); if (st.scSel === 0) this.focusLater(() => [...document.querySelectorAll('[aria-label="Next section"]')].find((e) => e.offsetParent)); } }, scNext: () => { if (st.scSel < this.secs.length - 1) { this.setState({ scSel: st.scSel + 1, scChange: false }); if (st.scSel === this.secs.length - 1) this.focusLater(() => [...document.querySelectorAll('[aria-label="Previous section"]')].find((e) => e.offsetParent)); } },
      scListKey: (e) => { const n = this.secs.length; const k = e.key; let i = st.scSel; if (k === 'ArrowDown' || k === 'ArrowRight') i = Math.min(n - 1, i + 1); else if (k === 'ArrowUp' || k === 'ArrowLeft') i = Math.max(0, i - 1); else if (k === 'Home') i = 0; else if (k === 'End') i = n - 1; else return; e.preventDefault(); this.setState({ scSel: i, scChange: false, scDraft: '' }); this.focusLater('.sclist button[aria-pressed=true]'); },
      scriptLenLine: this.secs.length + ' sections, about ' + lengthText + (model === 'v3' ? ' at ' + paceText + ' pace' : ''),
      // voice
      voiceName: voicePretty, voiceColor: vcol(voice), line: line, caption: caption,
      voices: st.mine.map((k) => { const ok = VO[k].models.indexOf(model) >= 0; const mName = (m) => m === 'v4' ? 'v4' : 'v3'; return { name: VO[k].name, desc: VO[k].desc, img: VO[k].img, bg: VO[k].c, on: voice === k ? 'true' : 'false', cls: 'vcard' + (voice === k ? ' on' : ''), aria: 'Pick ' + VO[k].name, hearAria: 'Hear ' + VO[k].name + (st.heardVoices[k] ? ', free replay' : ', about ' + SAMPLE_COST + ' credits'), badge: st.heardVoices[k] ? 'Replay' : 'Hear', modelTag: VO[k].models.length === 2 ? 'Both models' : mName(VO[k].models[0]) + ' only',
        pick: () => { if (voice === k) return; const prevVoice = D.voice; const prevModel = model; const prevVals = st.vals; const switchModel = VO[k].models.indexOf(model) < 0; this.patchDemo({ voice: k, model: switchModel ? VO[k].models[0] : model }); this.setState({ vals: this.recFor(k, D.kind) }); this.say(switchModel ? 'Switched to Eleven ' + VO[k].models[0] + ' for ' + pretty(k) : 'Picked ' + pretty(k), () => { this.patchDemo({ voice: prevVoice, model: prevModel }); this.setState({ vals: prevVals }); }); },
        hear: () => { if (this.needKey()) return; if (this.live) { this.act('demo.sample', { demo: D.id, voice: k, model: model }, { ok: 'Asked Claude for a sample of ' + pretty(k) + '. Claude shows the credits first.' }); return; } const first = !st.heardVoices[k]; const h = Object.assign({}, st.heardVoices); h[k] = true; this.setState({ heardVoices: h }); if (first) this.spend(SAMPLE_COST); this.say('Playing ' + pretty(k) + (first ? ', ' + SAMPLE_COST + ' credits' : ', free replay')); } }; }),
      models: segOf([['v4', 'Eleven v4 (recommended)'], ['v3', 'Eleven v3']], model, (x) => this.patchDemo({ model: x })).map((o, i) => Object.assign(o, { short: ['v4 (recommended)', 'v3'][i] })),
      voiceWarn: !voiceOk,
      openLib: () => { this.setState({ lib: true }); this.focusLater('#libclose'); }, closeLib: () => { this.setState({ lib: false }); this.focusLater('#vmore'); }, libOpen: st.lib,
      libFilters: [['all', 'All'], ['f', 'Female'], ['m', 'Male']].map((o) => ({ label: o[1], on: st.libF === o[0] ? 'true' : 'false', pick: () => this.setState({ libF: o[0] }) })),
      lib: Object.keys(VO).filter((k) => st.libF === 'all' || VO[k].g === st.libF).map((k) => ({ name: VO[k].name, desc: VO[k].desc + ', ' + (VO[k].models.length === 2 ? 'both models' : VO[k].models[0] + ' only'), img: VO[k].img, c: VO[k].c, canAdd: st.mine.indexOf(k) < 0, added: st.mine.indexOf(k) >= 0, hearAria: 'Hear ' + VO[k].name,
        hear: () => { if (this.needKey()) return; const first = !st.heardVoices[k]; const h = Object.assign({}, st.heardVoices); h[k] = true; this.setState({ heardVoices: h }); if (first) this.spend(SAMPLE_COST); this.say('Playing ' + pretty(k) + (first ? ', ' + SAMPLE_COST + ' credits' : ', free replay')); },
        add: () => { this.setState({ mine: st.mine.concat([k]) }); this.say(pretty(k) + ' added to your voices', () => this.setState({ mine: this.state.mine.filter((x) => x !== k) })); } })),
      kinds: [['course', 'Walkthrough'], ['saas', 'Quick demo'], ['tour', 'Product tour']].map((o) => ({ label: o[1], on: D.kind === o[0] ? 'true' : 'false', pick: () => { if (D.kind === o[0]) return; const prevV = st.vals; const prevK = D.kind; this.patchDemo({ kind: o[0] }); this.setState({ vals: this.recFor(voice, o[0]) }); this.say('Switched to ' + o[1].toLowerCase() + ' settings', () => { this.patchDemo({ kind: prevK }); this.setState({ vals: prevV }); }); } })),
      fineNote: changed ? changed + ' changed' : 'All recommended', fineLine: fineLine, fineOpen: st.fineOpen, toggleFine: () => this.setState({ fineOpen: !st.fineOpen }), sliders: sliders.filter((x) => x.k !== 'pace' && x.k !== 'swear'), paceSliders: sliders.filter((x) => x.k === 'pace'),
      swearPills: ['Off', 'One', 'A few'].map((l, i) => ({ label: l, on: v.swear === i ? 'true' : 'false', pick: () => setV('swear', i) })), swearHelp: 'Off: fine for any audience. On: at natural reactions, never in instructions.', sliderHelp: st.sliderHelp, toggleSliderHelp: () => this.setState({ sliderHelp: !st.sliderHelp }), sliderHelpLabel: st.sliderHelp ? 'Hide what these do' : 'What do these do?',
      resetAll: () => { const prev = st.vals; setVals(Object.assign({}, rec), 'Back to the recommended settings', prev); this.focusLater('#slhelp'); }, anyChanged: changed > 0,
      capsOn: a.onStr, capsCls: a.cls, toggleCaps: () => { if (v.swear > 0) this.setState({ caps: !st.caps }); }, capsDown: (e) => { if (!(v.swear > 0)) e.preventDefault(); },
      playSample: () => { if (st.sampling) { this.stop('sample'); this.setState({ sampling: false }); return; } if (this.needKey()) return; if (this.live) { this.act('demo.sample', { demo: D.id, voice: voice, model: model, sliders: v }, { ok: 'Asked Claude for this sample. Claude shows the credits first.' }); return; } const free = st.lastSample === sampleKey; if (!free) this.spend(SAMPLE_COST); this.setState({ sampling: true, lastSample: sampleKey }); this.later('sample', 6000, () => this.setState({ sampling: false })); },
      samplePlaying: st.sampling, sampleStopped: !st.sampling, playAria: st.sampling ? 'Stop sample' : 'Play sample', wvClass: st.sampling ? 'wv on' : 'wv',
      wbars: [30, 55, 40, 75, 50, 90, 62, 100, 48, 70, 36, 64, 88, 52, 96, 58, 44, 80, 50, 72, 34, 60, 92, 46, 70, 40, 66, 30].map((h, i) => ({ h: h + '%', d: (i % 7) * 70 + 'ms' })),
      sampleCostLong: 'Hearing a voice the first time costs about ' + SAMPLE_COST + ' credits. Replays are free.', sampleFree: st.lastSample === sampleKey, swearOn: v.swear > 0, isDefVoice: st.defVoice === voice, makeDefault: () => { const prev = st.defVoice; if (prev === voice) { if (this.prevDef && this.prevDef !== voice) { this.setState({ defVoice: this.prevDef }); this.say(pretty(this.prevDef) + ' is the default again'); } return; } this.prevDef = prev; this.setState({ defVoice: voice }); this.say(voicePretty + ' is now your default voice', () => this.setState({ defVoice: prev })); },
      videoCostText: this.num(videoCost), leftAfterText: this.num(leftAfter), creditsNowText: this.num(st.credits), thisPct: (D.recorded || !st.credits ? 0 : Math.min(1, videoCost / st.credits) * 100) + '%', restPct: (D.recorded || !st.credits ? 100 : Math.max(0, 1 - videoCost / st.credits) * 100) + '%',
      lengthText: lengthText, paceText: paceText, isV3: model === 'v3',
      lockOn: l.onStr, lockCls: l.cls, toggleLock: () => this.setState({ lock: !st.lock }),
      // privacy
      always: ['API keys and tokens', 'Passwords', '2FA and recovery codes', 'Card and bank numbers', 'ID numbers', 'Private keys', 'Login links'],
      presets: [['strict', 'Strict', 'Blur personal info, money, customers, counts, usage, prices and dates.'], ['standard', 'Standard', 'Blur personal info, money, customers and counts. Show usage, prices and dates.'], ['test', 'Test account', 'Fake data, so names and emails can show. Money, customers and counts stay blurred.']].map((o) => ({ id: o[0], name: o[1], desc: o[2], rec: o[0] === 'standard', on: preset === o[0] ? 'true' : 'false', cls: 'preset' + (preset === o[0] ? ' on' : ''), pick: () => { const prev = st.shown; if (preset === o[0]) return; this.setState({ shown: Object.assign({}, PRESETS[o[0]]) }); this.say(o[1] + ' privacy', () => this.setState({ shown: prev })); } })),
      isCustom: preset === 'custom', pvCount: String(Object.keys(ITEM_NAMES).length),
      // The summary names usage, prices and dates the way the preset cards do; Customize keeps ITEM_NAMES' longer names.
      pvBlurLine: (() => { const g = []; if (['email', 'phone', 'names', 'address'].every((k) => !st.shown[k])) g.push('personal info'); else ['email', 'phone', 'names', 'address'].filter((k) => !st.shown[k]).forEach((k) => g.push(ITEM_NAMES[k])); if (!st.shown.money) g.push('money'); if (!st.shown.customers) g.push('customers'); if (!st.shown.counts) g.push('counts'); ['usage', 'prices', 'dates'].filter((k) => !st.shown[k]).forEach((k) => g.push(k)); g.push('passwords and keys'); return g.join(', ') + '.'; })(),
      pvShowLine: (() => { const g = []; if (['email', 'phone', 'names', 'address'].every((k) => st.shown[k])) g.push('personal info'); else ['email', 'phone', 'names', 'address'].filter((k) => st.shown[k]).forEach((k) => g.push(ITEM_NAMES[k])); if (st.shown.money) g.push('money'); if (st.shown.customers) g.push('customers'); if (st.shown.counts) g.push('counts'); ['usage', 'prices', 'dates'].filter((k) => st.shown[k]).forEach((k) => g.push(k)); return g.length ? g.join(', ') + '.' : 'nothing that could be private.'; })(),
      pvMore: st.pvMore, togglePvMore: () => { this.setState({ pvMore: !st.pvMore }); }, pvMoreLabel: 'Customize all ' + Object.keys(ITEM_NAMES).length + ' items',
      hide: st.hide.map((w, hi) => ({ w: w, aria: 'Remove ' + w, rm: () => { const prev = st.hide; this.setState({ hide: st.hide.filter((x) => x !== w) }); this.focusLater(() => { const xs = document.querySelectorAll('.chip button'); return xs[hi] || xs[hi - 1] || document.getElementById('hw'); }); this.say('Removed “' + w + '”', () => this.setState({ hide: prev })); this.undoFrom = { id: '', aria: 'Remove ' + w, text: '', tag: 'BUTTON' }; } })),
      noHide: !st.hide.length, hideDup: !!st.hideDraft.trim() && st.hide.some((x) => x.toLowerCase() === st.hideDraft.trim().toLowerCase()), hideAddOff: !st.hideDraft.trim() || st.hide.some((x) => x.toLowerCase() === st.hideDraft.trim().toLowerCase()), alwaysText: 'API keys and tokens, passwords, 2FA and recovery codes, card and bank numbers, ID numbers, private keys and login links',
      hideDraft: st.hideDraft, onHideDraft: (e) => this.setState({ hideDraft: e.target.value }), addHide: () => { const w = st.hideDraft.trim(); if (!w) { this.focusLater('#hw'); return; } if (!st.hide.some((x) => x.toLowerCase() === w.toLowerCase())) { this.setState({ hide: st.hide.concat([w]), hideDraft: '' }); this.say('Will always blur “' + w + '”'); } else this.focusLater('#hw'); },
      hideKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); const w = st.hideDraft.trim(); if (w && !st.hide.some((x) => x.toLowerCase() === w.toLowerCase())) { this.setState({ hide: st.hide.concat([w]), hideDraft: '' }); this.say('Will always blur “' + w + '”'); } } },
      tier2: [row('email', 'Email addresses'), row('phone', 'Phone numbers'), row('names', 'Real names and profile photos'), row('address', 'Addresses'), row('money', 'Revenue and money figures'), row('customers', 'Customer details'), row('counts', 'Follower and member counts')],
      tier3: [row('usage', 'Usage stats, like token usage'), row('prices', 'Prices on public pages'), row('dates', 'Dates')],
      // record
      recBadge: D.recorded ? 'Recorded' : st.recStopped ? 'Stopped' : st.recPaused ? 'Paused' : 'Recording live', recCover: D.cover, recBadgeDot: D.recorded ? 'done' : st.recPaused || st.recStopped ? 'wait' : 'rec',
      isRecording: !D.recorded, recDone: !!D.recorded,
      recHeadWords: D.recorded ? 'All sections recorded' : st.recStopped ? 'Stopped after' : 'Section', recHeadNum: D.recorded ? '' : (st.recStopped ? st.recPos : Math.min(N, st.recPos + 1)) + ' of ' + N, recLeft: D.recorded ? lengthText : String(Math.max(1, Math.ceil((N - st.recPos) * 0.4))), recLeftWords: D.recorded ? '' : 'min left',
      recPct: (D.recorded ? 100 : st.recPos / N * 100) + '%',
      recNowName: this.secs[Math.min(N - 1, st.recPos)].n, recNowLine: lineOf(Math.min(N - 1, st.recPos)), recAllLines: this.secs.map((x, i) => lineOf(i)),
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
      pauseRec: () => { if (this.live) this.act(st.recPaused ? 'demo.resume' : 'demo.pause', { demo: D.id }, { quiet: true }); if (st.recPaused) { this.setState({ recPaused: false }); this.startRecording(st.recPos); this.setState({ recPos: st.recPos }); } else { this.stop('rec'); this.setState({ recPaused: true }); this.patchDemo({ status: 'Paused at ' + (st.recPos + 1) + ' of ' + N, dot: 'wait' }); } },
      resumeStopped: () => { if (this.needKey()) return; if (this.live) this.act('demo.resume', { demo: D.id }, { quiet: true }); this.startRecording(st.recPos); this.focusLater('#recpause'); },
      recNote: D.recorded ? 'Want a fresh take? Record again redoes every section.' : 'You can close this page. Claude tells you in chat when the draft is ready.',
      // review
      totalSec: String(this.total), revSec: String(st.revT), revCaption: this.secs[secAt(st.revT)].c, revTime: this.fmt(st.revT), revLeft: (st.revT / this.total * 100) + '%',
      ticks: this.starts.slice(1).filter((s) => Math.abs(s - st.revT) > this.total * 0.03).map((s) => (s / this.total * 100) + '%'),
      // Hovering near a section tick names that section in a small chip above the ruler (absolutely placed, so nothing moves).
      tipOn: st.tipSec != null, tipName: st.tipSec != null ? this.secs[st.tipSec].n : '', tipLeft: st.tipSec != null ? (this.starts[st.tipSec] / this.total * 100) + '%' : '0%',
      tipHover: tipHover,
      tipLeave: () => { if (this.state.tipSec != null) this.setState({ tipSec: null }); },
      markPins: (() => { const g = []; allMarks.forEach((m) => { const last = g[g.length - 1]; if (last && m.t - last.t <= this.total * 0.012) last.items.push(m); else g.push({ t: m.t, items: [m] }); }); return g.map((x) => ({ left: (x.t / this.total * 100) + '%', count: x.items.length, label: this.fmt(x.t) + ', ' + x.items.map((m) => m.text).join(', '), aria: x.items.length > 1 ? 'Jump to ' + x.items.length + ' marks at ' + this.fmt(x.t) : 'Jump to mark ' + this.fmt(x.t) + ', ' + x.items[0].text, jump: () => { this.stop('player'); this.setState({ revT: x.t, player: false }); } })); })(),
      scrub: (e) => { const el = e.currentTarget; if (!el || !el.getBoundingClientRect) return; this.stop('player'); this.scrubbing = true; try { el.setPointerCapture(e.pointerId); } catch (x) {} const r = el.getBoundingClientRect(); this.setState({ player: false, revT: Math.round(Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * this.total) }); },
      scrubMove: (e) => { if (!this.scrubbing) { tipHover(e); return; } const r = e.currentTarget.getBoundingClientRect(); const t = Math.round(Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * this.total); if (t !== this.state.revT) this.setState({ revT: t }); },
      scrubUp: () => { this.scrubbing = false; },
      scrubKey: (e) => { const k = e.key; const T = this.total; const now = this.state.revT; let t = null; if (k === 'ArrowRight' || k === 'ArrowUp') t = now + 5; else if (k === 'ArrowLeft' || k === 'ArrowDown') t = now - 5; else if (k === 'PageUp') t = now + 30; else if (k === 'PageDown') t = now - 30; else if (k === 'Home') t = 0; else if (k === 'End') t = T; else if (k === ' ' || k === 'Spacebar') { e.preventDefault(); this.renderVals().togglePlayer(); return; } if (t === null) return; e.preventDefault(); this.stop('player'); this.setState({ player: false, revT: Math.max(0, Math.min(T, t)) }); },
      playerOn: st.player, playerOff: !st.player, playerAria: st.player ? 'Pause' : 'Play',
      togglePlayer: () => { const vid = this.live && document.getElementById('revvideo'); if (vid) { if (vid.paused || vid.ended) { if (vid.ended) vid.currentTime = 0; this.setState({ markOpen: false }); vid.play().catch(() => {}); } else vid.pause(); return; } if (st.player) { this.stop('player'); this.setState({ player: false }); return; } this.setState({ player: true, markOpen: false }); this.every('player', 250, () => { const t = this.state.revT + 1; if (t >= this.total) { this.stop('player'); this.setState({ player: false, revT: this.total }); return; } this.setState({ revT: t }); }); },
      markOpen: st.markOpen, markClosed: !st.markOpen, markOther: st.markOther, openOther: () => { this.setState({ markOther: true }); requestAnimationFrame(() => { const el = document.getElementById('mown'); if (el) el.focus(); }); }, openMark: () => { this.stop('player'); this.setState({ player: false, markOpen: true, markOther: false, markDraft: '' }); this.focusLater('#markfirst'); }, closeMark: () => { this.setState({ markOpen: false, markOther: false, markDraft: '' }); this.focusLater('#markbtn'); },
      markAi: () => addMark('Sounds like AI'), markBlur: () => addMark('Needs a blur'), markFast: () => addMark('Too fast'),
      markDraft: st.markDraft, onMarkDraft: (e) => this.setState({ markDraft: e.target.value }), markOwn: () => { const d = st.markDraft.trim(); if (d) addMark(d); },
      markKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); const d = (e.target.value || '').trim(); if (d) addMark(d); } },
      marks: allMarks.map((m) => ({ t: this.fmt(m.t), text: m.text.length > 40 ? m.text.slice(0, 39).replace(/\s+$/, '') + '…' : m.text, full: m.text, sec: this.secs[Number(m.k)].n, jumpAria: 'Jump to ' + this.fmt(m.t), jump: () => this.setState({ revT: m.t, player: false }), rmAria: 'Remove mark at ' + this.fmt(m.t),
        rm: () => { const prev = D.notes; const n = Object.assign({}, prev); n[m.k] = prev[m.k].filter((x, k) => k !== m.j); this.patchDemo({ notes: n }); if (allMarks.length === 1) this.focusLater('#markbtn'); const run = this.rmRun && this.rmRun.at === this.toastAt && this.state.toast ? this.rmRun : null; const first = run ? run.first : prev; const cnt = run ? run.n + 1 : 1; const from = run ? this.undoFrom : null; this.say(cnt === 1 ? 'Mark removed' : cnt + ' marks removed', () => this.patchDemo({ notes: first })); if (from) this.undoFrom = from; this.rmRun = { first: first, n: cnt, at: this.toastAt }; } })),
      reviewReminder: D.reminder || 'Watch every video all the way through before you publish it. Blurring lowers the risk; it doesn’t remove it.',
      revVideo: this.live ? (D.video || null) : null,
      hasMarks: marks > 0, noMarks: marks === 0, marksCount: marks ? '(' + marks + ')' : '', revCover: D.cover,
      hasUnsure: unsure > 0, unsureText: this.plural(unsure, 'blur') + ' to check', hasSkip: !!cur.skip && !st.confirm, skipHold: st.step === 4 && !cur.skip && !st.confirm && !st.fromBatch && !D.batchOf, skipLabel: cur.skip || '', doSkip: () => { this.setState({ confirm: 'approve' }); this.focusLater('#cfno'); }, blurOpen: st.blurOpen, toggleBlurs: () => this.setState({ blurOpen: !st.blurOpen }),
      blurs: unsureBlurs.map((b) => ({ t: b.t, what: b.what, keep: () => { const prev = D.blurs; this.patchDemo({ blurs: D.blurs.map((x) => x.id === b.id ? Object.assign({}, x, { s: 'keep' }) : x) }); this.say('Kept blurred', () => this.patchDemo({ blurs: prev })); }, show: () => { const prev = D.blurs; this.patchDemo({ blurs: D.blurs.map((x) => x.id === b.id ? Object.assign({}, x, { s: 'show' }) : x) }); this.say('Will be shown', () => this.patchDemo({ blurs: prev })); } })),
      // export
      revCaps: segOf(capOpts, dCap, (x) => { this.patchDemo({ capMode: x, dirty: !!D.exported }); }),
      revCorner: cornerCtl(dCorner, (x) => this.patchDemo({ corner: x, dirty: !!D.exported }), 'rct'),
      revCornerText: dCornerText, onRevCornerText: (e) => this.patchDemo({ cornerText: e.target.value, dirty: !!D.exported }), revCornerOff: dCorner === 'off',
      showCapPreview: dCap === 'burn', cornerShown: dCorner !== 'off', cornerStyle: posCss[dCorner] || '', cornerTextShown: dCornerText.trim() || 'Your label here',
      files: [{ n: base + '.mp4', s: '1080p · ' + lengthText + (dCap === 'burn' ? ' · captions in the video' : '') }].concat([{ n: base + ' transcript.txt', s: 'Transcript' }]).concat(dCap === 'file' ? [{ n: base + '.srt', s: 'Captions file' }] : []).concat(dP720 ? [{ n: base + ' (720p preview).mp4', s: 'Small preview' }] : []).concat(D.speed ? [{ n: base + ' (' + D.speed + 'x).mp4', s: 'Sped up, ' + this.fmt(lengthSec / D.speed) }] : []),
      filesHead: D.exported && !D.dirty ? 'Saved files' : 'You’ll get', fileMark: D.exported && !D.dirty ? '✓' : '', fileWill: D.exported && D.dirty,
      firstCaption: this.secs[0].c, showInFinder: () => this.openFolder(), p720On: p.onStr, p720Cls: p.cls, toggle720: () => { this.patchDemo({ p720: !dP720, dirty: !!D.exported }); },
      revStyles: segOf([['casual', 'Casual'], ['recordly', 'Recordly style']], D.style || 'casual', (x) => this.patchDemo({ style: x, dirty: !!D.exported })),
      revLooks: segOf([['mona-rounded', 'Mona Sans, rounded'], ['helvetica-square', 'Helvetica, square']], D.look || 'mona-rounded', (x) => { if (dCap !== 'burn') return; this.patchDemo({ look: x, dirty: !!D.exported }); }), lookOff: dCap !== 'burn',
      capLookStyle: (D.look || 'mona-rounded') === 'helvetica-square' ? 'border-radius: 0; font-family: Helvetica Neue, Helvetica, Arial, sans-serif' : 'border-radius: 8px',
      revSpeed: { on: !!D.speed, onStr: D.speed ? 'true' : 'false', cls: D.speed ? 'sw on' : 'sw', toggle: () => { if (D.speed) { this.patchDemo({ speed: null, dirty: !!D.exported }); return; } const v = speedOk(st.speedDraft) ? Number(st.speedDraft) : 1.35; this.setState({ speedDraft: String(v) }); this.patchDemo({ speed: v, dirty: !!D.exported }); this.focusLater('#spd'); } },
      revSpeedVal: st.speedDraft, revSpeedBad: !!D.speed && !speedOk(st.speedDraft), revSpeedHint: !!D.speed && !speedOk(st.speedDraft) ? 'Pick 1.05 to 2' : 'times as fast',
      onRevSpeed: (e) => { const x = e.target.value; this.setState({ speedDraft: x }); if (speedOk(x) && Number(x) !== D.speed) this.patchDemo({ speed: Number(x), dirty: !!D.exported }); },
      
      // settings / welcome
      defCaps: segOf(capOpts, st.defCap, (x) => { this.setState({ defCap: x }); this.say('Saved'); }),
      defCorner: cornerCtl(st.defCorner, (x) => this.setState({ defCorner: x }), 'dct'),
      defCornerText: st.defCornerText, onDefCornerText: (e) => this.setState({ defCornerText: e.target.value }), defCornerOff: st.defCorner === 'off',
      defLooks: segOf([['mona-rounded', 'Mona Sans, rounded'], ['helvetica-square', 'Helvetica, square']], st.defLook, (x) => { this.setState({ defLook: x }); this.say('Saved'); }),
      defStyles: segOf([['casual', 'Casual'], ['recordly', 'Recordly style']], st.defStyle, (x) => { this.setState({ defStyle: x }); this.say('Saved'); }),
      defSpeed: { on: !!st.defSpeed, onStr: st.defSpeed ? 'true' : 'false', cls: st.defSpeed ? 'sw on' : 'sw', toggle: () => { if (st.defSpeed) { this.setState({ defSpeed: null }); return; } const v = speedOk(st.defSpeedDraft) ? Number(st.defSpeedDraft) : 1.35; this.setState({ defSpeed: v, defSpeedDraft: String(v) }); this.focusLater('#dspd'); } },
      defSpeedVal: st.defSpeedDraft, defSpeedBad: !!st.defSpeed && !speedOk(st.defSpeedDraft), defSpeedHint: !!st.defSpeed && !speedOk(st.defSpeedDraft) ? 'Pick 1.05 to 2' : 'times as fast',
      limitVal: st.limitDraft, limitBad: !/^\d{1,7}$/.test(String(st.limitDraft).replace(/[,\s]/g, '')), onLimit: (e) => { const raw = e.target.value; const x = raw.replace(/[,\s]/g, ''); this.setState(/^\d{1,7}$/.test(x) ? { limitDraft: raw, creditLimit: Number(x) } : { limitDraft: raw }); },
      jobRows: (st.jobs || []).map((j) => ({ label: j.label, sub: { Planning: 'Plans what each video shows', Exploring: 'Looks around the pages first', Writing: 'Writes the scripts', Checks: 'Checks every script', 'Batch check': 'A last look before you watch' }[j.label] || '', val: j.model + ' · ' + j.effort, then: j.then ? 'then ' + j.then : '' })), hasJobs: (st.jobs || []).length > 0, jobWarnings: st.jobWarnings || [], hasJobWarnings: (st.jobWarnings || []).length > 0,
      autoGo: { on: !!st.autoGo, onStr: st.autoGo ? 'true' : 'false', cls: st.autoGo ? 'sw on' : 'sw', toggle: () => this.setState({ autoGo: !st.autoGo }) },
      onDefSpeed: (e) => { const x = e.target.value; this.setState(speedOk(x) ? { defSpeedDraft: x, defSpeed: Number(x) } : { defSpeedDraft: x }); },
      key: st.key, onKey: (e) => { if (e.target.value !== this.state.key) { this.stop('keycheck'); this.setState({ key: e.target.value, keyRes: null }); } }, keyType: st.keyType, keyTypeLabel: st.keyType === 'password' ? 'Show key' : 'Hide key', keyShown: st.keyType !== 'password', toggleKeyType: () => this.setState({ keyType: st.keyType === 'password' ? 'text' : 'password' }),
      testKey: () => {
        if (st.keyRes === 'checking') return;
        const k = st.key.trim(); const onSet = st.screen === 'settings'; const field = onSet ? '#key2' : '#key';
        if (!k) { this.setState({ keyRes: 'empty' }); this.focusLater(field); return; }
        this.setState({ keyRes: 'checking' });
        const finish = (res) => {
          if (this.state.keyRes !== 'checking' || this.state.key.trim() !== k) return;
          this.setState({ keyRes: res, keyOn: res === 'ok' ? true : this.state.keyOn, keyEnd: res === 'ok' ? k.slice(-4) : this.state.keyEnd });
          if (res === 'bad') this.focusLater(() => { const el = document.querySelector(field); if (el) el.select(); return el; }); else if (res === 'ok' && onSet) { const f = document.getElementById('key2'); if (f && f.parentElement.contains(document.activeElement)) { this.focusAt = Date.now(); requestAnimationFrame(() => { const el = document.getElementById('keytoggle'); if (el) el.focus({ preventScroll: true }); }); } }
        };
        // Live: ElevenLabs checks the key (GET /v1/user/subscription) and NAVI saves it to the Keychain only if it works.
        if (this.live) { this.liveTestKey(k, (res, r) => { if (res === 'ok' && r.credits_left != null) this.setState({ credits: r.credits_left }); finish(res); if (res === 'ok') this.refresh(true).catch(() => {}); }); return; }
        // Sample mode: simulated after about 1.2 s. Offline (or ?net=off) can't reach ElevenLabs; a key that starts with sk_ and has at least 20 characters works.
        this.later('keycheck', 1200, () => {
          const off = navigator.onLine === false || new URLSearchParams(location.search).get('net') === 'off';
          finish(off ? 'offline' : (/^sk_/.test(k) && k.length >= 20 ? 'ok' : 'bad'));
        });
      },
      keyEnter: (e) => { if (e.key === 'Enter') { e.preventDefault(); this.state.key = e.target.value; this.renderVals().testKey(); } },
      wSiteKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); this.state.wSite = e.target.value; this.renderVals().loginSite(); } },
      siteKey: (e) => { if (e.key === 'Enter') { e.preventDefault(); this.state.siteDraft = e.target.value; this.renderVals().addSite(); } },
      keyMsg: keyMsg, keyMsgColor: st.keyRes === 'bad' || st.keyRes === 'empty' || st.keyRes === 'offline' ? 'var(--danger)' : 'var(--ink)', keyBad: st.keyRes === 'bad' || st.keyRes === 'empty', keyChecking: st.keyRes === 'checking', keyBusy: st.keyRes === 'checking' ? 'true' : 'false',
      w1Cls: wsw(st.keyRes === 'ok'), w1Mark: st.keyRes === 'ok' ? '✓' : '1', w2Cls: wsw(st.tools === 'done'), w2Mark: st.tools === 'done' ? '✓' : '2', w3Cls: wsw(st.logged), w3Mark: st.logged ? '✓' : '3',
      toolsIdle: st.tools === 'idle', toolsAsking: st.tools === 'ask',
      toolsText: st.tools === 'done' ? 'Installed. NAVI can drive a browser and save video.' : st.tools === 'ask' ? 'Install now? About 300 MB, takes about 2 minutes, one time.' : st.tools === 'busy' ? 'Installing… about 2 minutes.' : 'Lets NAVI drive a browser and save video. About 300 MB, one time.',
      askTools: () => { this.setState({ tools: 'ask' }); this.focusLater('#toolsno'); }, cancelTools: () => { this.setState({ tools: 'idle' }); this.focusLater('#toolsinstall'); }, installTools: () => { if (this.live) { this.setState({ tools: 'idle' }); this.act('app.message', { text: 'Install the recording tools (scripts/setup/install.sh)', screen: 'welcome' }, { ok: 'Asked Claude to install them. Claude says the size and asks you first.' }); return; } this.setState({ tools: 'busy' }); this.focusLater('#toolstext'); this.later('tools', 1600, () => this.setState({ tools: 'done' })); },
      wSite: st.wSite, onWSite: (e) => this.setState({ wSite: e.target.value, wSiteMsg: '' }), wSiteMsg: st.wSiteMsg,
      loginLabel: st.logged ? 'Logged in' : 'Open browser', loginSite: () => { const u = st.wSite.trim(); if (!u || !siteOk(u)) { this.setState({ wSiteMsg: !u ? 'Type the site first, e.g. whop.com' : 'That doesn’t look like a web address.' }); this.focusLater('#wsite'); return; } if (this.live) this.act('login.start', { url: u }, { quiet: true }); this.setState({ wSiteMsg: '', logged: true, sites: st.sites.some((s) => s.u === u) ? st.sites : [{ u: u, note: 'Saved Nov 5' }].concat(st.sites) }); },
      welcomeBlocked: !(st.keyRes === 'ok' && st.tools === 'done'), welcomeStatus: st.keyRes === 'ok' && st.tools === 'done' ? 'All set.' : (st.keyRes !== 'ok' && st.tools !== 'done' ? 'Finish steps 1 and 2 to continue.' : st.keyRes !== 'ok' ? 'Connect ElevenLabs to continue.' : 'Install the tools to continue.') ||  ((st.keyRes === 'ok' ? 0 : 1) + (st.tools === 'done' ? 0 : 1)) + (((st.keyRes === 'ok' ? 0 : 1) + (st.tools === 'done' ? 0 : 1)) === 1 ? ' step left' : ' steps left'),
      finishWelcome: () => { if (!(st.keyRes === 'ok' && st.tools === 'done')) { this.focusLater(st.keyRes !== 'ok' ? '#key' : () => document.querySelector('#toolsinstall, #toolsno') || document.getElementById('toolstext')); return; } this.setState({ screen: 'home', keyOn: true, key: '', keyRes: null }); },
      appear: [['system', 'Follow Mac'], ['light', 'Light'], ['dark', 'Dark']].map((o) => ({ label: o[1], on: (st.theme || 'system') === o[0] ? 'true' : 'false', pick: () => { this.setState({ theme: o[0] === 'system' ? null : o[0] }); this.say('Saved'); } })),
      defVoices: st.mine.map((k) => ({ label: pretty(k), on: st.defVoice === k ? 'true' : 'false', pick: () => { this.setState({ defVoice: k }); this.say(pretty(k) + ' is now the default for new demos'); } })),
      keyRow: st.keyOn ? (st.keyEnd || !this.live ? 'Ending ' + (st.keyEnd || '4f2a') + ' · ' : 'In your Keychain · ') + this.num(st.credits) + ' credits left' : 'No key, so demos can’t be voiced.', keyRowColor: st.keyOn ? 'var(--ink2)' : 'var(--danger)',
      keyEdit: st.keyEdit, keyEditLabel: st.keyEdit ? (st.keyRes === 'ok' ? 'Done' : 'Cancel') : (st.keyOn ? 'Change' : 'Add key'), toggleKeyEdit: () => { const open = !this.state.keyEdit; this.setState({ keyEdit: open, key: '', keyRes: null }); if (open) this.focusLater('#key2'); },
      canRemoveKey: st.keyOn && !st.keyEdit, removeKey: () => { this.setState({ keyOn: false }); this.focusLater('#keytoggle'); const cancel = this.live ? this.deferred('key', () => this.act('data.plan_delete', { what: 'key' }, { quiet: true }).then((r) => r && r.token && this.act('data.confirm_delete', { token: r.token }, { quiet: true }))) : null; this.say('Key removed here. It still works at ElevenLabs.', () => { if (cancel) cancel(); this.setState({ keyOn: true }); }); },
      // Settings > Logins: one row per site and seat, its status checked live, the businesses it opens, one Log in
      // button. The login window opens only on that click.
      sites: st.sites.map((s) => ({ u: s.u, title: s.u + (s.label ? ' · ' + s.label : ''), note: loginNote(s), dot: { working: 'k-done', checking: 'k-busy', 'needs login': 'k-bad' }[s.status] || 'k-wait', needs: s.status === 'needs login', canForget: s.saved !== false, relog: () => { if (this.live) this.act('login.start', { url: s.home || s.u, seat: s.seat }, { quiet: true }); this.say('A browser opens on ' + s.u + '. Log in, then close it. NAVI ticks "remember me" for you.'); }, forget: () => { const key = s.u + '/' + (s.seat || ''); const prev = st.sites; const left = st.sites.filter((x) => (x.u + '/' + (x.seat || '')) !== key); if (this.live) this.deferred('site:' + key, () => this.act('login.forget', { site: s.u, seat: s.seat }, { quiet: true })); const from0 = this.describe(document.activeElement); this.setState({ sites: left }); if (!left.length) { this.focusAt = Date.now(); requestAnimationFrame(() => { const el = document.getElementById('addsite'); if (el) el.focus({ preventScroll: true }); }); } const run = this.fgRun && this.fgRun.at === this.toastAt && this.state.toast ? this.fgRun : null; const first = run ? run.first : prev; const cnt = run ? run.n + 1 : 1; const from = run ? this.undoFrom : from0; this.say(cnt === 1 ? 'Forgot ' + s.u : cnt + ' logins forgotten', () => { first.forEach((x) => { if (this.pending && this.pending['site:' + x.u + '/' + (x.seat || '')]) { clearTimeout(this.pending['site:' + x.u + '/' + (x.seat || '')].t); delete this.pending['site:' + x.u + '/' + (x.seat || '')]; } }); this.setState({ sites: first }); }); if (from) this.undoFrom = from; this.fgRun = { first: first, n: cnt, at: this.toastAt }; } })),
      noSites: !st.sites.length, loginsChecking: st.loginsChecking, checkLogins: () => { if (this.live) this.act('logins.check', {}, { quiet: true }); this.setState({ loginsChecking: true, sites: st.sites.map((x) => x.saved !== false ? Object.assign({}, x, { status: 'checking' }) : x) }); if (!this.live) this.later('lcheck', 1500, () => this.setState({ loginsChecking: false, sites: this.state.sites.map((x) => x.status === 'checking' ? Object.assign({}, x, { status: x.u === 'whop.com' ? 'working' : 'needs login', ago: 'just now' }) : x) })); },
      siteDraft: st.siteDraft, siteBad: !!st.siteBad, siteBadText: st.siteBad === 'empty' ? 'Type the site first, e.g. whop.com' : st.siteBad ? 'That doesn’t look like a web address.' : '', onSiteDraft: (e) => { if (e.target.value !== this.state.siteDraft) this.setState({ siteDraft: e.target.value, siteBad: false }); }, addSite: () => { const u = st.siteDraft.trim(); if (!u) { this.setState({ siteBad: 'empty' }); this.focusLater('#addsite'); return; } if (!siteOk(u)) { this.setState({ siteBad: true }); return; } if (this.live) { this.act('login.start', { url: u }, { quiet: true }); this.setState({ siteDraft: '' }); this.say('A browser opens so you can log in to ' + u + '. Close it when you’re in.'); return; } this.setState({ sites: st.sites.concat([{ u: u, note: 'Saved Nov 5' }]), siteDraft: '' }); this.say('A browser opens so you can log in to ' + u); },
      data: dataDefs.map((d) => ({ n: d.n, w: d.w, l: d.l, can: !!d.l, act: dataAct[d.id] || (() => {}) })), forgetAll: dataAct.logins,
      wipeConfirm: st.wipeConfirm, notWipeConfirm: !st.wipeConfirm, askWipe: () => { this.setState({ wipeConfirm: true }); this.focusLater('#wipecancel'); }, cancelWipe: () => { this.setState({ wipeConfirm: false }); this.focusLater('#wipebtn'); },
      doWipe: () => { if (this.live) { this.setState({ wipeConfirm: false }); this.act('data.plan_delete', { what: 'everything' }).then((r) => r && r.token && this.act('data.confirm_delete', { token: r.token }).then((d) => { if (d) { this.refresh(true).catch(() => {}); this.say('Everything this skill saved is gone. Your videos are untouched.', null, () => this.setState({ screen: 'welcome', keyRes: null, logged: false, wSite: '', wSiteMsg: '' }), 'Set up again'); } })); return; } this.focusLater('#wipebtn'); this.setState({ wipeConfirm: false, keyOn: false, sites: [], hide: [], vals: Object.assign({}, this.presetVals.course), defVoice: 'alex', mine: ['alex', 'jessica', 'george'], heardVoices: {}, tools: 'idle' }); this.say('Everything this skill saved is gone. Your videos are untouched.', null, () => this.setState({ screen: 'welcome', keyRes: null, logged: false, wSite: '', wSiteMsg: '' }), 'Set up again'); },
      showWelcome: () => { this.setState({ screen: 'welcome', keyRes: null, key: '', tools: st.tools === 'done' ? 'done' : 'idle', logged: false, wSite: '', wSiteMsg: '' }); this.focusLater('#wel-h'); },
      // chat + toast
      recLock: st.screen === 'demo' && st.step === 3 && !D.recorded && !st.recStopped,
      chatHidden: st.screen === 'new' || (st.screen === 'demo' && st.step === 3 && !D.recorded && !st.recStopped) || (st.screen === 'demo' && st.step === 1 && st.fineOpen),
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
    if (this.live) { this.act('app.message', { text: m, screen: st.screen, demo: st.screen === 'demo' ? st.cur : null }, { quiet: false }); this.setState({ chat: st.chat.concat([{ me: true, t: m }, { me: false, t: 'Sent to Claude. The answer comes in your Claude chat, and changes show up here.' }]), chatDraft: '', chatAct: null }); return; }
    const switching = /instead|new demo|different|switch/i.test(m);
    const reply = switching ? 'Got it. I’ll keep this one as a draft and start a new brief from what you said. Check it before I write anything?' : (st.screen === 'demo' ? 'On it. I’ll change that and only redo the parts it touches. You’ll see it update here.' : 'Sure. Tell me what you’d like to show and I’ll set up a new demo.');
    this.setState({ chat: st.chat.concat([{ me: true, t: m }, { me: false, t: reply }]), chatDraft: '', chatAct: switching ? m : null });
  }
}

if (window.NaviEngine) NaviEngine.install(Component);

(function () {
  const q = new URLSearchParams(location.search);
  const comp = new Component({ startOn: q.get('start') || 'welcome', theme: q.get('theme') || 'system' });
  const scope = PetiteVue.reactive(comp.renderVals());
  let stripKey = null, stripBox = null; const keepStepVisible = () => requestAnimationFrame(() => { const box = document.querySelector('.steplist'); const el = box && box.querySelector('.stepbtn.now'); if (!box) return; const key = comp.state.screen + '/' + comp.state.cur + '/' + comp.state.step; const fresh = key !== stripKey || box !== stripBox; stripKey = key; stripBox = box; if (fresh && el && box.scrollWidth > box.clientWidth) { const prev = el.previousElementSibling && el.previousElementSibling.classList.contains('stepbtn') ? el.previousElementSibling : (el.parentElement.previousElementSibling && el.parentElement.previousElementSibling.querySelector ? el.parentElement.previousElementSibling.querySelector('.stepbtn') : null); const target = prev || el; box.scrollLeft = Math.max(0, box.scrollLeft + target.getBoundingClientRect().left - box.getBoundingClientRect().left - 6); } const upd = () => box.classList.toggle('at-start', box.scrollLeft < 4); upd(); if (!box._navi) { box._navi = 1; box.addEventListener('scroll', upd, { passive: true }); } });
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
  // Any other toast belongs to its screen: opening another screen later (not in the same action) drops it, so it never sits over the next screen's content.
  comp.setState = function (s) { Object.assign(comp.state, s); const tw = comp.toastWhere; if (comp.state.toast && tw && ((comp.state.toastUndo && tw !== comp.state.screen + '/' + comp.state.step) || (tw.split('/')[0] !== comp.state.screen && Date.now() - (comp.toastAt || 0) > 400))) Object.assign(comp.state, { toast: '', toastUndo: null, toastGo: null }); Object.assign(scope, comp.renderVals()); keepStepVisible(); if (comp.live) { comp.watchLocal(); if (comp.seekVideo) comp.seekVideo(); } if (s && 'toast' in s) requestAnimationFrame(placeToast); afterRender(); };
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !e.defaultPrevented) { if (comp.escape()) e.preventDefault(); return; }
    if (e.key === 'Tab' && comp.state.lib) { const d = document.getElementById('libdlg'); if (!d) return; const f = [...d.querySelectorAll('button, input, [tabindex="0"]')].filter((x) => !x.disabled && x.offsetParent !== null); if (!f.length) return; const i = f.indexOf(document.activeElement); if (e.shiftKey && (i <= 0)) { e.preventDefault(); f[f.length - 1].focus(); } else if (!e.shiftKey && (i === f.length - 1 || i < 0)) { e.preventDefault(); f[0].focus(); } }
  });
  document.addEventListener('pointerdown', (e) => comp.outside(e.target), true);
  try { window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => comp.setState({})); } catch (e) {}
  PetiteVue.createApp(scope).mount('#app');
  keepStepVisible(); window.addEventListener('resize', () => { stripKey = null; comp.setState({}); });
  window.navi = comp;
  if (q.get('start') === 'new' && q.get('mode') === 'batch') comp.setState({ mode: 'batch' });
  if (comp.live) comp.engineBoot(q.get('start'));
})();
