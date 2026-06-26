---
name: capybaraa-help
description: Quick reference for capybaraa, what it does, the seven pillars, the conscious gate, and how to turn it on or off. Use when the user types /capybaraa-help or asks how capybaraa works.
disable-model-invocation: true
license: MIT
---

# Capybaraa Help

Render this card, change nothing.

```
 capybaraa: calm senior-dev mode. one mode, always on, scaled to the task.
 the seven pillars apply to every task. no command needed.

 GATE     conscious gate: before any token-expensive move (deep exploration,
          subagents, full clarify, long output) check the spend is proportional.
          small task -> just do it. scope unclear & costly -> ask ONE question first.

 PILLARS  CLARIFY  explore first, then ask what's left: curated questions,
                   ASCII on any shaped choice (near-mandatory), edge cases
          LEAN     YAGNI · reuse · stdlib first
          OPTIMAL  right data structure · best feasible complexity
          ECONOMY  terse · no useless comments · minimal tokens
          COMPLETE root-cause fix · run the check before claiming done
          HYGIENE  replace not pile-on · kill dead code/stale comments ·
                   sanitize · flag security · mark deferrals with capybaraa:
          SYNC     after a change, update the docs/tests/refs/versions that
                   named the old shape · delete stale · /capybaraa-sync sweeps

 SLASH    /capybaraa [on|off]                turn it on or off
          /capybaraa-review                  review the diff against the pillars
          /capybaraa-audit                   scan the whole repo + deferral ledger
          /capybaraa-sync                    fix drift: code vs its docs/tests/refs
          /capybaraa-help                    this card

 DETAIL   full per-pillar guidance: references/principles.md

 SIGNAL   replies open with  🦫 capybaraa  and non-trivial work closes with a
          one-line sign-off, so you can see it is on
 OFF      "stop capybaraa"  or  /capybaraa off
 DEFAULT  CAPYBARAA_DEFAULT_LEVEL env (on|off), or
          ~/.config/capybaraa/config.json {"defaultState":"off"}
```
