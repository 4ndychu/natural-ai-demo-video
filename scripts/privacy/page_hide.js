// NAVI: page parts taken off the page before recording (config recording.hide_on_page), such as a site's own
// nagging banner that isn't part of any lesson (Andy, 13 Nov 2026: Whop's yellow "Confirm your tax details").
// Hidden, not blurred: the page closes up as if the banner weren't there.
// Each rule: {site, text, max_chars?, max_height?}. The banner is the largest element around that text that still
// holds little else (at most max_chars of text, at most max_height px tall), so the page around it is never hidden.
// Runs in every page (the recorder's initScript, after the blur) and again whenever the page changes.
(() => {
  const host = location.hostname;
  const rules = (window.__NAVI_HIDE__ || []).filter((r) => !r.site || host === r.site || host.endsWith("." + r.site));
  if (!rules.length) return;
  window.__naviHidden = window.__naviHidden || [];
  const boxFor = (node, r) => {
    let box = null;
    for (let e = node.parentElement; e && e !== document.body && e !== document.documentElement; e = e.parentElement) {
      const text = (e.innerText || e.textContent || "").trim();
      const h = e.getBoundingClientRect().height;
      if (text.length > (r.max_chars || 400) || h > (r.max_height || 160)) break;
      box = e;
    }
    return box;
  };
  const run = () => {
    if (!document.body) return;
    for (const r of rules) {
      const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      for (let n; (n = walk.nextNode()); ) {
        if (!n.nodeValue || !n.nodeValue.includes(r.text)) continue;
        const box = boxFor(n, r);
        if (!box || box.hasAttribute("data-navi-hidden")) continue;
        box.style.setProperty("display", "none", "important");
        box.setAttribute("data-navi-hidden", r.text);
        window.__naviHidden.push(r.text);
      }
    }
  };
  let queued = false;
  const soon = () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; run(); }); } };
  const start = () => { run(); new MutationObserver(soon).observe(document.documentElement, { childList: true, subtree: true, characterData: true }); };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
