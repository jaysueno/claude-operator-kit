#!/usr/bin/env python3
"""SessionStart hook: list background processes that past sessions left running.

Prints NOTHING when the machine is clean, so a normal session pays no context
cost. When something is left over it prints a short block the new session
relays to the user. It never stops anything: reporting only.
Rule: rules/stop-what-you-start.md

Born 2026-10-04 (a hot laptop: 14 sessions, 5 orphan preview servers, a
headless Chrome with 191 CPU-minutes, all left behind by sessions that had
ended).

Settings (environment variables, all optional):
  LEFTOVER_CHECK_DISABLE=1   stay silent on this machine. Use it on a server
                             that runs long-lived services on purpose.
  LEFTOVER_CHECK_SCRATCH     a path fragment that marks a session's scratch
                             folder. Default "/tmp/claude-". A dev server
                             started from there is a leftover once it is stale.
"""
import os
import re
import subprocess
import sys

STALE_HOURS = 24          # a leftover younger than this is probably still in use
OLD_CHAT_HOURS = 48       # an open session older than this is worth a nudge
OLD_CHAT_COUNT = 4        # report old sessions only when at least this many are open
MAX_LINES = 12
DEFAULT_SCRATCH = "/tmp/claude-"

SERVER = re.compile(
    r"(pnpm .*\bdev\b|astro(\.js)? (dev|preview)|next-server|next dev|\bvite\b|"
    r"node \S*server\.m?js|http\.server|uvicorn|flask run)"
)


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=4).stdout
    except Exception:
        return ""


def hours(etime):
    """ps etime ([[dd-]hh:]mm:ss) -> hours."""
    days = 0
    if "-" in etime:
        d, etime = etime.split("-", 1)
        days = int(d)
    parts = [int(p) for p in etime.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts
    return days * 24 + h + m / 60 + s / 3600


def age(h):
    return f"{h / 24:.0f}d" if h >= 48 else f"{h:.0f}h"


def cwd_of(pid, run=sh):
    """The working folder of a process, or "" when it cannot be read (or it is gone)."""
    proc = f"/proc/{pid}/cwd"
    if os.path.exists(proc):
        try:
            return os.readlink(proc)
        except OSError:
            return ""
    out = run(["lsof", "-a", "-p", pid, "-d", "cwd", "-Fn"])
    for line in out.splitlines():
        if line.startswith("n"):
            return line[1:]
    return ""


def parse_ps(text):
    rows = []
    for line in text.splitlines():
        parts = line.split(None, 3)
        if len(parts) == 4:
            rows.append(parts)
    return rows


def find_leftovers(rows, cwd_lookup, scratch=DEFAULT_SCRATCH):
    """Rows are (pid, ppid, etime, command) from ps. Returns the report lines (empty = clean)."""
    found, old_chats, docker_h = [], 0, None
    for pid, ppid, etime, cmd in rows:
        try:
            h = hours(etime)
        except ValueError:
            continue
        if "native-binary/claude" in cmd or cmd.startswith("claude "):
            if h >= OLD_CHAT_HOURS:
                old_chats += 1
            continue
        if "com.docker.backend" in cmd and "fork" not in cmd:
            docker_h = max(docker_h or 0, h)
            continue
        if h < STALE_HOURS:
            continue

        what = None
        if "Chrome" in cmd and "--type=" not in cmd and (
            "--headless" in cmd or "--remote-debugging-port" in cmd
        ):
            what = "hidden Chrome"
        elif "bash -c" in cmd and "while true" in cmd:
            m = re.search(r"eval '(.{0,60})", cmd)
            what = f"endless loop: {m.group(1) if m else cmd[:60]}"
        elif SERVER.search(cmd) and "bash -c" not in cmd:
            if ppid == "1" or scratch in cmd or scratch in cwd_lookup(pid):
                m = re.search(r"--port[= ](\d+)", cmd)
                what = "preview server" + (f" on port {m.group(1)}" if m else "")
                what += f": {SERVER.search(cmd).group(1)[:40]}"
        if what:
            found.append((h, pid, what))

    lines = [f"- {what}, running {age(h)} (pid {pid})" for h, pid, what in sorted(found, reverse=True)]
    if docker_h is not None and docker_h >= STALE_HOURS:
        lines.append(f"- Docker Desktop has been open {age(docker_h)}; quit it if no agent is using it")
    if old_chats >= OLD_CHAT_COUNT:
        lines.append(f"- {old_chats} Claude sessions have been open more than 2 days (each holds memory)")
    extra = len(lines) - MAX_LINES
    return lines[:MAX_LINES] + ([f"- and {extra} more"] if extra > 0 else [])


def render(lines):
    if not lines:
        return ""
    head = [
        "# Leftover background processes on this machine",
        "Past sessions left these running. Tell the user in ONE plain line near the top of",
        "your first reply and offer to stop them. Never stop another session's process",
        "without the user's go. Rule: rules/stop-what-you-start.md",
    ]
    return "\n".join(head + lines)


def main(env=os.environ, run=sh):
    if env.get("LEFTOVER_CHECK_DISABLE", "") not in ("", "0"):
        return ""
    scratch = env.get("LEFTOVER_CHECK_SCRATCH") or DEFAULT_SCRATCH
    rows = parse_ps(run(["ps", "-Ao", "pid=,ppid=,etime=,command="]))
    text = render(find_leftovers(rows, lambda pid: cwd_of(pid, run), scratch))
    if text:
        print(text)
    return text


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)  # a broken check must never block a session from starting
