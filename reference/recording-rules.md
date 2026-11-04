# Recording rules: how NAVI records the screen

Read this before recording anything. These rules came from building a real walkthrough end to end, including the takes that went wrong. They apply to any web app being demonstrated.

## Picture follows the voice

1. **Record to the voice; never retime footage afterwards.** Generate the voice first. Start each browser action live, at the moment its cue word is spoken in the finished take. The recording then plays at normal speed under the voice: no held frames, no speed-ups, no jumps. Retiming footage after the fact (holding a frame, then speeding up, then jumping) is what looked glitchy. *(Draft 1's rough opening; draft 2 recorded live with every action within 0.5 s of its word.)*
2. **Never pause, cut or speed up the voice to fit the picture.**
3. **Show page loads at real speed and cut only after the page has settled.** A real 2 to 4 s load looks like someone using the app; a sped-up or cut-short one looks like a glitch. Put long loads at section boundaries (see `voice-rules.md`, section 6) instead of squeezing the voice. *(Draft 1 cut 0.8 s after a click.)*
4. **No still screen for more than about 5 s.** Something moves, highlights or changes at least every 4 to 5 s, and the voice names what's on screen as it happens.
5. **The first 30 to 40 s carry the most action.** Open on the app doing things, not on talk over a still.
6. **Expect pop-ups right after a create step** (upsells, onboarding, notices). Cut on the settled page before they appear, or dismiss them on camera as part of the step.
7. Join checks before any draft goes to the user: no frozen frame over 1.5 s unless the voice is on that step, no jump cuts, no cut within 1.5 s of a click.

## Look

8. **No music bed.** A walkthrough is someone talking over their screen. Faint room tone only.
9. **Nothing on screen the user didn't ask for.** No "Illustrative", "Demo" or "Example" tags, no watermark. Captions and the corner label follow the user's settings (captions burned in by default, corner label off by default). If content is made up, say so in the voice or the description.
10. **Standard black system cursor.** Click feedback subtle and neutral (dark grey). A coloured cursor reads as generated.
11. Smooth eased cursor paths, and a gentle zoom on the element being clicked.
12. **When the user rejects an element, remove it at its source** (the script, brief or settings that asked for it), not just in the render, so the next run can't bring it back.

## Working safely in a real account

13. **Test accounts with fake data only.** The user logs in themselves; NAVI never types passwords or codes. Save the session so they log in once per site.
14. **Rehearse the whole flow before recording,** in a disposable copy if the flow creates things. Pop-ups that only appear after a create button are what break takes.
15. **Any step that creates something (a workspace, product, business, account) needs a disposable test account or a scratch copy,** so takes can be repeated cleanly. Every retake of a create step leaves a real duplicate behind, and many apps can't delete just one. Check before recording.
16. **Don't assume a repeated name stays the same.** Apps quietly rename duplicates ("Demo Academy" became "Demo Academy 2"). Check the real name on the page before the next section.
17. **Target elements by stable attributes** (link addresses, placeholders, field values), not visible labels that change after an install.
18. **Keep every raw recording.** Look changes (cursor, captions, corner label, audio) are re-renders, never re-recordings.
19. **Never publish, sell, delete, or open payouts, balances or account settings** unless the demo is about that and the user said so.

## Tools

20. **Check a recorder can be driven without a person** (command line, scripting or a local API) before choosing it. A recorder with only buttons can't go in an automated pipeline. Look in the app itself; don't guess from its website. *(One popular screen recorder had none of these.)*
21. Playwright drives the browser and records. Audio is NAVI's own takes, played as one continuous track per section; the recorder's own text-to-speech is never used.
