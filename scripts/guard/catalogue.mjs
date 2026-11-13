// NAVI guard: list every GraphQL operation a site's own JavaScript can send, to build or check its guard pack.
// Opens the given pages headless with a saved seat (the guard on, in learn mode, so nothing can change), collects
// every script the pages load, and prints each operation name with its kind (mutation or query), one per line.
//
//   node scripts/guard/catalogue.mjs --site whop.com --seat owner --out ops.json <url> [<url> ...]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const { launchBrowser, realUserAgent } = await import(path.join(ROOT, "recorder", "agent-screenplay", "dist", "drivers", "browser.js"));
const { sessionFile, guardConfig } = await import(path.join(ROOT, "scripts", "seats", "seats.mjs"));
const { installGuard } = await import(path.join(ROOT, "scripts", "guard", "guard.mjs"));
const argv = process.argv.slice(2);
const opt = (k) => (argv.includes(`--${k}`) ? argv[argv.indexOf(`--${k}`) + 1] : undefined);
const urls = argv.filter((a, i) => /^https?:/.test(a) && !/^--/.test(argv[i - 1] || ""));
const site = opt("site");
const out = opt("out");
const b = await launchBrowser({ headless: true });
const ops = new Map();
try {
  const c = await b.newContext({ userAgent: await realUserAgent(b), viewport: { width: 1440, height: 810 }, storageState: sessionFile(site, opt("seat")) });
  await installGuard(c, guardConfig({ site, seat: opt("seat"), mode: "learn" }));
  const seen = new Set();
  c.on("response", async (r) => {
    const u = r.url();
    if (r.request().resourceType() !== "script" || seen.has(u)) return;
    seen.add(u);
    const js = await r.text().catch(() => "");
    for (const m of js.matchAll(/\b(mutation|query|subscription)\s+([A-Za-z_]\w*)\s*[({]/g)) {
      const k = `${m[1]} ${m[2]}`;
      if (!ops.has(k)) ops.set(k, { kind: m[1], name: m[2], fields: [] });
      const tail = js.slice(m.index, m.index + 400).match(/\{\s*([A-Za-z_]\w*)\s*[({]/);
      if (tail && !ops.get(k).fields.includes(tail[1])) ops.get(k).fields.push(tail[1]);
    }
  });
  const p = await c.newPage();
  for (const u of urls) {
    await p.goto(u, { waitUntil: "load", timeout: 60000 }).catch((e) => console.error(u, e.message));
    await p.waitForTimeout(6000);
    console.error(`${u}: ${ops.size} operations so far (${seen.size} scripts)`);
  }
} finally {
  await b.close();
}
const list = [...ops.values()].sort((a, b) => a.kind.localeCompare(b.kind) || a.name.localeCompare(b.name));
if (out) fs.writeFileSync(out, JSON.stringify(list, null, 1));
for (const o of list) console.log(`${o.kind}\t${o.name}\t${o.fields.join(",")}`);
