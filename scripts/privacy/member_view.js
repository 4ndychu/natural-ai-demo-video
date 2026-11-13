// NAVI member view: film a buyer's view with the owner's login (reference/recording-rules.md 13e).
//
// Runs in every page after blur.js, only for a member-view video. It needs window.__NAVI_MEMBER__ =
// {ownerOnly: [rules], avoid: {url, reason}, current: "/<business slug>/"} from the site's pack
// (config/guard/<site>.json "member_view"). The site's own "preview as a buyer" is already set (a cookie), so this
// only covers what still shows to the owner alone:
// - ownerOnly: controls a buyer never sees (edit menus, dashboard links, the owner's other businesses) are blurred
//   with the same blur as private details, before the browser paints them. A rule is a CSS selector (css), or
//   text (text, a regex on the element's own text, max_chars), narrowed by label_re (its label or text), min_x /
//   max_x (where its left edge is), max_w (how wide it may be) and not_current (skip a link to the business itself).
// - avoid: pages the owner only sees as an editor (whop's lesson pages). Opening one is reported, and the
//   recording fails that video with the reason, rather than show the editor as if it were a buyer's page.
(() => {
  const M = window.__NAVI_MEMBER__;
  if (!M || window.__naviMemberOn) return;
  window.__naviMemberOn = true;
  const mark = window.__naviMark; // blur.js: blur an element and list it for Review
  const rules = (M.ownerOnly || []).map((r) => ({
    ...r,
    textRx: r.text ? new RegExp(r.text, "i") : null,
    labelRx: r.label_re ? new RegExp(r.label_re, "i") : null,
  }));
  const avoidRx = M.avoid?.url ? new RegExp(M.avoid.url) : null;
  const report = (e) => {
    try { window.__screenplayReport?.(e); } catch {}
  };

  const fits = (el, r) => {
    if (el.getAttribute("data-navi-blur")) return false;
    if (r.labelRx) {
      const l = (el.getAttribute("aria-label") || el.innerText || "").trim();
      if (!r.labelRx.test(l)) return false;
    }
    if (r.not_current && M.current && (el.getAttribute("href") || "") === M.current) return false;
    if (r.min_x != null || r.max_x != null || r.max_w != null) {
      const b = el.getBoundingClientRect();
      if (!b.width) return false;
      if (r.min_x != null && b.left < r.min_x) return false;
      if (r.max_x != null && b.left > r.max_x) return false;
      if (r.max_w != null && b.width > r.max_w) return false;
    }
    return true;
  };
  function sweep() {
    if (!document.body) return;
    for (const r of rules) {
      if (r.css) {
        for (const el of document.querySelectorAll(r.css)) if (fits(el, r)) hide(el, r);
      } else if (r.textRx) {
        // the smallest element whose own text matches: the label row, not the whole sidebar
        // textContent, not innerText: it doesn't make the browser lay the page out on every change
        for (const el of document.querySelectorAll("div, li, span, p, label, section")) {
          const t = (el.textContent || "").trim();
          if (!t || t.length > (r.max_chars || 80) || !r.textRx.test(t)) continue;
          if ([...el.children].some((c) => r.textRx.test((c.textContent || "").trim()))) continue;
          if (fits(el, r)) hide(el, r);
        }
      }
    }
  }
  function hide(el, r) {
    if (mark) mark(el, "owner_only", "owner-only control", r.label);
    else el.setAttribute("data-navi-blur", "owner_only");
  }

  let avoided = false;
  const checkPage = () => {
    if (!avoidRx || avoided || !avoidRx.test(location.pathname)) return;
    avoided = true;
    window.__naviAvoided = M.avoid.reason;
    report({ kind: "member-view", event: "avoid", page: location.pathname, reason: M.avoid.reason });
  };
  for (const k of ["pushState", "replaceState"]) {
    const orig = history[k];
    history[k] = function (...args) { const out = orig.apply(this, args); checkPage(); return out; };
  }
  addEventListener("popstate", checkPage);
  checkPage();

  new MutationObserver(() => sweep()).observe(document, { subtree: true, childList: true });
  addEventListener("resize", sweep);
  setInterval(sweep, 250); // layout can move a control into a rule's area without any new element
})();
