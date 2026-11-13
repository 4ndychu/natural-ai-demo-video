// NAVI privacy, live page check (reference/privacy.md: "check the blur on a live page before the first take").
// Reads {url, out, width, height, script, storageState} as JSON on stdin. Opens the page at 2x with the blur
// script, waits for it to settle, saves a screenshot, prints {hits, title} as JSON. Masked previews only.
import fs from "node:fs"; import path from "node:path";
const HERE = path.dirname(new URL(import.meta.url).pathname);
const { chromium, devices } = await import(path.join(HERE, "..", "..", "recorder", "agent-screenplay", "node_modules", "playwright-core", "index.mjs"));
const cfg = JSON.parse(fs.readFileSync(0, "utf8"));
const browser = await chromium.launch({ headless: true, args: ["--force-device-scale-factor=2", "--hide-scrollbars"] });
try {
  // cfg.device: a phone profile from Playwright's list ("iPhone 15"), as in the recording
  const dev = cfg.device ? devices[cfg.device] : null;
  const context = await browser.newContext({ viewport: dev ? dev.viewport : { width: cfg.width, height: cfg.height }, deviceScaleFactor: 2,
    ...(dev ? { userAgent: dev.userAgent, isMobile: dev.isMobile, hasTouch: dev.hasTouch } : {}),
    storageState: cfg.storageState && fs.existsSync(cfg.storageState) ? cfg.storageState : undefined });
  await context.addInitScript({ content: cfg.script });
  if (cfg.guard) await (await import(cfg.guard.module)).installFromFile(context, cfg.guard.config, () => {});
  const page = await context.newPage();
  await page.goto(cfg.url, { waitUntil: "load", timeout: 60000 });
  await page.waitForLoadState("networkidle", { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(1200);
  await page.screenshot({ path: cfg.out });
  const hits = await page.evaluate(() => window.__naviPrivacyHits || null);
  if (hits === null) throw new Error("The blur script didn't run on this page.");
  const hidden = await page.evaluate(() => window.__naviHidden || []);    // page parts taken off (recording.hide_on_page)
  console.log(JSON.stringify({ title: await page.title(), hits, hidden }));
} finally { await browser.close(); }
