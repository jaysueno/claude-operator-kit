# Install

The hooks are plain Python 3 scripts with no dependencies. Claude Code runs them as commands
and passes the hook input as JSON on stdin.

## 1. Put the kit somewhere stable

```bash
git clone https://github.com/jaysueno/claude-operator-kit.git <path-to-kit>
```

Replace `<path-to-kit>` with an absolute path you will not move, for example a folder under
your home directory.

## 2. Wire the hooks in a settings file

Add this to a Claude Code settings file. `~/.claude/settings.json` applies to every
project; `<repo>/.claude/settings.json` applies to one repo. Merge it with any `hooks` and
`env` keys you already have.

```json
{
  "env": {
    "GUARD_SHARED_ROOTS": "<folder-that-holds-your-shared-checkouts>"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 <path-to-kit>/hooks/guard-git-destructive.py",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 <path-to-kit>/hooks/leftover-check.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Placeholders:

| Placeholder | Replace with |
|---|---|
| `<path-to-kit>` | the absolute path of your clone |
| `<folder-that-holds-your-shared-checkouts>` | the parent folder of the repos several sessions share. Several folders: join them with `:`. Leave the whole `env` entry out to guard every folder. |

When `GUARD_SHARED_ROOTS` is unset or empty, the guard checks every folder.

Optional environment variables:

| Variable | Default | Effect |
|---|---|---|
| `GUARD_SHARED_ROOTS` | unset (guard everywhere) | only a cwd under these folders is guarded |
| `GUARD_ISOLATED_MARKERS` | `/tmp/claude-,scratchpad` | path fragments that mark an isolated worktree; a cwd or command containing one is not guarded |
| `LEFTOVER_CHECK_DISABLE` | unset | set to `1` to keep the leftover check silent on this machine |
| `LEFTOVER_CHECK_SCRATCH` | `/tmp/claude-` | path fragment of a session's scratch folder; a dev server started there counts as a leftover once it is stale |

## 3. Check that it works

Start a new session in a shared checkout and ask it to run `git stash`. The call is
denied with a reason that names the command and the folder. Then ask it to run
`git status`; that passes.

Run the leftover check by hand. On a clean machine it prints nothing:

```bash
python3 <path-to-kit>/hooks/leftover-check.py; echo "exit $?"
```

## 4. Rules and skills

- Rules: copy the files you want from `rules/` into the folder your sessions read, for
  example `~/.claude/rules/`, and list them in your `CLAUDE.md`.
- Skills: copy a folder from `skills/` into `~/.claude/skills/` or
  `<repo>/.claude/skills/`. Claude Code finds it by the `name` in its `SKILL.md`.

## Remove

Delete the two hook entries from the settings file. Nothing else was installed.
