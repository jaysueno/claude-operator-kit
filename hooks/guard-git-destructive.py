#!/usr/bin/env python3
"""PreToolUse guard: deny destructive git commands in shared working trees.

Enforces rules/many-chats-one-tree.md ("Never, in the shared tree") as code
instead of prose: git reset --hard / checkout -- . / clean -f / stash /
add -A|.|-u / commit -a / push --force are denied when the session cwd is a
shared working tree. Isolated worktrees (the session scratchpad or a temp
folder) pass through to the normal permission flow.

Which folders count as shared:
  GUARD_SHARED_ROOTS   a list of folders separated by the path separator
                       (":" on macOS and Linux). A cwd under any of them is
                       guarded. When unset or empty, every cwd is guarded.
  GUARD_ISOLATED_MARKERS
                       a comma-separated list of path fragments that mark an
                       isolated worktree. Default: "/tmp/claude-,scratchpad".
                       A cwd containing one, or a command that mentions one
                       (for example a cd into the worktree), is not guarded.

Fail-open by design: any error exits 0 with no output so a guard bug can
never brick the harness. Wire it with a PreToolUse matcher "Bash" in a Claude
Code settings file (see install.md).
"""
import json
import os
import re
import sys

DEFAULT_ISOLATED_MARKERS = "/tmp/claude-,scratchpad"

# Anchored at command start or after a separator so quoted/echoed strings
# don't false-positive. An opening "(" or "{" also starts a command, but only
# at the start or after whitespace or a separator, so echo "(git stash)" passes.
SEP = r"(?:^|[;&|]\s*|(?<![^\s;&|])[({]\s*|\bthen\s+|\bdo\s+)"
# What may follow a command word: whitespace, the end, or a shell separator
# or a closing subshell paren, so "git stash; echo x" is caught too.
END = r"(\s|$|[;&|)])"
PATTERNS = [
    (rf"{SEP}git\s+reset\s+--hard", "git reset --hard"),
    (rf"{SEP}git\s+checkout\s+(--\s+)?\.{END}", "git checkout ."),
    (rf"{SEP}git\s+clean\s+-\w*f", "git clean -f"),
    (rf"{SEP}git\s+stash{END}", "git stash"),
    (rf"{SEP}git\s+add\s+(-A|-u|--all){END}", "git add -A/-u"),
    (rf"{SEP}git\s+add\s+\.{END}", "git add ."),
    (rf"{SEP}git\s+commit\s+-\w*a", "git commit -a"),
    (rf"{SEP}git\s+push\s+.*(--force(?!-with-lease)|\s-f{END})", "git push --force"),
]


def shared_roots(env):
    """The guarded roots, resolved. An empty list means: guard every cwd."""
    raw = env.get("GUARD_SHARED_ROOTS", "") or ""
    roots = []
    for part in raw.split(os.pathsep):
        part = part.strip()
        if part:
            roots.append(os.path.realpath(os.path.expanduser(part)))
    return roots


def isolated_markers(env):
    raw = env.get("GUARD_ISOLATED_MARKERS")
    if raw is None:
        raw = DEFAULT_ISOLATED_MARKERS
    return [m.strip() for m in raw.split(",") if m.strip()]


def under(path, root):
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def decide(data, env):
    """Return the deny payload for one hook input, or None to pass through."""
    if data.get("tool_name") != "Bash":
        return None
    cmd = (data.get("tool_input") or {}).get("command", "") or ""
    cwd = data.get("cwd") or os.getcwd()
    cwd = os.path.realpath(os.path.expanduser(cwd))

    roots = shared_roots(env)
    if roots and not any(under(cwd, r) for r in roots):
        return None
    markers = isolated_markers(env)
    # A session already inside an isolated worktree, or a command that cd's
    # into one first, is exempt.
    if any(m in cwd for m in markers) or any(m in cmd for m in markers):
        return None

    for pat, label in PATTERNS:
        if re.search(pat, cmd):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"Blocked '{label}' in shared tree {cwd}. "
                        "Many sessions share this working tree (rules/many-chats-one-tree.md): "
                        "stage by explicit path only; destructive git commands belong in an "
                        "isolated worktree off origin/main (create it in the session scratchpad)."
                    ),
                }
            }
    return None


def main():
    data = json.load(sys.stdin)
    out = decide(data, os.environ)
    if out is not None:
        print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
