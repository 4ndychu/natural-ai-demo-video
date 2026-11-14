// Paying is blocked on EVERY site (config/guard/_payments.json), with or without the site's own pack, in every seat
// and business (a test business, the owner's account, logged out); the processors' background reports pass, so a
// checkout page can be filmed (FG08, 14 Nov 2026: Stripe's csp-report, m.stripe.com and r.stripe.com stopped it on
// Whop's checkout when every POST to Stripe was blocked).
//   node scripts/guard/test_payments.mjs     (exit 1 on any failure)
import { classify, loadPack, describeRequest, PAYMENTS } from "./guard.mjs";

let fails = 0;
const ok = (label, good, extra = "") => {
  if (!good) fails++;
  console.log(`${good ? "ok  " : "FAIL"}  ${label}${extra ? `  (${extra})` : ""}`);
};
const req = (method, url, body = "", headers = { "content-type": "application/json" }) => describeRequest(method, url, headers, body);
const gql = (url, op) => req("POST", url, JSON.stringify({ query: `mutation ${op} { x }`, operationName: op }));

// every site NAVI has a pack for, plus sites with none (a public page filmed logged out, a SaaS without rules yet)
const SITES = ["x.com", "claude.ai", "whop.com", "linktr.ee", "example-shop.com"];
const WHO = {
  "the owner's account": { name: "your own account (the owner login)", real: true },
  "logged out": { name: "no account (logged out)", real: true },
  "a test business": { name: "NAVI Test", test: true, real: false },
  "nobody (no business)": null,
};
const ALL_ALLOWED = ["grok-message", "grok-intro", "claude-message", "product", "checkout"];

const PAY = [
  ["Stripe: confirm a payment intent", req("POST", "https://api.stripe.com/v1/payment_intents/pi_1/confirm", "payment_method=pm_1")],
  ["Stripe: create a payment intent", req("POST", "https://api.stripe.com/v1/payment_intents", "amount=800")],
  ["Stripe: save a card (payment method)", req("POST", "https://api.stripe.com/v1/payment_methods", "type=card")],
  ["Stripe: confirmation token", req("POST", "https://api.stripe.com/v1/confirmation_tokens", "x=1")],
  ["Stripe: setup intent confirm", req("POST", "https://api.stripe.com/v1/setup_intents/seti_1/confirm", "x=1")],
  ["Stripe: card token", req("POST", "https://api.stripe.com/v1/tokens", "card[number]=x")],
  ["Stripe: checkout session", req("POST", "https://api.stripe.com/v1/checkout/sessions", "x=1")],
  ["Stripe Checkout's hosted page: confirm", req("POST", "https://api.stripe.com/v1/payment_pages/cs_live_a1B2/confirm", "x=1")],
  ["Stripe: subscription change", req("POST", "https://api.stripe.com/v1/subscriptions/sub_1", "x=1")],
  ["Stripe: pay an invoice", req("POST", "https://api.stripe.com/v1/invoices/in_1/pay", "x=1")],
  ["Stripe: billing portal", req("POST", "https://billing.stripe.com/v1/billing_portal/sessions/bps_1/flows", "x=1")],
  ["Stripe: a 3-D Secure frame's own pay call (stripe.network)", req("POST", "https://js.stripe.network/v1/payment_intents/pi_1/confirm", "x=1")],
  ["PayPal: capture an order", req("POST", "https://www.paypal.com/v2/checkout/orders/5O1/capture", "{}")],
  ["PayPal: any change", req("POST", "https://www.paypal.com/smart/api/vault/abc", "{}")],
  ["Braintree: a card", req("POST", "https://payments.braintree-api.com/graphql", '{"query":"mutation TokenizeCreditCard"}')],
  ["Braintree gateway", req("POST", "https://api.braintreegateway.com/merchants/x/client_api/v1/payment_methods/credit_cards", "{}")],
  ["Venmo", req("POST", "https://venmo.com/api/v5/payments", "{}")],
  ["Apple: a purchase address", req("POST", "https://secure.store.apple.com/shop/checkoutx", "{}")],
  ["Apple Pay gateway", req("POST", "https://apple-pay-gateway.apple.com/paymentservices/paymentSession", "{}")],
  ["Apple: buying in iTunes", req("POST", "https://buy.itunes.apple.com/WebObjects/MZBuy.woa/wa/buyProduct", "{}")],
  ["Google Pay: approving", req("POST", "https://pay.google.com/gp/p/apis/buyflow/process", "{}")],
  ["Shopify's card vault", req("POST", "https://deposit.shopifycs.com/sessions", "{}")],
  ["Adyen: a session payment", req("POST", "https://checkoutshopper-live.adyen.com/checkoutshopper/v1/sessions/CS1/payments", "{}")],
  ["Checkout.com: a card token", req("POST", "https://api.checkout.com/tokens", "{}")],
  ["Square: a card nonce", req("POST", "https://pci-connect.squareup.com/v2/card-nonce", "{}")],
  ["Paddle: paying", req("POST", "https://checkout-service.paddle.com/transaction-checkout/pay", "{}")],
  ["Klarna: authorising", req("POST", "https://js.klarna.com/eu/payments/authorize", "{}")],
  ["any site: place an order", req("POST", "https://shop.example.com/api/place-order", "{}")],
  ["any site: complete the checkout", req("POST", "https://shop.example.com/checkout/complete", "{}")],
  ["any site: a GraphQL placeOrder", gql("https://shop.example.com/graphql", "placeOrder")],
];

// a processor's background traffic on a checkout page: passes on every site (it pays nothing)
const BACKGROUND = [
  ["Stripe: CSP report (q.stripe.com)", req("POST", "https://q.stripe.com/csp-report?p=v3", "{}")],
  ["Stripe: fraud fingerprint (m.stripe.com/6)", req("POST", "https://m.stripe.com/6", "data")],
  ["Stripe: page events (r.stripe.com/b)", req("POST", "https://r.stripe.com/b", "{}")],
  ["Stripe: Radar session", req("POST", "https://api.stripe.com/v1/radar/session", "x=1")],
  ["Stripe Checkout's hosted page: opening it (init)", req("POST", "https://api.stripe.com/v1/payment_pages/cs_live_a1B2/init", "x=1")],
  ["Stripe Link: looking up an email", req("POST", "https://api.stripe.com/v1/consumers/sessions/lookup", "x=1")],
  ["PayPal: its button's logs", req("POST", "https://www.paypal.com/xoplatform/logger/api/logger", "{}")],
];

for (const site of SITES) {
  const pack = loadPack(site);
  const tag = `${site}${pack ? "" : " (no pack)"}`;
  for (const [what, r] of PAY) {
    const res = Object.entries(WHO).map(([who, business]) => [who, classify(r, pack, { business, allow: ALL_ALLOWED })]);
    const bad = res.filter(([, x]) => !(x.verdict === "block" && x.category === "pay" && !x.quiet));
    ok(`${tag}: ${what} -> blocked in every seat, even with every change allowed`, !bad.length,
      bad.map(([w, x]) => `${w}: ${x.verdict} ${x.why}`).join("; "));
  }
  for (const [what, r] of BACKGROUND) {
    const res = classify(r, pack, { business: WHO["logged out"], allow: [] });
    ok(`${tag}: ${what} -> passes`, res.verdict === "allow", res.why);
  }
}

// a site's own ways of paying stay in its pack and still block
const own = { business: WHO["the owner's account"], allow: ALL_ALLOWED };
const xb = classify(req("POST", "https://x.com/i/api/graphql/AbC/CreatePremiumSubscription", JSON.stringify({ variables: {}, queryId: "AbC" })), loadPack("x.com"), own);
ok("x.com: subscribing to Premium (X's own operation) -> blocked", xb.verdict === "block" && xb.category === "pay", xb.why);
const wb = classify(gql("https://whop.com/api/graphql/processCheckout", "processCheckout"), loadPack("whop.com"), own);
ok("whop.com: processCheckout (Whop's own operation) -> blocked", wb.verdict === "block" && wb.category === "pay", wb.why);
const cb = classify(req("POST", "https://claude.ai/api/organizations/o/billing/checkout", "{}"), loadPack("claude.ai"), own);
ok("claude.ai: upgrading the plan (claude.ai's own address) -> blocked", cb.verdict === "block" && cb.category === "pay", cb.why);
const xq = classify(req("POST", "https://grok.com/commerce.prepurchase.v1.PrePurchaseService/CreateCheckoutSession", "x"), loadPack("x.com"), own);
ok("x.com: X's background checkout prefetch is still refused quietly (the shared rules don't take it over)", xq.verdict === "block" && xq.quiet, xq.why);

// a site's own ignore list can't let a payment through: the shared rules come first
const leaky = { ignore: [{ label: "everything", path: "." }], dangerous: [] };
const lk = classify(PAY[0][1], leaky, own);
ok("a pack that ignores everything still can't let a payment through", lk.verdict === "block" && lk.category === "pay", lk.why);

// no processor is matched on every request any more (what stopped FG08)
const hosts = PAYMENTS.dangerous.flatMap((d) => d.match).filter((m) => /stripe/.test(m.host || ""));
ok("Stripe is matched on its paying addresses, never on every request", hosts.length && hosts.every((m) => m.path), hosts.length);
for (const site of ["x.com", "claude.ai", "whop.com"]) {
  const pay = loadPack(site).dangerous.filter((d) => d.category === "pay").flatMap((d) => d.match);
  ok(`${site}: card processors live only in the shared rules (no copy to drift)`, !pay.some((m) => /stripe|paypal|braintree|apple/.test(m.host || "")));
}

console.log(fails ? `\n${fails} FAILED` : "\nall payment checks passed");
process.exit(fails ? 1 : 0);
