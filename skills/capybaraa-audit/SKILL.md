---
name: capybaraa-audit
description: >
  Scan the whole repository against capybaraa's seven pillars: clarify, lean, optimal,
  economy, complete, hygiene, sync. A ranked, codebase-wide report of over-engineering,
  dead code, bad complexity, filler, unfinished work, missing validation, and docs/tests
  out of sync with the code. One line per finding, biggest impact first, lists only, does
  not apply fixes.
  Use when the user says "audit this repo against the pillars", "capybaraa audit",
  "/capybaraa-audit", "what can I delete from this repo", or "find the bloat".
license: MIT
---

# Capybaraa Audit

Scan the entire repository against the seven pillars and report what a calm senior dev
would cut or fix. This is the whole-repo counterpart to `/capybaraa-review` (which only
looks at the current diff). It is a quality pass, not a correctness audit, and not a
security audit: for runtime bugs use `/code-review`, for exploits use `/security-review`.

Detailed guidance on each pillar: `references/principles.md`.

## How to run it

1. Map the repo first: source layout, entry points, the dependency manifest. Skip
   vendored code, lockfiles, build output, and `.git`.
2. Read the real source. For every problem, emit ONE line:

   `path:line: <tag> <what's wrong>. <the fix>.`

3. Rank the findings by impact, biggest first: the abstraction nobody uses, the
   dependency a few lines would replace, the dead module, before the stray comment.
4. Group nothing, pad nothing. End with a one-line verdict naming the top one to three
   things to delete or fix.

## Tags (one per pillar, same vocabulary as /capybaraa-review)

- `clarify:` a spec was guessed where nothing said it: a flag, a branch, a config key
  built on an assumption. Name the assumption.
- `lean:` something that does not need to exist: an abstraction with one caller, a
  config for a constant, a dependency for what stdlib or a few lines already do, dead
  flexibility kept "for later". Name what to delete or inline.
- `optimal:` wrong data structure or needless O(n^2) on a hot path. Name the better one.
- `economy:` filler comments that restate the code, dead prose, docs that lie about the
  code. Name the lines to cut.
- `complete:` a leftover TODO, a symptom patch over a real cause, or non-trivial logic
  with no test anywhere near it. Name the missing check or the real fix.
- `hygiene:` dead code, an orphaned old version left beside its replacement, a stale
  comment, or an unsanitized input at a trust boundary. Name what to remove or guard.
- `sync:` a doc, README, comment, test, or version string that describes a shape the code
  no longer has: a renamed symbol, a removed flag, a lagging version. Name what to update
  or delete so the repo stops lying about itself.

## Output shape

```
src/cache/CacheManager.js:1: lean: 180-line cache class wraps one Map with no eviction. Replace with a Map, add eviction when it's actually needed.
src/util/dates.js:1: lean: moment imported for one format() call. Use Intl.DateTimeFormat, drop the dependency.
src/legacy/parseV1.js:1: hygiene: whole module dead since v2 parser landed, no callers. Delete it.
src/api/handler.js:55: hygiene: req.body.id passed straight into the query, no validation. Guard it at the boundary.
src/report/build.js:30: optimal: findUser called inside the row loop, O(n^2). Build a Map of users once.
README.md:12: sync: documents a --verbose flag removed in v3, no longer parsed. Delete the line.
verdict: delete CacheManager and parseV1, drop moment. That's the bulk of the bloat.
```

## Boundaries

Lists findings only, does not edit files. Over-engineering, mess, dead code, and
unfinished work are in scope. Correctness bugs, security exploits, and performance
profiling are not, that is what `/code-review` and `/security-review` are for. If you
spot a real security hole while reading, flag it in one line and tell the user to run
`/security-review`. Do not fix it silently.
