# Privacy rules

NAVI lowers the risk of showing something private. It can't remove it. Say so to the user, and tell them to watch every video before publishing.

## Four layers

1. **Test account with fake data.** The main protection. The user logs in themselves; NAVI never types passwords, codes or keys.
2. **Blur inside the page before recording.** Read the page's text and attributes and blur matching elements with an injected stylesheet that targets the elements themselves: avatars, profile menus, balances, the user's name and email, other workspaces in switchers and sidebars. Fixed blur boxes added afterwards miss things as soon as the camera zooms or the page scrolls.
3. **Check the frames after recording.** Run text recognition on sampled frames to catch text inside images, canvases and screenshots. Blur hits over their time range.
4. **The user reviews the list.** Everything blurred, and everything NAVI wasn't sure about, is listed with a timestamp in Review, with Keep blurred / Show it.

Check the blur on a live page before the first take, looking for over-blurring as well as leaks.

## Three tiers

| Tier | What | Can the user change it? |
|---|---|---|
| Always blurred | API keys and tokens, passwords, 2FA and recovery codes, card and bank numbers, government ID numbers, private keys, login and magic links | No |
| Blurred unless allowed | Emails, phone numbers, real names and profile photos, addresses, revenue and money figures, customer details, follower and member counts | Yes, per demo |
| Shown unless blurred | Usage stats (like token usage), prices on public pages, dates | Yes, per demo |

Plus the user's own **hide words** (a client's name, their surname), always blurred.

## Warnings

- Switching on money or results figures: "Showing earnings or results in marketing can count as a claim you have to back up."
- Switching on other people's data (customer emails or names): warn every time, even when switched on.
- Context-only private information (a client's company named in a sentence, a face in an image) can be missed. Say so plainly.

## Keys and logins

- The ElevenLabs key lives in the system keychain (macOS) or a user-only file outside the skill folder (Linux). It is only ever sent to ElevenLabs, never printed, logged or committed.
- Saved browser sessions are stored per site in NAVI's settings folder, outside the repository, and can be forgotten from Settings.
