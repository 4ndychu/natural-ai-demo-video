// NAVI action guard: what a browser NAVI opens may DO, enforced in code with Chrome's own request interception
// (CDP Fetch, on the whole browser; not by a prompt). NAVI may open and film any page; the guard blocks only the
// actions.
//
// Every request that can change something (any method but GET, HEAD and OPTIONS) is classified against the site's
// guard pack (config/guard/<site>.json) before it leaves the browser:
//   - a known read (a GraphQL query, a listed read-only operation)                        -> allowed
//   - paying, saving a card or subscribing, on EVERY site, with or without a pack (config/guard/_payments.json) -> blocked
//   - a dangerous action (withdraw, transfer, refund, bank/payout details, API keys, team
//     or ownership, deleting anything), in every seat and every business                  -> blocked
//       except deleting NAVI's own "NAVI test" products in a test business, when the
//       caller allows it (the cleanup step)
//   - any other change, in a business marked "real" (Real Biz)                   -> blocked, unless the job
//                                                                                            allowed that change
//   - any other change in the test business                                               -> allowed
//   - a change the pack can't name, in a real business                                    -> blocked (default deny)
//   - a dangerous rule marked "quiet" (a site's own background call, e.g. X preparing a
//     Premium checkout on every page load)                                                -> refused and logged,
//                                                                                            the run carries on
// A blocked request is aborted, written to the guard log (one JSON line each) and, in enforce mode, the run is
// stopped: the caller fails that video with the reason. Nothing ever asks the user mid-run.
//
//   import { installGuard } from "scripts/guard/guard.mjs";
//   const guard = await installGuard(context, { site, seat, business, mode, allow, allowTestDeletes, log });
//   ... guard.blocked  (list of blocked actions)
//
// mode: "enforce" (default), or "learn" (log every write; block every write that isn't a known read, so a
// learning run in a real business can't change anything).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const SAFE = new Set(["GET", "HEAD", "OPTIONS"]);

export function loadPack(site) {
  const f = path.join(ROOT, "config", "guard", `${site}.json`);
  return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : null;
}

const rx = (s) => (s ? new RegExp(s, "i") : null);

// Paying, on every site (config/guard/_payments.json): checked before a site's own pack, and on sites with no pack.
export const PAYMENTS = loadPack("_payments");

// What a request is trying to do: its operations (GraphQL names, server-action ids) and a short text to match.
export function describeRequest(method, url, headers, body) {
  const u = new URL(url);
  const ops = [];
  let parsed;
  if (body && /^\s*[[{]/.test(body)) {
    try {
      parsed = JSON.parse(body);
    } catch {
      /* not JSON */
    }
  }
  for (const item of Array.isArray(parsed) ? parsed : parsed ? [parsed] : []) {
    if (item && typeof item === "object" && (item.query || item.operationName || item.extensions?.persistedQuery)) {
      const q = typeof item.query === "string" ? item.query.trim() : "";
      const kind = /^mutation\b/.test(q) ? "mutation" : /^subscription\b/.test(q) ? "subscription" : q ? "query" : "persisted";
      const name = item.operationName || (q.match(/^(?:query|mutation|subscription)\s+(\w+)/) || [])[1] || "";
      ops.push({ kind, name });
    }
  }
  const action = headers["next-action"];
  if (action) ops.push({ kind: "server-action", name: action });
  return { method, host: u.host, path: u.pathname, query: u.search.slice(0, 200), ops, body: (body || "").slice(0, 4000) };
}

// Classify one write request against the pack. Returns {verdict: "allow"|"block", why, category}.
export function classify(req, pack, opts) {
  const { business = null, allow = [], allowTestDeletes = false } = opts;
  const text = `${req.method} ${req.host}${req.path}${req.query} ${req.ops.map((o) => `${o.kind}:${o.name}`).join(" ")} ${req.body}`;
  const opOk = (m) =>
    (!m.op && !m.kind) || req.ops.some((o) => (!m.op || rx(m.op).test(o.name)) && (!m.kind || rx(m.kind).test(o.kind)));
  const matches = (m) =>
    (!m.host || rx(m.host).test(req.host)) &&
    (!m.path || rx(m.path).test(req.path)) &&
    (!m.method || rx(m.method).test(req.method)) &&
    opOk(m) &&
    (!m.empty_body || !req.body.trim()) &&
    (!m.body || rx(m.body).test(req.body)) &&
    (!m.text || rx(m.text).test(text));
  // A request made only of GraphQL queries reads: opening any page (payouts, API keys...) is allowed, so for it only
  // the rules that name a reading operation outright (revealing a key) apply, never an address that mentions refunds.
  const queryOnly = req.ops.length > 0 && req.ops.every((o) => o.kind === "query");
  const dangerMatch = (m) => (queryOnly ? m.op && !m.kind && matches(m) : matches(m));
  // 0. paying, saving a card or subscribing: blocked on every site, with or without a pack, before the pack's own
  //    ignore list (a site's telemetry rule can never let a payment through)
  const shared = opts.payments === undefined ? PAYMENTS : opts.payments;
  if (shared && !(shared.ignore || []).some(matches))
    for (const d of shared.dangerous || []) if ((d.match || []).some(dangerMatch)) return { verdict: "block", category: d.category, why: d.reason };
  if (!pack) return { verdict: "allow", why: "no guard pack for this site" };
  // 1. ignored traffic (analytics, error reporting, telemetry): never a change to the user's account
  for (const m of pack.ignore || []) if (matches(m)) return { verdict: "allow", why: `ignored: ${m.label || "telemetry"}` };
  // 2. dangerous actions: blocked in every seat and every business
  for (const d of pack.dangerous || []) {
    if (!(d.match || []).some(dangerMatch)) continue;
    if (d.category === "delete" && allowTestDeletes && business?.test && (d.test_delete_ok || []).some((k) => text.includes(k)))
      return { verdict: "allow", why: `deleting NAVI's own test item in the test business ${business.name}` };
    // quiet: something the site sends by itself in the background (X preparing a checkout on every page): refused,
    // logged, and the run carries on, since nothing the video does asked for it
    return { verdict: "block", category: d.category, why: d.reason, ...(d.quiet ? { quiet: true } : {}) };
  }
  // 3. reads that happen to use POST (GraphQL queries, read-only server actions): allowed
  const reads = req.ops.length && req.ops.every((o) => o.kind === "query" || (pack.reads || []).some((r) => rx(r).test(o.name)));
  if (reads) return { verdict: "allow", why: "read" };
  for (const m of pack.read_requests || []) if (matches(m)) return { verdict: "allow", why: `read: ${m.label || ""}` };
  // 4. other changes: fine outside a real business; in a real business only what the job allows. Another company's
  //    service inside the page (captcha, payment form) can't change the user's account except through the dangerous
  //    rules above (paying, for example), so it isn't held to the business's rules.
  if (pack.own_hosts && !rx(pack.own_hosts).test(req.host)) return { verdict: "allow", why: `another service (${req.host})` };
  const known = (pack.changes || []).find((c) => (c.match || []).some(matches));
  if (!business?.real) return { verdict: "allow", why: known ? `change: ${known.label}` : "change outside a real business" };
  if (known && allow.includes(known.id)) return { verdict: "allow", why: `change the job asked for: ${known.label}` };
  return {
    verdict: "block",
    category: known ? "change" : "unknown",
    why: known
      ? `${known.label} in ${business.name} (a real business); the job didn't ask for it`
      : `an unrecognised change in ${business.name} (a real business): blocked by default`,
  };
}

// Which business a request acts in: the business whose id is in the page's address (so an owner run that wanders
// from the test business into a real one gets the real business's rules at once). Outside any business dashboard,
// a login acts on the user's own (real) account (this includes a buyer's view on the member-facing pages), so
// unknown changes are blocked there too.
export function businessFor(cfg, pageUrl) {
  // logged out: no saved login is in the browser, so no account of the user's can be changed; unknown changes are
  // still blocked by default, but the reason must not suggest a login was used (FG08, 14 Nov 2026)
  if (cfg.seat === "logged-out") return { name: "no account (logged out)", real: true };
  const u = (pageUrl || "").toLowerCase();
  const hit = (cfg.businesses || []).find((b) => b.id && u.includes(b.id.toLowerCase()));
  if (hit) return hit;
  // a business's community pages (whop.com/navi-test/..., where its courses live) carry its slug, not its id
  let p = "";
  try {
    p = new URL(pageUrl).pathname.toLowerCase();
  } catch {}
  const page = (cfg.businesses || []).find((b) => (b.pages || []).some((x) => x && p.startsWith(x.toLowerCase())));
  if (page) return page;
  if (/\/dashboard\/biz_/.test(u)) return { name: "a business NAVI doesn't know", real: true };
  return { name: "your own account (the owner login)", real: true };
}

// Chrome's own request interception (CDP Fetch), set once on the BROWSER, so it covers every page, popup,
// cross-site frame (payment and captcha frames) and worker in it, before any request leaves the browser. Unlike
// Playwright's route interception it leaves the browser cache on, so pages load and repaint exactly as they would
// without the guard (Andy, 11 Nov 2026: the whop before/after showed more repeated frames with the cache off).
const installed = new WeakMap(); // browser -> state
const header = (h, k) => {
  for (const [n, v] of Object.entries(h || {})) if (n.toLowerCase() === k) return v;
  return undefined;
};
const bodyOf = (req) =>
  req.postData ??
  (req.postDataEntries || []).map((e) => (e.bytes ? Buffer.from(e.bytes, "base64").toString("utf8") : "")).join("");

export async function installGuard(context, cfg) {
  const browser = context.browser();
  if (!browser?.newBrowserCDPSession) throw new Error("The action guard needs Chromium (Chrome's own interception).");
  if (installed.has(browser)) throw new Error("The action guard is already on in this browser.");
  // one pack per site whose login the browser holds (a video on X and Google Sheets uses both); each request is
  // checked against the pack of the site it goes to, else the pack of the page it comes from, else the main site's
  const sites = [...new Set([cfg.site, ...(cfg.sites || [])].filter(Boolean))];
  const packs = cfg.pack ? [[cfg.site, cfg.pack]] : sites.map((s) => [s, loadPack(s)]);
  const hostOf = (u) => {
    try {
      return new URL(u).host;
    } catch {
      return "";
    }
  };
  const onSite = (host, site) => host === site || host.endsWith("." + site);
  const packFor = (host, pageUrl) => {
    const own = (h) => packs.find(([, p]) => p?.own_hosts && rx(p.own_hosts).test(h));
    const hit = own(host) || own(hostOf(pageUrl));
    if (hit) return { site: hit[0], pack: hit[1] };
    const site = sites.find((x) => onSite(host, x)) || sites.find((x) => onSite(hostOf(pageUrl), x)) || cfg.site;
    return { site, pack: (packs.find(([x]) => x === site) || [])[1] ?? null };
  };
  const mode = cfg.mode || "enforce";
  const state = { blocked: [], writes: [], stopped: false };
  installed.set(browser, state);
  const write = (entry) => {
    if (cfg.log) fs.appendFileSync(cfg.log, JSON.stringify({ t: Date.now() / 1000, ...entry }) + "\n");
  };
  const session = await browser.newBrowserCDPSession();
  // the page the user would see: a payment or captcha frame inside it belongs to that page
  const pageUrlFor = async (e) => {
    const pages = context.pages();
    if (pages.length === 1) return pages[0].url();
    const { targetInfos } = await session.send("Target.getTargets").catch(() => ({ targetInfos: [] }));
    const tab = targetInfos.find((t) => t.type === "page" && t.targetId === e.frameId);
    return tab?.url || header(e.request.headers, "referer") || pages[pages.length - 1]?.url() || "";
  };
  const decide = async (e) => {
    const method = e.request.method;
    if (SAFE.has(method)) return true;
    const headers = Object.fromEntries(Object.entries(e.request.headers || {}).map(([k, v]) => [k.toLowerCase(), v]));
    const req = describeRequest(method, e.request.url, headers, bodyOf(e.request));
    const pageUrl = await pageUrlFor(e);
    const business = businessFor(cfg, pageUrl);
    const { site: reqSite, pack } = packFor(req.host, pageUrl);
    let res = classify(req, pack, { ...cfg, business });
    // a site the browser is logged in to, with no rules written for it yet: its changes are blocked (default deny),
    // so a real account is never changed by a site the guard can't read (the old "no pack: allow" only ever applied
    // to single-site runs, where record.py doesn't start the guard without a pack)
    if (!pack && sites.length > 1 && sites.some((x) => onSite(req.host, x)))
      res = { verdict: "block", category: "unknown", why: `no guard rules for ${reqSite} yet: changes on that logged-in account are blocked` };
    if (res.verdict === "allow" && res.why === "change outside a real business") res.why += ` (${reqSite})`;
    if (mode === "learn" && res.verdict === "allow" && !/^(read|ignored)/.test(res.why)) {
      res = { verdict: "block", category: "learn", why: "learning run: every change is blocked" };
    }
    const entry = { seat: cfg.seat, business: business?.name ?? null, page: pageUrl.slice(0, 200), ...req, ...res };
    if (mode === "learn" || cfg.logAll) write({ kind: "write", ...entry });
    if (res.verdict === "allow") return true;
    if (res.quiet && mode !== "learn") {
      write({ kind: "refused", ...entry });
      return false;
    }
    state.blocked.push(entry);
    if (mode !== "learn") write({ kind: "blocked", ...entry });
    if (mode === "enforce" && !state.stopped) {
      state.stopped = true;
      cfg.onBlock?.(entry);
    }
    return false;
  };
  session.on("Fetch.requestPaused", async (e) => {
    let ok = false;
    try {
      ok = await decide(e);
    } catch (err) {
      // never let a request through because the guard itself failed: block it, and say why
      const entry = { seat: cfg.seat, method: e.request.method, host: "", path: e.request.url.slice(0, 200), verdict: "block",
        category: "guard-error", why: `the guard couldn't check this request (${String(err?.message || err).slice(0, 120)})` };
      if (!SAFE.has(e.request.method)) {
        state.blocked.push(entry);
        write({ kind: "blocked", ...entry });
        if (mode === "enforce" && !state.stopped) {
          state.stopped = true;
          cfg.onBlock?.(entry);
        }
      } else ok = true;
    }
    await session
      .send(ok ? "Fetch.continueRequest" : "Fetch.failRequest", ok ? { requestId: e.requestId } : { requestId: e.requestId, errorReason: "BlockedByClient" })
      .catch(() => {});
  });
  await session.send("Fetch.enable", { patterns: [{ urlPattern: "*", requestStage: "Request" }] });
  if (mode === "learn" && context.routeWebSocket) {
    await context.routeWebSocket(/.*/, (ws) => {
      const server = ws.connectToServer();
      ws.onMessage((m) => {
        write({ kind: "ws-send", url: ws.url(), data: String(m).slice(0, 600) });
        server.send(m);
      });
    });
  }
  return state;
}

// The guard's settings for a run, from a JSON file (the recorder passes the path in its scenario).
export async function installFromFile(context, file, onBlock) {
  const cfg = JSON.parse(fs.readFileSync(file, "utf8"));
  return installGuard(context, { ...cfg, onBlock });
}
