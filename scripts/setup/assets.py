"""Test assets that are not in the repo. The batch, blind, runner, focus and load checks reuse the voice takes of the
approved to-do demo (examples/test-todo-b.json), so they spend no credits. Those takes are audio, which never goes in
the repo: each clone makes them once. Without them those checks stop with exit code 77 ("skipped") and say how.
"""
import glob
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TODO_TAKES = os.path.join(ROOT, 'output', 'test-todo-v4')
SKIPPED = 77

HOW = ('This check reuses the to-do demo\'s voice takes in output/test-todo-v4, which aren\'t in the repo (they are audio). '
       'Make them once (it prints the credits first and spends nothing without --yes):\n'
       '  .venv/bin/python scripts/voice/generate.py examples/test-todo-b.json --out output/test-todo-v4 --takes 2\n'
       '  .venv/bin/python scripts/timing/timing.py examples/test-todo-b.json output/test-todo-v4')


def need_todo_takes():
    """Stop the calling check, as skipped, when the saved to-do takes aren't there."""
    if not glob.glob(os.path.join(TODO_TAKES, '*_take1*')) or not os.path.exists(os.path.join(TODO_TAKES, 'timing.json')):
        print('SKIPPED: ' + HOW, flush=True)
        sys.exit(SKIPPED)
