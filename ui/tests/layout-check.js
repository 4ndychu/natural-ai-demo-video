// Layout check for every NAVI screen at every width, in light and dark.
//
//   node ui/tests/layout-check.js            check everything, exit 1 on any problem
//   node ui/tests/layout-check.js --shots D  also save a screenshot of each run into folder D
//   WIDTHS=1024,1100 SCREENS=script,review node ui/tests/layout-check.js   check a subset
//
// It fails when:
//   - the page scrolls sideways;
//   - two things on screen overlap (text on text, a control over a label, a dot on a word, boxes that cross);
//   - text is clipped by its box or cut off with "…";
//   - a word breaks across lines (like "INTRO" stacking one letter per line);
//   - at the bottom of the page, the chat bar covers anything.
// Things placed on purpose inside another thing (a knob in its track, a label on an image, a badge on a cover) are fine.
// A pinned bar (position: sticky) is its own layer: the page scrolling under it is fine, its own parts may not overlap.
// Two attributes mark deliberate cases: data-lc-layers (children drawn in layers, like a slider's fill under its label)
// and data-lc-scroll (a strip meant to be swiped sideways, like the step strip on phones).
// Playwright comes from the recorder's install, so nothing new is installed. Set PLAYWRIGHT to point elsewhere.
const PW = process.env.PLAYWRIGHT || require('path').join(__dirname, '..', '..', 'recorder', 'agent-screenplay', 'node_modules', 'playwright-core');
const { chromium } = require(PW);
const path = require('path'); const fs = require('fs');
const UI = 'file://' + path.resolve(process.env.UI_DIR || path.join(__dirname, '..')) + '/index.html';
const WIDTHS = (process.env.WIDTHS || '390,768,900,1024,1050,1100,1280,1440,1920').split(',').map(Number);
const THEMES = (process.env.THEMES || 'light,dark').split(',');
const shotsAt = process.argv.indexOf('--shots') > 0 ? process.argv[process.argv.indexOf('--shots') + 1] : null;
const heightFor = (w) => (w <= 400 ? 844 : w <= 800 ? 1024 : w >= 1900 ? 1080 : 900);

const demo = (step, patch, extra) => `navi.setState({screen:'demo',cur:'whop'}); navi.patchDemo(Object.assign({recorded:false,exported:false,notes:{},blurs:[],status:''}, ${JSON.stringify(patch)})); navi.setState(Object.assign({step:${step}}, ${JSON.stringify(extra || {})}));`;
const SCREENS = [
  { id: 'welcome', start: 'welcome' },
  { id: 'home', start: 'home' },
  { id: 'new', start: 'new' },
  { id: 'new-options', start: 'new', js: `const b=[...document.querySelectorAll('main button')].find(b=>b.textContent.trim().startsWith('Change')); if(b) b.click();` },
  { id: 'new-batch', start: 'new', js: `navi.setState({mode:'batch', btText: navi.state.batches[0].items.slice(0,12).map(x=>x.t).join('\\n'), btName:'Whop course, module 3'})` },
  { id: 'batch', start: 'batch' },
  { id: 'batch-live', start: 'batch', js: `navi.setState({liveOpen:true})` },
  // the Go screen: every video's seat and cost, the logins needed (one needs a login first), the total, a "not started" reason
  { id: 'batch-go', start: 'batch', js: `navi.patchBatch({stage:'approve', items: navi.state.batches[0].items.map((x,i)=>Object.assign({}, x, {st:'script', cost: 1860 + i * 10})), logins: [{key:'whop.com/owner', site:'whop.com', seat:'owner', label:'whop.com · Owner', status:'working', home:'https://whop.com/'}, {key:'app.yourproduct.com/owner', site:'app.yourproduct.com', seat:'owner', label:'app.yourproduct.com · Owner', status:'needs login', home:'https://app.yourproduct.com/'}], needsYou: 'log in again first: app.yourproduct.com/owner', mac: {busy: true, heavy: ['Spotify', 'Roblox', 'Google Chrome'], line: 'Your Mac is busy (load 42; recordings come out best under 4). Quit Spotify, Roblox and Google Chrome before Go. iCloud Drive is busy syncing too: let it finish first.'}})` },
  { id: 'batch-go-quiet', start: 'batch', js: `navi.patchBatch({stage:'approve', items: navi.state.batches[0].items.map((x,i)=>Object.assign({}, x, {st:'script', cost: 1860 + i * 10})), needsYou: '', mac: {busy: false, heavy: [], line: 'Your Mac is quiet (load 1.8).'}})` },
  // the morning report: done and skipped videos, with the reason
  { id: 'batch-report', start: 'batch', js: `navi.patchBatch({stage:'review', items: navi.state.batches[0].items.map((x,i)=>Object.assign({}, x, i % 5 === 4 ? {st:'skipped', why:'NAVI’s action guard blocked deleting something (DELETE whop.com/api/v1/products/prod_x)'} : {st: i < 3 ? 'approved' : 'recorded'}))})` },
  // blind A/B/C: a video's three versions to listen to and pick; one version's script open; the plans; the result; a paused batch
  { id: 'batch-pick', start: 'batch', js: `navi.sampleBlind('lesson')` },
  { id: 'batch-pick-read', start: 'batch', js: `navi.sampleBlind('lesson'); navi.setState({pickRead:'B', pickPlaying:'7/A', pickPos:0.4})` },
  { id: 'batch-pick-plan', start: 'batch', js: `navi.sampleBlind('plan')` },
  { id: 'batch-pick-plan-read', start: 'batch', js: `navi.sampleBlind('plan'); navi.setState({pickRead:'A'})` },
  { id: 'batch-picked', start: 'batch', js: `navi.sampleBlind('revealed')` },
  { id: 'batch-paused', start: 'batch', js: `navi.sampleBlind('paused')` },
  { id: 'script', start: 'home', js: demo(0, { max: 0 }, { scSel: 2 }) },
  { id: 'script-captions', start: 'home', js: demo(0, { max: 0 }, { scSel: 2, scCaps: true }) },
  { id: 'voice', start: 'home', js: demo(1, { max: 1 }) },
  { id: 'voice-finetune', start: 'home', js: demo(1, { max: 1 }, { fineOpen: true }) },
  { id: 'voice-switch', start: 'home', js: demo(1, { max: 1, voice: 'jessica', model: 'v3' }) },
  { id: 'privacy', start: 'home', js: demo(2, { max: 2 }) },
  { id: 'privacy-custom', start: 'home', js: demo(2, { max: 2 }, { pvMore: true }) },
  { id: 'record', start: 'home', js: demo(3, { max: 3 }, { recPos: 4 }) },
  { id: 'record-paused', start: 'home', js: demo(3, { max: 3 }, { recPos: 4, recPaused: true }) },
  { id: 'review', start: 'review' },
  { id: 'review-mark', start: 'review', js: `navi.setState({markOpen:true})` },
  { id: 'export-pre', start: 'home', js: demo(5, { max: 5, recorded: true, dirty: false }) },
  { id: 'export', start: 'home', js: demo(5, { max: 5, recorded: true, exported: true, dirty: false, status: 'Exported Nov 5' }) },
  { id: 'settings', start: 'settings' },
].filter((s) => !process.env.SCREENS || process.env.SCREENS.split(',').includes(s.id));

// Runs inside the page. Returns a list of problems.
function audit() {
  const W = window.innerWidth; const out = [];
  const desc = (el) => { const t = (el.innerText || el.getAttribute('aria-label') || el.value || '').trim().replace(/\s+/g, ' ').slice(0, 40); return el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '') + (t ? ' "' + t + '"' : ''); };
  const shown = (el) => { for (let e = el; e && e !== document.documentElement; e = e.parentElement) { const c = getComputedStyle(e); if (c.display === 'none' || +c.opacity === 0) return false; } const c = getComputedStyle(el); return c.visibility === 'visible'; };
  const srOnly = (el) => { for (let e = el; e && e !== document.body; e = e.parentElement) { const c = getComputedStyle(e); if ((c.clip && c.clip !== 'auto') || (c.clipPath && c.clipPath !== 'none')) return true; const r = e.getBoundingClientRect(); if (r.width <= 1 || r.height <= 1) { if (c.overflow !== 'visible' || c.position === 'absolute') return true; } } return false; };
  const fixedOf = (el) => { for (let e = el; e; e = e.parentElement) if (getComputedStyle(e).position === 'fixed') return e; return null; };
  // a pinned bar (position: sticky, like the review screen's buttons) is drawn over the page as it scrolls under it
  const stickyOf = (el) => { for (let e = el; e; e = e.parentElement) if (getComputedStyle(e).position === 'sticky') return e; return null; };
  const ownText = (el) => [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
  // Text boxes are trimmed to their line height, so tight display type (line-height under 1) doesn't count as touching the next line.
  const textRect = (nodes, lh) => { let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; for (const n of nodes) { const r = document.createRange(); r.selectNodeContents(n); for (const q of r.getClientRects()) { if (q.width < 1) continue; const cut = lh && q.height > lh ? (q.height - lh) / 2 : 0; x0 = Math.min(x0, q.left); y0 = Math.min(y0, q.top + cut); x1 = Math.max(x1, q.right); y1 = Math.max(y1, q.bottom - cut); } } return x1 > x0 ? { left: x0, top: y0, right: x1, bottom: y1 } : null; };
  const painted = (el, c) => { if (/^(IMG|svg|CANVAS|VIDEO|INPUT|TEXTAREA|SELECT)$/.test(el.tagName)) return true; const bg = c.backgroundColor; if (bg && !/rgba\(.*,\s*0\)$/.test(bg) && bg !== 'transparent') return true; if (c.backgroundImage !== 'none') return true; for (const s of ['Top', 'Right', 'Bottom', 'Left']) if (parseFloat(c['border' + s + 'Width']) > 0 && !/rgba\(.*,\s*0\)$/.test(c['border' + s + 'Color'])) return true; return false; };
  // Clip by every scrolling or clipping ancestor, so things scrolled out of a scroller don't count.
  const clipTo = (el, r) => { let { left, top, right, bottom } = r; for (let e = el.parentElement; e && e !== document.body; e = e.parentElement) { const c = getComputedStyle(e); if (c.overflowX !== 'visible' || c.overflowY !== 'visible') { const q = e.getBoundingClientRect(); if (c.overflowX !== 'visible') { left = Math.max(left, q.left); right = Math.min(right, q.right); } if (c.overflowY !== 'visible') { top = Math.max(top, q.top); bottom = Math.min(bottom, q.bottom); } } } return right - left > 1 && bottom - top > 1 ? { left, top, right, bottom } : null; };

  // 1. sideways scroll
  if (document.documentElement.scrollWidth > W + 1) out.push({ kind: 'sideways-scroll', what: 'page is ' + document.documentElement.scrollWidth + ' px wide in a ' + W + ' px window' });

  const items = [];
  for (const el of document.body.querySelectorAll('*')) {
    if (el.closest('svg') && el.tagName !== 'svg') continue;
    if (/^(SCRIPT|STYLE|TEMPLATE|OPTION|BR)$/.test(el.tagName)) continue;
    if (el.closest('[data-lc-skip]')) continue;
    const r0 = el.getBoundingClientRect(); const tn = ownText(el);
    if ((r0.width < 1 || r0.height < 1) && !tn.length) continue;
    if (!shown(el) || srOnly(el)) continue;
    const c = getComputedStyle(el); const p = painted(el, c);
    if (tn.length && (r0.width < 1 || r0.height < 1)) out.push({ kind: 'squeezed', what: desc(el) + ' has no room (' + Math.round(r0.width) + ' x ' + Math.round(r0.height) + ' px)' });
    if (!tn.length && !p) continue;
    if (el.closest('[aria-hidden="true"]') && c.visibility === 'hidden') continue;
    const rect = p ? r0 : textRect(tn, parseFloat(c.lineHeight) || 0); if (!rect) continue;
    const vis = clipTo(el, rect); if (!vis) continue;
    items.push({ el, text: tn.length > 0, paint: p, r: vis, full: rect, fixed: fixedOf(el), sticky: stickyOf(el), c, tn });

    // 2. text checks
    if (tn.length) {
      // cut off with an ellipsis, or clipped by its own box
      const ov = c.overflowX !== 'visible' || c.overflowY !== 'visible';
      if (c.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth + 1) out.push({ kind: 'text-cut', what: desc(el) + ' ends in "…"' });
      else if (ov && (el.scrollWidth > el.clientWidth + 1 || (c.overflowY !== 'visible' && el.scrollHeight - el.clientHeight > 0.35 * parseFloat(c.fontSize) && c.overflowY !== 'auto' && c.overflowY !== 'scroll'))) out.push({ kind: 'text-clipped', what: desc(el) + ' is cut by its own box' });
      // clipped by a hidden ancestor (not a scroller)
      for (let e = el.parentElement; e && e !== document.body; e = e.parentElement) { const ec = getComputedStyle(e); const hx = ec.overflowX === 'hidden' || ec.overflowX === 'clip'; const hy = ec.overflowY === 'hidden' || ec.overflowY === 'clip'; if (!hx && !hy) continue; const q = e.getBoundingClientRect(); if ((hx && (rect.left < q.left - 1 || rect.right > q.right + 1)) || (hy && (rect.top < q.top - 2 || rect.bottom > q.bottom + 2))) { out.push({ kind: 'text-clipped', what: desc(el) + ' is cut by ' + desc(e) }); break; } }
      // off the side of the window (outside any sideways scroller)
      let inScroller = false; for (let e = el.parentElement; e && e !== document.body; e = e.parentElement) { const ec = getComputedStyle(e); if (ec.overflowX === 'auto' || ec.overflowX === 'scroll') { inScroller = true; break; } }
      if (!inScroller && (rect.right > W + 1 || rect.left < -1)) out.push({ kind: 'text-offscreen', what: desc(el) + ' runs past the window edge' });
      // a word broken across lines
      for (const n of tn) { const re = /[A-Za-z0-9’']{2,}/g; let m; while ((m = re.exec(n.textContent))) { const r = document.createRange(); r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length); const tops = new Set([...r.getClientRects()].filter((q) => q.width > 0.5).map((q) => Math.round(q.top / 4))); if (tops.size > 1) { out.push({ kind: 'word-broken', what: '"' + m[0] + '" breaks across ' + tops.size + ' lines in ' + desc(el) }); break; } } }
    }
  }

  // 3. a box that scrolls on its own but hides part of what's in it (a list cut halfway through a row). Sideways strips meant to swipe carry data-lc-scroll.
  for (const el of document.body.querySelectorAll('*')) {
    if (el.closest('[data-lc-scroll]') || el.closest('[data-lc-skip]')) continue;
    const c = getComputedStyle(el); const sy = c.overflowY === 'auto' || c.overflowY === 'scroll'; const sx = c.overflowX === 'auto' || c.overflowX === 'scroll';
    if (!sy && !sx) continue; if (!shown(el) || el.tagName === 'TEXTAREA') continue;
    if (!(el.innerText || '').trim()) continue;
    if ((sy && el.scrollHeight > el.clientHeight + 2) || (sx && el.scrollWidth > el.clientWidth + 2)) out.push({ kind: 'content-hidden', what: desc(el) + ' hides part of its content (' + el.scrollWidth + 'x' + el.scrollHeight + ' in ' + el.clientWidth + 'x' + el.clientHeight + ')' });
  }

  // 4. overlaps among things in the page flow
  const inter = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2;
  const inside = (a, b) => a.left >= b.left - 1 && a.right <= b.right + 1 && a.top >= b.top - 1 && a.bottom <= b.bottom + 1; // a inside b
  const flow = items.filter((i) => !i.fixed);
  const seen = new Set();
  for (let i = 0; i < flow.length; i++) for (let j = i + 1; j < flow.length; j++) {
    const A = flow[i], B = flow[j];
    if (A.el.contains(B.el) || B.el.contains(A.el)) continue;
    const la = A.el.closest('[data-lc-layers]'); if (la && la === B.el.closest('[data-lc-layers]')) continue; // drawn in layers on purpose (a slider's fill under its label)
    if (A.sticky !== B.sticky) continue; // the page under a pinned bar; what's inside the bar is still checked against itself
    if (!inter(A.r, B.r)) continue;
    let bad = false;
    if (A.text && B.text && !(A.paint && inside(B.r, A.r)) && !(B.paint && inside(A.r, B.r))) bad = true;
    else if (inside(B.r, A.r)) bad = !A.paint; // B sits on A's text
    else if (inside(A.r, B.r)) bad = !B.paint;
    else bad = true; // crossing edges
    if (bad) { const k = desc(A.el) + ' | ' + desc(B.el); if (!seen.has(k)) { seen.add(k); out.push({ kind: 'overlap', what: desc(A.el) + ' overlaps ' + desc(B.el) }); } }
  }
  if (window.__lcDebug) window.__lcItems = items.map((i) => ({ d: desc(i.el), r: i.r, text: i.text, paint: i.paint, fixed: !!i.fixed }));
  return { out, fixedItems: items.filter((i) => i.fixed).length };
}

// At the bottom of the page, nothing may sit under the fixed chat bar or footers.
function auditBottom() {
  const out = []; const band = document.querySelector('.chatwrap:not(.chatoff) .chatband'); if (!band) return out;
  const b = band.getBoundingClientRect(); if (b.height < 1) return out;
  for (const el of document.querySelectorAll('main *, .stepfoot *')) {
    if (el.closest('.chatwrap') || el.closest('.toast')) continue;
    const c = getComputedStyle(el); if (c.position === 'fixed') continue;
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()) || /^(BUTTON|INPUT|IMG|TEXTAREA)$/.test(el.tagName);
    if (!own) continue; let hidden = false; for (let e = el; e; e = e.parentElement) { const ec = getComputedStyle(e); if (ec.display === 'none' || ec.visibility === 'hidden' || +ec.opacity === 0) { hidden = true; break; } } if (hidden) continue;
    const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
    if (r.bottom > b.top + 2 && r.top < b.bottom) out.push({ kind: 'under-chat-bar', what: el.tagName.toLowerCase() + ' "' + (el.innerText || el.value || '').trim().slice(0, 40) + '" is under the chat bar at the bottom of the page' });
  }
  return out;
}

module.exports = { audit, auditBottom };
if (require.main === module) (async () => {
  const browser = await chromium.launch();
  let total = 0; const summary = [];
  if (shotsAt) fs.mkdirSync(shotsAt, { recursive: true });
  for (const s of SCREENS) for (const w of WIDTHS) for (const theme of THEMES) {
    const h = heightFor(w);
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: shotsAt ? 2 : 1, colorScheme: theme });
    const page = await ctx.newPage(); const errs = [];
    page.on('pageerror', (e) => errs.push(e.message));
    await page.goto(UI + '?start=' + s.start + '&theme=' + theme);
    await page.evaluate(() => document.fonts.ready); await page.waitForTimeout(150);
    if (s.js) await page.evaluate('(async()=>{' + s.js + '})()');
    await page.waitForTimeout(450);
    const res = await page.evaluate(audit);
    const probs = res.out.concat(errs.map((e) => ({ kind: 'js-error', what: e })));
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight)); await page.waitForTimeout(80);
    probs.push(...(await page.evaluate(auditBottom)));
    await page.evaluate(() => window.scrollTo(0, 0));
    if (shotsAt) await page.screenshot({ path: path.join(shotsAt, `${s.id}-${w}-${theme}.png`), fullPage: true });
    const tag = `${s.id} @ ${w} ${theme}`;
    if (probs.length) { total += probs.length; summary.push(tag + ': ' + probs.length); console.log('FAIL ' + tag); for (const p of probs) console.log('   ' + p.kind + ': ' + p.what); }
    else console.log('ok   ' + tag);
    await ctx.close();
  }
  await browser.close();
  const runs = SCREENS.length * WIDTHS.length * THEMES.length;
  console.log(`\n${runs} runs (${SCREENS.length} screens x ${WIDTHS.length} widths x ${THEMES.length} themes), ${total} problems`);
  if (total) { console.log(summary.join('\n')); process.exit(1); }
})();
