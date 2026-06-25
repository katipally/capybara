---
name: capybaraa-help
description: Quick reference for capybaraa, what it does, the six pillars, and how to set the mode. Use when the user types /capybaraa-help or asks how capybaraa works.
disable-model-invocation: true
license: MIT
---

# Capybaraa Help

Render this card, change nothing.

```
 capybaraa: calm senior-dev mode.
 the six pillars are ALWAYS ON; they apply to every task. no command needed.

 PILLARS  CLARIFY  explore first, then clarify before coding: curated
                   questions + ASCII on the options + edge cases
          LEAN     YAGNI · reuse · stdlib first
          OPTIMAL  right data structure · best feasible complexity
          ECONOMY  terse · no useless comments · minimal tokens
          COMPLETE root-cause fix · run the check before claiming done
          HYGIENE  replace not pile-on · kill dead code/stale comments ·
                   sanitize · flag security

 SLASH    /capybaraa [lean|deep|off]         pick the mode
          /capybaraa-review                  review the diff against the pillars
          /capybaraa-audit                   scan the whole repo against the pillars
          /capybaraa-help                    this card

 DETAIL   full per-pillar guidance: references/principles.md

 MODES    lean = min tokens, build tight, ask only what blocks correctness
          deep = default; full clarify + ASCII + edge cases, complete code
 SIGNAL   replies open with  🦫 capybaraa · <mode>  and non-trivial work
          closes with a one-line sign-off, so you can see it is on
 OFF      "stop capybaraa"  or  /capybaraa off
 DEFAULT  CAPYBARAA_DEFAULT_LEVEL env (lean|deep|off), or
          ~/.config/capybaraa/config.json {"defaultLevel":"lean"}
```
