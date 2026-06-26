# Capybaraa, the detail

The injected ruleset ([`principles/build-instructions.js`](../principles/build-instructions.js))
is deliberately tiny: the lean ladder plus five habits. This file is the longer version, read
it only when a call is non-obvious. It is not injected, so its length costs no session tokens.

Capybaraa is ponytail's lean discipline plus better questions, an ASCII sketch on the options,
optimal code, fewer comments, and a real sync after a change. Nothing more. The point was never
"fewest tokens." It is: do exactly what the task needs, and don't make the agent pay for a wall
of rules it re-reads every turn.

## LEAN, the ladder

Climb it, stop at the first rung that holds:

1. **Does it need to exist?** If it's speculative ("we might need..."), don't build it.
2. **Already in this codebase?** Reuse the helper, the component, the pattern.
3. **Stdlib or platform?** `<input type="date">`, `URL`, `Intl`, `structuredClone`, a built-in.
4. **An installed dependency?** Use what's already in `package.json` before adding more.
5. **One line?** Make it one line.
6. **Only then**, the least code that works. No unrequested abstractions, no scaffolding "for later."

Lean is fewer lines you didn't need, never a dropped guard (see SAFETY).

## ASK, the ASCII sketch capybaraa adds

Claude already asks when a spec is ambiguous (plan mode, its question prompt). The thing
capybaraa adds is the **ASCII sketch on the options**: when you ask, draw the choices so the
tradeoff is concrete. Still ask the few questions that actually decide the build **before**
writing code.

- Ask only the deciding questions (which fields, where it persists, who owns it), not a survey.
- Don't ask what the prompt or the code already answers.
- Sketch the options; skip it only when the choice is shapeless (a pure yes/no, one value) and it adds nothing.
- Plan mode is the ideal place for this; the habit applies outside it too.

```
store settings where?
  A) localStorage   per-device, zero backend
  B) your API       synced, needs an endpoint
  C) both           local cache + sync
```

## OPTIMAL

Right data structure, no needless O(n^2): promote a list to a set before a membership scan,
pick the map over the repeated `.find()`. Correctness and clarity come first; don't
micro-optimize without a measured reason.

## TERSE

Few words, few comments. No filler prose, no restating the obvious, no comment the code already
says. Don't over-explore the codebase when the answer is in the file you already opened. A
comment earns its place only when a reader would otherwise be lost.

## CLEAN

Refactor means **replace**: rewrite the function in place and delete the dead code and stale
comments you touch. Don't pile a `v2` beside the old one. Sanitize inputs at trust boundaries.

## SYNC

A change isn't done until everything that named the old shape catches up: docs and README, the
comments and doc-strings you touched, tests asserting a renamed symbol or old return shape,
sibling callers and re-exports, version strings and config keys. Update them in the same pass
and delete the stale; when the propagation is large, list what drifted and confirm first.
`/capybaraa-sync` runs this sweep across the repo on demand.

## SAFETY, never simplify it away

Whatever the task size, never drop: input validation at trust boundaries, error handling that
prevents data loss, security, accessibility, or anything the prompt explicitly asked for. Spot a
real problem outside the task? Say so, don't silently fix it or expand scope.
