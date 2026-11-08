> Since 2026-09-02. One evening an agent wrote about 8,500 rows to a production database on a
> plan that had been approved in general terms. One assumption inside it was wrong, and the scope
> had grown from "thirty periods" to three years of history. Nobody had asked.

# Ask before acting on shared state

Shared state is anything another person or system reads: a database, a schema, a deploy, a file
other people sync. Three tiers.

**Tier 1, free.** Reading, probing, research, scratch files, code on a branch, an unmerged pull
request, dry runs, previews. Nothing shared changes. Do this without asking.

**Tier 2, ask the fact first.** When a design depends on something only the owner knows (whose
account a thing is, whether something was paid, what a label means), ask that one question before
designing. Show the two readings and what each one does. Never infer it from a phrase in a note.
Look at what the system already models before inventing anything.

**Tier 3, describe, then ask, before any write.** Every write to shared state gets one written
request in a fixed shape, then waits for a go:

    WRITE REQUEST: <object> | <row count or scope> | <amount if money> | <effect> | reverses by: <how>

A plan approval covers only the writes the plan listed with their numbers. "Go", "fix it", and
"do what you need" never cover a write the owner has not seen described. Batch pending requests
into one message. No new tables, columns, or functions unless that object was approved by name.
The smallest possible write, or none.

Adjacent problems come back as questions, not fixes.
