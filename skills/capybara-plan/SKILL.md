---
name: capybara-plan
description: Plan a feature or change the capybara way — clarify with ASCII diagrams, grouped questions, and edge-case coverage before writing code. Use when the user asks to build/design/implement something non-trivial, or types /capybara-plan.
argument-hint: "[what to plan]"
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
license: MIT
---

# Capybara Plan — CLARIFY before code

The flagship. A complete, minimal spec beats a fast wrong one. But stay
**proportional**: a one-line change does NOT need this — just do it. Run this flow
for features, multi-file changes, or anything ambiguous.

## Flow

1. **Read first.** Explore read-only. Find existing code/patterns/utilities to
   reuse (LEAN) before proposing anything new. Trace the real flow end to end.

2. **Diagram it.** Show your understanding as a small ASCII diagram — architecture,
   data flow, or state. Make the user's mental model and yours match before deciding.
   ```
   [user] -> (validate) -> [store] -> (notify)
   ```

3. **Ask, batched.** Use AskUserQuestion: **3-4 grouped questions per round, 1-3
   rounds**. Explain each tradeoff so the user can actually decide. Don't ask what
   the code or a sensible default already answers (ECONOMY). Recommend an option.

4. **Edge cases, explicit.** List them and confirm handling: empty/null, huge
   input, concurrent access, failure/retry, auth/permission, malformed input,
   the boundary values. Naming the edge case is half the fix.

5. **Spec, minimal.** Write the recommended approach only — not every alternative.
   Name the files to touch and the existing functions to reuse. Then climb the LEAN
   ladder to implement, and finish with the COMPLETE done-gate (see capybara-done).

Output the plan terse and scannable. No filler. If a question has a clear default,
take it and say so in one line rather than asking.
