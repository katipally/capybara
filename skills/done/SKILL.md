---
name: done
description: The done-gate — verify a change actually works before claiming "done". Use when finishing a non-trivial change, before saying it's complete, or when the user types /capybara:done.
allowed-tools: Read, Grep, Glob, Bash
license: MIT
---

# Capybara Done — verify, then claim

"Agent said done but it wasn't" is the failure this kills. Never claim success
unverified. **Proportional:** a typo or one-liner needs no gate; non-trivial
logic (a branch, loop, parser, money/security/data path) does.

## Gate

1. **Checklist** (read the diff against it):
   - Does what was asked — all of it, no half-done corners.
   - No leftover TODOs, no commented-out old code, no dead branches.
   - Edge cases from planning handled.
   - HYGIENE: stale comments removed, inputs sanitized, no security regression.
   - Root cause fixed, not just the reported symptom.

2. **Run the real check.** Actually execute the relevant test / build / lint /
   typecheck. Report the REAL output — pass or fail. If it fails, say so and fix;
   do not narrate success over a failing command.

3. **Leave one runnable check** for non-trivial logic — the smallest thing that
   fails if the logic breaks (an assert-based self-check or one small test). No
   frameworks or fixtures unless the repo already uses them.

Sign-off line, honest and short: what you ran, what it returned, what's left.
