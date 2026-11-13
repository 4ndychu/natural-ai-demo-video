// NAVI: is every saved login still working? Checked live, headless (nothing comes to the front), with the action
// guard on, so a check can't change anything.
//
// For each seat (scripts/seats/seats.py), open its home page with its saved session and decide:
//   working      the page stays put and shows no sign-in form
//   needs login  no saved session, or the site sent it to a sign-in page, bounced it elsewhere with a "next=" back
//                to the page, or shows a password field
//   unreachable  the page didn't load (offline, the site is down)
// Writes $NAVI_DATA/login-status.json ({"<site>/<seat>": {status, url, checked, detail}}) and prints it.
//
//   node scripts/seats/check_logins.mjs [--site whop.com] [--seat owner] [--pages url1,url2]
//     --pages: also check these pages are reachable with that login (the batch preflight passes each video's
//              start page); each gets {url, ok, status, final}.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const { launchBrowser, realUserAgent } = await import(path.join(ROOT, "recorder", "agent-screenplay", "dist", "drivers", "browser.js"));
const { config, sessionFile, guardConfig, dataDir } = await import(path.join(ROOT, "scripts", "seats", "seats.mjs"));
const { installGuard, loadPack } = await import(path.join(ROOT, "scripts", "guard", "guard.mjs"));

const argv = process.argv.slice(2);
const opt = (k) => (argv.includes(`--${k}`) ? argv[argv.indexOf(`--${k}`) + 1] : undefined);
const SIGN_IN_URL = /\/(login|log-in|signin|sign-in|sign_in|auth|sso|oauth|session\/new)(\/|\?|$)/i;

const cfg = config();
const wanted = [];
for (const [site, s] of Object.entries(cfg)) {
  if (opt("site") && site !== opt("site")) continue;
  for (const [seat, info] of Object.entries(s.seats || {})) {
    if (opt("seat") && seat !== opt("seat")) continue;
    wanted.push({ site, seat, home: info.home || `https://${site}/` });
  }
}
const pages = (opt("pages") || "").split(",").filter(Boolean);
const statusFile = path.join(dataDir(), "login-status.json");
let all = {};
try {
  all = JSON.parse(fs.readFileSync(statusFile, "utf8"));
} catch {
  /* first check */
}

async function check({ site, seat, home }) {
  const out = { site, seat, url: home, checked: Math.round(Date.now() / 1000) };
  const session = sessionFile(site, seat);
  if (!session) return { ...out, status: "needs login", detail: "never logged in" };
  const b = await launchBrowser({ headless: true });
  try {
    const c = await b.newContext({ userAgent: await realUserAgent(b), viewport: { width: 1440, height: 810 }, storageState: session });
    if (loadPack(site)) await installGuard(c, guardConfig({ site, seat }));
    const p = await c.newPage();
    const loggedIn = async (url) => {
      const r = await p.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 }).catch((e) => ({ error: e }));
      if (r?.error) return { reachable: false, detail: String(r.error.message).split("\n")[0].slice(0, 120) };
      await p.waitForLoadState("load", { timeout: 15000 }).catch(() => {});
      await p.waitForTimeout(2500);
      const final = p.url();
      const password = await p.locator("input[type=password]:visible").count().catch(() => 0);
      const f = new URL(final);
      const asked = new URL(url);
      // sent somewhere else with a "come back to" address (whop: whop.com/?next=/dashboard/...): a sign-in bounce
      const bounced = f.pathname !== asked.pathname && [...f.searchParams.keys()].some((k) => /^(next|redirect|redirect_?to|return_?to|returnTo|continue|callbackUrl|from)$/i.test(k));
      const signIn = SIGN_IN_URL.test(f.pathname + f.search) || password > 0 || bounced;
      return { reachable: true, signIn, final, http: r?.status?.() ?? null };
    };
    const h = await loggedIn(home);
    if (!h.reachable) return { ...out, status: "unreachable", detail: h.detail };
    const res = { ...out, status: h.signIn ? "needs login" : "working", final: h.final, detail: h.signIn ? "the site asked to sign in again" : "" };
    if (pages.length && !h.signIn) {
      res.pages = [];
      for (const u of pages) {
        const r = await loggedIn(u);
        res.pages.push({ url: u, ok: r.reachable && !r.signIn && (r.http == null || r.http < 400), status: r.http, final: r.final, detail: r.detail || (r.signIn ? "asked to sign in" : "") });
      }
    }
    return res;
  } finally {
    await b.close();
  }
}

const results = [];
for (const w of wanted) {
  const r = await check(w);
  results.push(r);
  all[`${w.site}/${w.seat}`] = r;
}
fs.mkdirSync(path.dirname(statusFile), { recursive: true });
fs.writeFileSync(statusFile, JSON.stringify(all, null, 1), { mode: 0o600 });
console.log(JSON.stringify(results));
