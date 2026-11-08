> Since 2026-06-16. A pay figure was stated from a spreadsheet instead of the engine that computes
> pay. It was wrong. The same month, a merged migration file was reported as "applied" when the
> database had never seen it.

# Verify against the live object, never the file

"Applied", "merged", "deployed", and "done" mean confirmed against the real thing: the database
row or policy, the running service, the real output. Never that a file was written or a pull
request was merged.

- A number is stated only after the real engine ran on live data and the result was reconciled.
  A value you cannot verify is "unknown", never a guess.
- A migration is applied when the live schema shows the object, not when the SQL is in the repo.
- A deploy is done when the running service answers with the new behavior, not when the pipeline
  went green.
- A commit message is a forecast. Re-probe the live system before you build on what it claims.

Verification is the bottleneck of every loop, so make it fast: one command that prints the live
state, pasted into the report next to the claim.
