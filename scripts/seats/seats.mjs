// NAVI seats, the browser side: which saved login a seat uses, and the action guard's settings for it.
// The same files and rules as scripts/seats/seats.py (read that for the full story); this side only reads.
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const dataDir = () => process.env.NAVI_DATA || path.join(os.homedir(), "Library", "Application Support", "NAVI");
const read = (f, d) => {
  try {
    return JSON.parse(fs.readFileSync(f, "utf8"));
  } catch {
    return d;
  }
};
const NAME = /^[a-z0-9][a-z0-9.-]*$/;

export const siteOf = (url) => (url.trim().toLowerCase().match(/^(?:[a-z]+:\/\/)?([^/:?#]+)/) || [])[1]?.replace(/^www\./, "") ?? "";
export const config = () => read(path.join(dataDir(), "seats.json"), {});

// The site whose saved login a page uses: itself, or the seats.json site that covers it ("google.com": {"covers":
// ["docs.google.com", ...]}), as seats.py login_site.
export function loginSite(site) {
  const cfg = config();
  if (cfg[site]) return site;
  for (const [name, c] of Object.entries(cfg)) if (!name.startsWith("_") && (c?.covers || []).includes(site)) return name;
  return site;
}

// the seat of a video that shows the public pages as a visitor sees them (seats.py LOGGED_OUT)
export const LOGGED_OUT = "logged-out";

export function defaultSeat(site) {
  site = loginSite(site);
  const seats = Object.keys(config()[site]?.seats ?? {});
  return seats.includes("owner") || !seats.length ? "owner" : seats[0];
}

// The seat's saved session file, or undefined when that seat isn't logged in. A login saved before seats existed
// (logins/<site>.json) still counts as the default seat's until seats.py moves it.
export function sessionFile(site, seat) {
  if (!NAME.test(site)) return undefined;
  // the logged-out seat never holds a login, even if a file was once saved under its name (FG08, 14 Nov 2026)
  if (seat === LOGGED_OUT) return undefined;
  site = loginSite(site);
  const s = seat || defaultSeat(site);
  if (!NAME.test(s)) throw new Error(`Not a seat name: ${s}`);
  const f = path.join(dataDir(), "logins", site, `${s}.json`);
  if (fs.existsSync(f)) return f;
  const legacy = path.join(dataDir(), "logins", `${site}.json`);
  return s === defaultSeat(site) && fs.existsSync(legacy) ? legacy : undefined;
}

export function businesses(site) {
  site = loginSite(site);
  const marks = read(path.join(dataDir(), "test-businesses.json"), []).filter((m) => m.site === site);
  return Object.entries(config()[site]?.businesses ?? {}).map(([key, b]) => {
    const test = marks.some((m) => b.id && (m.match || "").includes(b.id));
    // pages: the business's own community pages (whop.com/<slug>/...), where its apps, courses and lessons live
    return { key, name: b.name, id: b.id, pages: b.pages || [], test, real: !test };
  });
}

// Several logins in one browser (a video on X and Google Sheets): every cookie and page storage of each seat's
// session in one file, as seats.py merged_login (same folder and naming, readable only by the user). pairs: [[site, seat]].
export function joinedSession(pairs) {
  pairs = pairs.filter(([, seat]) => seat !== LOGGED_OUT);     // a site shown logged out adds no login
  if (!pairs.length) return undefined;
  const files = pairs.map(([site, seat]) => {
    const f = sessionFile(site, seat);
    if (!f) throw new Error(`The ${seat || defaultSeat(site)} seat on ${loginSite(site)} isn't logged in. Log it in from Settings > Logins first.`);
    return f;
  });
  if (files.length === 1) return files[0];
  const key = crypto.createHash("sha1").update(files.slice().sort().map((f) => `${f}:${fs.statSync(f).mtimeMs / 1000}`).join("|")).digest("hex").slice(0, 16);
  const dir = path.join(dataDir(), "logins", "_joined");
  fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
  const out = path.join(dir, `${key}.json`);
  if (fs.existsSync(out)) return out;
  const cookies = new Map();
  const origins = new Map();
  for (const f of files) {
    const st = read(f, {});
    for (const c of st.cookies || []) cookies.set(`${c.name}|${c.domain}|${c.path}`, c);
    for (const o of st.origins || []) origins.set(o.origin, o);
  }
  fs.writeFileSync(out, JSON.stringify({ cookies: [...cookies.values()], origins: [...origins.values()] }), { mode: 0o600 });
  return out;
}

// The guard's settings for a run in this seat (scripts/guard/guard.mjs). sites: every site whose login the run holds.
export function guardConfig({ site, seat, business, allow = [], mode = "enforce", allowTestDeletes = false, log, sites }) {
  site = loginSite(site);
  const all = [...new Set([site, ...(sites || []).map(loginSite)])];
  const biz = all.flatMap((s) => businesses(s));
  return {
    site,
    sites: all,
    seat: seat || defaultSeat(site),
    business: business ? biz.find((b) => b.key === business) ?? null : null,
    businesses: biz,
    allow,
    mode,
    allowTestDeletes,
    log,
  };
}
