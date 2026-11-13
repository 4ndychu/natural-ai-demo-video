# Privacy rules

NAVI lowers the risk of showing something private. It can't remove it. Say so to the user, and tell them to watch every video before publishing.

## Four layers

1. **Test account with fake data.** The main protection. The user logs in themselves; NAVI never types passwords, codes or keys.
2. **Blur inside the page before recording.** Read the page's text and attributes and blur matching elements with an injected stylesheet that targets the elements themselves: avatars, profile menus, balances, the user's name and email, other workspaces in switchers and sidebars. Fixed blur boxes added afterwards miss things as soon as the camera zooms or the page scrolls.
3. **Check the frames after recording.** Run text recognition on sampled frames to catch text inside images, canvases and screenshots. Blur hits over their time range.
4. **The user reviews the list.** Everything blurred, and everything NAVI wasn't sure about, is listed with a timestamp in Review, with Keep blurred / Show it.

Check the blur on a live page before the first take, looking for over-blurring as well as leaks.

How NAVI does each layer (Phase 4): see `docs/engine.md` section 5 and `scripts/privacy/`. The patterns for every tier live in one file (`scripts/privacy/patterns.json`), used both inside the page and in the frame scan. Example addresses (`@example.com`, `.test`) and prices with a per-month or per-seat suffix are left visible. The test (`scripts/privacy/test_privacy.py`) reads the finished videos back and fails on any readable fake private value, and on any over-blurred public one.

Known limits: plain names with no context (for example "Created by Remo H. Jansen" in a footer) aren't recognised as names. Text split across elements can only be caught by the frame scan. Text inside images is blurred where it's readable, but faces in images are not detected.

## Three tiers

| Tier | What | Can the user change it? |
|---|---|---|
| Always blurred | API keys and tokens, passwords, 2FA and recovery codes, card and bank numbers, government ID numbers, private keys, login and magic links | No |
| Blurred unless allowed | Emails, phone numbers, real names and profile photos, addresses, revenue and money figures, customer details, follower and member counts | Yes, per demo |
| Shown unless blurred | Usage stats (like token usage), prices on public pages, dates | Yes, per demo |

Plus the user's own **hide words** (a client's name, their surname), always blurred.

**Names in "Joined by …" lines and split member counts are blurred.** whop's member page shows "Joined by Charlie, Henry Lai, and 3 others" and "6 members" with each name or number as its own piece of text, so the normal patterns missed them. A capitalised name inside a "Joined by / Liked by / Followed by / Bought by" control, and a number next to "members", "followers" and the like, are now blurred, looking only at that control's own text (a page-wide look blurred the tabs too). *(Found in the buyer-view test video, 11 Nov 2026.)*

**Navigation labels are never blurred.** Menu items, tabs and sidebar links ("Customers", "Payments") stay readable. The frame scan once read the people icon next to "Customers" as an "8" and blurred the menu item as a customer count; a line that is only an icon misread as one or two characters plus a short label, in the left quarter or top eighth of the frame (where menus sit), is now treated as a menu item. A real count keeps a longer number ("1,204 Customers") or sits in a sentence, so it's still blurred. Known limit: a one-digit count written like a menu item ("2 Members") in a sidebar would show. *(Andy, 10 Nov 2026.)*

**Test businesses show money.** In a business the user has marked as a test (`$NAVI_DATA/test-businesses.json`, by its address, for example NAVI Test's `whop.com/dashboard/biz_…`), prices and money amounts are shown by default: it's fake data, and a demo about setting a price has to show the price. In a real business, money stays blurred unless the user says "show" for that one video. Only the user marks a business as a test; NAVI never guesses from a name. *(Andy, 10 Nov 2026.)*

**Money and key pages blur everything that matters.** NAVI may open and film payout, balance, billing, bank, card and API key pages (the action guard stops it from changing anything there; `recording-rules.md` 13d). On those pages, matched by their address (`sensitive_pages` in `scripts/privacy/patterns.json`), the in-page blur covers every number, every filled-in field and every account detail (emails, names, photos, addresses, counts, money, dates), whatever the preset, in every business, test or real. It checks again whenever a single-page app changes its address. Known limit: the frame scan after recording doesn't know which page a frame came from, so a number drawn inside an image on such a page is only blurred if it matches a normal pattern. *(Andy, 10 Nov 2026.)*

## Warnings

- Switching on money or results figures: "Showing earnings or results in marketing can count as a claim you have to back up."
- Switching on other people's data (customer emails or names): warn every time, even when switched on.
- Context-only private information (a client's company named in a sentence, a face in an image) can be missed. Say so plainly.

## Keys and logins

- The ElevenLabs key lives in the system keychain (macOS) or a user-only file outside the skill folder (Linux). It is only ever sent to ElevenLabs, never printed, logged or committed.
- Saved browser sessions are stored per site in NAVI's settings folder, outside the repository, and can be forgotten from Settings.
