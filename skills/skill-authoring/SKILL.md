---
name: skill-authoring
description: >
  Scaffold a NEW Claude Code skill or review an EXISTING one against the house
  standard. Run when the user says "new skill", "write a skill for X", "review this
  skill", "skill audit", or when any session is about to create or modify a SKILL.md
  in any repo. Two modes: SCAFFOLD (create a convention-correct skill) and REVIEW
  (PASS/WARN/FAIL checklist). Salvaged 2026-07-12 from an older review-skill and
  skill-template pair, translated to Claude Code conventions.
argument-hint: "scaffold <name> <what it does> | review <path-or-name>"
---

# skill-authoring: scaffold and review skills to one house standard

A skill is a standing decision. The house standard: **a great skill encodes named
failures and executable checks, not aspirations.** Every rule in a skill body should
trace to something that actually went wrong (with a date) or a gate that binds (with a
pointer). If a rule can be a grep or a command instead of prose, make it one: notes and
prose demonstrably do not fire on their own (the lesson: a migration checklist lived in
notes for months and did not fire on its own).

## Mode: SCAFFOLD

1. **Conflict check first.** Search existing skills before creating one:
   `~/.claude/skills/` (global), `<repo>/.claude/skills/` (repo), and the loaded-skills
   list. If a skill half-covers the need, extend it. Do not fork a near-duplicate (a
   sharing skill once existed in three copies).
2. **Pick the scope deliberately.** Global (`~/.claude/skills/`) only if it applies
   across repos; otherwise the owning repo. One skill, one job.
3. **Write the frontmatter contract:**
   - `name`: kebab-case, matches the directory.
   - `description`: written so the MODEL knows WHEN to invoke it. Lead with the action,
     include trigger phrases users actually say, include when NOT to use it. This is the
     only part loaded every turn; it earns or wastes context.
   - `disable-model-invocation: true` on any skill with side effects (deploys, commits,
     sends, file moves, publishes): explicit `/` invocation only.
   - `allowed-tools`: restrict when the job does not need everything (review and read
     skills get Read, Grep, Glob; deploy skills do not need Write outside their lane).
   - `context: fork` for heavy read-only walks whose detail should not bloat the main
     session.
   - `argument-hint` when arguments exist.
4. **Body discipline.** State the WHY in one line, then executable steps. Reference
   canonical docs by path instead of restating them (cross-reference, do not duplicate).
   No hardcoded values that rot (campaign ids, counts, "verified" claims: live-surface
   claims expire); say where to fetch the live value instead. No secrets, ever. Scripts
   belong in `scripts/`, reference data in `references/`, state files nowhere in the
   skill folder.
5. **Wire the gates.** If the skill can touch outbound messages, money, personal or
   health records, spending, or publishing, name the binding gate
   (`rules/human-go-gates.md` in this kit) in the body. Standing autonomy never overrides
   a gate.
6. **Finish with REVIEW mode** on the new skill before handing it over.

## Mode: REVIEW: report PASS / WARN / FAIL per item, then a numbered fix list

### Structure
- [ ] `SKILL.md` exists; directory name equals frontmatter `name`
- [ ] Supporting files in `scripts/` or `references/`; no state files in the skill folder
- [ ] No duplicate or near-duplicate of another skill in scope (grep the fleet)

### Frontmatter
- [ ] `description` says WHEN to invoke (trigger phrases) and when NOT to
- [ ] Side-effect skill has `disable-model-invocation: true`
- [ ] `allowed-tools` present where the job is naturally narrow
- [ ] No secrets, no API keys, no tokens anywhere

### Body
- [ ] Rules trace to named incidents or gates (dates or doc pointers), not vibes
- [ ] Checks are executable (commands, greps) wherever possible
- [ ] References canonical sources by path; does not restate them
- [ ] No hardcoded values that rot (ids, counts, dated "verified" claims)
- [ ] Human-go gates named if the domain can touch them
- [ ] Proportionality stated: what the full protocol covers and what the light path is

### Fit
- [ ] Right scope (global or repo) for where it is used
- [ ] Description short enough to earn its per-turn context cost
- [ ] Would a fresh session with ONLY this skill succeed at the job? (The real test:
      skills run without the author's context.)

Severity: FAIL = will misfire or break a rule (fix before merge). WARN = style or
sturdiness. Be strict on FAIL, lenient on WARN.
