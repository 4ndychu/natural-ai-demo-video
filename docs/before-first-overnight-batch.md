# Before your first overnight batch: the 2-minute restart test

NAVI's batches are built to carry on by themselves after the Mac restarts. That was tested by killing a running batch
(macOS started it again and it carried on), but not with a real restart of your Mac. Do this once, before you leave a
real batch running overnight. It uses a practice batch: two short test videos, no credits, nothing published, kept
apart from your real demos.

It takes about 2 minutes of your time, plus the restart.

1. **Start the practice batch.** In the NAVI folder, in Terminal (or ask Claude to run it):

   ```
   .venv/bin/python scripts/batch/restart_check.py start
   ```

   It says "The practice batch is running in the background". It records for about 8 minutes, so there's no rush,
   but do the next step within a few minutes.

2. **Restart the Mac.** Apple menu, then Restart. (Save anything else you have open first.)

3. **Log in.** The batch starts again when you log in, not before: macOS only runs it for a logged-in user. If your
   Mac asks for your password after a restart, a batch waits at that screen until you type it.

4. **Check.** Wait about a minute, then:

   ```
   .venv/bin/python scripts/batch/restart_check.py check
   ```

   - **PASS:** "after the restart the batch started again by itself and carried on". You're set. Run `check` again a
     few minutes later if it says it is still recording; when the batch is done it tidies itself away.
   - **NOT TESTED:** the Mac wasn't restarted since step 1. Do steps 2 to 4 again.
   - **FAIL:** tell Claude and include the last lines of the file it names.

## For the overnight batch itself

- **Keep the Mac on power.** NAVI keeps the Mac awake by itself while a batch is working, but a MacBook on battery
  with the lid shut goes to sleep whatever any app asks.
- **Don't shut the lid** unless an external screen is attached.
- **A restart in the night** (a macOS update, a power cut) stops the batch at the login screen until you log in.
  To stop macOS restarting for updates by itself: System Settings > General > Software Update > Automatic Updates,
  and switch off "Install macOS updates" for the night.
- You don't need to keep T3 Code, Claude Code or the NAVI app open. In the morning, open the app (or
  `scripts/batch/runner.py status <batch>`) and read the batch report.
