# Listening notes: Phase 2 timing preview

Date: 5 November 2026. Listener: Andy. File: `output/test-todo-v4/timing-preview.mp4` (the approved Phase 1 track with the planned actions on screen; not in git).

## Andy's note, verbatim

> "Now it's just the two left" sounds terribly
> well, not terribly, but it does sound like AI, sort of. Other than that, it sounds pretty good.

> I meant "Ai slop"

## Result

The last line of section 3, "Now it's just the two left.", sounds like AI slop. Its last word ends about 10 semitones above Alex's floor (a rising wrap-up, the same fault as the original opening). Fix: an ending test like the one for section 1 (voice-rules.md, "the last line of a section is a plain statement that ends low").

## Ending tests for section 3

Test 1 (`examples/experiments/2026-11-05-ending3.json`), blind: Andy picked A, "So now there's just the two left up top." His note, verbatim:

> Okay, A sounds a lot more natural. A is probably my favourite one out of there, but still, depending on human behaviour, are you sure the research papers were enough?
>
> Usually, if I were to say it, I probably would have been like, "So now there are just two left, okay?" It also kind of sounds like, "Now there are just two left." It sounds quite positive, but usually, I don't know. Maybe, please correct me if I'm wrong. Feel free to disagree with me, but usually, in terms of human behaviour, when you're approaching the end of a video, you may not sound as positive. It may just be lower, like, "So now there are just two left now."
>
> Say something like that, maybe even add a very unnecessary filler word at the end, based on human behaviour. That's my opinion. Please feel free to disagree because you've just pulled a bunch of research papers and a bunch of evidence and stuff about natural human speech. Please correct me if I'm wrong and find any flaws within my argument. Yeah, A sounds the best out of the three of them.

Test 2 (`examples/experiments/2026-11-05-ending3b.json`), four lines after the same lead-in, unlabelled in random order. Andy's note, verbatim:

> 2 and 3 sound best.

Key: line 1 "…just the two left now." (ends 0.2 st above floor), **line 2 "…just the two left now, so yeah." (4.1 st)**, **line 3 "…just the two left up top." (0.6 st)**, line 4 "…just the two left, okay." (3.4 st). Section 3 was regenerated with line 3 (picked blind twice, lower ending); both new takes ended low (2.6 and 3.3 st).

## Ending test for section 1 ("so that's on the list now")

Andy's note on the preview, verbatim:

> The preview is good, no other complaints. One thing: "that's on the list now" sounds unnatural to me. Too enthusiastic, too upbeat, it doesn't match the rest. That's my opinion though. Feel free to find flaws in it or disagree, and tell me if the research or your measurements say otherwise.

Measured: its last word ended low (1.3 st above floor) and its pitch level, peak and swing were no brighter than lines Andy liked, so pitch didn't explain it. Reading: the line announces the result of the action, which real narrators rarely do.

Test (`examples/experiments/2026-11-05-ending1b.json`): full section 1 reads, three endings, unlabelled in random order. Andy's notes, verbatim:

> Uh, 2 in one sound is the best, and I'm edging more towards two.

> I meant and 1

Key: **ending 2 "…and hit Enter, so that's one." (6.8 st above floor), picked first**; **ending 1 "…and hit Enter." (9.1 st), picked second**; ending 3 "…and hit Enter, so yeah." (2.1 st, the lowest), not picked. Section 1 now uses ending 2, take 2.
