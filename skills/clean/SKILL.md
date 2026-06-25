---
name: clean
description: Hygiene pass over code you're changing — remove dead code and stale comments, sanitize inputs, and surface security issues. Use when refactoring, after a big change, or when the user types /capybara:clean.
allowed-tools: Read, Grep, Glob, Bash
license: MIT
---

# Capybara Clean — leave it cleaner than you found it

Scope to what the change touches (don't re-audit the whole repo — that's a
separate ask). HYGIENE pillar in action.

Pass:
1. **Replace, don't pile on.** Refactor left the old version behind? Delete it.
   No `foo_old`, no commented-out blocks "just in case".
2. **Stale comments.** A comment that describes code that no longer exists, or
   lies about what's there now → fix or delete. Comments explain PRESENT code,
   only where a reader needs them. Remove noise comments (`// increment i`).
3. **Sanitize.** Inputs crossing a trust boundary (user, network, file, env) →
   validate/escape. Don't simplify this away.
4. **Security smell.** Hardcoded secret, injection vector, missing authz, unsafe
   deserialization → flag it.

**Out-of-scope finds → surface & ask, don't silently fix.** Report: file:line,
what, why it matters, suggested fix. Let the user decide before you expand scope.
