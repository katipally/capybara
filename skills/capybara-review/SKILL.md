---
name: capybara-review
description: >
  Review the current diff against capybara's six pillars: clarify, lean, optimal,
  economy, complete, hygiene. Finds guessed specs, speculative abstractions, bad
  complexity, filler, unfinished work, and mess left behind. One line per finding,
  lists only, does not apply fixes.
  Use when the user says "review against the pillars", "capybara review", "/capybara-review",
  or asks what's wrong with a change before they ship it.
license: MIT
---

# Capybara Review

Review the current change (the staged/unstaged diff, or the files the user names)
against the six pillars. This is a quality pass, not a correctness audit: it hunts
the things a calm senior dev would flag in review, not runtime bugs. For correctness
bugs use `/code-review`.

## How to run it

1. Get the diff: `git diff` plus `git diff --staged` (or read the files the user points at).
2. Read each changed hunk. For every problem, emit ONE line:

   `path:line: <tag> <what's wrong>. <the fix>.`

3. Group nothing, pad nothing. If a hunk is clean, say so and move on.
4. End with a one-line verdict: ship it, or fix the flagged lines first.

## Tags (one per pillar)

- `clarify:` the spec was guessed where the code or the request did not say. Name the
  assumption that should have been a question.
- `lean:` something that does not need to exist: an abstraction with one caller, a
  config for a constant, a dependency for what stdlib or a few lines already do, dead
  flexibility "for later". Name what to delete or inline.
- `optimal:` wrong data structure or needless O(n^2) on a hot path. Name the better one.
- `economy:` filler comments that restate the code, dead prose, a comment that explains
  the obvious. Name the lines to cut.
- `complete:` a leftover TODO, a symptom patch over the real cause, or non-trivial logic
  shipped with no test/build/lint run. Name the missing check or the real fix.
- `hygiene:` the old version left next to the new, a stale comment, dead code the change
  orphaned, or an unsanitized input at a trust boundary. Name what to remove or guard.

## Output shape

```
src/auth.js:42: lean: AuthFactory wraps one constructor. Inline it, call the class directly.
src/auth.js:88: complete: TODO "handle expiry" left in. Either handle it or open an issue and link it.
src/parse.js:15: optimal: nested .find in a loop, O(n^2). Build a Map once, look up in O(1).
src/parse.js:60: hygiene: old parseLine() still here, dead since line 15 replaced it. Delete it.
verdict: fix the four lines above, then ship.
```

## Boundaries

Lists findings only, does not edit files. Over-engineering, mess, and unfinished work
are in scope. Correctness bugs, security exploits, and performance profiling are not,
that is what `/code-review` and `/security-review` are for. If you spot a real security
hole while reading, flag it in one line and tell the user to run `/security-review`,
do not fix it silently.
