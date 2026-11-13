Plan a batch of demo videos before anything is explored or written.

The videos, in order (id: "title" | what to show; site; the saved login it records with):
{videos}
{known}
Rules: one step of the task per section, about 15 to 35 seconds each; the opening is 10 to 12 seconds and starts on the app doing something; page loads and waits fall between sections. Keep to what each line asks for; add no videos, and invent no pages or buttons (say what must be explored instead). No two videos cover the same step. Anything a video creates in an account (a product, a course, a post) is named as a test ("NAVI test 1") and left unpublished; on a page that saves nothing to an account, use ordinary everyday examples instead. A buyer's view (login "as a member") never opens the dashboard, changes nothing, and shows course and module pages only: it never opens a lesson page (the owner's login sees the course editor there, not a buyer's lesson). A video about a lesson shows the module page that lists it.

Answer with this JSON and nothing else:

{{"videos": [{{"id": "<id>", "goal": "<one plain sentence: what the viewer can do after watching>",
  "start_url": "<the page the video opens on>",
  "sections": [{{"name": "<short_snake_case>", "shows": "<the one step this section shows, and what is clicked or typed>", "seconds": 20}}],
  "explore": ["<what the explorer must find out on the real pages: exact button names, where things sit, slow loads>"],
  "risks": ["<anything that could break the take, or that changes something it shouldn't>"]}}],
 "order_note": "<why this order, and what each video may assume from the one before>"}}
