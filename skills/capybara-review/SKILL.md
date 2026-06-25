---
name: capybara-review
description: Review the current diff against the 6 capybara pillars — what to delete, simplify, optimize, or clean. Use when the user says "capybara review", "review for bloat", or types /capybara-review.
allowed-tools: Read, Grep, Glob, Bash
license: MIT
---

# Capybara Review

Review the diff (`git diff`) for pillar violations only — not general correctness
(use /code-review for bugs). One line per finding: location, tag, what, fix.

```
L<line>: <tag> <what>. <replacement>.
```

Tags:
- `lean:`    reinvented stdlib/existing util, unneeded dep, abstraction with one user
- `optimal:` needless O(n^2), wrong data structure, repeated work
- `economy:` useless comment, dead code, filler, restating the obvious
- `complete:` leftover TODO, unverified claim, symptom-patch not root cause
- `hygiene:` old code left beside new, stale comment, unsanitized input, security smell

End with: `net: -<N> lines, -<M> deps, +<K> checks.` Only flag what you're
confident about. No nitpicking style the repo already accepts.
