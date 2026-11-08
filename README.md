# claude-operator-kit

On October 4, 2026 my laptop ran hot. Fourteen Claude Code chats had been open for days, five
preview servers nobody remembered starting, a hidden Chrome that had burned 191 CPU-minutes, memory
full. On July 3 a fix had landed on top of another chat's uncommitted edits in the same file, in a
working tree holding 17 modified and 20 untracked files from several chats. Every rule in this kit carries the date of
the mistake that caused it. The two hooks put the ones that matter most into code, one that blocks
and one that reports, because a rule in a markdown file is a wish.

## What it does

Three kinds of files for a Claude Code setup where several sessions share one machine and
one working tree.

Two hooks:

- `hooks/guard-git-destructive.py` runs before every Bash command. In a shared working tree
  it denies `git reset --hard`, `git checkout -- .`, `git clean -f`, `git stash`,
  `git add -A`, `git add .`, `git add -u`, `git commit -a` and `git push --force`. It
  catches them at the start of the command, after `;`, `&`, `|`, `then` or `do`, and after
  an opening `(` or `{`. The command may be followed by a space, the end of the text, `;`,
  `&`, `|` or a closing `)`. So `git stash; echo x`, `(cd sub && git reset --hard)`,
  `git clean -fd|cat`, `(git stash)` and `{ git stash; }` are all denied. Quoted text does
  not trip it: `echo "git reset --hard"` and `echo "(git stash)"` pass, and so does a commit
  message that mentions one of those commands.
- `hooks/leftover-check.py` runs at session start. It lists what past sessions left
  running: hidden browsers, orphan dev servers, endless shell loops, Docker Desktop open
  for days, Claude sessions open for days. On a clean machine it prints nothing. It never
  stops anything.

Six rules, each opening with the date of the mistake behind it:

| Rule | Since | What it says |
|---|---|---|
| `rules/human-go-gates.md` | 2026-03-05 | Outbound messages, money, personal records, spending and publishing need a human go per run |
| `rules/verify-the-live-object.md` | 2026-06-16 | "Done" means checked against the live system, never the file |
| `rules/many-chats-one-tree.md` | 2026-07-03 | Several sessions, one checkout: work in your own worktree, stage by path |
| `rules/write-like-a-person.md` | 2026-08-13 | No em dashes, no chatbot phrasing, plain English |
| `rules/ask-before-shared-state-writes.md` | 2026-09-02 | Three tiers: read freely, ask the deciding fact, describe every write before it happens |
| `rules/stop-what-you-start.md` | 2026-10-04 | A session stops every background process it started |

Four skills:

| Skill | Use it when |
|---|---|
| `skills/handoff` | Work passes to another session. Every claim carries the command that proves it, and the receiver re-runs the proofs. |
| `skills/secret-exposure-responder` | A key shows up in output, a log, or a commit. Rotate now, with the rotation page for common providers. |
| `skills/skill-authoring` | You are writing or reviewing a skill. |
| `skills/visual-qa` | A UI change needs screenshots at three widths, read like a human, before anyone calls it done. |

## Run it

Clone the kit somewhere stable, then point your Claude Code settings at the hooks.
`install.md` has the exact settings block.

```bash
git clone https://github.com/jaysueno/claude-operator-kit.git
cd claude-operator-kit
```

- **Rules:** copy the files you want from `rules/` into the folder your sessions read
  rules from (for example `~/.claude/rules/`) and reference them from your `CLAUDE.md`.
- Skills: copy a skill folder into `~/.claude/skills/` (every repo) or
  `<repo>/.claude/skills/` (one repo).
- Hooks: wire both in a settings file as shown in `install.md`. Set
  `GUARD_SHARED_ROOTS` to the folder that holds your shared checkouts, or leave it unset
  to guard every folder.

Try the guard by hand:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git stash"},"cwd":"/srv/code/app"}' \
  | python3 hooks/guard-git-destructive.py
```

It prints a JSON deny decision. A safe command prints nothing.

## Test it

[![ci](https://github.com/jaysueno/claude-operator-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/jaysueno/claude-operator-kit/actions/workflows/ci.yml)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

78 tests, standard library plus pytest. The guard tests cover each blocked command and
the same commands after `;`, `&`, `&&`, `|`, `||`, `then`, `do`, `(` and `{`. They also cover
commands followed directly by `;`, `&`, `&&`, `|` or `)`, the quoted-text false-positive case,
and longer words that must still pass (`git add .gitignore`). The rest cover safe commands,
the shared-root and worktree exemptions, and three runs of the real hook over stdin.

The leftover tests feed invented process lists, so they never depend on what the test
machine is running. A clean machine stays silent. Hidden browsers, dev servers and endless
loops are reported with their pid. Docker Desktop is reported with how long it has been
open, and old Claude sessions with a count; neither line carries a pid. A pid that is gone
is not reported, and the report is capped.

## How it works

```text
 Claude Code session
   |
   |  before each Bash call (PreToolUse, matcher "Bash")
   v
 guard-git-destructive.py  <- JSON on stdin: tool_name, tool_input.command, cwd
   |   cwd under GUARD_SHARED_ROOTS (or no roots set)?        no  -> print nothing
   |   cwd or command inside an isolated worktree?            yes -> print nothing
   |   a destructive pattern at command position?             yes -> print a deny decision
   v
 Claude Code blocks the call and shows the reason


 session start (SessionStart)
   |
   v
 leftover-check.py -> ps -Ao pid,ppid,etime,command
   |   older than 24 hours and a known leftover shape?
   |   (dev servers count only when orphaned or started from a scratch folder)
   v
 nothing at all, or a short list the session relays in one line
```

The guard anchors each pattern at the start of the command, right after a separator (`;`,
`&`, `|`, `then`, `do`), or right after an opening `(` or `{`. The `(` or `{` counts only when
it sits at the start or after whitespace or a separator. That is why quoted text passes: in
`echo "git reset --hard"` the word `git` follows a quote, and in `echo "(git stash)"` the
paren follows a quote. It fails open:
bad input, a missing field or any exception means exit 0 with no output, so a guard bug can
never stop a session from working. Two environment variables shape it:

- `GUARD_SHARED_ROOTS`: folders whose checkouts are shared, separated by `:`. Unset means
  every folder is guarded.
- `GUARD_ISOLATED_MARKERS`: comma-separated path fragments that mark an isolated worktree.
  Default `/tmp/claude-,scratchpad`, which matches where Claude Code keeps a session's
  scratch folder.

The leftover check treats anything younger than 24 hours as probably still in use. It
counts Claude sessions open longer than 48 hours and mentions them only when there are at
least four. It reads a process's working folder through `/proc` on Linux and `lsof` on
macOS. Set `LEFTOVER_CHECK_DISABLE=1` on a server that runs long-lived services on purpose.

### Surgical scope at close-out

The kit does not ship a close-out skill, but this part of one belongs here. When several
sessions share a working tree, the session that finishes a task touches only the files it
created or changed for that task. Every other modified or untracked file is someone else's
work in progress.

- Re-run `git status -s` at the start. A status snapshot handed to you earlier is stale.
  Build the explicit list of files you touched.
- Stage by explicit path only: `git add <path1> <path2>`.
- Never run a whole-tree command: no hard reset, no `checkout -- .`, no stash, no clean.
- Never switch branches in a way that clobbers untracked files. Check `origin/main` with
  `git fetch` and `git show origin/main:<path>` instead.
- After staging, print `git status -s --untracked-files=no` and confirm nothing foreign is
  staged. If you are not sure a file is yours, ask, or leave it out.

## What it will not do

- **The guard is a pattern match, not a shell parser.** It reads the command text. A
  destructive command inside a script file passes, and so does one at the very start of a
  quoted `bash -c` string (`bash -c "git stash"`). A separator inside quotes can trip it
  (`echo "x; git reset --hard"` is denied).
- It is not your permission system. It denies a short list of commands and passes
  everything else to Claude Code's normal permission flow.
- The leftover check never stops a process. It reports. Stopping is the user's call.
- The rules enforce nothing on their own. They are text a session reads. The two hooks are
  the only parts that act.
- No business logic, no data, no network calls. Nothing here phones home.

## License

MIT. See `LICENSE`.
