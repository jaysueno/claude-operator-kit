# AGENTS.md

Instructions for an AI agent working in this repo.

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Python 3.10 or newer. pytest is the only dependency, and it goes in `.venv`, never into the
system Python.

## Run

The hooks read JSON on stdin and print a decision or nothing:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git status"},"cwd":"/srv/code/app"}' \
  | python3 hooks/guard-git-destructive.py
LEFTOVER_CHECK_DISABLE=1 python3 hooks/leftover-check.py
```

## Test

```bash
.venv/bin/python -m pytest -q
```

CI runs the same `pytest` command (`.github/workflows/ci.yml`). Every change to `hooks/`
needs a passing run, and a new behavior needs a new test.

## Where you may edit

- `hooks/`, `tests/`: code and its tests. Keep the hooks fail-open (any error means exit 0
  and no output) and keep them on the standard library.
- `skills/`, `README.md`, `install.md`, `AGENTS.md`: plain technical prose.

## Where you may not edit

- `rules/`: the six rule files are the owner's words, frozen. Change one only with the
  owner's go.
- `LICENSE`.

## Never

- Never commit `.venv/`, caches, or anything listed in `.gitignore`.
- Never add a real person's name, a home-folder path, an IP address, an email address, or a
  key or token, not even in a test. Tests use invented pids, commands and paths.
- Never write a literal key prefix in the secret skill. Name providers in words.
- Never make a hook stop a process or change a file. The guard denies; the leftover check
  reports.
- Never use em dashes in prose (`rules/write-like-a-person.md`).

## Before each commit

Run the identity and secret scan over the tree and the history: no names, home paths,
addresses, emails, or key shapes. The maintainer's scan reads a private term list named
`identity-terms.txt`, which is gitignored here so it can never ship. Then run the tests.
