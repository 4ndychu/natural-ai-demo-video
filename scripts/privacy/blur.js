// NAVI privacy, layer 2 (reference/privacy.md): blur private things inside the page before they are painted.
//
// Runs in every page and frame before the page's own scripts (the recorder's initScript). It needs
// window.__NAVI_PRIVACY__ = {patterns, categories, blur: [categories to blur], hideWords, blurPx, elementHints,
// typingPrefixes, ignore} set just before it (record.py builds that from patterns.json and the demo's settings).
//
// - Text: matching words are blurred with the CSS Custom Highlight API, so the page's own elements are never
//   changed or wrapped. The blur follows scrolling, layout and zoom by itself.
// - Fields, avatars and account menus: the element itself gets a CSS blur (data-navi-blur attribute).
// - New content is checked in a MutationObserver callback, and field values when they are set or typed. Both run
//   before the browser paints the next frame, so a match is never shown unblurred.
// - Money and key pages (payouts, balances, billing, bank, cards, API keys: C.sensitivePages, matched on the page's
//   address): every number, every filled-in field and every account detail is blurred, whatever the preset, so NAVI
//   can open and film them. The page is checked again whenever its address changes (single-page apps).
// - Every blur is logged (masked, never the text itself) through window.__screenplayReport when the recorder
//   provides it, and kept in window.__naviPrivacyHits.
(() => {
  const C = window.__NAVI_PRIVACY__;
  if (!C || window.__naviPrivacyOn) return;
  window.__naviPrivacyOn = true;

  const active = new Set(C.blur);
  const tierOf = (cat) => (cat === "hide" ? 1 : C.categories[cat]?.tier ?? 2);
  const sensitiveRx = C.sensitivePages ? new RegExp(C.sensitivePages, "i") : null;
  const sensitiveCats = new Set(C.sensitiveCats || []);
  let sensitive = Boolean(sensitiveRx && sensitiveRx.test(location.pathname + location.search));
  const on = (cat) => active.has(cat) || (sensitive && sensitiveCats.has(cat));
  const NUMBER = /\d(?:[\d.,:/\- ]*\d)?/g;
  const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pats = C.patterns.map((p) => ({
    ...p,
    rx: new RegExp(p.re, (p.flags || "") + "g"),
    nearRx: p.near ? new RegExp(p.near, "i") : null,
    suffixRx: p.price_suffix ? new RegExp(p.price_suffix, "i") : null,
  }));
  if (C.hideWords?.length) pats.push({ cat: "hide", rx: new RegExp("\\b(?:" + C.hideWords.map(esc).join("|") + ")\\b", "gi") });
  const ignore = Object.fromEntries(Object.entries(C.ignore || {}).map(([k, v]) => [k, new RegExp(v, "i")]));
  const hints = Object.fromEntries(Object.entries(C.elementHints || {}).map(([k, v]) => [k, new RegExp(v, "i")]));
  const typing = Object.entries(C.typingPrefixes || {}).map(([k, v]) => [k, new RegExp(v)]);
  // Text NAVI will type that has something private in it: the field is blurred from the first letter.
  const typed = (C.typed || []).filter((t) => t.text);

  const luhn = (s) => {
    const d = s.replace(/\D/g, "");
    let sum = 0;
    for (let i = 0; i < d.length; i++) {
      let n = +d[d.length - 1 - i];
      if (i % 2) { n *= 2; if (n > 9) n -= 9; }
      sum += n;
    }
    return d.length >= 13 && sum % 10 === 0;
  };

  /** Matches in `text` to blur: [{s, e, cat}]. `ctx()` gives nearby text, for the context-only categories. */
  function find(text, ctx) {
    const out = [];
    const near = {}; // nearby text, per scope ("control": only the button, link or row the text is in)
    if (sensitive) {
      NUMBER.lastIndex = 0;
      for (let m; (m = NUMBER.exec(text)); ) out.push({ s: m.index, e: m.index + m[0].length, cat: "money_page" });
    }
    for (const p of pats) {
      if (p.cat !== "hide" && !on(p.cat) && !(p.suffixRx && on("price"))) continue;
      const scope = p.near_scope || "";
      if (p.nearRx && !p.nearRx.test(near[scope] ??= (ctx ? ctx(scope) : text))) continue;
      p.rx.lastIndex = 0;
      let m;
      while ((m = p.rx.exec(text))) {
        if (!m[0]) { p.rx.lastIndex++; continue; }
        let s = m.index, e = s + m[0].length;
        if (p.group) {
          const g = m[p.group];
          if (!g) continue;
          s += m[0].lastIndexOf(g); e = s + g.length;
        }
        if (p.min_digits && m[0].replace(/\D/g, "").length < p.min_digits) continue;
        if (p.luhn && !luhn(m[0])) continue;
        let cat = p.cat;
        if (p.suffixRx && p.suffixRx.test(text.slice(e, e + 24))) cat = "price";
        if (ignore[cat] && ignore[cat].test(text.slice(s, e))) continue;
        if (cat !== "hide" && !on(cat)) continue;
        out.push({ s, e, cat });
      }
    }
    return out;
  }

  // ---- styles (an adopted sheet survives the page rewriting its <head>) --------------------------------------
  const px = C.blurPx || 12;
  const sheet = new CSSStyleSheet();
  sheet.replaceSync(
    `::highlight(navi-blur){color:transparent!important;text-shadow:0 0 ${px}px rgba(0,0,0,.8)!important}` +
    `::highlight(navi-blur-light){color:transparent!important;text-shadow:0 0 ${px}px rgba(255,255,255,.85)!important}` +
    `[data-navi-blur]{filter:blur(${px}px)!important}`,
  );
  const adopt = (root) => { if (!root.adoptedStyleSheets.includes(sheet)) root.adoptedStyleSheets = [...root.adoptedStyleSheets, sheet]; };
  adopt(document);
  const dark = new Highlight(), light = new Highlight();
  CSS.highlights.set("navi-blur", dark);
  CSS.highlights.set("navi-blur-light", light);

  // ---- reporting -------------------------------------------------------------------------------------------
  const hits = (window.__naviPrivacyHits = []);
  const tracked = []; // {id, el?, ranges?, visible}
  let nextId = 1;
  const mask = (t, cat) => {
    t = t.trim();
    if (tierOf(cat) === 1) return `${"•".repeat(4)} (${t.length} characters)`;
    return t.length <= 3 ? "•••" : `${t[0]}•••${t[t.length - 1]} (${t.length} characters)`;
  };
  const describe = (el) => {
    if (!el) return "";
    const id = el.id ? `#${el.id}` : "";
    const cls = typeof el.className === "string" && el.className.trim() ? "." + el.className.trim().split(/\s+/).slice(0, 2).join(".") : "";
    return (el.tagName || "").toLowerCase() + id + cls;
  };
  const report = (entry) => {
    try { window.__screenplayReport?.(entry); } catch {}
  };
  function track(cat, how, text, el, ranges) {
    const hit = { id: `${location.host}#${nextId++}`, cat, tier: tierOf(cat), how, preview: mask(text, cat), where: describe(el), page: location.pathname };
    hits.push(hit);
    tracked.push({ id: hit.id, el, ranges, visible: false });
    report({ kind: "privacy", event: "blur", ...hit });
  }

  // ---- text ------------------------------------------------------------------------------------------------
  const textRanges = new WeakMap(); // Text -> {ranges, hl}
  const SKIP = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE", "TITLE", "TEXTAREA"]);
  const context = (node) => {
    const p = node.parentElement;
    const box = p?.closest("label,li,tr,td,dd,dl,p,fieldset,form,section,article") || p?.parentElement || p;
    return ((box?.textContent || "") + " " + (p?.getAttribute?.("aria-label") || "")).slice(0, 600);
  };
  // the button, link, list row or paragraph the text is in, and nothing around it
  const controlContext = (node) => {
    // a control within three levels up; otherwise the two levels around the text ("6" + "members")
    let box = null;
    for (let e = node.parentElement, i = 0; e && i < 3 && !box; e = e.parentElement, i++) if (e.matches("button,a,li,p,label,td,dd")) box = e;
    return ((box || node.parentElement?.parentElement || node.parentElement)?.textContent || "").slice(0, 300);
  };
  const isLight = (el) => {
    const m = getComputedStyle(el).color.match(/\d+(\.\d+)?/g);
    if (!m) return false;
    const [r, g, b] = m.map(Number);
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255 > 0.6;
  };
  function scanText(node) {
    const old = textRanges.get(node);
    if (old) { for (const r of old.ranges) old.hl.delete(r); textRanges.delete(node); }
    const p = node.parentElement;
    if (!p || SKIP.has(p.tagName) || !node.data.trim()) return;
    const found = find(node.data, (scope) => (scope === "control" ? controlContext(node) : context(node)));
    if (!found.length) return;
    const hl = isLight(p) ? light : dark;
    const ranges = [];
    for (const f of dedupe(found)) {
      const r = new Range();
      r.setStart(node, f.s); r.setEnd(node, f.e);
      hl.add(r); ranges.push(r);
      track(f.cat, "text", node.data.slice(f.s, f.e), p, [r]);
    }
    textRanges.set(node, { ranges, hl });
  }
  const dedupe = (fs) => {
    fs.sort((a, b) => a.s - b.s || b.e - a.e);
    const out = [];
    for (const f of fs) {
      const last = out[out.length - 1];
      if (!last || f.s >= last.e) out.push(f);
      // on a money or key page, overlapping matches join, so a number running past a date ("May 13, 2025, 8:01")
      // is blurred to its end; elsewhere the first match wins, as before
      else if (sensitive && f.e > last.e) last.e = f.e;
    }
    return out;
  };

  // ---- elements: fields, avatars, account menus ------------------------------------------------------------
  const attrs = (el) => el ? [el.id, typeof el.className === "string" ? el.className : "", el.getAttribute("aria-label"), el.getAttribute("alt"),
    el.getAttribute("title"), el.getAttribute("data-testid"), el.getAttribute("name"), (el.getAttribute("src") || "").split("/").pop()].filter(Boolean).join(" ") : "";
  function mark(el, cat, how, text) {
    if (el.getAttribute("data-navi-blur")) return;
    el.setAttribute("data-navi-blur", cat);
    track(cat, how, text || attrs(el) || el.tagName, el, null);
  }
  window.__naviMark = mark; // for member_view.js: owner-only controls get the same blur and the same Review entry
  function checkField(el) {
    const type = (el.getAttribute("type") || "").toLowerCase();
    if (type === "password") { if (active.has("password")) mark(el, "password", "field", "password"); return; }
    if (el.getAttribute("autocomplete") === "one-time-code" && active.has("code")) return mark(el, "code", "field", "code");
    const v = el.value || "";
    if (!v) return;
    if (sensitive && type !== "search" && v.trim()) return mark(el, "money_page", "field", v);
    const t = typed.find((x) => x.text.startsWith(v) || v.includes(x.text));
    if (t) return mark(el, t.cat, "field", v);
    const ctx = () => [el.getAttribute("aria-label"), el.getAttribute("name"), el.getAttribute("placeholder"), el.labels?.[0]?.textContent, context(el)].join(" ");
    const f = find(v, ctx)[0];
    if (f) return mark(el, f.cat, "field", v);
    for (const [cat, rx] of typing) if (active.has(cat) && rx.test(v)) return mark(el, cat, "field", v);
  }
  function checkElement(el) {
    if (!(el instanceof Element)) return;
    if (el.shadowRoot) watch(el.shadowRoot);
    const tag = el.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") return checkField(el);
    if (el.getAttribute("data-navi-blur")) return;
    const a = attrs(el), pa = attrs(el.parentElement);
    const visual = tag === "IMG" || tag === "svg" || tag === "CANVAS" || tag === "PICTURE" || tag === "VIDEO" ||
      (el.style?.backgroundImage || "").includes("url(");
    if (on("photo") && visual && (hints.photo?.test(a) || hints.photo?.test(pa) || roundSmall(el))) return mark(el, "photo", "image");
    if (on("name") && hints.name?.test(a) && (el.textContent || "").trim().length <= 80 && (el.textContent || "").trim())
      return mark(el, "name", "element", el.textContent);
  }
  function roundSmall(el) {
    if (el.tagName !== "IMG") return false;
    const r = el.getBoundingClientRect(), br = parseFloat(getComputedStyle(el).borderTopLeftRadius) || 0;
    return r.width > 0 && r.width <= 96 && Math.abs(r.width - r.height) < 4 && br >= r.width * 0.4;
  }

  // Field values set by the page's scripts (React and others set .value directly; no event, no mutation).
  for (const proto of [HTMLInputElement.prototype, HTMLTextAreaElement.prototype]) {
    const d = Object.getOwnPropertyDescriptor(proto, "value");
    Object.defineProperty(proto, "value", { ...d, set(v) { d.set.call(this, v); queueMicrotask(() => checkField(this)); } });
  }
  document.addEventListener("input", (e) => checkElement(e.target), true);

  // ---- walking and watching --------------------------------------------------------------------------------
  function scanTree(root) {
    if (!root) return;  // the script runs before the page has a document element; the observer sees it arrive
    if (root.nodeType === Node.TEXT_NODE) return scanText(root);
    if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_FRAGMENT_NODE) return;
    if (root.nodeType === Node.ELEMENT_NODE) checkElement(root);
    const w = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) n.nodeType === Node.TEXT_NODE ? scanText(n) : checkElement(n);
  }
  // New text can turn an empty account menu into one with a name in it, so the elements around it are checked again.
  const recheckAround = (node) => {
    let el = node.nodeType === Node.ELEMENT_NODE ? node.parentElement : node.parentElement?.parentElement;
    for (let i = 0; el && i < 4; i++, el = el.parentElement) if (!el.getAttribute("data-navi-blur")) checkElement(el);
  };
  const mo = new MutationObserver((recs) => {
    for (const r of recs) {
      if (r.type === "characterData") { scanText(r.target); recheckAround(r.target); }
      else if (r.type === "attributes") { if (r.attributeName !== "data-navi-blur") checkElement(r.target); }
      else { for (const n of r.addedNodes) scanTree(n); if (r.addedNodes.length) recheckAround(r.addedNodes[0]); }
    }
  });
  const opts = { subtree: true, childList: true, characterData: true, attributes: true,
    attributeFilter: ["value", "src", "alt", "class", "aria-label", "type", "style", "autocomplete"] };
  function watch(root) {
    if (root.__naviWatched) return;
    root.__naviWatched = true;
    if (root !== document) adopt(root);
    mo.observe(root, opts);
    scanTree(root === document ? document.documentElement : root);
  }
  watch(document);
  // a single-page app changes its address without a new page: check again when a money or key page opens
  let lastPath = location.pathname + location.search;
  const pageChanged = () => {
    const now = location.pathname + location.search;
    if (now === lastPath) return;
    lastPath = now;
    const was = sensitive;
    sensitive = Boolean(sensitiveRx && sensitiveRx.test(now));
    if (sensitive !== was && document.documentElement) scanTree(document.documentElement);
  };
  for (const k of ["pushState", "replaceState"]) {
    const orig = history[k];
    history[k] = function (...args) { const r = orig.apply(this, args); pageChanged(); return r; };
  }
  addEventListener("popstate", pageChanged);

  // ---- when each blur is on screen, for the Review list ------------------------------------------------------
  const onScreen = (t) => {
    const rects = t.ranges ? t.ranges.flatMap((r) => [...r.getClientRects()]) : t.el?.isConnected ? [t.el.getBoundingClientRect()] : [];
    return rects.some((q) => q.width > 0 && q.height > 0 && q.bottom > 0 && q.right > 0 && q.top < innerHeight && q.left < innerWidth);
  };
  setInterval(() => {
    for (const t of tracked) {
      const v = onScreen(t);
      if (v !== t.visible) { t.visible = v; report({ kind: "privacy", event: v ? "show" : "hide", id: t.id }); }
    }
  }, 100);
})();
