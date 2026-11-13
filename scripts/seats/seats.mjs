// NAVI seats, the browser side: which saved login a seat uses, and the action guard's settings for it.
// The same files and rules as scripts/seats/seats.py (read that for the full story); this side only reads.
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

export function defaultSeat(site) {
  const seats = Object.keys(config()[site]?.seats ?? {});
  return seats.includes("owner") || !seats.length ? "owner" : seats[0];
}

// The seat's saved session file, or undefined when that seat isn't logged in. A login saved before seats existed
// (logins/<site>.json) still counts as the default seat's until seats.py moves it.
export function sessionFile(site, seat) {
  if (!NAME.test(site)) return undefined;
  const s = seat || defaultSeat(site);
  if (!NAME.test(s)) throw new Error(`Not a seat name: ${s}`);
  const f = path.join(dataDir(), "logins", site, `${s}.json`);
  if (fs.existsSync(f)) return f;
  const legacy = path.join(dataDir(), "logins", `${site}.json`);
  return s === defaultSeat(site) && fs.existsSync(legacy) ? legacy : undefined;
}

export function businesses(site) {
  const marks = read(path.join(dataDir(), "test-businesses.json"), []).filter((m) => m.site === site);
  return Object.entries(config()[site]?.businesses ?? {}).map(([key, b]) => {
    const test = marks.some((m) => b.id && (m.match || "").includes(b.id));
    // pages: the business's own community pages (whop.com/<slug>/...), where its apps, courses and lessons live
    return { key, name: b.name, id: b.id, pages: b.pages || [], test, real: !test };
  });
}

// The guard's settings for a run in this seat (scripts/guard/guard.mjs).
export function guardConfig({ site, seat, business, allow = [], mode = "enforce", allowTestDeletes = false, log }) {
  const biz = businesses(site);
  return {
    site,
    seat: seat || defaultSeat(site),
    business: business ? biz.find((b) => b.key === business) ?? null : null,
    businesses: biz,
    allow,
    mode,
    allowTestDeletes,
    log,
  };
}
