// NAVI explore: look around a site before writing the script, without ever taking over the Mac.
//
// The browser is always headless: no window, no Dock icon, nothing comes to the front, the mouse and keyboard stay
// the user's. There is deliberately no option to show it (recording-rules.md rule 22). It uses the saved login
// and the same browser, size and user agent as the recording, so what it finds is what the recording will meet.
//
//   node scripts/explore/explore.mjs --url https://whop.com/dashboard --site whop.com [--seat owner] --out <folder> [--steps steps.json]
//
// --allow a,b: the changes the video's job asks for (the script's seat "allow"; on a real account nothing else changes).
// --seats x.com:owner,google.com:owner: a video on two or more logins (X and Google Sheets, Claude and Grok): one
// browser holding every one of them (scripts/seats/seats.py merged_login); the guard checks each site with its own pack.
// --seat picks which saved login to use (scripts/seats/seats.py; default: the site's default seat). The action guard
// (scripts/guard/guard.mjs) runs on every page: a blocked action stops the explore with the reason (exit code 3).
// In a real business the privacy blur runs too, so the screenshots never keep real numbers.
// --learn: log every request that could change something to guard-log.jsonl and block all of them (used to find a
// site's real operations for its guard pack, safely, even in a real business).
// --log-writes: guard as usual, and also log the changes it lets through (in a test business, to learn a flow).
// --member <business> --preview-as <product>: a buyer's view with the owner login (recording-rules.md 13e): the
// site's own preview-as-a-buyer is set first, the privacy blur and the owner-only blur are on, as in the recording.
//
// steps.json is a list run in order, one screenshot after each:
//   {"goto": "https://..."}  {"click": "Create product"}  {"click": {"role": "button", "name": "Next"}}
//   {"click": {"css": "#id"}}  {"fill": ["Product name", "Test product"]}  {"press": "Enter"}  {"hover": "Module 01"}  {"wait": 1500}
//   {"scroll": 600}
// Text is matched as on screen (button, link, label or placeholder text). Any page may be opened; the guard blocks the actions
// (withdraw, transfers, refunds, bank and payout details, API keys, team, deleting, and in a real business any change
// the job didn't ask for).
//
// Writes into <folder>: 00-start.png, 01-<step>.png ... and explore.json (per screen: url, title, load time, every
// visible button/link/field with its text and box). Nothing leaves the Mac.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const AS = path.join(ROOT, "recorder", "agent-screenplay");
const { launchBrowser, realUserAgent, botCheck } = await import(path.join(AS, "dist", "drivers", "browser.js"));
const { sessionFile, guardConfig, businesses, joinedSession, loginSite } = await import(path.join(ROOT, "scripts", "seats", "seats.mjs"));
const { installGuard, loadPack, businessFor } = await import(path.join(ROOT, "scripts", "guard", "guard.mjs"));

const argv = process.argv.slice(2);
const opt = (k) => {
  const i = argv.indexOf(`--${k}`);
  return i >= 0 ? argv[i + 1] : undefined;
};
if (argv.includes("--headed") || argv.includes("--show")) {
  console.error("explore never shows a browser: NAVI must not take over the Mac. Only `login` opens a window.");
  process.exit(2);
}
const url = opt("url");
const out = opt("out");
if (!url || !out) {
  console.error("usage: node scripts/explore/explore.mjs --url <url> --out <folder> [--site <site> | --session <file>] [--steps steps.json]");
  process.exit(2);
}
const outAbs = path.resolve(out);
if ((outAbs === ROOT || outAbs.startsWith(ROOT + path.sep)) && !outAbs.startsWith(path.join(ROOT, "output") + path.sep)) {
  console.error("Explore output goes in output/ (gitignored), never elsewhere in the repo.");
  process.exit(2);
}
const dataDir = process.env.NAVI_DATA || path.join(os.homedir(), "Library", "Application Support", "NAVI");
const site = opt("site");
const seat = opt("seat");
// --seats: every login the video uses, the main one (--site/--seat) first
const pairs = (opt("seats") || "").split(",").filter(Boolean).map((x) => x.split(":"));
if (site && pairs.length && !pairs.some(([s]) => loginSite(s) === loginSite(site))) pairs.unshift([site, seat]);
let session;
try {
  // --logged-out (or the seat "logged-out"): the public pages as a visitor sees them, even with a saved login
  session = argv.includes("--logged-out") || seat === "logged-out" ? undefined
    : opt("session") || (pairs.length > 1 ? joinedSession(pairs) : site ? sessionFile(site, seat) : undefined);
} catch (e) {
  console.error(e.message);
  process.exit(2);
}
if (pairs.length > 1) console.log(`logins: ${pairs.map(([s, st]) => `${loginSite(s)} (${st || "owner"})`).join(" + ")}, in one browser`);
if (opt("session") && !fs.existsSync(session)) throw new Error(`No saved session at ${session}.`);
if (site && !session && (argv.includes("--logged-out") || seat === "logged-out")) console.log("logged out: the pages as a visitor sees them");
else if (site && !session) {
  if (seat) {
    console.error(`The ${seat} seat on ${site} isn't logged in. Log it in from Settings > Logins first.`);
    process.exit(2);
  }
  console.error(`No saved login for ${site}: exploring logged out. Log in first (the one time a window opens).`);
}
void dataDir;
const steps = opt("steps") ? JSON.parse(fs.readFileSync(opt("steps"), "utf8")) : [];
const defaults = JSON.parse(fs.readFileSync(path.join(ROOT, "config", "defaults.json"), "utf8"));
// --device "iPhone 15": the phone profile the recording uses (Playwright's device list): size, user agent, touch
const { devices } = await import(path.join(AS, "node_modules", "playwright-core", "index.mjs"));
const device = opt("device") ? devices[opt("device")] : null;
if (opt("device") && !device) {
  console.error(`Unknown device "${opt("device")}" (Playwright's device list, e.g. "iPhone 15").`);
  process.exit(2);
}
const [vw, vh] = device ? [device.viewport.width, device.viewport.height] : defaults.recording?.viewport ?? [1440, 810];

fs.mkdirSync(out, { recursive: true });
const browser = await launchBrowser({ headless: true });
const context = await browser.newContext({
  userAgent: device ? device.userAgent : await realUserAgent(browser),
  viewport: { width: vw, height: vh },
  ...(device ? { isMobile: device.isMobile, hasTouch: device.hasTouch } : {}),
  storageState: session,
});
// the action guard, on every page of every seat; a blocked action ends the explore with the reason
const guardSite = site || new URL(url).hostname.replace(/^www\./, "");
let blocked;
const guardCfg = guardConfig({ site: guardSite, seat, mode: argv.includes("--learn") ? "learn" : "enforce",
  log: path.join(outAbs, "guard-log.jsonl"), sites: pairs.map(([s]) => s),
  // --allow grok-message,claude-message: the changes this video's job asks for (its seat's "allow"), as in the take
  allow: (opt("allow") || "").split(",").filter(Boolean) });
guardCfg.logAll = argv.includes("--log-writes"); // log every change the guard lets through too
const guard = guardCfg.sites.some((x) => loadPack(x)) || guardCfg.sites.length > 1 || argv.includes("--learn")
  ? await installGuard(context, { ...guardCfg, onBlock: (e) => (blocked = e) })
  : null;
// a real business: blur before paint, so screenshots keep no real numbers (the same blur as the recording)
const biz = businessFor(guardCfg, url);
if (guard && biz?.real && biz.name !== "your own account (the owner login)") {
  const { execFileSync } = await import("node:child_process");
  const js = execFileSync(path.join(ROOT, ".venv", "bin", "python"), ["-c",
    "import sys,json;sys.path.insert(0,'scripts/privacy');import privacy;print(privacy.init_script(privacy.settings({})))"],
    { cwd: ROOT, encoding: "utf8", maxBuffer: 1 << 24 });
  await context.addInitScript({ content: js });
  console.log(`${biz.name} is a real business: the privacy blur is on for every screenshot.`);
}
void businesses;
// a buyer's view: the same preview cookie, blur and owner-only blur as the recording (record.py member_view)
if (opt("member")) {
  const mv = loadPack(guardSite)?.member_view;
  const bz = businesses(guardSite).find((x) => x.key === opt("member"));
  if (!mv || !bz || !opt("preview-as")) {
    console.error("--member needs a business key from seats.json, --preview-as <product id>, and member_view rules in the site's pack.");
    process.exit(2);
  }
  await context.addCookies([{ name: mv.preview_cookie.replace("{business_id}", bz.id), value: opt("preview-as"), domain: guardSite, path: "/" }]);
  const { execFileSync } = await import("node:child_process");
  const blurJs = execFileSync(path.join(ROOT, ".venv", "bin", "python"), ["-c",
    "import sys,json;sys.path.insert(0,'scripts/privacy');import privacy;print(privacy.init_script(privacy.settings({})))"],
    { cwd: ROOT, encoding: "utf8", maxBuffer: 1 << 24 });
  const current = (new URL(url).pathname.match(/^\/[^/]+\//) || [null])[0];
  await context.addInitScript({ content: blurJs + "\nwindow.__NAVI_MEMBER__ = " + JSON.stringify({ ownerOnly: mv.owner_only, avoid: mv.avoid, current }) + ";\n" +
    fs.readFileSync(path.join(ROOT, "scripts", "privacy", "member_view.js"), "utf8") });
  console.log(`member view: previewing as a buyer of ${opt("preview-as")} in ${bz.name}; owner-only controls blurred`);
}
const page = await context.newPage();
const screens = [];

const slugOf = (s) => JSON.stringify(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40);
const settle = async () => {
  const t = Date.now();
  await page.waitForLoadState("load", { timeout: 30000 }).catch(() => {});
  // Settled = the network went quiet, or the page stopped changing for 0.9 s, whichever comes first (at most 8 s).
  // Apps that keep live connections open (whop.com) never go quiet, so waiting for the network alone cost the
  // full 8 s on every single step: 5 runs of 27 steps took 18 minutes (12 Nov 2026).
  const still = page.evaluate(() => new Promise((done) => {
    let timer = setTimeout(done, 900);
    const o = new MutationObserver(() => { clearTimeout(timer); timer = setTimeout(() => { o.disconnect(); done(); }, 900); });
    o.observe(document.documentElement, { childList: true, subtree: true });
    setTimeout(() => { o.disconnect(); done(); }, 8000);
  })).catch(() => {});
  await Promise.race([page.waitForLoadState("networkidle", { timeout: 8000 }).catch(() => {}), still]);
  return Date.now() - t;
};
const describe = () =>
  page.evaluate(() => {
    const seen = [];
    const sel = 'a[href], button, [role="button"], [role="link"], [role="tab"], [role="menuitem"], input, select, textarea, [contenteditable="true"]';
    // page areas too (a script may point at a list or a footer), so positions can be checked for them as well
    const areas = 'header, footer, nav, aside, main, form, section, ul, ol, table, [role="dialog"], [role="navigation"]';
    const isArea = (el) => el.matches(areas) && !el.matches(sel);
    for (const el of [...document.querySelectorAll(sel)].concat([...document.querySelectorAll(areas)].filter(isArea))) {
      const r = el.getBoundingClientRect();
      if (r.width < 2 || r.height < 2 || r.bottom < 0 || r.top > innerHeight * 3) continue;
      const cs = getComputedStyle(el);
      if (cs.visibility === "hidden" || cs.display === "none" || Number(cs.opacity) === 0) continue;
      const label = el.labels?.[0]?.innerText || el.getAttribute("aria-label") || el.getAttribute("placeholder") || "";
      // the panel it sits in (a form, side panel, dialog or card narrower than the page), so a script can say where
      // it is in a way a viewer reads it: "the bottom right of the form" can be the bottom left of the screen
      let panel;
      for (let p = el.parentElement, i = 0; p && p !== document.body && i < 25; p = p.parentElement, i++) {
        const q = p.getBoundingClientRect();
        if ((q.width >= r.width * 1.4 || q.height >= r.height * 1.4) && q.width <= innerWidth * 0.75 && q.height >= innerHeight * 0.35) {
          panel = { box: [Math.round(q.x), Math.round(q.y), Math.round(q.width), Math.round(q.height)],
                    kind: p.getAttribute("role") || p.tagName.toLowerCase() };
          break;
        }
      }
      const text = (el.innerText || el.value || "").trim().replace(/\s+/g, " ").slice(0, 80);
      seen.push({
        tag: el.tagName.toLowerCase(),
        role: el.getAttribute("role") || undefined,
        id: el.id || undefined,
        cls: (typeof el.className === "string" ? el.className : "").trim().split(/\s+/).filter(Boolean).slice(0, 6).join(" ") || undefined,
        area: isArea(el) || undefined,
        text: text || undefined,
        href: el.getAttribute("href") || undefined,
        label: label.trim().slice(0, 80) || undefined,
        box: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
        below_fold: r.top > innerHeight || undefined,
        panel: panel ?? null,
      });
    }
    return seen;
  });
const locate = (target) => {
  if (typeof target === "string") {
    return page
      .getByRole("button", { name: target })
      .or(page.getByRole("link", { name: target }))
      .or(page.getByLabel(target))
      .or(page.getByPlaceholder(target))
      .or(page.getByText(target, { exact: true }))
      .first();
  }
  if (target.css) return page.locator(target.css).first();
  return page.getByRole(target.role, { name: target.name }).first();
};
const shot = async (n, label, ms, error) => {
  const file = `${String(n).padStart(2, "0")}-${label}.png`;
  await page.screenshot({ path: path.join(out, file) });
  const s = { n, step: label, file, url: page.url(), title: await page.title().catch(() => ""), settle_ms: ms, error, check: await botCheck(page) };
  s.elements = await describe().catch(() => []);
  screens.push(s);
  console.log(`${file}  ${s.url}  (${ms} ms${error ? `, ${error}` : ""}${s.check ? `, bot check: ${s.check}` : ""}) ${s.elements.length} controls`);
};

try {
  const t = Date.now();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
  await shot(0, "start", Date.now() - t + (await settle()));
  for (const [i, st] of steps.entries()) {
    const label = slugOf(st);
    const t0 = Date.now();
    let error;
    try {
      if (st.goto) await page.goto(st.goto, { waitUntil: "domcontentloaded", timeout: 45000 });
      else if (st.click) await locate(st.click).click({ timeout: 10000 });
      else if (st.fill) await locate(st.fill[0]).fill(st.fill[1], { timeout: 10000 });
      else if (st.press) await page.keyboard.press(st.press);
      else if (st.hover) await locate(st.hover).hover({ timeout: 10000 });
      else if (st.scroll) await page.mouse.wheel(0, st.scroll);
      // the page has already settled after the step before (settle()); a long wait only costs time on every run
      else if (st.wait) await page.waitForTimeout(Math.min(st.wait, 3000));
    } catch (e) {
      error = String(e.message || e).split("\n")[0];
    }
    await shot(i + 1, label, Date.now() - t0 + (await settle()), error);
    if (blocked && guardCfg.mode === "enforce") break;
  }
} finally {
  fs.writeFileSync(path.join(out, "explore.json"), JSON.stringify({ url, site, seat: guardCfg.seat, viewport: [vw, vh], screens,
    blocked: guard?.blocked ?? [] }, null, 1));
  await browser.close();
}
if (blocked && guardCfg.mode === "enforce") {
  console.error(`Stopped by the action guard: ${blocked.why} (${blocked.method} ${blocked.path}).`);
  process.exit(3);
}
if (guard && guardCfg.mode === "learn") console.log(`learning run: ${guard.blocked.length} change(s) blocked and logged in guard-log.jsonl`);
