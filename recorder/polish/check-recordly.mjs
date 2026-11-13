// Checks that every Recordly file under recordly/ is exactly the pinned one (same git blob hash as the commit in
// recordly/PINNED.json), and that nothing was added. Run before every build; the build refuses to run if it fails.
//   node check-recordly.mjs           check
//   node check-recordly.mjs --fetch   re-download any missing or changed file from GitHub at the pinned commit
import fs from "node:fs"; import path from "node:path"; import crypto from "node:crypto"; import { execFileSync } from "node:child_process";
const DIR = path.join(path.dirname(new URL(import.meta.url).pathname), "recordly");
const pin = JSON.parse(fs.readFileSync(path.join(DIR, "PINNED.json"), "utf8"));
const blob = (buf) => crypto.createHash("sha1").update(`blob ${buf.length}\0`).update(buf).digest("hex");
const fetchFile = process.argv.includes("--fetch");
const problems = [];
for (const [rel, want] of Object.entries(pin.files)) {
  const p = path.join(DIR, rel);
  let ok = fs.existsSync(p) && blob(fs.readFileSync(p)) === want;
  if (!ok && fetchFile) {
    const url = `repos/${pin.repo.replace("https://github.com/", "")}/contents/${rel}?ref=${pin.commit}`;
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, execFileSync("gh", ["api", url, "-H", "Accept: application/vnd.github.raw"]));
    ok = blob(fs.readFileSync(p)) === want;
  }
  if (!ok) problems.push(`changed or missing: ${rel}`);
}
const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(path.join(d, e.name)) : [path.relative(DIR, path.join(d, e.name))]);
for (const rel of walk(DIR)) if (rel !== "PINNED.json" && !(rel in pin.files)) problems.push(`not Recordly's (added): ${rel}`);
if (problems.length) { console.error(`Recordly files don't match the pinned commit ${pin.commit.slice(0, 7)}:\n  ` + problems.join("\n  ")); process.exit(1); }
console.log(`Recordly ${pin.version} at ${pin.commit.slice(0, 7)}: all ${Object.keys(pin.files).length} files unedited.`);
