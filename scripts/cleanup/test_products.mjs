// NAVI cleanup: delete the test products, courses and chapters NAVI itself created, in a TEST business only
// (recording-rules.md 13c; courses and chapters since 13 Nov 2026: a course goes with its chapters and lessons).
//
// Safety, every one required:
//   - the products page belongs to a business the user marked as a test ($NAVI_DATA/test-businesses.json, with
//     "products" and "cleanup": "whop-products"); any other address is refused, whatever its name says
//   - the page title names that business ("Products | NAVI Test")
//   - only rows whose product name starts with "NAVI test" are touched; likewise courses (the course cards in the
//     business's own Courses apps, on its community pages, e.g. whop.com/navi-test/...) and chapters
//   - a community page must be one of the business's own (its "pages" in seats.json) and its title must name it
//   - the site's own confirm box must name the same product ("Delete NAVI test 2?") before Delete is pressed
//   - the action guard (scripts/guard/guard.mjs) runs too, allowing deletes only of NAVI's own test items in a
//     business the user marked as a test; anything else it would block stops the cleanup
// Headless: nothing comes to the front (rule 22). Never used in a real business.
//
//   node scripts/cleanup/test_products.mjs --business whop.com/dashboard/biz_... [--dry-run] [--guard-log file]
// Prints one JSON line: {"business", "deleted": [names], "left": [names of all rows still there]}.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const { launchBrowser, realUserAgent } = await import(path.join(ROOT, "recorder", "agent-screenplay", "dist", "drivers", "browser.js"));
const { sessionFile, guardConfig, businesses } = await import(path.join(ROOT, "scripts", "seats", "seats.mjs"));
const { installGuard } = await import(path.join(ROOT, "scripts", "guard", "guard.mjs"));
const argv = process.argv.slice(2);
const opt = (k) => (argv.includes(`--${k}`) ? argv[argv.indexOf(`--${k}`) + 1] : undefined);
const dry = argv.includes("--dry-run");
const PREFIX = "NAVI test";

const data = process.env.NAVI_DATA || path.join(os.homedir(), "Library", "Application Support", "NAVI");
const reg = path.join(data, "test-businesses.json");
const want = (opt("business") || "").replace(/^[a-z]+:\/\/(www\.)?/, "").replace(/\/+$/, "");
const biz = (fs.existsSync(reg) ? JSON.parse(fs.readFileSync(reg, "utf8")) : []).find(
  (b) => want && b.match.replace(/\/+$/, "") === want,
);
if (!biz) {
  console.error(`Refused: "${want}" isn't marked as a test business in ${reg}. NAVI never deletes anything in a real business.`);
  process.exit(2);
}
if (biz.cleanup !== "whop-products" || !biz.products || !biz.products.replace(/^[a-z]+:\/\/(www\.)?/, "").startsWith(biz.match)) {
  console.error(`Refused: no products page with a known cleanup for ${biz.name}.`);
  process.exit(2);
}
// the owner seat: the one that opens the business dashboards (scripts/seats/seats.py)
const session = sessionFile(biz.site, "owner");

const b = await launchBrowser({ headless: true });
const out = { business: biz.name, deleted: [], left: [], courses_deleted: [], chapters_deleted: [], courses_left: [] };
// the business's own community pages (seats.json "pages"), where its Courses apps live
const pages = (businesses(biz.site).find((x) => x.id && biz.match.includes(x.id))?.pages || []).filter((x) => /^\/[a-z0-9-]+\/$/.test(x));
try {
  const c = await b.newContext({ userAgent: await realUserAgent(b), viewport: { width: 1440, height: 810 }, storageState: session });
  let blocked;
  const g = guardConfig({ site: biz.site, seat: "owner", allowTestDeletes: true, log: opt("guard-log") });
  g.logAll = Boolean(opt("guard-log"));
  await installGuard(c, { ...g, onBlock: (e) => (blocked = e) });
  const guardStop = () => {
    if (blocked) throw new Error(`Stopped by the action guard: ${blocked.why}`);
  };
  const p = await c.newPage();
  const open = async () => {
    await p.goto(biz.products, { waitUntil: "domcontentloaded", timeout: 45000 });
    await p.locator("tbody tr").or(p.getByText("No products yet")).first().waitFor({ timeout: 30000 }).catch(() => {});
    await p.waitForTimeout(1500);
    const title = await p.title();
    if (!title.trim().endsWith(`| ${biz.name}`)) throw new Error(`Refused: the page is "${title}", not ${biz.name}'s.`);
  };
  const nameOf = (t) => t.trim().split(/[\t\n]/)[0].trim(); // the first cell with text is the product name
  const names = async () => (await p.locator("tbody tr").allInnerTexts()).map(nameOf).filter(Boolean);
  await open();
  for (let k = 0; k < 100 && !dry; k++) {
    const row = p.locator("tbody tr").filter({ hasText: new RegExp(`^\\s*${PREFIX}`) }).first();
    if (!(await row.count())) break;
    const name = nameOf(await row.innerText());
    if (!name.startsWith(PREFIX)) break;
    await row.locator("button[aria-haspopup]").focus();
    await p.keyboard.press("Enter");
    await p.getByRole("menuitem", { name: "Delete" }).click({ timeout: 10000 });
    const dlg = p.locator("[role=alertdialog], [role=dialog]").last();
    await dlg.waitFor({ timeout: 10000 });
    const text = (await dlg.innerText()).replace(/\s+/g, " ").trim();
    if (!text.startsWith(`Delete ${name}?`)) {
      await p.keyboard.press("Escape");
      throw new Error(`Stopped: the confirm box says "${text.slice(0, 80)}", not "Delete ${name}?".`);
    }
    await dlg.getByRole("button", { name: "Delete", exact: true }).click();
    await dlg.waitFor({ state: "detached", timeout: 15000 }).catch(() => {});
    await p.waitForTimeout(300);
    guardStop();
    out.deleted.push(name);
    await p.waitForTimeout(1200);
    if (k % 5 === 4) await open(); // reload now and then so the list is the server's, not a stale one
  }
  await open();
  out.left = await names();
  if (dry) out.would_delete = out.left.filter((n) => n.startsWith(PREFIX));

  // ---- courses and chapters, in the business's Courses apps on its own community pages ------------------------
  const confirm = async (want, button) => {
    const dlg = p.locator("[role=alertdialog], [role=dialog]").last();
    await dlg.waitFor({ timeout: 10000 });
    const text = (await dlg.innerText()).replace(/\s+/g, " ").trim();
    if (!text.startsWith(`Delete ${want}?`)) {
      await p.keyboard.press("Escape");
      throw new Error(`Stopped: the confirm box says "${text.slice(0, 80)}", not "Delete ${want}?".`);
    }
    await dlg.getByRole("button", { name: button }).click();
    await dlg.waitFor({ state: "detached", timeout: 15000 }).catch(() => {});
    await p.waitForTimeout(1200);
    guardStop();
  };
  const ours = async () => {
    const t = await p.title();
    // whop titles its community pages "NAVI Test | Whop" and their apps "Courses | NAVI Test | Whop"
    const ok = t.trim() === `${biz.name} | Whop` || t.trim().endsWith(` | ${biz.name} | Whop`);
    if (!ok) throw new Error(`Refused: the page is "${t}", not ${biz.name}'s.`);
  };
  for (const home of pages) {
    const base = new URL(home, "https://" + biz.site).toString();
    await p.goto(base, { waitUntil: "domcontentloaded", timeout: 45000 });
    await p.waitForTimeout(4000);
    await ours();
    const apps = [...new Set(await p.locator(`a[href^="${home}exp_"][href$="/app/"]`).evaluateAll((as) => as.map((a) => a.getAttribute("href"))))];
    for (const app of apps) {
      const appUrl = new URL(app, base).toString();
      const openApp = async () => { await p.goto(appUrl, { waitUntil: "domcontentloaded", timeout: 45000 }); await p.waitForTimeout(4000); await ours(); };
      await openApp();
      if (!(await p.getByRole("button", { name: "Add course" }).count())) continue;     // not a Courses app
      const cards = () => p.getByRole("button").filter({ hasText: /\d+\s*chapters?\s*\d+\s*lessons?/ });
      const titleOf = (txt) => txt.trim().split(/\n/)[0].replace(/\s*\d+\s+chapters?[\s\S]*$/, "").trim();
      // whole courses named "NAVI test...": their chapters and lessons go with them
      for (let k = 0; k < 30 && !dry; k++) {
        const card = cards().filter({ hasText: new RegExp(`^\\s*${PREFIX}`) }).first();
        if (!(await card.count())) break;
        const name = titleOf(await card.innerText());
        if (!name.startsWith(PREFIX)) break;
        await card.hover();
        await p.waitForTimeout(500);
        const bb = await card.boundingBox();
        const btns = p.locator("button.fui-reset");
        let menu = null;
        for (let i = 0; i < (await btns.count()); i++) {
          const x = await btns.nth(i).boundingBox();
          if (x && bb && x.x > bb.x && x.x < bb.x + bb.width && x.y > bb.y && x.y < bb.y + bb.height) { menu = btns.nth(i); break; }
        }
        if (!menu) throw new Error(`Stopped: no menu on the course "${name}".`);
        await menu.click();
        await p.getByRole("menuitem", { name: "Delete course" }).click({ timeout: 10000 });
        await confirm(name, /^Delete/);
        out.courses_deleted.push(name);
        await openApp();
      }
      // chapters named "NAVI test..." inside the other courses: each course's editor, its chapter headers
      const all = (await cards().allInnerTexts()).map(titleOf);
      if (dry) out.would_delete_courses = (out.would_delete_courses || []).concat(all.filter((n) => n.startsWith(PREFIX)));
      const others = all.filter((n) => !n.startsWith(PREFIX));
      out.courses_left.push(...others);
      for (const course of others) {
        if (dry) break;
        for (let k = 0; k < 30; k++) {
          await openApp();
          await cards().filter({ hasText: course }).first().click();
          await p.waitForTimeout(5000);
          await ours();
          const heads = p.locator("input").filter({ has: p.locator(":scope") });
          const all = await p.locator("input").evaluateAll((els) => els.map((e) => e.value));
          const name = all.find((v) => v && v.startsWith(PREFIX));
          if (!name) break;
          const head = p.locator(`input[value="${name.replace(/"/g, '\\"')}"]`).first();
          const hb = await head.boundingBox();
          const btns = p.locator("button.fui-reset");
          let bin = null;
          for (let i = 0; i < (await btns.count()); i++) {
            const x = await btns.nth(i).boundingBox();
            if (x && hb && Math.abs(x.y + x.height / 2 - (hb.y + hb.height / 2)) < 12 && x.x > hb.x + hb.width + 30) bin = btns.nth(i);
          }
          if (!bin) break;          // a lesson, not a chapter, is named so: lessons go with their chapter or course
          await bin.click();
          await confirm(name, /^Delete chapter/);
          out.chapters_deleted.push(`${course} / ${name}`);
        }
      }
    }
  }
} finally {
  await b.close();
}
console.log(JSON.stringify(out));
