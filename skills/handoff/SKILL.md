---
name: handoff
description: >
  Standardized cross-repo and cross-session handoff with a verification contract. Two
  modes. HANDOFF: run when work passes to another session, repo or agent, or a session
  ends mid-project ("write a handoff", "hand this to the other repo", "pickup doc",
  end of session with open work). PICKUP: run when starting FROM a handoff doc ("pick up
  from", "continue the handoff", reading any *-HANDOFF*.md or PICKUP-*.md). Core contract:
  every factual claim carries the command or query that proves it, and pickup RE-RUNS the
  proofs before building on them. Exists because handoffs were hand-written every time
  and claims arrived unverified: a mapping that arrived inverted (2026-07-12) was only
  caught because the receiving session happened to re-derive it.
argument-hint: "handoff <target repo or session> | pickup <path to handoff doc>"
---

# handoff / pickup: claims travel with their proofs

## Mode: HANDOFF

Write `<PREFIX>-HANDOFF-<topic>-<YYYY-MM-DD>.md` in the OWNING repo's docs/ (or the
agreed relay location). Required sections, omit none:

1. **State of the world.** What is DONE and LIVE, what is done but unverified, what is
   not started. Every "live", "applied" or "merged" claim gets a **Proof:** line: the
   exact command or query the reader runs to confirm it (a git log line, a database
   query, a curl, an ls). A claim without a proof line may not be written; say
   "unverified" instead.
2. **The ask.** Precisely what the receiver should do, with acceptance criteria they
   can check themselves.
3. **Constraints and gates.** Which human-go gates, repo rules, or in-flight sessions
   bound the work. Name the files and the owners (for example, "one session owns the
   billing migration").
4. **Landmines.** Known gotchas with pointers to the doc or note that explains each
   one, so the receiver does not relearn them.
5. **Freshness stamp.** Date and time (with the timezone) plus the branch and commit the
   facts were read at. Live-surface claims expire; a stale stamp means re-verify
   everything.

Give the user the exact file path. They carry it to the next session.

## Mode: PICKUP

1. Read the handoff end to end, including any addenda at the bottom.
2. **Re-run every Proof line before building on its claim.** A proof that fails, or a
   claim without a proof, is treated as FALSE until re-derived from ground truth. This
   is the step that catches the inverted-mapping class of error.
3. Compare the freshness stamp with the live tree (`git log --oneline -5`, a fresh
   `git status`). The repo has usually moved since the handoff was written.
4. Write a 5-line pickup note at the bottom of the handoff doc (a dated ADDENDUM):
   proofs re-run (pass or fail per claim), deviations found, and what you are starting
   on. The handoff doc stays the single thread of record for the relay.

## Boundaries

Handoffs never contain secrets, personal data, or health records. Aggregates and
pointers only (see `rules/human-go-gates.md`). Money figures appear only with the proof
of the engine run attached, never a remembered number (see
`rules/verify-the-live-object.md`).
