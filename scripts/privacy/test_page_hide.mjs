// Check for page_hide.js (config recording.hide_on_page): the banner around the text goes, the page around it stays,
// a banner that arrives later goes too, and another site's page is left alone.
//   node scripts/privacy/test_page_hide.mjs
import fs from "node:fs"; import path from "node:path";
const HERE = path.dirname(new URL(import.meta.url).pathname);
const { chromium } = await import(path.join(HERE, "..", "..", "recorder", "agent-screenplay", "node_modules", "playwright-core", "index.mjs"));
const js = fs.readFileSync(path.join(HERE, "page_hide.js"), "utf8");
const PAGE = `<main id="page"><h1>Total balance</h1>
  <div id="wrap"><div id="banner"><b>Confirm your tax details by November 30, 2026</b><p>It only takes about 2 minutes.</p><button>Update</button></div></div>
  <p id="rest">${"Everything else on the page. ".repeat(30)}</p></main>`;
let ok = true;
const check = (name, cond) => { ok &&= !!cond; console.log(`| ${name} | ${cond ? "pass" : "**FAIL**"} |`); };
const browser = await chromium.launch();
try {
  const run = async (site) => {
    const page = await browser.newPage();
    await page.setContent(PAGE);
    await page.addScriptTag({ content: `window.__NAVI_HIDE__ = ${JSON.stringify([{ site, text: "Confirm your tax details" }])};\n` + js });
    return page;
  };
  const page = await run("");
  const shown = (sel) => page.$eval(sel, (e) => getComputedStyle(e).display !== "none");
  check("the banner is hidden, not blurred", !(await shown("#wrap")) || !(await shown("#banner")));
  check("the page around it stays", (await shown("#page")) && (await shown("#rest")) && (await shown("h1")));
  await page.evaluate(() => { const d = document.createElement("div"); d.id = "late"; d.innerHTML = "<b>Confirm your tax details</b> <button>Update</button>"; document.body.append(d); });
  await page.waitForTimeout(200);
  check("a banner that appears later is hidden too", !(await shown("#late")));
  const other = await run("whop.com");      // the test page is not on whop.com
  check("another site's page is left alone", await other.$eval("#banner", (e) => getComputedStyle(e).display !== "none"));
} finally { await browser.close(); }
console.log(ok ? "**PASS**" : "**FAIL**");
process.exit(ok ? 0 : 1);
