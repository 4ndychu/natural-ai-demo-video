// Renders one take through Recordly's export renderer and writes a silent MP4 on the take's own clock.
//   node render.mjs <take dir> <out.mp4> [--style casual|recordly] [--seconds N] [--zooms file.json] [--fps 60]
// Prints a JSON summary (Recordly's settings, the zooms it chose, timings) on the last line.
import fs from "node:fs"; import path from "node:path"; import { spawn } from "node:child_process";
const HERE = path.dirname(new URL(import.meta.url).pathname), ROOT = path.join(HERE, "..", "..");
const { chromium } = await import(path.join(HERE, "..", "agent-screenplay", "node_modules", "playwright-core", "index.mjs"));
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const [takeDir, outFile] = args.filter((a, i) => !a.startsWith("--") && !(i > 0 && args[i - 1].startsWith("--")));
const style = opt("--style", "casual"), fps = Number(opt("--fps", 60)), W = 1920, H = 1080;
const take = JSON.parse(fs.readFileSync(path.join(takeDir, "take.json"), "utf8"));
const seconds = Number(opt("--seconds", take.duration));
const zooms = opt("--zooms") ? JSON.parse(fs.readFileSync(opt("--zooms"), "utf8")) : undefined;
if (!fs.existsSync(path.join(HERE, "dist", "navi-polish.js"))) throw new Error("Run node recorder/polish/build.mjs first.");

// ---- the cursor log, as Recordly's telemetry (what Recordly records from the OS on a Mac) -------------------
// The recorder moves the cursor on an eased straight line from travelStart to actionAt (agent-screenplay's path),
// so the samples follow that line every 16 ms. Clicks get a mouseup 90 ms later. cursorType is the page's own CSS
// cursor, which the recorder logs along each path (cursorShapes, NAVI's patch). Older takes without it get the
// I-beam wherever the cursor is over a text box the script typed into, as in the approved test clips.
const VW = take.width, VH = take.height, ease = (k) => (k < 0.5 ? 2 * k * k : 1 - (-2 * k + 2) ** 2 / 2);
let pos = { ...take.cursorStart }, shape = "arrow";
const tel = [{ timeMs: 0, cx: pos.x / VW, cy: pos.y / VH, interactionType: "move", cursorType: shape }];
const shapeAt = (s, k) => { let c = shape; for (const [f, t] of s.cursorShapes ?? []) if (f <= k + 1e-9) c = t; return c; };
const legacy = !take.steps.some((s) => s.cursorShapes);
const textBoxes = take.steps.filter((s) => s.box && /placeholder=|type_into|input|textarea/.test(s.label)).map((s) => s.box);
const overText = (x, y) => textBoxes.some((b) => x >= b.x && x <= b.x + b.width && y >= b.y && y <= b.y + b.height);
for (const s of take.steps) {
  if (s.travelStart === undefined || !s.point) continue;
  const a = s.travelStart * 1000, b = (s.actionAt ?? s.end) * 1000, from = { ...pos };
  const at = (t, k, type = "move") => { const x = from.x + (s.point.x - from.x) * k, y = from.y + (s.point.y - from.y) * k;
    tel.push({ timeMs: t, cx: x / VW, cy: y / VH, interactionType: type, cursorType: legacy ? (overText(x, y) ? "text" : "arrow") : shapeAt(s, k) }); };
  at(a, 0);
  for (let t = a + 16; t < b; t += 16) at(t, ease((t - a) / (b - a)));
  at(b, 1, s.kind === "click" ? "click" : "move");
  if (s.kind === "click") tel.push({ ...tel[tel.length - 1], timeMs: b + 90, interactionType: "mouseup" });
  pos = { ...s.point }; shape = tel[tel.length - 1].cursorType;
}
tel.sort((p, q) => p.timeMs - q.timeMs);

// ---- render -----------------------------------------------------------------------------------------------
const frames = take.source.frames.filter(([t]) => t <= seconds + 1).map(([t, f]) => [t, "/frames/" + f]);
const browser = await chromium.launch({ headless: true, args: (process.env.NAVI_GL ?? "--use-angle=metal --ignore-gpu-blocklist --enable-gpu").split(" ").filter(Boolean) });
const page = await browser.newPage({ viewport: { width: W, height: H } });
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text().slice(0, 300)); });
await page.route("http://navi.local/**", (r) => {
  const u = decodeURIComponent(new URL(r.request().url()).pathname);
  const f = u.startsWith("/frames/") ? path.join(takeDir, take.source.dir, u.slice(8))
    : u.startsWith("/wallpapers/") ? path.join(HERE, "recordly", "public", u)
    : path.join(HERE, u === "/" ? "page.html" : u);
  return fs.existsSync(f) ? r.fulfill({ path: f }) : r.fulfill({ status: 404, body: "" });
});
await page.goto("http://navi.local/");
await page.waitForFunction(() => window.naviReady && window.navi, null, { timeout: 60000 });
const first = await page.evaluate(async (f) => { const b = await createImageBitmap(await (await fetch(f)).blob()); return [b.width, b.height]; }, frames[0][1]);
const info = await page.evaluate((j) => window.navi.init(j), { style, width: W, height: H, videoWidth: first[0], videoHeight: first[1],
  totalMs: Math.round(take.duration * 1000), telemetry: tel, zoomRegions: zooms });
// privacy frame scan (scripts/privacy/privacy.py): boxes to blur in the raw frames
const pb = path.join(takeDir, "post-blur.json"), postBlur = fs.existsSync(pb) ? JSON.parse(fs.readFileSync(pb, "utf8")) : [];
await page.evaluate(([f, b]) => window.navi.setFrames(f, b), [frames, postBlur]);

const FF = path.join(ROOT, ".venv", "bin", "ffmpeg");
const ff = spawn(FF, ["-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
  "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", String(fps), "-movflags", "+faststart", outFile], { stdio: ["pipe", "inherit", "inherit"] });
const done = new Promise((res, rej) => ff.on("close", (c) => (c === 0 ? res() : rej(new Error("ffmpeg failed " + c)))));
const total = Math.round(seconds * fps), BATCH = 30, t0 = Date.now();
for (let i = 0; i < total; i += BATCH) {
  const n = Math.min(BATCH, total - i);
  const jpgs = await page.evaluate(([a, s, c]) => window.navi.frames(a, s, c), [i * 1000 / fps, 1000 / fps, n]);
  for (const j of jpgs) if (!ff.stdin.write(Buffer.from(j, "base64"))) await new Promise((r) => ff.stdin.once("drain", r));
  if (process.stderr.isTTY || (i / BATCH) % 20 === 0) process.stderr.write(`\rpolish: ${Math.min(i + n, total)}/${total} frames`);
}
ff.stdin.end(); await done; await browser.close();
const secs = (Date.now() - t0) / 1000;
process.stderr.write("\n");
console.log(JSON.stringify({ style, out: outFile, frames: total, fps, render_s: +secs.toFixed(1), render_fps: +(total / secs).toFixed(1),
  source: first, cursor_shapes: legacy ? "inferred (old take)" : "logged", post_blur_boxes: postBlur.length, ...info, page_errors: errors.slice(0, 5) }));
