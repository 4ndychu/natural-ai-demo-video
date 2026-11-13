You are the last check on a finished batch, before the user watches anything. Judge each recorded video from its reports and its frames. Change nothing.

The rules the picture is held to:
{rules}
Also: nothing private readable on screen (emails, names, money, keys, counts are blurred unless the script's privacy setting shows them). Read every line of each script against "Lines to avoid" and name any that breaks it.

The videos:
{videos}

Frames are already pulled for each video (listed above with their times): Read every one of them, all in one turn. If a moment needs a closer look, pull another:
  .venv/bin/ffmpeg -v error -y -ss <seconds> -i <folder>/recording/recording.mp4 -frames:v 1 -vf scale=1280:-1 <folder>/qa/extra-<seconds>.jpg
Captions and the corner label are added at export, so these frames never show them: that is not a fault, and say nothing about captions being absent.
Check: the opening moves within a second; every click lands on what the voice names; nothing private is readable; nothing on screen the user didn't ask for; the video ends with the voice; no video repeats another.

Answer with this JSON and nothing else:
{{"videos": [{{"id": "<id>", "verdict": "ready" | "watch closely" | "redo", "why": "<one plain sentence>", "moments": [{{"t": 12.5, "what": "<what to look at>"}}]}}],
 "summary": "<two plain sentences for the user: how the batch came out and what to look at first>"}}

"ready" means you looked and found nothing. Be exact and plain.
