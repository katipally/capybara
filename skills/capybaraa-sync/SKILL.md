---
name: capybaraa-sync
description: >
  Find and fix drift between the code and everything that describes it: docs, README,
  comments, tests, sibling code, config, version strings. Lists each gap, confirms, then
  updates in one pass and deletes the stale. Use when the user says "capybaraa sync",
  "/capybaraa-sync", "keep the docs in sync", "did anything go stale after that change",
  or after a rename/refactor/version bump that ripples outward.
license: MIT
---

# Capybaraa Sync

A change isn't done until everything that referenced the old shape catches up (COMPLETE
pillar). This skill sweeps the repo for that drift and closes it, so the codebase stays
coherent without the user having to chase every reference by hand. It is the deliberate,
whole-repo version of the always-on reflex; `/capybaraa-review` and `/capybaraa-audit`
judge quality, this one fixes coherence.

Detailed guidance: [`references/principles.md`](../../references/principles.md) (COMPLETE, HYGIENE).

## How to run it

1. Establish what changed. Prefer the diff (`git diff`, `git diff --staged`, recent
   commits); if there's no VCS signal, take the area the user names as the source of truth.
2. From the changed code, find what now disagrees with it. Skip vendored code, lockfiles,
   build output, and `.git`. Look for drift in:
   - **docs**: README, CHANGELOG, `references/`, skill descriptions, help cards
   - **comments**: doc comments and inline notes that describe the old behavior
   - **tests**: assertions naming a renamed symbol, an old return shape, a dropped flag
   - **sibling code**: other callers, re-exports, type defs built on the old shape
   - **config & metadata**: version strings across manifests, env-var names, keywords
3. For every gap, emit ONE line:

   `path:line - <what's stale> drifted from <the change>. <the fix>.`

4. **Confirm before applying.** Show the list, say what you'll change and what you'll
   delete, and wait for a go-ahead - unless the user already said "just sync it". For a
   one-line obvious propagation, just do it and note it; the confirm is for the big or
   risky sweeps.
5. Apply in one pass: update the live references, **delete** the stale ones (don't leave
   the old line beside the new - HYGIENE), and re-run the repo's check if one exists.
6. End with a one-line tally: `N references synced, M stale removed.` or
   `In sync. Nothing drifted.`

## Output shape

```
README.md:140 - "two modes lean/deep" drifted from the single-mode change. Rewrite to on/off.
plugin.json:3 - version 0.2.4 drifted from the 0.3.0 bump. Bump to match.
test/auth.test.js:22 - asserts getLevel(), renamed to getState(). Update the call.
src/legacy.js:1 - re-exports parseV1, deleted in this change. Remove the dead re-export.
verdict: 4 references drift. Apply? (3 updates, 1 deletion)
```

## Boundaries

Coherence only: it makes the docs/tests/refs agree with the code, it does not redesign or
add features. It will delete stale text and dead references it can prove are orphaned by
the change, after confirming. It does not invent new docs the repo never had, and it does
not touch out-of-scope code unrelated to the change (that's a HYGIENE "surface and ask",
not a silent edit). Correctness bugs and over-engineering stay with `/capybaraa-review`
and `/capybaraa-audit`.
