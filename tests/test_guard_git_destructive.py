"""Tests for hooks/guard-git-destructive.py.

Most tests call decide() directly. Three run the hook as Claude Code does: JSON on stdin,
the decision on stdout, exit code 0 in every case.
"""
import json
import subprocess
import sys

import pytest

from conftest import HOOKS, load_hook

guard = load_hook("guard-git-destructive.py")
HOOK = str(HOOKS / "guard-git-destructive.py")


def bash(cmd, cwd):
    return {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": str(cwd)}


# Fixed fake paths, never created on disk: decide() only resolves them. A real temp folder
# could itself contain an isolation marker (some runners put TMPDIR under /tmp/claude-...).
SHARED_ROOT = "/srv/code"
REPO = "/srv/code/app"
OUTSIDE = "/srv/elsewhere"


@pytest.fixture
def shared():
    """A shared tree, a folder outside it, and an env that guards only the shared root."""
    env = {"GUARD_SHARED_ROOTS": SHARED_ROOT}
    return REPO, OUTSIDE, env


def denied(result):
    return (result or {}).get("hookSpecificOutput", {}).get("permissionDecision") == "deny"


@pytest.mark.parametrize("cmd", [
    "git reset --hard",
    "git reset --hard origin/main",
    "git checkout -- .",
    "git checkout .",
    "git clean -fd",
    "git stash",
    "git stash pop",
    "git add -A",
    "git add --all",
    "git add -u",
    "git add .",
    "git commit -am 'wip'",
    "git push --force",
    "git push origin main -f",
])
def test_blocks_destructive_command_in_shared_tree(shared, cmd):
    repo, _other, env = shared
    assert denied(guard.decide(bash(cmd, repo), env))


@pytest.mark.parametrize("cmd", [
    "cd sub && git reset --hard",
    "true; git stash",
    "make || git clean -f",
    "if true; then git reset --hard; fi",
    "while false; do git stash pop; done",
    "sleep 1 & git stash",
    "true | git reset --hard",
    "true|git stash",
])
def test_blocks_after_a_separator(shared, cmd):
    repo, _other, env = shared
    assert denied(guard.decide(bash(cmd, repo), env))


@pytest.mark.parametrize("cmd", [
    "git stash; echo x",
    "(cd sub && git reset --hard)",
    "git clean -fd|cat",
    "git add -A; echo x",
    "git add .; echo x",
    "git checkout -- .; echo x",
    "(cd sub && git stash)",
    "(git stash)",
    "{ git stash; }",
    "make && (git add -A)",
    "git stash&& echo x",
    "git stash& sleep 1",
    "git add -A|cat",
    "git push origin main -f; echo x",
])
def test_blocks_when_a_separator_follows_the_command(shared, cmd):
    repo, _other, env = shared
    assert denied(guard.decide(bash(cmd, repo), env))


@pytest.mark.parametrize("cmd", [
    "git add .gitignore; echo x",
    "git checkout ./src/app.py; echo x",
    "git stash-helper; echo x",
])
def test_a_longer_word_after_the_command_still_passes(shared, cmd):
    repo, _other, env = shared
    assert guard.decide(bash(cmd, repo), env) is None


@pytest.mark.parametrize("cmd", [
    'echo "git reset --hard"',
    "printf '%s\\n' 'never run git add -A here'",
    'git commit -m "explain why git stash was blocked"',
    'grep -n "git push --force" notes.md',
    'echo "(git stash)"',
    "echo '{git reset --hard}'",
])
def test_quoted_text_is_not_a_false_positive(shared, cmd):
    repo, _other, env = shared
    assert guard.decide(bash(cmd, repo), env) is None


@pytest.mark.parametrize("cmd", [
    "git add src/app.py tests/test_app.py",
    "git status -s",
    "git commit -m 'fix: stage by path'",
    "git commit --amend --no-edit",
    "git push --force-with-lease",
    "git checkout -b feat/x",
])
def test_allows_safe_commands_in_shared_tree(shared, cmd):
    repo, _other, env = shared
    assert guard.decide(bash(cmd, repo), env) is None


def test_allows_destructive_command_outside_shared_roots(shared):
    _repo, other, env = shared
    assert guard.decide(bash("git reset --hard", other), env) is None


def test_guards_every_folder_when_no_root_is_configured(shared):
    _repo, other, _env = shared
    assert denied(guard.decide(bash("git reset --hard", other), {}))


def test_allows_command_that_enters_an_isolated_worktree(shared):
    repo, _other, env = shared
    cmd = "cd /tmp/claude-1/session/scratchpad/wt && git reset --hard origin/main"
    assert guard.decide(bash(cmd, repo), env) is None


def test_allows_session_already_inside_an_isolated_worktree():
    assert guard.decide(bash("git stash", "/srv/session/scratchpad/wt"), {}) is None


def test_custom_isolated_markers_replace_the_default(shared):
    repo, _other, env = shared
    env = dict(env, GUARD_ISOLATED_MARKERS="/srv/worktrees/")
    assert denied(guard.decide(bash("cd scratchpad && git stash", repo), env))
    assert guard.decide(bash("cd /srv/worktrees/x && git stash", repo), env) is None


def test_ignores_tools_other_than_bash(shared):
    repo, _other, env = shared
    data = {"tool_name": "Edit", "tool_input": {"command": "git reset --hard"}, "cwd": str(repo)}
    assert guard.decide(data, env) is None


def test_deny_reason_names_the_command_and_the_tree(shared):
    repo, _other, env = shared
    out = guard.decide(bash("git stash", repo), env)
    reason = out["hookSpecificOutput"]["permissionDecisionReason"]
    assert "git stash" in reason
    assert REPO in reason
    assert out["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def run_hook(stdin_text, env):
    return subprocess.run([sys.executable, HOOK], input=stdin_text, capture_output=True,
                          text=True, env=env, timeout=20)


def test_end_to_end_deny_prints_json_and_exits_zero(shared):
    repo, _other, env = shared
    r = run_hook(json.dumps(bash("git reset --hard", repo)), env)
    assert r.returncode == 0
    assert json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_end_to_end_allow_prints_nothing(shared):
    repo, _other, env = shared
    r = run_hook(json.dumps(bash("git status", repo)), env)
    assert r.returncode == 0
    assert r.stdout == ""


def test_fails_open_on_malformed_input():
    r = run_hook("this is not json", {})
    assert r.returncode == 0
    assert r.stdout == ""
