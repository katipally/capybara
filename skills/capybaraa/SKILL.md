---
name: capybaraa
description: Turn capybaraa on or off, or explain what it is. Use when the user types /capybaraa, says "capybaraa", "stop capybaraa", "start capybaraa", or asks what capybaraa does.
argument-hint: "[on|off]"
license: MIT
---

# Capybaraa

Lean senior-dev mode. One mode, always-on, no dial: a tiny ruleset is injected every
session and applies to every task, scaled to its size. No command needed to use it.

It is ponytail's lean discipline plus five habits:

**LEAN** (the ladder: does it need to exist? reuse what's here? stdlib or platform? installed
dep? one line? then minimal code) · **ASK** (Claude already asks; capybaraa adds an ASCII
sketch on the options when you do, for the questions that decide the build) · **OPTIMAL** (right data
structure, no needless O(n^2)) · **TERSE** (few words, few comments, no filler) · **CLEAN**
(refactor means replace: rewrite in place, delete the dead code you touch) · **SYNC** (a change
isn't done until the docs, tests, and refs that named the old shape catch up;
`/capybaraa-sync` sweeps the repo on demand).

It never drops a guard for fewer lines: input validation, error handling, security, and
accessibility stay, whatever the task size.

The ruleset is deliberately small; a plugin that preaches lean while injecting a wall of rules
every turn is the irony. Longer guidance lives in
[`references/principles.md`](../../references/principles.md), read it when a call is non-obvious.

Substantive replies open with a `🦫` so you can see capybaraa is on. No other ceremony.

## On / off (this is all the slash command does)

There is no `lean`/`deep` to pick anymore: capybaraa adapts to each task on its own.
The command only toggles it.

| `/capybaraa on` | turn it on (default; this is the normal state) |
| `/capybaraa off` | turn it off. "stop capybaraa" / "normal mode" also turn it off |

When invoked with an argument, the UserPromptSubmit hook persists it, so just
acknowledge the new state in one line. With no argument, explain what capybaraa is and
report the current state. To make `off` the default for every session, set
`CAPYBARAA_DEFAULT_LEVEL=off` (or `defaultState` in `~/.config/capybaraa/config.json`).

Related: `/capybaraa-review` reviews the current diff against the rules,
`/capybaraa-audit` scans the whole repo for bloat and drift,
`/capybaraa-sync` fixes drift between the code and its docs/tests/refs, and
`/capybaraa-help` prints the quick-reference card.
