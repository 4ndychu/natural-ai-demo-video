// The x.com and claude.ai guard packs on the owner's REAL accounts (Andy, 13 Nov 2026): posting, likes, follows,
// DMs, payments, account and security changes and deleting are always blocked; a Grok or Claude prompt only when the
// job asks for one; any change the pack can't name is blocked (default deny); analytics pass.
//   node scripts/guard/test_site_packs.mjs
import { classify, loadPack, describeRequest } from "./guard.mjs";

const own = { business: { name: "your own account (the owner login)", real: true } };
let fails = 0;
const check = (site, what, req, allow, want) => {
  const res = classify(req, loadPack(site), { ...own, allow });
  const ok = res.verdict === want;
  if (!ok) fails++;
  console.log(`${ok ? "ok  " : "FAIL"}  ${site}: ${what} -> ${res.verdict}${res.category ? ` (${res.category})` : ""}  ${res.why}`);
};
const gql = (host, op, kind = "mutation") =>
  describeRequest("POST", `https://${host}/i/api/graphql/AbC123/${op}`, { "content-type": "application/json" },
    JSON.stringify({ query: `${kind} ${op} { x }`, operationName: op }));
const persisted = (host, op) =>
  describeRequest("POST", `https://${host}/i/api/graphql/AbC123/${op}`, { "content-type": "application/json" },
    JSON.stringify({ variables: {}, queryId: "AbC123", operationName: op, extensions: { persistedQuery: { sha256Hash: "x" } } }));
const rest = (method, url, body = "") => describeRequest(method, url, { "content-type": "application/json" }, body);
const both = (site, what, req) => {
  check(site, what, req, [], "block");
  check(site, what + " (even with every allowed change on)", req, ["grok-message", "claude-message"], "block");
};

// ---- x.com --------------------------------------------------------------------------------------------------
for (const op of ["CreateTweet", "CreateNoteTweet", "CreateRetweet", "CreateScheduledTweet", "CreateDraftTweet", "PinTweet"])
  both("x.com", `post: ${op}`, persisted("x.com", op));
both("x.com", "post: REST statuses/update", rest("POST", "https://x.com/i/api/1.1/statuses/update.json", "status=hi"));
for (const op of ["FavoriteTweet", "UnfavoriteTweet", "CreateBookmark", "ListAddMember"]) both("x.com", `engage: ${op}`, persisted("x.com", op));
both("x.com", "follow: friendships/create", rest("POST", "https://x.com/i/api/1.1/friendships/create.json", "user_id=1"));
both("x.com", "unfollow: friendships/destroy", rest("POST", "https://x.com/i/api/1.1/friendships/destroy.json", "user_id=1"));
both("x.com", "block: blocks/create", rest("POST", "https://x.com/i/api/1.1/blocks/create.json", "user_id=1"));
both("x.com", "mute: mutes/users/create", rest("POST", "https://x.com/i/api/1.1/mutes/users/create.json", "user_id=1"));
both("x.com", "DM: dm/new2", rest("POST", "https://x.com/i/api/1.1/dm/new2.json", '{"text":"hi"}'));
both("x.com", "DM: a GraphQL DM send", persisted("x.com", "useSendMessageMutation"));
both("x.com", "pay: Stripe payment intent", rest("POST", "https://api.stripe.com/v1/payment_intents", "amount=800"));
both("x.com", "pay: subscribe to Premium", persisted("x.com", "CreatePremiumSubscription"));
both("x.com", "pay: checkout", rest("POST", "https://x.com/i/api/1.1/subscriptions/checkout.json", "{}"));
both("x.com", "account: update profile", rest("POST", "https://x.com/i/api/1.1/account/update_profile.json", "name=x"));
both("x.com", "security: two-factor", persisted("x.com", "TwoFactorAuthEnroll"));
both("x.com", "security: password reset protection", rest("POST", "https://x.com/i/api/1.1/account/settings.json", "protect_password_reset=true"));
both("x.com", "delete: DeleteTweet", persisted("x.com", "DeleteTweet"));
both("x.com", "delete: any DELETE", rest("DELETE", "https://x.com/i/api/1.1/whatever/1"));
both("x.com", "API keys: developer portal", rest("POST", "https://developer.x.com/api/apps/new", "{}"));
// X often names the operation only in the address ({"variables", "queryId"} bodies): still caught by name
const bare = (op) => describeRequest("POST", `https://x.com/i/api/graphql/AbC123/${op}`, { "content-type": "application/json" },
  JSON.stringify({ variables: {}, queryId: "AbC123" }));
for (const [op, cat] of [["CreateTweet", "post"], ["CreateRetweet", "post"], ["FavoriteTweet", "engage"], ["CreateBookmark", "engage"],
  ["DeleteTweet", "delete"], ["useSendMessageMutation", "dm"]]) {
  const res = classify(bare(op), loadPack("x.com"), { ...own, allow: ["grok-message", "grok-intro"] });
  const ok = res.verdict === "block" && res.category === cat && !res.quiet;
  if (!ok) fails++;
  console.log(`${ok ? "ok  " : "FAIL"}  x.com: ${op} named only in the address -> ${res.verdict} (${res.category})`);
}
const quiet = classify(rest("POST", "https://grok.com/commerce.prepurchase.v1.PrePurchaseService/CreateCheckoutSession", "x"), loadPack("x.com"), { ...own, allow: [] });
if (!(quiet.verdict === "block" && quiet.quiet)) fails++;
console.log(`${quiet.verdict === "block" && quiet.quiet ? "ok  " : "FAIL"}  x.com: X's background checkout prefetch -> refused quietly, the run carries on`);
both("x.com", "link the X account to a Grok account", rest("POST", "https://grok.com/rest/auth/link-account", "{}"));
check("x.com", "Grok intro 'Not now', job asks for Grok", bare("PutClientEducationFlag"), ["grok-intro"], "allow");
check("x.com", "Grok intro 'Not now', job doesn't", bare("PutClientEducationFlag"), [], "block");
check("x.com", "timeline read sent by POST", bare("HomeTimeline"), [], "allow");
check("x.com", "Grok prompt (grok.x.com), job asks for Grok", rest("POST", "https://grok.x.com/2/grok/add_response.json", "{}"), ["grok-message"], "allow");
check("x.com", "Grok prompt, job asks for Grok", rest("POST", "https://x.com/i/api/2/grok/add_response.json", '{"message":"hi"}'), ["grok-message"], "allow");
check("x.com", "Grok prompt, job doesn't ask", rest("POST", "https://x.com/i/api/2/grok/add_response.json", '{"message":"hi"}'), [], "block");
check("x.com", "a change the pack can't name", persisted("x.com", "SomethingNew"), ["grok-message"], "block");
check("x.com", "a GraphQL query sent by POST", gql("x.com", "SearchTimeline", "query"), [], "allow");
check("x.com", "X's own client events", rest("POST", "https://x.com/i/api/1.1/jot/client_event.json", "log=[]"), [], "allow");

// ---- claude.ai ----------------------------------------------------------------------------------------------
const org = "https://claude.ai/api/organizations/0f1e2d3c-4b5a-6978-8a9b-0c1d2e3f4a5b";
both("claude.ai", "pay: Stripe", rest("POST", "https://api.stripe.com/v1/payment_methods", "type=card"));
both("claude.ai", "pay: upgrade plan", rest("POST", `${org}/billing/checkout`, "{}"));
both("claude.ai", "pay: subscription change", rest("PUT", `${org}/subscription`, "{}"));
both("claude.ai", "API key", rest("POST", `${org}/api_keys`, "{}"));
both("claude.ai", "invite a member", rest("POST", `${org}/invites`, "{}"));
both("claude.ai", "connect a connector", rest("POST", `${org}/mcp/remote_servers`, "{}"));
both("claude.ai", "account: profile", rest("PUT", "https://claude.ai/api/account/profile", "{}"));
both("claude.ai", "account: settings", rest("PATCH", "https://claude.ai/api/account/settings", "{}"));
both("claude.ai", "account: memory", rest("POST", `${org}/memory`, "{}"));
both("claude.ai", "delete a chat", rest("DELETE", `${org}/chat_conversations/abc`));
both("claude.ai", "share a chat", rest("POST", `${org}/chat_conversations/abc/share`, "{}"));
check("claude.ai", "new chat, job asks for a Claude prompt", rest("POST", `${org}/chat_conversations`, '{"name":""}'), ["claude-message"], "allow");
check("claude.ai", "send prompt, job asks", rest("POST", `${org}/chat_conversations/abc/completion`, '{"prompt":"hi"}'), ["claude-message"], "allow");
check("claude.ai", "send prompt, job doesn't ask", rest("POST", `${org}/chat_conversations/abc/completion`, '{"prompt":"hi"}'), [], "block");
check("claude.ai", "a change the pack can't name", rest("POST", `${org}/projects`, "{}"), ["claude-message"], "block");

// claude.ai's real addresses (logged 13 Nov 2026)
const rpc = (m, body) => rest("POST", `https://claude.ai/claudeai-rpc/anthropic.bard.api.v1alpha.ConversationService/${m}`, body);
const mcp = (method) => rest("POST", "https://claude.ai/v1/toolbox/shttp/mcp/fe145411-913f-4102-a4f3-2b31dfa86e67", JSON.stringify({ jsonrpc: "2.0", id: 1, method, params: {} }));
check("claude.ai", "connector discovery on page load", mcp("server/discover"), [], "allow");
check("claude.ai", "connector initialize on page load", mcp("initialize"), [], "allow");
both("claude.ai", "a connector action sent from the page (tools/call)", mcp("tools/call"));
check("claude.ai", "reading the conversation (StreamTimeline)", rpc("StreamTimeline", "x"), [], "allow");
check("claude.ai", "sending a prompt (PerformAction), job asks", rpc("PerformAction", "Say hello claude-opus-5-5"), ["claude-message"], "allow");
check("claude.ai", "sending a prompt (PerformAction), job doesn't ask", rpc("PerformAction", "Say hello claude-opus-5-5"), [], "block");
check("claude.ai", "another PerformAction (no model in it)", rpc("PerformAction", "rename"), ["claude-message"], "block");
check("claude.ai", "page-speed reports", rest("POST", "https://claude.ai/api/v2/rum", "x"), [], "allow");

console.log(fails ? `\n${fails} FAILED` : "\nall site-pack checks passed");
process.exit(fails ? 1 : 0);
