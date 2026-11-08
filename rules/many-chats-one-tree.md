> Since 2026-07-03. A fix landed on top of another session's uncommitted edits in the same file.
> The shared working tree held 17 modified and 20 untracked files from several sessions and ten
> merged branches nobody had deleted. Nothing ever looked clean, and close-out could not tell
> whose file was whose.

# Many sessions, one working tree

Several sessions editing one checkout gives zero isolation. The rule for any non-trivial change:
work in your own git worktree off the remote default branch.

1. `git fetch origin`, then `git worktree add -b <branch> <path> origin/main`, with `<path>` in a
   scratch folder outside the repo. If you already drafted an edit in the shared tree, capture it
   as a patch and re-apply it in the worktree.
2. Do the work and verify it in the worktree. Its `git status` is truthful because it is isolated.
3. Pull request, squash merge, then remove the worktree and delete the branch in the same session.

**Never, in the shared tree:** `checkout -- .`, `reset --hard`, `stash`, `clean`, `add -A`,
`add .`, `add -u`, or a branch switch that clobbers another session's untracked files. Stage by
explicit path only. Any status snapshot you were handed at session start is stale; re-run
`git status` before acting.

Hygiene: cap active branches at about three, delete local branches whose remote is gone once
their content is on the default branch, and fast-forward local main when it drifts behind.
