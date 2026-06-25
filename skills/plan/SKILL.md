---
name: plan
description: Plan a feature or change the capybara way — clarify with ASCII diagrams, curated questions, and edge-case coverage before writing code. Use when the user asks to build/design/implement something non-trivial, or types /capybara:plan.
argument-hint: "[what to plan]"
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
license: MIT
---

# Capybara Plan — understand, then clarify, then build

The flagship, and the thesis of capybara: **understand before you act.** A
complete, future-proof spec beats a fast wrong one — and a real root-cause
implementation beats a patchwork. Stay **proportional**: a one-line change does
NOT need this. Run the full flow for features, multi-file changes, refactors, or
anything ambiguous.

## Flow

1. **Understand & research FIRST — before any question.** Read the prompt closely.
   Gather real context, learn the codebase, trace the actual flow end to end, and
   research/explore (read-only). Find existing code, patterns, and utilities to
   reuse (LEAN). Questions asked before this step are generic noise; questions
   asked after it are curated and worth the user's time.

2. **Diagram your understanding.** Show it as an ASCII diagram — architecture, data
   flow, or state — so your model and the user's match before any decision.
   ```
   [user] -> (validate) -> [store] -> (notify)
   ```

3. **Ask curated questions — as many as the requirement needs.** No fixed quota:
   it might be one question, it might be a dozen. Ask everything needed to clarify
   the spec fully; don't stop short and don't pad. Each question is grounded in what
   your exploration surfaced (AskUserQuestion caps at 4 per round — loop rounds
   until it's genuinely clear). **Put an ASCII diagram/sketch in (almost) every
   question** to make the options concrete and easy to understand — omit it only
   when a diagram would truly add nothing. Give the user the best option(s) up
   front — optimal and future-sighted — with tradeoffs and a recommendation. Never
   ask what the code or a sensible default already answers (ECONOMY).

4. **Edge cases, explicit.** List them and confirm handling: empty/null, huge
   input, concurrent access, failure/retry, auth/permission, malformed input,
   boundary values. Naming the edge case is half the fix.

5. **Spec → real implementation.** Write the recommended approach only — name the
   files to touch and the existing functions to reuse. Climb the LEAN ladder and
   implement the proper root fix, not a patch over the symptom. Finish with the
   COMPLETE done-gate (see /capybara:done).

Output terse and scannable. No filler. If a question has a clear default, take it
and say so in one line rather than asking.
