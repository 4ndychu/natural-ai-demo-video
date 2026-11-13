// NAVI captions drawn by the browser: one transparent 1920x1080 PNG per caption (and one for the corner label),
// so captions can use any web font (Mona Sans) and rounded boxes, which ffmpeg's subtitle renderer can't.
// Reads {"out": dir, "look": {...}, "items": [{"name", "lines": [...], "kind": "caption"|"label", "corner"}]} on stdin.
import fs from "node:fs"; import path from "node:path";
const HERE = path.dirname(new URL(import.meta.url).pathname), ROOT = path.join(HERE, "..", "..");
const { chromium } = await import(path.join(ROOT, "recorder", "agent-screenplay", "node_modules", "playwright-core", "index.mjs"));
const job = JSON.parse(fs.readFileSync(0, "utf8")), L = job.look;
// the font is embedded (a blank page may not read files from disk)
const mona = fs.readFileSync(path.join(ROOT, "ui", "fonts", "mona-sans.woff2")).toString("base64");
const font = `@font-face{font-family:'Mona Sans';src:url(data:font/woff2;base64,${mona}) format('woff2');font-weight:200 900;font-stretch:75% 125%}`;
const css = `${font}
html,body{margin:0;width:1920px;height:1080px;background:transparent;overflow:hidden}
.wrap{position:absolute;display:flex;flex-direction:column;gap:${L.gap}px}
.cap{left:0;right:0;bottom:${L.bottom}px;align-items:center}
.cap.top{bottom:auto;top:${L.bottom}px}
.line{font-family:${L.family};font-weight:${L.weight};font-size:${L.size}px;line-height:1.18;color:#fff;
  background:${L.box};padding:${L.padY}px ${L.padX}px;border-radius:${L.radius}px;white-space:pre;
  -webkit-font-smoothing:antialiased;letter-spacing:${L.tracking || 0}em}
.label .line{font-size:${L.labelSize}px;padding:${L.labelPadY}px ${L.labelPadX}px}
.tl{top:${L.labelMargin}px;left:${L.labelMargin}px}.tr{top:${L.labelMargin}px;right:${L.labelMargin}px;align-items:flex-end}
.bl{bottom:${L.labelMargin}px;left:${L.labelMargin}px}.br{bottom:${L.labelMargin}px;right:${L.labelMargin}px;align-items:flex-end}`;
const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.setContent(`<style>${css}</style><div id="root"></div>`);
await page.evaluate(() => document.fonts.load("500 44px 'Mona Sans'"));
fs.mkdirSync(job.out, { recursive: true });
for (const it of job.items) {
  const cls = it.kind === "label" ? `wrap label ${it.corner}` : `wrap cap${it.pos === "top" ? " top" : ""}`;
  await page.evaluate((h) => { document.getElementById("root").innerHTML = h; }, `<div class="${cls}">${it.lines.map((l) => `<div class="line">${esc(l)}</div>`).join("")}</div>`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(job.out, it.name + ".png"), omitBackground: true });
}
await browser.close();
console.log(JSON.stringify({ made: job.items.length }));
