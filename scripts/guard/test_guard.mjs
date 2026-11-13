// NAVI action guard, the offline check: whop's real operations (as logged on 10 Nov 2026) against the guard pack.
// Every dangerous action is blocked in every seat and business; reads and telemetry pass everywhere; other changes
// pass in the test business, and are blocked in a real business and on a buyer's member pages unless the job asked.
//
//   node scripts/guard/test_guard.mjs            (exit 1 on any failure)
//   node scripts/guard/test_guard.mjs --live     (also a real headless run in NAVI Test treated as a real business:
//                                                  the guard must stop "Create product" before it reaches whop)
import path from "node:path";
import fs from "node:fs";
import os from "node:os";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { classify, describeRequest, loadPack, businessFor } from "./guard.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const pack = loadPack("whop.com");
const REAL = { name: "Real Biz", id: "biz_RealBiz0000001", real: true, test: false };
const NT = { name: "NAVI Test", id: "biz_NaviTest000001", real: false, test: true };
const seats = {
  "owner in Real Biz": { seat: "owner", business: REAL },
  "owner in NAVI Test": { seat: "owner", business: NT },
  "owner on member pages": { seat: "owner", business: { name: "your own account (the owner login)", real: true } },
};
const gql = (kind, name, field = name) =>
  describeRequest("POST", `https://whop.com/api/graphql/${name}`, {}, JSON.stringify({ query: `${kind} ${name}($input: X!) {\n  ${field}(input: $input) { id }\n}`, operationName: name }));
const rest = (method, url, body = "") => describeRequest(method, url, {}, body);

let fails = 0;
const check = (label, ok, extra = "") => {
  console.log(`${ok ? "ok  " : "FAIL"}  ${label}${extra ? `  (${extra})` : ""}`);
  if (!ok) fails++;
};

// 1. dangerous: blocked in every seat
const dangerous = [
  ["withdraw", gql("mutation", "createLedgerWithdrawal")],
  ["transfer", gql("mutation", "transferMyMembership", "transferLinkMyMembership")],
  ["transfer", rest("POST", "https://whop.com/api/v1/transfers", '{"amount":5}')],
  ["refund", gql("mutation", "coreRefundPayment", "refundPayment")],
  ["bank", gql("mutation", "coreUpdateMasspayPayoutAccount", "updateMasspayPayoutAccount")],
  ["bank", gql("mutation", "coreSetupBankDeposit", "setupBankDeposit")],
  ["bank", gql("mutation", "deletePaypal", "deletePaypalAccount")],
  ["bank", gql("mutation", "updateCompanyBillingInformation", "updateCompanyBilling")],
  ["api-key", gql("mutation", "createCompanyApiKey")],
  ["api-key", gql("query", "revealApiKey")],
  ["api-key", gql("mutation", "coreGenerateInternalOauthCode", "generateInternalOauthCode")],
  ["api-key", rest("POST", "https://whop.com/api/v1/api_keys", '{"name":"x"}')],
  ["team", gql("mutation", "deleteCompanyTeamMember", "deleteAuthorizedUser")],
  ["team", gql("mutation", "coreAcceptAuthorizedUserInvite", "acceptAuthorizedUserInvite")],
  ["team", gql("mutation", "transferCompanyOwnership")],
  ["delete", gql("mutation", "deleteCompany")],
  ["delete", gql("mutation", "deleteMyAccount")],
  ["delete", gql("mutation", "chatDeleteMessage", "deleteMessage")],
  ["delete", rest("DELETE", "https://whop.com/api/v1/products/prod_xxx")],
  ["pay", rest("POST", "https://api.stripe.com/v1/payment_intents/pi_1/confirm", "payment_method=pm_1")],
  ["pay", gql("mutation", "billingCreatePaymentToken", "createPaymentToken")],
];
for (const [cat, req] of dangerous)
  for (const [seat, s] of Object.entries(seats)) {
    const r = classify(req, pack, { ...s });
    check(`${cat}: ${req.method} ${req.path} blocked for ${seat}`, r.verdict === "block" && r.category === cat, r.why);
  }

// 2. the one delete allowed: NAVI's own test product, in the test business, by the cleanup only
const del = rest("DELETE", "https://whop.com/api/v1/products/prod_FakeProd00001");
check("cleanup may delete a product in NAVI Test", classify(del, pack, { ...seats["owner in NAVI Test"], allowTestDeletes: true }).verdict === "allow");
check("a recording may not delete a product in NAVI Test", classify(del, pack, { ...seats["owner in NAVI Test"] }).verdict === "block");
check("cleanup may not delete anything in Real Biz", classify(del, pack, { ...seats["owner in Real Biz"], allowTestDeletes: true }).verdict === "block");
// courses, chapters and lessons (13 Nov 2026): the same rule as products, on the business's own community pages too
for (const [what, url] of [["course", "https://whop.com/api/v1/courses/cors_x"], ["chapter", "https://whop.com/api/v1/course_chapters/chap_x"], ["lesson", "https://whop.com/api/v1/course_lessons/lesn_x"]]) {
  const d = rest("DELETE", url);
  check(`cleanup may delete a ${what} in NAVI Test`, classify(d, pack, { ...seats["owner in NAVI Test"], allowTestDeletes: true }).verdict === "allow");
  check(`cleanup may not delete a ${what} in Real Biz`, classify(d, pack, { ...seats["owner in Real Biz"], allowTestDeletes: true }).verdict === "block");
  check(`a ${what} delete outside the cleanup is blocked, even in NAVI Test`, classify(d, pack, { ...seats["owner in NAVI Test"] }).verdict === "block");
}
check("cleanup may not delete a whole business", classify(gql("mutation", "deleteCompany"), pack, { ...seats["owner in NAVI Test"], allowTestDeletes: true }).verdict === "block");

// 3. reads and background traffic: allowed everywhere, even on money and key pages
const reads = [
  gql("query", "fetchCompanyAccessPasses"),
  gql("query", "fetchCompanyRefunds", "refunds"),
  gql("query", "fetchApiKeys", "apiKeys"),
  gql("query", "fetchPayoutMethods", "payoutMethods"),
  gql("mutation", "GenerateWebsocketJwt", "generateWebsocketJwt"),
  rest("POST", "https://whop.com/_serverFn/dbd476332d294098435804d9eaecc5a7b34323d8ad84580a12356da4e5e96211"),
  rest("POST", "https://segapi.whop.com/v1/b", '{"batch":[]}'),
  rest("POST", "https://o1320754.ingest.us.sentry.io/api/4511820255133696/envelope/", "{}"),
  rest("POST", "https://whop.com/cdn-cgi/rum", "{}"),
  rest("POST", "https://whop.com/api/v1/users/me/acknowledgements", '{"id":"customers_inbox_intro"}'),
  gql("mutation", "chatMarkMessageAsViewed", "markFeedPostsAsViewed"),
  rest("POST", "https://api.hcaptcha.com/checksiteconfig"),
];
for (const req of reads)
  for (const [seat, s] of Object.entries(seats)) {
    const r = classify(req, pack, { ...s });
    check(`read/background ${req.host}${req.path.slice(0, 50)} allowed for ${seat}`, r.verdict === "allow", r.why);
  }

// 4. ordinary changes: allowed in NAVI Test; blocked in Real Biz unless the job asked, and always on member pages
const create = gql("mutation", "coreCreateOrUpdateAccessPass", "createOrUpdateAccessPass");
const hide = rest("PATCH", "https://whop.com/api/v1/products/prod_x", '{"visibility":"hidden"}');
const unknown = rest("POST", "https://whop.com/api/v1/something_new", '{"a":1}');
const opaque = describeRequest("POST", "https://whop.com/_serverFn/abc", {}, '{"data":{"x":1}}');
for (const req of [create, hide, unknown, opaque]) {
  check(`change ${req.path} allowed in NAVI Test`, classify(req, pack, seats["owner in NAVI Test"]).verdict === "allow");
  check(`change ${req.path} blocked on a buyer's member pages`, classify(req, pack, seats["owner on member pages"]).verdict === "block");
  check(`change ${req.path} blocked in Real Biz (job didn't ask)`, classify(req, pack, seats["owner in Real Biz"]).verdict === "block");
}
check("product change allowed in Real Biz when the job asks for it", classify(create, pack, { ...seats["owner in Real Biz"], allow: ["product"] }).verdict === "allow");
check("unknown change still blocked in Real Biz when the job asks for a product change", classify(unknown, pack, { ...seats["owner in Real Biz"], allow: ["product"] }).verdict === "block");
check("a job's allowance never covers a dangerous action", classify(gql("mutation", "coreRefundPayment", "refundPayment"), pack, { ...seats["owner in Real Biz"], allow: ["product", "member", "settings"] }).verdict === "block");

// 5. which business a request acts in: by the page's address
const cfg = { seat: "owner", businesses: [{ ...REAL, pages: ["/real-biz/"] }, { ...NT, pages: ["/navi-test/"] }] };
// community pages (whop.com/<slug>/...) belong to their business, so NAVI Test's course pages are the test business
// and Real Biz's stay real; any other page is the owner's own account (13 Nov 2026)
check("NAVI Test's course pages count as NAVI Test", businessFor(cfg, "https://whop.com/navi-test/exp_x/app/courses/cors_y/lessons/lesn_z/").name === "NAVI Test");
check("Real Biz's course pages count as Real Biz (real)", businessFor(cfg, "https://whop.com/real-biz/exp_x/app/").real === true && businessFor(cfg, "https://whop.com/real-biz/exp_x/app/").name === "Real Biz");
check("a look-alike slug is not NAVI Test", businessFor(cfg, "https://whop.com/navi-testing/").name !== "NAVI Test");
check("a page in Real Biz's dashboard is Real Biz", businessFor(cfg, "https://whop.com/dashboard/biz_RealBiz0000001/payments/")?.name === "Real Biz");
check("a page in NAVI Test's dashboard is NAVI Test", businessFor(cfg, "https://whop.com/dashboard/biz_NaviTest000001/")?.test === true);
check("an unknown business counts as real", businessFor(cfg, "https://whop.com/dashboard/biz_zzz/")?.real === true);
check("the owner outside a dashboard acts on their real account", businessFor(cfg, "https://whop.com/home/")?.real === true);
check("a buyer's member pages count as the owner's real account", businessFor(cfg, "https://whop.com/joined/x/")?.real === true);

// 6. live: NAVI Test treated as a real business; the guard must block "Create product" before it leaves the browser
if (process.argv.includes("--live")) {
  const real = path.join(os.homedir(), "Library", "Application Support", "NAVI");
  const tmp = fs.mkdtempSync(path.join(ROOT, "output", "guard-live-"));
  fs.cpSync(path.join(real, "logins"), path.join(tmp, "logins"), { recursive: true });
  fs.copyFileSync(path.join(real, "seats.json"), path.join(tmp, "seats.json"));
  fs.writeFileSync(path.join(tmp, "test-businesses.json"), "[]"); // nothing marked as a test: NAVI Test counts as real
  // the real NAVI Test business id comes from the user's own seats.json, never from the repo
  const naviTest = Object.values(JSON.parse(fs.readFileSync(path.join(real, "seats.json"), "utf8"))["whop.com"].businesses).find((x) => x.name === "NAVI Test");
  if (!naviTest?.id) throw new Error("--live needs a business named NAVI Test in " + path.join(real, "seats.json"));
  const steps = path.join(tmp, "steps.json");
  fs.writeFileSync(steps, JSON.stringify([
    { click: { css: "a:has-text('Create product')" } }, { wait: 2000 }, { fill: ["Basic access", "NAVI test guard"] },
    { click: { role: "button", name: "Create product" } }, { wait: 3000 },
  ]));
  let code = 0;
  try {
    execFileSync("node", [path.join(ROOT, "scripts", "explore", "explore.mjs"), "--url", `https://whop.com/dashboard/${naviTest.id}/products/`,
      "--site", "whop.com", "--seat", "owner", "--steps", steps, "--out", path.join(tmp, "explore")], { env: { ...process.env, NAVI_DATA: tmp }, stdio: "pipe" });
  } catch (e) {
    code = e.status;
  }
  const log = fs.readFileSync(path.join(tmp, "explore", "guard-log.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l));
  const b = log.find((e) => e.kind === "blocked");
  check("live: explore stopped with exit code 3", code === 3, `exit ${code}`);
  check("live: the product create was the blocked request", b?.path === "/api/graphql/coreCreateOrUpdateAccessPass", b?.why);
  // and nothing was created: NAVI Test's product list still has no "NAVI test guard"
  const out = execFileSync("node", [path.join(ROOT, "scripts", "cleanup", "test_products.mjs"), "--business", `whop.com/dashboard/${naviTest.id}`, "--dry-run"], { encoding: "utf8" });
  check("live: nothing was created in whop", !JSON.parse(out.trim().split("\n").pop()).left.includes("NAVI test guard"));
  fs.rmSync(tmp, { recursive: true, force: true });
}

// 7. live: Chrome's own interception covers the page, a cross-site frame and a popup, and leaves the cache on
if (process.argv.includes("--live")) {
  const { installGuard } = await import("./guard.mjs");
  const { launchBrowser } = await import(path.join(ROOT, "recorder", "agent-screenplay", "dist", "drivers", "browser.js"));
  const b = await launchBrowser({ headless: true });
  try {
    const c = await b.newContext();
    // a pack where httpbin.org is the site's own host and the page a real business: any change there is blocked
    const testPack = { own_hosts: "httpbin\\.org$", ignore: [], reads: [], read_requests: [], dangerous: [], changes: [] };
    const g = await installGuard(c, { pack: testPack, seat: "owner", businesses: [], mode: "enforce" });
    const p = await c.newPage();
    const post = (where) => where.evaluate(() => fetch("https://httpbin.org/post", { method: "POST", body: "x=1" }).then(() => "sent", () => "blocked"));
    await p.goto("https://example.com/");
    check("live: a change from the page is blocked", (await post(p)) === "blocked");
    await p.setContent('<iframe src="https://httpbin.org/forms/post"></iframe>');
    await p.waitForTimeout(3000);
    check("live: a change from a cross-site frame is blocked", (await post(p.frames()[1])) === "blocked");
    const [pop] = await Promise.all([c.waitForEvent("page"), p.evaluate(() => window.open("https://example.org/"))]);
    await pop.waitForLoadState();
    check("live: a change from a popup is blocked", (await post(pop)) === "blocked");
    check("live: each blocked change was logged", g.blocked.length === 3, `${g.blocked.length}`);
    const cdp = await c.newCDPSession(p);
    await cdp.send("Network.enable");
    let cached = 0;
    cdp.on("Network.requestServedFromCache", () => cached++);
    cdp.on("Network.responseReceived", (e) => { if (e.response.fromDiskCache || e.response.fromPrefetchCache) cached++; });
    await p.goto("https://www.wikipedia.org/");
    await p.goto("https://www.wikipedia.org/");
    check("live: the browser cache stays on (a reload is served from cache)", cached > 0, `${cached} from cache`);
  } finally {
    await b.close();
  }
}

console.log(fails ? `\n${fails} FAILED` : "\nall guard checks passed");
process.exit(fails ? 1 : 0);
