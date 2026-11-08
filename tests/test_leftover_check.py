"""Tests for hooks/leftover-check.py.

The hook reads `ps` and, for dev servers, a process's working folder. Every test here feeds a
synthetic process list instead, so the result never depends on what this machine is running.
The pids and commands are invented.
"""
import subprocess
import sys

from conftest import HOOKS, load_hook

lc = load_hook("leftover-check.py")
HOOK = str(HOOKS / "leftover-check.py")

STALE = "2-03:00:00"      # 51 hours, past the 24 hour threshold
FRESH = "03:10:00"        # 3 hours, still in use


def no_cwd(_pid):
    return ""


def fake_run(ps_text, cwds=None):
    """A stand-in for the hook's sh(): answers ps and lsof from fixed text."""
    cwds = cwds or {}

    def run(cmd):
        if cmd[0] == "ps":
            return ps_text
        if cmd[0] == "lsof":
            pid = cmd[cmd.index("-p") + 1]
            return f"p{pid}\nfcwd\nn{cwds[pid]}\n" if pid in cwds else ""
        return ""
    return run


def test_clean_machine_is_silent(capsys):
    assert lc.main(env={}, run=fake_run("")) == ""
    assert capsys.readouterr().out == ""


def test_young_processes_stay_silent():
    rows = [
        ("4101", "1", FRESH, "/usr/bin/Google Chrome --headless --remote-debugging-port=9222"),
        ("4102", "1", FRESH, "node node_modules/.bin/astro dev --port 4321"),
    ]
    assert lc.find_leftovers(rows, no_cwd) == []


def test_reports_hidden_chrome_with_its_pid():
    rows = [("4201", "1", STALE, "/Applications/Chrome --headless --remote-debugging-port=9222")]
    lines = lc.find_leftovers(rows, no_cwd)
    assert lines == ["- hidden Chrome, running 2d (pid 4201)"]


def test_chrome_helper_processes_are_not_reported():
    rows = [("4202", "4201", STALE, "/Applications/Chrome --type=renderer --headless")]
    assert lc.find_leftovers(rows, no_cwd) == []


def test_reports_orphan_preview_server_with_port():
    rows = [("4301", "1", STALE, "node node_modules/.bin/astro dev --port 4321")]
    lines = lc.find_leftovers(rows, no_cwd)
    assert len(lines) == 1
    assert "preview server on port 4321" in lines[0]
    assert "(pid 4301)" in lines[0]


def test_reports_server_started_from_a_session_scratch_folder():
    rows = [("4401", "777", STALE, "python3 -m http.server 8000")]
    lines = lc.find_leftovers(rows, lambda pid: "/tmp/claude-1/session/scratchpad/site")
    assert len(lines) == 1 and "http.server" in lines[0]


def test_server_with_a_live_parent_outside_scratch_is_not_reported():
    rows = [("4501", "777", STALE, "pnpm --filter web dev")]
    assert lc.find_leftovers(rows, lambda pid: "/srv/code/web") == []


def test_dead_pid_is_not_reported():
    # The server exits between the ps snapshot and the folder lookup: lsof answers nothing for
    # that pid, so nothing ties it to a session and it is not reported. The pid is above the
    # largest pid Linux or macOS hands out, so no real /proc entry can answer for it.
    ps = "4999999   777 2-03:00:00 pnpm --filter web dev\n"
    assert lc.main(env={}, run=fake_run(ps, cwds={})) == ""


def test_reports_endless_loop():
    rows = [("4701", "1", STALE, "bash -c eval 'while true; do curl localhost:3000; sleep 5; done'")]
    lines = lc.find_leftovers(rows, no_cwd)
    assert len(lines) == 1 and lines[0].startswith("- endless loop: while true")
    assert lines[0].endswith("(pid 4701)")


def test_reports_docker_desktop_open_too_long():
    rows = [("4801", "1", "3-00:00:00", "/Applications/Docker.app/Contents/MacOS/com.docker.backend")]
    assert lc.find_leftovers(rows, no_cwd) == [
        "- Docker Desktop has been open 3d; quit it if no agent is using it"]


def test_reports_many_old_sessions_only_past_the_count():
    old = [(str(4900 + i), "1", "3-00:00:00", "claude --resume") for i in range(4)]
    assert lc.find_leftovers(old[:3], no_cwd) == []
    assert lc.find_leftovers(old, no_cwd) == [
        "- 4 Claude sessions have been open more than 2 days (each holds memory)"]


def test_report_is_capped_with_a_count_of_the_rest():
    rows = [(str(5000 + i), "1", STALE, "/Applications/Chrome --headless") for i in range(15)]
    lines = lc.find_leftovers(rows, no_cwd)
    assert len(lines) == lc.MAX_LINES + 1
    assert lines[-1] == "- and 3 more"


def test_report_block_tells_the_session_what_to_do(capsys):
    ps = "5101     1 2-03:00:00 /Applications/Chrome --headless\n"
    out = lc.main(env={}, run=fake_run(ps))
    assert out.startswith("# Leftover background processes on this machine")
    assert "Never stop another session's process" in out
    assert "(pid 5101)" in capsys.readouterr().out


def test_disabled_by_env_stays_silent():
    ps = "5201     1 2-03:00:00 /Applications/Chrome --headless\n"
    assert lc.main(env={"LEFTOVER_CHECK_DISABLE": "1"}, run=fake_run(ps)) == ""


def test_etime_parsing():
    assert lc.hours("05:00") == 5 / 60
    assert lc.hours("01:00:00") == 1
    assert lc.hours("2-00:00:00") == 48


def test_unreadable_ps_line_is_skipped_not_fatal():
    rows = [("5301", "1", "not-a-time", "/Applications/Chrome --headless")]
    assert lc.find_leftovers(rows, no_cwd) == []


def test_end_to_end_exits_zero():
    r = subprocess.run([sys.executable, HOOK], capture_output=True, text=True, timeout=30,
                       env={"LEFTOVER_CHECK_DISABLE": "1"})
    assert r.returncode == 0
    assert r.stdout == ""
